import random

import numpy as np

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position
from crawlai.math_utils import clamp
from crawlai.grid import Grid
from crawlai.grid_item import Turn


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

	@staticmethod
	def get_instance_grid(grid: Grid, pos: Position, radius: int) -> np.ndarray:
		"""Get a numpy array of obj IDs surrounding a particular area.
		This function will always return an array of shape (radius, radius),
		where the value is the object ID. """

		x1, y1 = pos.x - radius, pos.y - radius
		x2, y2 = pos.x + radius + 1, pos.y + radius + 1

		crop = grid.array[
			   clamp(x1, 0, grid.width):clamp(x2, 0, grid.width),
			   clamp(y1, 0, grid.height):clamp(y2, 0, grid.height)]
		w, h = crop.shape
		if x1 < 0:
			concat = np.full((abs(x1), h),
							 fill_value=-1, dtype=np.int8)
			crop = np.vstack((concat, crop))
		if x2 > grid.width:
			concat = np.full((x2 - grid.width, h),
							 fill_value=-1, dtype=np.int8)
			crop = np.vstack((crop, concat))

		w, h = crop.shape
		if y1 < 0:
			concat = np.full((w, abs(y1)),
							 fill_value=-1, dtype=np.int8)
			crop = np.hstack((concat, crop))
		if y2 > grid.height:
			concat = np.full((w, y2 - grid.height),
							 fill_value=-1, dtype=np.int8)
			crop = np.hstack((crop, concat))
		return crop

	def get_turn(self, grid: Grid) -> Turn:
		"""Super smart AI goes here"""

		"""
		Indexing: 
		input[x][y][Z] where Z can be 0: Critter, 1: Food
		"""
		net_input = self.get_instance_grid(
			grid=grid,
			pos=grid.id_to_pos[self.id],
			radius=self.AREA_AROUND)
		return random.choice(self.CHOICES)
