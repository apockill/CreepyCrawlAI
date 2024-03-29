from unittest.mock import patch

import pytest

from crawlai.grid import Grid
from crawlai.items.critter.critter import Critter
from crawlai.items.food import Food
from crawlai.position import Position
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
    argnames=("w", "h", "successful", "xy"), argvalues=test_add_item_parameters
)
def test_add_item(w: int, h: int, successful: bool, xy: tuple[int, int]) -> None:
    grid = Grid(width=w, height=h)
    item = Critter()
    pos = Position(*xy)

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


def test_apply_action_in_different_scenarios() -> None:
    grid = Grid(width=3, height=3)
    item = Critter()
    grid.add_item(Position(0, 0), grid_item=item)

    with patch.object(
        item, "perform_action_onto", wraps=item.perform_action_onto
    ) as perform_action_onto:
        # Test applying action out of bounds fails
        assert not grid.apply_action(Position(-1, 0), item)
        assert not grid.apply_action(Position(-1, -1), item)
        assert not grid.apply_action(Position(0, -1), item)
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


test_move_item_parameters = [
    # Valid locations
    *[((x, y), True) for x in range(3) for y in range(3) if (x, y) != (0, 0)],
    # Bad coordinates past the top left of the grid
    ((0, 0), False),
    ((-1, 0), False),
    ((0, -1), False),
    ((-1, -1), False),
    # Bad coordinates past the bottom right of the grid
    *[((x, y), False) for x in range(4, 7) for y in range(4, 7)],
]


@pytest.mark.parametrize(
    argnames=("pos", "expected_success"), argvalues=test_move_item_parameters
)
def test_move_item(pos: tuple[int, int], expected_success: bool) -> None:
    grid = Grid(width=3, height=3)
    item = Critter()
    start_pos = Position(0, 0)
    end_pos = Position(*pos)
    grid.add_item(start_pos, grid_item=item)

    validate_grid(grid)
    assert (
        grid.try_move_item(end_pos, item) is expected_success
    ), f"Failed to move from {grid.id_to_pos[item.id]} to {pos}"
    validate_grid(grid)

    expected_pos = end_pos if expected_success else start_pos
    assert grid.id_to_pos[item.id] == expected_pos
    assert grid.id_to_obj[item.id] is item
    assert grid.array[expected_pos.x][expected_pos.y] == item.id


def test_grid_locking() -> None:
    """Test that a grid is locked while in a context manager"""
    grid = Grid(width=5, height=100)
    item = Critter()

    grid.add_item(Position(1, 1), item)

    # Test none of the following work
    with pytest.raises(TypeError):
        hash(grid)
    with grid as locked_grid:
        assert isinstance(hash(grid), int)
        with pytest.raises(Grid.WritingToLockedGrid):
            locked_grid.move_item_relative(Position(1, 1), item)
        with pytest.raises(Grid.WritingToLockedGrid):
            locked_grid.add_item(locked_grid.random_free_cell, Critter())
        with pytest.raises(Grid.WritingToLockedGrid):
            locked_grid.try_move_item(locked_grid.random_free_cell, item)
    validate_grid(grid)

    # Test all of the following do work
    assert locked_grid.move_item_relative(Position(1, 1), item)
    assert locked_grid.add_item(locked_grid.random_free_cell, Critter())
    assert locked_grid.try_move_item(locked_grid.random_free_cell, item)
    validate_grid(grid)
