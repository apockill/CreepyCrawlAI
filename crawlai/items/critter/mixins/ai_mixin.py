import random
from multiprocessing.pool import ThreadPool

import numpy as np
import tensorflow as tf
from tf_agents.agents import DqnAgent
from tf_agents.networks.q_network import QNetwork
from tf_agents.utils import common
from tf_agents.environments.tf_py_environment import TFPyEnvironment

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
		global threadpool
		threadpool = threadpool or ThreadPool(processes=1)
		self.environment = (environment or
							TFPyEnvironment(CritterEnvironment(),
											isolation=threadpool))
		assert len(self.CHOICES) == self.environment.action_spec()[0].maximum

		# Hyperparameters
		num_iterations = 20000

		initial_collect_steps = 1000
		collect_steps_per_iteration = 1
		replay_buffer_max_length = 100000

		batch_size = 64
		learning_rate = 1e-3
		log_interval = 200

		num_eval_episodes = 10
		eval_interval = 1000

		# The number and size of the model's hidden layers
		fc_layer_params = (100,)
		train_step_counter = tf.Variable(0)
		q_net = QNetwork(
			self.environment.observation_spec(),
			self.environment.action_spec(),
			fc_layer_params=fc_layer_params)
		self.agent = DqnAgent(
			self.environment.time_step_spec(),
			self.environment.action_spec(),
			q_network=q_net,
			optimizer=tf.compat.v1.train.AdamOptimizer(
				learning_rate=learning_rate),
			td_errors_loss_fn=common.element_wise_squared_loss,
			train_step_counter=train_step_counter)

	def get_turn(self, grid: Grid) -> Turn:
		"""Super smart AI goes here"""
		_ = get_instance_grid(
			grid=grid,
			pos=grid.id_to_pos[self.id])
		return random.choice(self.CHOICES)
