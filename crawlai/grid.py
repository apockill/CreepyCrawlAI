import random
from typing import Dict, Tuple

from godot.bindings import Node, Vector2
import numpy as np

from crawlai.grid_item import GridItem
from crawlai.position import Position
from crawlai.math_utils import clamp

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

		# Settings
		self.rendering = True
		"""When false, object instances don't get set_position called"""

	def __iter__(self):
		for grid_item in self.id_to_obj.values():
			yield grid_item

	def get_grid_around(self, pos: Position, radius: int) -> np.ndarray:
		"""Get a numpy array of obj IDs surrounding a particular area.
		This function will always return an array of shape (radius, radius),
		where the value is the object ID. """

		x1, y1 = pos.x - radius, pos.y - radius
		x2, y2 = pos.x + radius + 1, pos.y + radius + 1

		crop = self._grid[
			   clamp(x1, 0, self.width):clamp(x2, 0, self.width),
			   clamp(y1, 0, self.height):clamp(y2, 0, self.height)]
		w, h = crop.shape
		if x1 < 0:
			concat = np.full((abs(x1), h),
							 fill_value=-1, dtype=np.int8)
			crop = np.vstack((concat, crop))
		if x2 > self.width:
			concat = np.full((x2 - self.width, h),
							 fill_value=-1, dtype=np.int8)
			crop = np.vstack((crop, concat))

		w, h = crop.shape
		if y1 < 0:
			concat = np.full((w, abs(y1)),
							 fill_value=-1, dtype=np.int8)
			crop = np.hstack((concat, crop))
		if y2 > self.height:
			concat = np.full((w, y2 - self.height),
							 fill_value=-1, dtype=np.int8)
			crop = np.hstack((crop, concat))
		return crop

	def add_item(self, pos: Position, grid_item: GridItem) \
			-> bool:
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

	def move_item_relative(self, rel_pos: Position, grid_item: GridItem) \
			-> bool:
		return self.try_move_item(
			pos=self.id_to_pos[grid_item.id] + rel_pos,
			grid_item=grid_item)

	def try_move_item(self, pos: Position, grid_item: GridItem, is_new=False) \
			-> bool:
		if not self.is_empty_coord(pos):
			return False
		if not is_new:
			# Reset current position
			cur_pos = self.id_to_pos[grid_item.id]
			self._grid[cur_pos.x][cur_pos.y] = 0

		# Apply new position
		self._grid[pos.x][pos.y] = grid_item.id
		self.id_to_pos[grid_item.id] = pos

		if self.rendering:
			grid_item.instance.set_position(
				Vector2(pos.x * self._spacing, pos.y * self._spacing))
		return True

	def is_empty_coord(self, pos: Position):
		"""Checks if this is a valid coordinate to move a critter into"""
		# Verify there is no object in that position
		try:
			if self._grid[pos[0]][pos[1]] != 0:
				return False
			return True
		except IndexError:
			return False

	@property
	def random_free_cell(self):
		"""Gets a random free cell"""
		free = np.argwhere(self._grid == 0)
		return Position(*random.choice(free))
