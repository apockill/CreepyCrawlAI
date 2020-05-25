import random
from multiprocessing.pool import ThreadPool

import numpy as np
import tensorflow as tf
from tf_agents.agents.dqn.dqn_agent import DqnAgent
from tf_agents.networks.q_network import QNetwork
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.trajectories.time_step import StepType, TimeStep
from tf_agents.utils import nest_utils

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.turn import Turn
from crawlai.model.environment import CritterEnvironment
from crawlai.model import extract_inputs

threadpool = None
"""This is a shared threadpool by all AICritterMixins"""

DISCOUNT = np.array([1.0])
"""Since we never change this value, it's more performant to create this array
once and never change it. """


class AICritterMixin(BaseCritter):
	CHOICES = [Turn(Position(*c), is_action)
			   for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
			   for is_action in (True, False)] + [Turn(Position(0, 0), False)]
	INPUT_RADIUS = 30

	# Step type constants
	class _BatchedStepType:
		"""Optimize away the expanding of dimensions when creating a 'batched'
		timestep of batch size 1."""
		FIRST = np.expand_dims(StepType.FIRST, axis=0)
		MID = np.expand_dims(StepType.MID, axis=0)
		LAST = np.expand_dims(StepType.LAST, axis=0)

	def __init__(self, environment: CritterEnvironment = None):
		super().__init__()
		if environment is None:
			global threadpool
			threadpool = threadpool or ThreadPool(processes=1)
			environment = CritterEnvironment(
				input_radius=self.INPUT_RADIUS,
				input_dtype=extract_inputs.INPUT_DTYPE,
				n_choices=len(self.CHOICES))
			environment = TFPyEnvironment(environment, isolation=threadpool)
		self.environment: TFPyEnvironment = environment
		self.timestep = None

		learning_rate = 1e-3

		q_net = QNetwork(
			self.environment.observation_spec(),
			self.environment.action_spec())
		self.agent = DqnAgent(
			time_step_spec=self.environment.time_step_spec(),
			action_spec=self.environment.action_spec(),
			q_network=q_net,
			optimizer=tf.compat.v1.train.AdamOptimizer(
				learning_rate=learning_rate))
		self.agent.initialize()

	def get_turn(self, grid: Grid) -> Turn:
		"""Super smart AI goes here"""
		observation = extract_inputs.get_instance_grid(
			grid=grid,
			pos=grid.id_to_pos[self.id],
			radius=self.INPUT_RADIUS)
		reward = self.age
		step_type = (self._BatchedStepType.MID if self.timestep
					 else self._BatchedStepType.FIRST)

		self.timestep = TimeStep(
			step_type=step_type,
			reward=np.array([reward]),
			observation=np.expand_dims(observation, axis=0),
			discount=DISCOUNT)

		# return self.CHOICES[ts[0][0]]
		return random.choice(self.CHOICES)
