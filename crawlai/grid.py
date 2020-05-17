import random
from typing import Dict, Tuple

from godot.bindings import Node, Vector2
import numpy as np

from crawlai.grid_item import GridItem
from crawlai.position import Position
from crawlai.math_utils import clamp


class Grid:
	def __init__(self, width, height):
		# Grid parameters
		self.width: int = width
		self.height: int = height

		# Grid state
		self.array: np.ndarray = np.zeros(shape=(width, height), dtype=np.int)
		"""Holds the instance ids of each object. 0 means empty"""
		self.id_to_obj: Dict[int, GridItem] = {}
		self.id_to_pos: Dict[int, Position] = {}

	def __iter__(self):
		for grid_item in self.id_to_obj.values():
			yield grid_item

	def add_item(self, pos: Position, grid_item: GridItem) -> bool:
		if not self.is_empty_coord(pos):
			return False

		assert self.array[pos.x][pos.y] == 0

		# Register the item
		self.id_to_obj[grid_item.id] = grid_item

		# Move the item to the correct place
		assert self.try_move_item(pos, grid_item, is_new=True)
		return True

	def apply_action(self, direction: Position, grid_item: GridItem) -> bool:
		"""Applies the grid_item's action onto the grid cell that is 'direction'
		relative to grid_item's position

		:return: True if an action was performed, False if no action was
		performed
		"""

		if direction.x == 0 and direction.y == 0:
			raise RuntimeError("A GridItem cannot perform an action on itself!")

		action_pos = self.id_to_pos[grid_item.id] + direction

		try:
			other_item_id = self.array[action_pos.x][action_pos.y]
		except IndexError:
			return False

		if other_item_id != 0:
			other_item = self.id_to_obj[other_item_id]
			grid_item.perform_action_onto(other_item)
			return True
		return False

	def move_item_relative(self, direction: Position,
						   grid_item: GridItem) -> bool:
		return self.try_move_item(
			pos=self.id_to_pos[grid_item.id] + direction,
			grid_item=grid_item)

	def try_move_item(self, pos: Position,
					  grid_item: GridItem,
					  is_new=False) -> bool:
		if not self.is_empty_coord(pos):
			return False
		if not is_new:
			# Reset current position
			cur_pos = self.id_to_pos[grid_item.id]
			self.array[cur_pos.x][cur_pos.y] = 0

		# Apply new position
		self.array[pos.x][pos.y] = grid_item.id
		self.id_to_pos[grid_item.id] = pos

		return True

	def is_empty_coord(self, pos: Position):
		"""Checks if this is a valid coordinate to move a critter into"""
		# Verify there is no object in that position
		try:
			if self.array[pos.x][pos.y] != 0:
				return False
			return True
		except IndexError:
			return False

	@property
	def random_free_cell(self):
		"""Gets a random free cell"""
		free = np.argwhere(self.array == 0)
		return Position(*random.choice(free))
