import random
from multiprocessing.pool import ThreadPool

import tensorflow as tf
from tf_agents.agents.dqn.dqn_agent import DqnAgent
from tf_agents.networks.q_network import QNetwork
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.trajectories import time_step

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.turn import Turn
from crawlai.model.environment import CritterEnvironment
from crawlai.model.extract_inputs import get_instance_grid

threadpool = None
"""This is a shared threadpool by all AICritterMixins"""


class AICritterMixin(BaseCritter):
	CHOICES = [Turn(Position(*c), is_action)
			   for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
			   for is_action in (True, False)] + [Turn(Position(0, 0), False)]

	def __init__(self, environment: CritterEnvironment = None):
		super().__init__()
		if environment is None:
			global threadpool
			threadpool = threadpool or ThreadPool(processes=1)
			environment = CritterEnvironment()
			environment = TFPyEnvironment(environment, isolation=threadpool)
			assert len(self.CHOICES) == environment.action_spec()[0].maximum
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
		observation = get_instance_grid(
			grid=grid,
			pos=grid.id_to_pos[self.id])

		if self.timestep is None:
			# Initialize the first timestep
			self.timestep = time_step.restart(observation=observation)
			print("First time step", self.timestep)
		else:
			self.timestep = time_step.transition(
				observation=observation,
				reward=float(self.age),
				discount=1.0)
		# TODO: This fails:
		action = self.agent.policy.action(self.timestep)
		return action
