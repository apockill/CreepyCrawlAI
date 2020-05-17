import pytest

from godot.bindings import Node2D

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
	grid = Grid(width=w, height=h)
	item = Critter()
	pos = Position(*pos)

	validate_grid(grid)
	added = grid.add_item(pos, item)
	validate_grid(grid)

	assert added is successful

	if successful:
		assert grid.array[pos.x][pos.y] == item.id
		assert grid.id_to_pos.get(item.id) == pos
		assert grid.id_to_obj.get(item.id) == item
	else:
		assert grid.id_to_obj.get(item.id) is None
		assert grid.id_to_pos.get(item.id) is None
	validate_grid(grid)


def test_random_movement_persists_safely():
	"""Test that randomly moving 'critters' will never end up being deleted
	off of the grid. This method will 'tick' and move critters, running
	validate_grid() every tick. """
	N_CREATURES = 900
	N_TICKS = 1000

	world = Node2D()
	grid = Grid(width=30, height=30)

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
