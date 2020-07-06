import pytest

import numpy as np

from crawlai.model import extract_inputs
from crawlai.grid import Grid
from crawlai.items.critter.critter import Critter
from crawlai.position import Position

# Layer codes for this test. 
E = -1  # Empty
W = 0  # Wall
C = 1  # Critter
F = 2  # Food
test_get_grid_around_parameters = [
	# # Basic checks at each corner-1 to check grid works normally without padding
	((1, 1), 1, np.asarray([[E, E, E],
							[E, C, E],
							[E, E, E]])),
	((2, 3), 1, np.asarray([[E, E, E],
							[E, C, E],
							[E, E, E]])),
	((2, 1), 1, np.asarray([[E, E, E],
							[E, C, E],
							[E, E, E]])),
	((1, 3), 1, np.asarray([[E, E, E],
							[E, C, E],
							[E, E, E]])),

	# Check actual corners to see the grid applies padding correctly
	((0, 0), 1, np.asarray([[W, W, W],
							[W, C, E],
							[W, E, E]])),
	((3, 4), 1, np.asarray([[E, E, W],
							[E, C, W],
							[W, W, W]])),
	((0, 4), 1, np.asarray([[W, W, W],
							[E, C, W],
							[E, E, W]])),
	((3, 0), 1, np.asarray([[W, E, E],
							[W, C, E],
							[W, W, W]])),

	# Check the middles of each grid edge
	((0, 2), 1, np.asarray([[W, W, W],
							[E, C, E],
							[E, E, E]])),
	((3, 2), 1, np.asarray([[E, E, E],
							[E, C, E],
							[W, W, W]])),
	((1, 4), 1, np.asarray([[E, E, W],
							[E, C, W],
							[E, E, W]])),
	((1, 0), 1, np.asarray([[W, E, E],
							[W, C, E],
							[W, E, E]])),

	# Check a radius of two near the center
	((1, 2), 2, np.asarray([[W, W, W, W, W],
							[E, E, E, E, E],
							[E, E, C, E, E],
							[E, E, E, E, E],
							[E, E, E, E, E]])),

	# Check a large, off-center radius
	((1, 1), 4, np.asarray([[W, W, W, W, W, W, W, W, W],
							[W, W, W, W, W, W, W, W, W],
							[W, W, W, W, W, W, W, W, W],
							[W, W, W, E, E, E, E, E, W],
							[W, W, W, E, C, E, E, E, W],
							[W, W, W, E, E, E, E, E, W],
							[W, W, W, E, E, E, E, E, W],
							[W, W, W, W, W, W, W, W, W],
							[W, W, W, W, W, W, W, W, W]]))
]


@pytest.mark.parametrize(
	argnames=('pos', 'radius', 'expected_occupied_layers'),
	argvalues=test_get_grid_around_parameters)
def test_get_grid_around(pos, radius, expected_occupied_layers):
	"""Creates a grid of shape:
	[[0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]]

	 and places a critter at position 'pos', then calls get_grid_around with a
	 radius of 'radius', and verifies the output grid is the same as
	 'output_grid'
    """
	layers = {"Critter": C, "Food": F}
	grid = Grid(width=4, height=5)
	grid.add_item(pos=Position(*pos), grid_item=Critter())
	with grid:
		grid_around = extract_inputs.get_instance_grid(
			grid=grid,
			pos=Position(*pos),
			radius=radius,
			layers=layers)

	w, h, n_layers = grid_around.shape
	assert h == w
	assert n_layers == len(Critter.LAYERS) + 1, \
		"There should be a 0 layer with walls, and any layers included by the" \
		" Critter!"
	assert grid_around[:, :, layers["Critter"]].sum() == 1, \
		"There should only be one critter on the map!"
	assert grid_around[:, :, layers["Food"]].sum() == 0, \
		"There should only be no food on the map!"
	assert grid_around.min() == 0
	assert grid_around.max() == 1

	# Now compare it to the output_grid
	for x in range(w):
		for y in range(h):
			occupied_layer = expected_occupied_layers[x, y]
			expect_is_occupied = int(occupied_layer != E)
			if occupied_layer == E:
				# If this block is supposed to be empty, all layers on that
				# coordinate should be 0.
				assert (grid_around[x, y, :] == 0).all(), \
					f"The layers at ({pos[0]},{pos[1]}) were supposed to be " \
					f"emtpy. Instead, they were: {grid_around[x, y, :]}"
				continue

			assert grid_around[x, y, occupied_layer] == expect_is_occupied, \
				f"Layer {occupied_layer} for position ({pos[0]},{pos[1]}) " \
				f"was expected have value {expect_is_occupied}"


def test_instance_grid_is_cached():
	"""Verify that the instance grid is calculated once and reused for the
	various different threads/critters"""
	grid = Grid(width=3, height=3)
	item = Critter()
	grid.add_item(Position(0, 0), item)

	assert len(list(extract_inputs._instance_grid_cache.keys())) == 0, \
		"The caches should start out empty!"

	def validate_cache_changes(changed, last_cache):
		cache = extract_inputs._instance_grid_cache
		assert len(cache) == 1
		assert ((list(last_cache.keys())[0] == list(cache.keys())[0])
				is not changed)

	# Initialize the cache
	extract_inputs.get_instance_grid(
		grid,
		pos=Position(1, 1),
		radius=5,
		layers=Critter.LAYERS)

	# Verify the cache doesn't change if the grid hasn't changed
	for i in range(10):
		last_cache = extract_inputs._instance_grid_cache.copy()
		extract_inputs.get_instance_grid(
			grid,
			pos=Position(1, 1),
			radius=5,
			layers=Critter.LAYERS)
		validate_cache_changes(False, last_cache)

	# Verify that the cache reloads when the radius changes
	last_cache = extract_inputs._instance_grid_cache.copy()
	extract_inputs.get_instance_grid(
		grid,
		pos=Position(1, 1),
		radius=10,
		layers=Critter.LAYERS)
	validate_cache_changes(True, last_cache)

	# Verify the cache reloads when the layers change
	last_cache = extract_inputs._instance_grid_cache.copy()
	extract_inputs.get_instance_grid(
		grid,
		pos=Position(1, 1),
		radius=10,
		layers={"Critter": 1})
	validate_cache_changes(True, last_cache)

	# Verify the cache does _not_ reload when position is changed
	last_cache = extract_inputs._instance_grid_cache.copy()
	extract_inputs.get_instance_grid(
		grid,
		pos=Position(1, 2),
		radius=10,
		layers={"Critter": 1})
	validate_cache_changes(False, last_cache)
