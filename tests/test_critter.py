from mock import patch

from crawlai.game_scripts.world import World
from crawlai.items.critter.critter import Critter
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.food import Food
from crawlai.turn import Turn
from crawlai.position import Position
from tests.helpers import validate_grid


def test_dies_of_hunger():
	"""Test the critter dies if left alone for the appropriate number of
	steps (without a food source). """

	# Instantiate the world
	world = World()
	world.min_num_food = 0
	world.min_num_critters = 1
	world._ready()

	assert len(list(world.grid)) == 1

	n_steps_till_death = int(Critter.MAX_HEALTH / Critter.HEALTH_TICK_PENALTY)

	with patch.object(world.grid, 'delete_item',
					  wraps=world.grid.delete_item) as delete_item:
		for i in range(n_steps_till_death - 1):
			world._process(0)
			assert not delete_item.called
			validate_grid(world.grid)

		world._process(0)
		assert delete_item.called
		validate_grid(world.grid)


def test_consumes_food_then_dies():
	"""Test that a critter consumes food then dies at the appropriate time"""

	class FoodEater(BaseCritter):
		def get_turn(self, grid) -> Turn:
			return Turn(Position(1, 0), is_action=True)

	world = World()
	world.min_num_critters = 0
	world.min_num_food = 0
	world._ready()

	assert len(list(world.grid)) == 0

	critter: FoodEater = world.add_item(Position(1, 1), item_type=FoodEater)
	food: Food = world.add_item(Position(2, 1), item_type=Food)

	n_steps_till_food_depleted = int(Food.MAX_NUTRITION
									 / Critter.HEALTH_TICK_PENALTY)
	n_steps_till_death = int(Critter.MAX_HEALTH / Critter.HEALTH_TICK_PENALTY)
	with patch.object(world.grid, 'delete_item',
					  wraps=world.grid.delete_item) as delete_item:
		# Verify the critter is consuming
		for i in range(n_steps_till_food_depleted - 1):
			world._process(0)
			assert food.nutrition != food.MAX_NUTRITION
			assert critter.health == Critter.MAX_HEALTH
			assert not delete_item.called

		# Verify the food is marked for deletion
		world._process(0)
		assert delete_item.call_count == 1

		# Wait for the critter to die of hunger
		for i in range(n_steps_till_death - 1):
			world._process(0)
			assert critter.health != Critter.MAX_HEALTH
			assert delete_item.call_count == 1

		world._process(0)
		assert delete_item.call_count == 2
