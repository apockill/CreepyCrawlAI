from typing import Dict, Type
from threading import RLock
from functools import lru_cache

import numpy as np

from crawlai.grid import Grid
from crawlai.position import Position
from crawlai.math_utils import clamp
from crawlai.items.food import Food
from crawlai.grid_item import GridItem

INPUT_DTYPE = np.int32
"""The smallest int type accepted by tensorflow"""


def _generate_layered_grid(grid: Grid,
						   layers: Dict[str, int],
						   radius: int):
	"""Converts the grid of shape (x, y) to (x, y, obj_layers)
	The 0th index of the grid always represents boundaries or walls.

	:param grid: The grid
	:param layers: A dictionary of {"GRID_ITEM_TYPE": LayerID}, where layer ID
	       must be the index on obj_layer for that item ID to appear on
	:param radius: The radius that critters will have. This will pad the sides
	of the grid with walls on the 0 layer.
	"""
	w, h = grid.array.shape
	full_grid = np.zeros(
		(w + radius * 2,
		 h + radius * 2,
		 len(layers) + 1),
		dtype=INPUT_DTYPE)

	for item in grid:
		layer = layers[type(item).__name__]
		pos = grid.id_to_pos[item.id]
		full_grid[pos.x + radius, pos.y + radius, layer] = 1

	# Fill in the "walls" around the radius
	before = full_grid.copy()
	full_grid[0:radius, :, 0] = 1
	assert not (full_grid == before).all()

	before = full_grid.copy()
	full_grid[w + radius:, :, 0] = 1
	assert not (full_grid == before).all()

	before = full_grid.copy()
	full_grid[:, 0:radius, 0] = 1
	assert not (full_grid == before).all()

	before = full_grid.copy()
	full_grid[:, h + radius:, 0] = 1  # TODO: verify why this is different
	assert not (full_grid == before).all()
	return full_grid


def get_instance_grid(
		grid: Grid,
		pos: Position,
		radius: int,
		layers: Dict[str, int]) -> np.ndarray:
	"""Get a numpy array of obj IDs surrounding a particular area.
	This function will always return an array of shape (radius, radius),
	where the value is the object ID.

	Shape: (x, y, object_layers)
		   where object_layers is 3:
		   0: walls
		   1: critters
		   2: food
	"""
	layered_grid = _generate_layered_grid(grid, layers, radius)

	x1, y1 = pos.x, pos.y
	x2, y2 = pos.x + radius * 2 + 1, pos.y + radius * 2 + 1
	crop = layered_grid[x1:x2, y1:y2, :]
	return crop
