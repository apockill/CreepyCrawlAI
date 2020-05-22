import random

import numpy as np

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position
from crawlai.math_utils import clamp
from crawlai.grid import Grid
from crawlai.turn import Turn
from crawlai.model.extract_inputs import get_instance_grid


class AICritterMixin(BaseCritter):
	"""
	Terms
		V: Velocity (x, y components)

	Inputs:
		self.vx
		self.vy
		self.health

		Nearest 10 critters:
			vx
			vy
			health
	Outputs:
		self.vx
		self.vy

	Desired Features:
		- Add a self.signal
		- Train each step on the outcome of the scenario after running
	"""
	CHOICES = [Turn(Position(*c), is_action)
			   for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
			   for is_action in (True, False)] + [Turn(Position(0, 0), False)]
	AREA_AROUND = 20

	def __init__(self):
		super().__init__()

	def get_turn(self, grid: Grid) -> Turn:
		"""Super smart AI goes here"""
		_ = get_instance_grid(
			grid=grid,
			pos=grid.id_to_pos[self.id])
		return random.choice(self.CHOICES)
