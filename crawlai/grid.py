import random
from typing import Dict

import numpy as np

from crawlai.grid_item import GridItem


class Grid:
	def __init__(self, width, height):
		self._grid: np.ndarray = np.zeros(shape=(width, height), dtype=np.int64)
		"""Holds the instance ids of each object. 0 means empty"""

		self.instance_to_obj: Dict[np.int64, GridItem] = {}

	def add_item(self, x, y, grid_item: GridItem):
		assert self._grid[x][y] == 0

		self.instance_to_obj[grid_item.id] = grid_item
		self._grid[x][y] = grid_item.id

	@property
	def random_free_cell(self):
		"""Gets a random free cell"""
		free = np.argwhere(self._grid == 0)
		return random.choice(free)
