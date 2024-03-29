from unittest.mock import patch

from crawlai.game_scripts.world import World
from crawlai.grid import Grid
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.critter.critter import Critter
from crawlai.items.critter.mixins.random_move_mixin import RandomMoveMixin
from crawlai.items.food import Food
from crawlai.position import Position
from crawlai.turn import Turn
from tests.helpers import validate_grid


def test_dies_of_hunger(world: World) -> None:
    """Test the critter dies if left alone for the appropriate number of
    steps (without a food source)."""

    # Instantiate the world
    world.min_num_food = 0
    world.min_num_critters = 0
    world._ready()

    world.add_item(world.grid.random_free_cell, RandomMoveMixin())

    assert len(list(world.grid)) == 1

    n_steps_till_death = int(BaseCritter.MAX_HEALTH / BaseCritter.HEALTH_TICK_PENALTY)
    print("n steps", n_steps_till_death)
    with patch.object(
        world.grid, "delete_item", wraps=world.grid.delete_item
    ) as delete_item:
        for _ in range(n_steps_till_death - 1):
            world._process()
            assert not delete_item.called
            validate_grid(world.grid)

        world._process()
        assert delete_item.called
        validate_grid(world.grid)


def test_consumes_food_then_dies(world: World) -> None:
    """Test that a critter consumes food then dies at the appropriate time"""

    class FoodEater(BaseCritter):
        def get_turn(self, grid: Grid) -> Turn:
            self._tick_stats()
            return Turn(Position(1, 0), is_action=True)

    world.min_num_critters = 0
    world.min_num_food = 0
    world._ready()

    assert len(list(world.grid)) == 0

    critter = world.add_item(Position(1, 1), item=FoodEater())
    food = world.add_item(Position(2, 1), item=Food())
    assert critter is not None
    assert food is not None

    n_steps_till_food_depleted = int(Food.MAX_NUTRITION / Critter.HEALTH_TICK_PENALTY)
    n_steps_till_death = int(Critter.MAX_HEALTH / Critter.HEALTH_TICK_PENALTY)
    with patch.object(
        world.grid, "delete_item", wraps=world.grid.delete_item
    ) as delete_item:
        # Verify the critter is consuming
        for _ in range(n_steps_till_food_depleted - 1):
            world._process()
            assert food.nutrition != food.MAX_NUTRITION
            assert critter.health == Critter.MAX_HEALTH
            assert not delete_item.called

        # Verify the food is marked for deletion
        world._process()
        assert delete_item.call_count == 1

        # Wait for the critter to die of hunger
        for _ in range(n_steps_till_death - 1):
            world._process()
            assert critter.health != Critter.MAX_HEALTH
            assert delete_item.call_count == 1

        world._process()
        assert delete_item.call_count == 2
