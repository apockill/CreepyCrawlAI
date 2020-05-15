import pytest
import mock

from godot.bindings import Node2D
import numpy as np

from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.items.critter.mixins.random_movement_mixin import \
	RandomCritterMixin
from crawlai.items.critter.critter import Critter
from tests.helpers import validate_grid

test_add_item_parameters = [
	# Test the grid boundaries
	(100, 100, True, (0, 0)),
	(100, 100, True, (0, 99)),
	(100, 100, True, (99, 0)),
	(100, 100, True, (99, 99)),
	(100, 100, False, (100, 0)),
	(100, 100, False, (0, 100)),
	(100, 100, False, (100, 100)),
]


@pytest.mark.parametrize(
	argnames=('w', 'h', 'successful', 'pos'),
	argvalues=test_add_item_parameters)
def test_add_item(w, h, successful, pos):
	grid = Grid(width=w, height=h, spacing=100, root_node=Node2D())
	item = Critter()
	pos = Position(*pos)

	with mock.patch.object(item.instance, 'queue_free'):
		added = grid.add_item(pos, item)

		if not successful: \
				# Verify item is deleted if it isn't added to the grid
			assert item.instance.queue_free.called

	assert added is successful

	if successful:
		assert grid.array[pos.x][pos.y] != 0
		assert grid.id_to_pos.get(item.id) == pos
		assert grid.id_to_obj.get(item.id) == item
	else:
		assert grid.id_to_obj.get(item.id) is None
		assert grid.id_to_pos.get(item.id) is None
	validate_grid(grid)


def test_random_movement_persists_safely():
	"""Test that randomly moving 'critters' will never end up being deleted
	off of the grid"""
	N_CREATURES = 900
	N_TICKS = 1000

	world = Node2D()
	grid = Grid(width=30, height=30, spacing=100, root_node=world)

	# Populate the grid
	for _ in range(N_CREATURES):
		grid.add_item(
			pos=grid.random_free_cell,
			grid_item=RandomCritterMixin())
	validate_grid(grid)

	# Move creatures randomly through the grid for a while
	for i in range(N_TICKS):
		for item in grid:
			item.tick()

		moves = {}
		for item in grid:
			moves[item.id] = item.get_move(grid)

		for i, item in enumerate(grid):
			grid.move_item_relative(moves[item.id], item)
		validate_grid(grid)

		# Verify that all of the critters are still around
		assert len(list(grid)) == N_CREATURES


test_get_grid_around_parameters = [
	# # Basic checks at each corner-1 to check grid works normally without padding
	((1, 1), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((2, 3), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((2, 1), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((1, 3), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),

	# Check actual corners to see the grid applies padding correctl
	((0, 0), 1, np.asarray([[-1, -1, -1], [-1, 1, 0], [-1, 0, 0]])),
	((3, 4), 1, np.asarray([[0, 0, -1], [0, 1, -1], [-1, -1, -1]])),
	((0, 4), 1, np.asarray([[-1, -1, -1], [0, 1, -1], [0, 0, -1]])),
	((3, 0), 1, np.asarray([[-1, 0, 0], [-1, 1, 0], [-1, -1, -1]])),

	# Check the middles of each grid edge
	((0, 2), 1, np.asarray([[-1, -1, -1], [0, 1, 0], [0, 0, 0]])),
	((3, 2), 1, np.asarray([[0, 0, 0], [0, 1, 0], [-1, -1, -1]])),
	((1, 4), 1, np.asarray([[0, 0, -1], [0, 1, -1], [0, 0, -1]])),
	((1, 0), 1, np.asarray([[-1, 0, 0], [-1, 1, 0], [-1, 0, 0]])),

	# Check a radius of two near the center
	((1, 2), 2, np.asarray([[-1, -1, -1, -1, -1],
							[0, 0, 0, 0, 0],
							[0, 0, 1, 0, 0],
							[0, 0, 0, 0, 0],
							[0, 0, 0, 0, 0]])),

	# Check a large, off-center radius
	((1, 1), 4, np.asarray([[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, 0, 1, 0, 0, 0, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1]]))
]


@pytest.mark.parametrize(
	argnames=('pos', 'radius', 'output_grid'),
	argvalues=test_get_grid_around_parameters)
def test_get_grid_around(pos, radius, output_grid):
	"""Creates a grid of shape:
	[[0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]]

	 and places a critter at position 'pos', then calls get_grid_around with a
	 radius of 'radius', and verifies the output grid is the same as
	 'output_grid'
    """
	# print("POS", pos)
	grid = Grid(width=4, height=5, spacing=0, root_node=Node2D())
	grid.add_item(pos=Position(*pos), grid_item=Critter())
	grid_around = Critter.get_instance_grid(
		grid=grid,
		pos=Position(*pos),
		radius=radius)

	h, w = grid_around.shape
	assert h == w
	assert (grid_around == output_grid).all()
