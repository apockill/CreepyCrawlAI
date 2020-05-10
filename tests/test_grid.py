import pytest
import mock
from godot.bindings import Node2D

from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.critter.base_critter import BaseCritter
from crawlai.critter.mixins.random_movement_mixin import RandomCritterMixin
from crawlai.critter.critter import Critter
from tests.helpers import validate_grid

parameters = [
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
	argvalues=parameters)
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
		assert grid._grid[pos.x][pos.y] != 0
		assert grid.id_to_pos.get(item.id) == pos
		assert grid.id_to_obj.get(item.id) == item
	else:
		assert grid.id_to_obj.get(item.id) is None
		assert grid.id_to_pos.get(item.id) is None
	validate_grid(grid)


def test_random_movement_persists_safely():
	"""Test that randomly moving 'critters' will never end up being deleted
	off of the grid"""
	N_CREATURES = 1250
	N_TICKS = 1000

	world = Node2D()
	grid = Grid(width=50, height=50, spacing=100, root_node=world)

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
			moves[item.id] = item.get_move()

		for i, item in enumerate(grid):
			grid.move_item_relative(moves[item.id], item)
		validate_grid(grid)

		# Verify that all of the critters are still around
		assert len(list(grid)) == N_CREATURES
