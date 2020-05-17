import pytest
from mock import patch

from crawlai.position import Position
from crawlai.grid import Grid
from crawlai.items.critter.critter import Critter
from crawlai.items.food import Food
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


def test_apply_action_in_different_scenarios():
	grid = Grid(width=3, height=3)
	item = Critter()
	grid.add_item(Position(0, 0), grid_item=item)

	with patch.object(item, 'perform_action_onto',
					  wraps=item.perform_action_onto) as perform_action_onto:
		# Test applying action out of bounds fails
		assert not grid.apply_action(Position(-1, 0), item)
		assert not grid.apply_action(Position(-1, -1), item)
		assert not perform_action_onto.called

		# Test applying action on self raises error
		with pytest.raises(RuntimeError):
			grid.apply_action(Position(0, 0), item)
		assert not perform_action_onto.called

		# Test applying action on empty cell does nothing
		assert not grid.apply_action(Position(1, 0), item)
		assert not perform_action_onto.called

		# Now, on the same cell, add a Food item and assert applying action runs
		grid.add_item(Position(1, 0), Food())
		grid.apply_action(Position(1, 0), item)
		assert perform_action_onto.called
