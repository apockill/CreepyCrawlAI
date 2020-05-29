from typing import Iterator

import numpy as np
import tensorflow as tf
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
	CHOICES = [Turn(Position(*c), is_action)
			   for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
			   for is_action in (True, False)] + [Turn(Position(0, 0), False)]
	INPUT_RADIUS = 30

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

	def __init__(self, environment: CritterEnvironment = None):
		super().__init__()
		self._move_loop_generator = None
		"""Created on first call of self.next_step"""

		if environment is None:
			environment = CritterEnvironment(
				input_radius=self.INPUT_RADIUS,
				input_dtype=extract_inputs.INPUT_DTYPE,
				n_choices=len(self.CHOICES))
			environment = TFPyEnvironment(environment, isolation=False)
		self.env: TFPyEnvironment = environment

		q_net = QNetwork(
			self.env.observation_spec(),
			self.env.action_spec())
		self.agent = DqnAgent(
			time_step_spec=self.env.time_step_spec(),
			action_spec=self.env.action_spec(),
			q_network=q_net,
			optimizer=tf.compat.v1.train.AdamOptimizer(
				learning_rate=self.LEARNING_RATE))
		self.agent.initialize()

	def get_turn(self, grid: Grid) -> Turn:
		if self._move_loop_generator is None:
			self._move_loop_generator = self._move_loop(grid)
		return next(self._move_loop_generator)

	def _move_loop(self, grid: Grid) -> Iterator[Turn]:
		"""Super smart AI goes here"""
		while True:
			observation = extract_inputs.get_instance_grid(
				grid=grid,
				pos=grid.id_to_pos[self.id],
				radius=self.INPUT_RADIUS)
			step_type = (self._BatchedStepType.MID if self.age == 0
						 else self._BatchedStepType.FIRST)

			choice = int(self._get_action(
				step_type=step_type,
				reward=self.age,
				observation=observation))

			yield self.CHOICES[choice]
