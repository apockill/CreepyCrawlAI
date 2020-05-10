import random
from typing import Dict, Tuple

from godot.bindings import Node, Vector2
import numpy as np

from crawlai.grid_item import GridItem
from crawlai.position import Position


class Grid:
	def __init__(self, width, height, spacing, root_node):
		# Grid parameters
		self._spacing: int = spacing
		self.width: int = width
		self.height: int = height

		# Grid state
		self._grid: np.ndarray = np.zeros(shape=(width, height), dtype=np.int64)
		"""Holds the instance ids of each object. 0 means empty"""
		self.id_to_obj: Dict[int, GridItem] = {}
		self.id_to_pos: Dict[int, Position] = {}

		# World node
		self._root_node: Node = root_node

	def __iter__(self):
		for grid_item in self.id_to_obj.values():
			yield grid_item

	def add_item(self, pos: Position, grid_item: GridItem):
		if not self.is_empty_coord(pos):
			grid_item.instance.queue_free()
			return False

		assert self._grid[pos.x][pos.y] == 0
		# Register the item
		self.id_to_obj[grid_item.id] = grid_item
		self._root_node.add_child(grid_item.instance)

		# Move the item to the correct place
		assert self.try_move_item(pos, grid_item, is_new=True)
		return True

	def move_item_relative(self, rel_pos: Position, grid_item: GridItem):
		self.try_move_item(
			pos=self.id_to_pos[grid_item.id] + rel_pos,
			grid_item=grid_item)

	def try_move_item(self, pos: Position, grid_item: GridItem, is_new=False):
		if not self.is_empty_coord(pos):
			return False
		if not is_new:
			# Reset current position
			cur_pos = self.id_to_pos[grid_item.id]
			self._grid[cur_pos.x][cur_pos.y] = 0

		# Apply new position
		self._grid[pos.x][pos.y] = grid_item.id
		self.id_to_pos[grid_item.id] = pos
		grid_item.instance.set_position(
			Vector2(pos.x * self._spacing, pos.y * self._spacing))
		return True

	def is_empty_coord(self, pos: Position):
		"""Checks if this is a valid coordinate to move a critter into"""
		# Do a bounds check
		if not 0 <= pos.x < self.width:
			return False
		if not 0 <= pos.y < self.height:
			return False

		# Verify there is no object in that position
		if self._grid[pos.x][pos.y] != 0:
			return False
		return True

	@property
	def random_free_cell(self):
		"""Gets a random free cell"""
		free = np.argwhere(self._grid == 0)
		return Position(*random.choice(free))
