import random
from typing import Iterator

import tensorflow as tf
import numpy as np
from tf_agents.trajectories import policy_step
from tf_agents.agents.dqn.dqn_agent import DqnAgent
from tf_agents.networks.q_network import QNetwork
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.trajectories.time_step import StepType, TimeStep
from tf_agents.replay_buffers.tf_uniform_replay_buffer import \
	TFUniformReplayBuffer
from tf_agents.trajectories import trajectory
import tf_agents.utils.common as tf_agents_common

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.turn import Turn
from crawlai.model.environment import CritterEnvironment
from crawlai.model import extract_inputs


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

	def __init__(self):

		super().__init__()
		# Stats
		self.train_loss = None
		self.step = 0
		self._last_step_health = self.health

		# Created on the first call of self.next_step
		self._move_loop_generator = None
		"""Created on first call of self.next_step"""

		environment = CritterEnvironment(
			input_radius=self.INPUT_RADIUS,
			input_dtype=extract_inputs.INPUT_DTYPE,
			n_choices=len(self.CHOICES),
			n_layers=len(self.LAYERS) + 1)
		environment = TFPyEnvironment(environment, isolation=False)
		self.env: TFPyEnvironment = environment

		q_net = QNetwork(
			self.env.observation_spec(),
			self.env.action_spec())
		self.agent = DqnAgent(
			time_step_spec=self.env.time_step_spec(),
			action_spec=self.env.action_spec(),
			gamma=0.6,
			# target_update_period=5,  # TODO: bench perf
			# target_update_tau=0.05,  # TODO: bench perf
			q_network=q_net,
			optimizer=tf.compat.v1.train.AdamOptimizer(
				learning_rate=self.LEARNING_RATE))
		self.agent.initialize()

		self.replay_buffer = TFUniformReplayBuffer(
			data_spec=self.agent.collect_data_spec,
			batch_size=self.env.batch_size,
			max_length=self.REPLAY_BUFFER_CAPACITY)

	def get_turn(self, grid: Grid) -> Turn:
		if self._move_loop_generator is None:
			self._move_loop_generator = self._move_loop(grid)
		return next(self._move_loop_generator)

	def _move_loop(self, grid: Grid) -> Iterator[Turn]:
		"""Super smart AI goes here"""

		replay_dataset = self.replay_buffer.as_dataset(
			num_parallel_calls=None,  # TODO: Play with this number
			sample_batch_size=self.TRAIN_BATCH_SIZE,
			num_steps=2)
		replay_iterator = iter(replay_dataset)

		# Wrap common functions with tf.function
		self.agent.train = tf_agents_common.function(
			self.agent.train, autograph=True)
		self.agent.collect_policy.action = tf_agents_common.function(
			self.agent.collect_policy.action, autograph=True)

		@tf_agents_common.function(autograph=True)
		def add_batch(time_step_old, action_step, time_step_new):
			self.replay_buffer.add_batch(
				trajectory.from_transition(
					time_step=time_step_old,
					action_step=action_step,
					next_time_step=time_step_new)
			)

		@tf_agents_common.function(autograph=True)
		def train_step():
			experience, _ = next(replay_iterator)
			return self.agent.train(experience)

		policy_state = self.agent.collect_policy.get_initial_state(
			self.env.batch_size)
		time_step_iterator = self._perform_episode(grid)
		time_step_new: TimeStep
		action_step = None
		time_step_old: TimeStep = None
		while True:
			try:
				time_step_new = next(time_step_iterator)
				self.step += 1
			except StopIteration:
				# It's important to reset time_step_old so we never get a
				# trajectory that goes from END to FIRST
				time_step_old = None
				time_step_iterator = self._perform_episode(grid)
				continue

			# Calculate the trajectory from the last loop
			if time_step_old is not None:
				add_batch(
					time_step_old=time_step_old,
					action_step=action_step,
					time_step_new=time_step_new)

			# Run a single train step, if there is replay_buffer data to do so
			if self.step > 2:
				self.train_loss = train_step()

			# TODO: Figure out a more concrete value for exploration
			if random.random() < 0.9:
				action_step = self.agent.collect_policy.action(
					time_step_new, policy_state)
			else:
				action_step = policy_step.PolicyStep(
					action=np.array([random.randint(0, len(self.CHOICES) - 1)]),
					state=(),
					info=())
			policy_state = action_step.state

			yield self.CHOICES[int(action_step[0][0])]

			time_step_old = time_step_new
			time_step_new = None
