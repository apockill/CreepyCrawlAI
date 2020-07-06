import random
from typing import Dict

import numpy as np

from crawlai.grid_item import GridItem
from crawlai.position import Position


def lockable(fn):
	"""Raises a WritingToLockedGrid exception when this method is accessed
	on a locked grid"""

	def wrapper(self: 'Grid', *args, **kwargs):
		if self.locked:
			raise Grid.WritingToLockedGrid
		return fn(self, *args, **kwargs)

	return wrapper


class Grid:
	class WritingToLockedGrid(Exception):
		"""Raised when a grid array is going to be changed, but the grid is
		in a locked state"""

	def __init__(self, width, height):
		# Grid parameters
		self.width: int = width
		self.height: int = height
		self.locked = False
		self._hash_cache = None

		# Grid state
		self.array: np.ndarray = np.zeros(shape=(width, height), dtype=np.int_)
		"""Holds the instance ids of each object. 0 means empty"""
		self.id_to_obj: Dict[int, GridItem] = {}
		self.id_to_pos: Dict[int, Position] = {}

	def __hash__(self):
		"""Only hashable when the grid is locked"""
		if self.locked:
			return self._hash_cache
		else:
			raise TypeError("A grid cannot be hashed when unlocked")

	def __iter__(self):
		for grid_item in self.id_to_obj.values():
			yield grid_item

	def __enter__(self):
		"""Lock the grid, and cache the grid.array hashes"""
		self.array.flags.writeable = False
		self.locked = True
		self._hash_cache = hash(self.array.data.tobytes())
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.array.flags.writeable = True
		self.locked = False
		self._hash_cache = None

	@lockable
	def add_item(self, pos: Position, grid_item: GridItem) -> bool:
		if not self.is_empty_coord(pos):
			return False

		assert self.array[pos.x][pos.y] == 0

		# Register the item
		self.id_to_obj[grid_item.id] = grid_item

		# Move the item to the correct place
		assert self.try_move_item(pos, grid_item, is_new=True)
		return True

	@lockable
	def delete_item(self, grid_item: GridItem):
		"""Dereference everything about the item, and then queue_free the
		instance"""
		pos = self.id_to_pos.pop(grid_item.id)
		del self.id_to_obj[grid_item.id]
		self.array[pos.x][pos.y] = 0
		grid_item.instance.queue_free()

	@lockable
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

	@lockable
	def move_item_relative(self, direction: Position,
						   grid_item: GridItem) -> bool:
		return self.try_move_item(
			pos=self.id_to_pos[grid_item.id] + direction,
			grid_item=grid_item)

	@lockable
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
			if self.array[pos.x][pos.y] != 0 or pos.x < 0 or pos.y < 0:
				return False
			return True
		except IndexError:
			return False

	@property
	def random_free_cell(self):
		"""Gets a random free cell"""
		free = np.argwhere(self.array == 0)
		return Position(*random.choice(free))
