import random
from collections.abc import Iterator
from typing import Generator

import numpy as np
import tensorflow as tf
import tf_agents.utils.common as tf_agents_common
from tf_agents.agents.dqn.dqn_agent import DqnAgent
from tf_agents.agents.tf_agent import LossInfo
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.networks.q_network import QNetwork
from tf_agents.replay_buffers.tf_uniform_replay_buffer import TFUniformReplayBuffer
from tf_agents.trajectories import PolicyStep, policy_step, trajectory
from tf_agents.trajectories.time_step import StepType, TimeStep

from crawlai.grid import Grid
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.model import extract_inputs
from crawlai.model.environment import CritterEnvironment
from crawlai.position import Position
from crawlai.turn import Turn


class AICritterMixin(BaseCritter):
    CHOICES = [
        Turn(Position(*c), is_action)
        for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
        for is_action in (True, False)
    ] + [Turn(Position(0, 0), False)]
    INPUT_RADIUS = 15  # TODO: Attempt making this much, much smaller
    LAYERS = {"Critter": 1, "Food": 2}

    # Params for data collection
    REPLAY_BUFFER_CAPACITY = 100000

    # Params for train
    TRAIN_BATCH_SIZE = 64
    LEARNING_RATE = 1e-3
    # TODO: Look into N_STEP_UPDATE

    # Step type constants
    class _BatchedStepType:
        """Optimize away the expanding of dimensions when creating a 'batched'
        timestep of batch size 1."""

        FIRST = tf.expand_dims(StepType.FIRST, axis=0)
        MID = tf.expand_dims(StepType.MID, axis=0)
        LAST = tf.expand_dims(StepType.LAST, axis=0)

    def __init__(self) -> None:
        super().__init__()
        # Stats
        self.train_loss: LossInfo | None = None
        self.steps = 0
        self._last_step_health = self.health

        # Stats purely for logging
        self.deaths = 0
        self.total_reward = 0

        # Created on the first call of self.next_step
        self._move_loop_generator: Iterator[Turn] | None = None

        environment = CritterEnvironment(
            input_radius=self.INPUT_RADIUS,
            input_dtype=extract_inputs.INPUT_DTYPE,
            n_choices=len(self.CHOICES),
            n_layers=len(self.LAYERS) + 1,
        )

        # TODO get rid of with tf-agents==0.5.0
        environment = TFPyEnvironment(environment, isolation=False)
        self.env: TFPyEnvironment = environment

        q_net = QNetwork(self.env.observation_spec(), self.env.action_spec())

        self.agent = DqnAgent(
            time_step_spec=self.env.time_step_spec(),
            action_spec=self.env.action_spec(),
            gamma=0.6,
            # target_update_period=5,  # TODO: bench perf
            # target_update_tau=0.05,  # TODO: bench perf
            q_network=q_net,
            optimizer=tf.compat.v1.train.AdamOptimizer(
                learning_rate=self.LEARNING_RATE
            ),
        )
        self.agent.initialize()

        self.replay_buffer = TFUniformReplayBuffer(
            data_spec=self.agent.collect_data_spec,
            batch_size=self.env.batch_size,
            max_length=self.REPLAY_BUFFER_CAPACITY,
        )

    def get_turn(self, grid: Grid) -> Turn:
        if self._move_loop_generator is None:
            self._move_loop_generator = self._move_loop(grid)
        return next(self._move_loop_generator)

    def _move_loop(self, grid: Grid) -> Generator[Turn, None, None]:
        """Super smart AI goes here"""

        replay_dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=None,  # TODO: Play with this number
            sample_batch_size=self.TRAIN_BATCH_SIZE,
            num_steps=2,
        )
        replay_iterator = iter(replay_dataset)

        # Wrap common functions with tf.function
        self.agent.train = tf_agents_common.function(self.agent.train, autograph=True)
        self.agent.collect_policy.action = tf_agents_common.function(
            self.agent.collect_policy.action, autograph=True
        )

        @tf_agents_common.function(autograph=True)
        def add_batch(
            time_step_old: TimeStep, action_step: PolicyStep, time_step_new: TimeStep
        ) -> None:
            self.replay_buffer.add_batch(
                trajectory.from_transition(
                    time_step=time_step_old,
                    action_step=action_step,
                    next_time_step=time_step_new,
                )
            )

        @tf_agents_common.function(autograph=True)
        def train_step() -> LossInfo:
            experience, _ = next(replay_iterator)
            return self.agent.train(experience)

        policy_state = self.agent.collect_policy.get_initial_state(self.env.batch_size)
        time_step_iterator = self._perform_episode(grid)
        time_step_new: TimeStep
        action_step = None
        time_step_old: TimeStep = None
        while True:
            try:
                time_step_new = next(time_step_iterator)
                self.steps += 1
                self.total_reward += time_step_new.reward
            except StopIteration:
                # It's important to reset time_step_old so we never get a
                # trajectory that goes from END to FIRST
                self.deaths += 1
                time_step_old = None
                time_step_iterator = self._perform_episode(grid)
                continue

            # Calculate the trajectory from the last loop
            if time_step_old is not None:
                add_batch(
                    time_step_old=time_step_old,
                    action_step=action_step,
                    time_step_new=time_step_new,
                )

            # Run a single train step, if there is replay_buffer data to do so
            if self.steps > 2:
                self.train_loss = train_step()

            # TODO: Figure out a more concrete value for exploration
            if random.random() < 0.9:
                action_step = self.agent.collect_policy.action(
                    time_step_new, policy_state
                )
            else:
                action_step = policy_step.PolicyStep(
                    action=np.array([random.randint(0, len(self.CHOICES) - 1)]),
                    state=(),
                    info=(),
                )
            policy_state = action_step.state

            yield self.CHOICES[int(action_step[0][0])]

            time_step_old = time_step_new

    def _perform_episode(self, grid: Grid) -> Generator[TimeStep, None, None]:
        """Run through an episode from start to finish, keeping stats
        correct and yielding time steps along the way"""

        time_step = self._next_time_step(
            grid=grid, step_type=self._BatchedStepType.FIRST
        )

        yield time_step
        self._last_step_health = self.health
        self._tick_stats()

        # Wait until the critter _would_ have died
        while not self.delete_queued:
            time_step = self._next_time_step(
                grid=grid, step_type=self._BatchedStepType.MID
            )

            self._last_step_health = self.health
            yield time_step
            self._tick_stats()

        time_step = self._next_time_step(
            grid=grid, step_type=self._BatchedStepType.LAST
        )
        print(
            f"Died at {self.age}, "
            f"Loss: {self.train_loss.loss if self.train_loss else None}, "
            f"Health: {self.health}, "
            f"Last Health: {self._last_step_health}, "
            f"Replay buffer: {self.replay_buffer.num_frames()}, "
            f"Position: {grid.id_to_pos[self.id]}"
        )
        self._reset_stats()
        assert not self.delete_queued  # TODO: Remove, consider adding a test
        yield time_step

    def _reset_stats(self) -> None:
        super()._reset_stats()
        self._last_step_health = self.health

    def _next_time_step(
        self, grid: Grid, step_type: "AICritterMixin._BatchedStepType"
    ) -> TimeStep:
        # Always start by getting a time_step
        observation = extract_inputs.get_instance_grid(
            grid=grid,
            pos=grid.id_to_pos[self.id],
            radius=self.INPUT_RADIUS,
            layers=self.LAYERS,
        )

        if step_type is self._BatchedStepType.FIRST:
            reward = 0
        elif step_type is self._BatchedStepType.LAST:
            reward = 0
        elif step_type is self._BatchedStepType.MID:
            reward = self.health - self._last_step_health
            reward = max(-1, min(1, reward))
        else:
            raise RuntimeError(f"Unknown step type: {step_type}")

		return TimeStep(
			step_type=step_type,
			reward=tf.convert_to_tensor([reward], dtype=tf.float32),
			observation=tf.expand_dims(observation, axis=0),
			# TODO: Look at tfagents example to figure out discount
			discount=tf.convert_to_tensor([1.0]))
