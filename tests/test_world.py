from mock import patch
import pytest

from godot.bindings import Node

from crawlai.items.critter.critter import Critter
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.game_scripts.world import World
from crawlai.position import Position
from crawlai.items.food import Food
from crawlai.turn import Turn
from tests.helpers import validate_grid


@pytest.fixture
def undying_base_critter_type():
	"""Modifies the BaseCritter class to never die"""
	original_tick_penalty = BaseCritter.HEALTH_TICK_PENALTY
	yield BaseCritter
	BaseCritter.HEALTH_TICK_PENALTY = original_tick_penalty


def test_random_movement_persists_safely(undying_base_critter_type,
										 world: World):
	"""Basically, make sure things don't crash during normal use"""
	world.min_num_critters = 10
	world.min_num_food = 100
	world.grid_height = 25
	world.grid_width = 15
	n_ticks = 100

	world._ready()
	validate_grid(world.grid)

	# Simulate the world for various ticks, asserting that the board state
	# is changing between ticks (very, _very_ unlikely that it doesn't)
	state_before = world.grid.array.copy()
	for i in range(0, n_ticks):
		world._process()
		validate_grid(world.grid)
	assert not (state_before == world.grid.array).all(), \
		f"There was no change in the grid!\n{world.grid.array}"


def test_add_item(world: World):
	world._ready()

	# Make sure world._ready() didn't instantiate anything
	assert len(list(world.grid)) == 0
	validate_grid(world.grid)

	class FakeItem:
		def __init__(self):
			self.instance = Node()
			self.id = self.instance.get_instance_id()

		id = 29

	with patch.object(Node, 'queue_free'):
		assert not Node.queue_free.called

		# Put an item in a location
		item = world.add_item(pos=Position(0, 0), item=FakeItem())
		validate_grid(world.grid)
		assert isinstance(item, FakeItem)
		assert not Node.queue_free.called

		# Try to put another item in the same location
		item = world.add_item(pos=Position(0, 0), item=FakeItem())
		assert Node.queue_free.called
		assert item is None
		validate_grid(world.grid)


directions = ((0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, 1))
test_critter_movement_parameters = [
	# Test all non-action cases with no obstruction
	((1, 1), (0, 1), (1, 2), False, False),
	((1, 1), (1, 0), (2, 1), False, False),
	((1, 1), (1, 1), (2, 2), False, False),
	((1, 1), (0, -1), (1, 0), False, False),
	((1, 1), (-1, 0), (0, 1), False, False),
	((1, 1), (-1, -1), (0, 0), False, False),

	# Test all non-action cases with obstructions
	*(((1, 1), direction, (1, 1), False, True) for direction in directions),

	# Test all action cases with an empty cell in the action position
	*(((1, 1), direction, (1, 1), True, False) for direction in directions),

	# Test all action cases with an occupied cell in the action position
	*(((1, 1), direction, (1, 1), True, True) for direction in directions),
]


@pytest.mark.parametrize(
	argnames=('pos', 'move', 'expected_pos', 'is_action', 'move_pos_occupied'),
	argvalues=test_critter_movement_parameters)
def test_critter_movement_and_actions(pos, move, expected_pos, is_action,
									  move_pos_occupied, world: World):
	"""Test different move cases and actions.
	If is_action is True, we verify that any critters that were in pos+move
	have their relevant functions called. If is_action performs onto an empty
	space, this is verified as well.
	:param pos: Starting position
	:param move: A direction
	:param is_action:
		If true, apply an action in the direction "move"
		If false, simply move (no action).
	:param expected_pos:
		If is_action, then this should be the same as pos.
		If not is_action, then this should be the position after moving.
	:param move_pos_occupied:
		If True, an item will be placed in the pos+move cell before the item
		is requested to move.
	"""

	class PresetCritter(Critter):
		def get_turn(self, inputs):
			return Turn(Position(*move), is_action)

	# Instantiate the world
	world.grid_width = 3
	world.grid_height = 3
	world._ready()
	assert len(list(world.grid)) == 0
	validate_grid(world.grid)

	# Add the item at the initial position
	item = world.add_item(Position(*pos), item=PresetCritter())
	assert len(list(world.grid)) == 1
	validate_grid(world.grid)

	# If the move position is supposed to be obsructed, add an item there
	if move_pos_occupied:
		world.add_item(Position(*pos) + Position(*move), item=Food())
		validate_grid(world.grid)
	grid_array_before = world.grid.array.copy()

	# Verify appropriate functions get called in each case
	with patch.object(world.grid, 'move_item_relative',
					  wraps=world.grid.move_item_relative) as move_item:
		with patch.object(world.grid, 'apply_action',
						  wraps=world.grid.apply_action) as apply_action:
			with patch.object(item, 'perform_action_onto',
							  wraps=item.perform_action_onto) as perform_action:
				assert not move_item.called
				assert not apply_action.called
				assert not perform_action.called
				world.step(world.grid, world.pool)

				# Apply action should always be called when a creature says
				# it wants to make an action
				assert apply_action.called == is_action

				# A creature should only perform an action if there is an item
				# in the action square, and if the creature said it wanted to
				# make an action
				assert perform_action.called == (
						move_pos_occupied and is_action)

				# Move item should always be attempted if the creature says
				# it wants to move.
				assert move_item.called == (not is_action)

	if move_pos_occupied or is_action:
		# Verify the grid didn't change if this wasn't an action and
		# there was an empty space
		assert (grid_array_before == world.grid.array).all()
	else:
		# Verify the grid did change if this wasn't an action and the creature
		# wanted to move into an unubstructed spot
		assert (grid_array_before != world.grid.array).any()

	validate_grid(world.grid)

	final_pos = world.grid.id_to_pos[item.id]
	assert final_pos == Position(*expected_pos)


def test_world_respawns_food(world):
	world.min_num_food = 100
	world._ready()

	def get_foods():
		return [item for item in world.grid if isinstance(item, Food)]

	# Verify the world spawned food as expected before the first tick
	assert len(get_foods()) == world.min_num_food

	# Smoke test
	world._process()
	assert len(get_foods()) == world.min_num_food

	# Delete some food and verify the world respawns it
	for i in range(10):
		food_item = get_foods()[0]
		world.grid.delete_item(food_item)
	assert len(get_foods()) == world.min_num_food - 10

	# Run world._process() and verify food was regenerated
	world._process()
	assert len(get_foods()) == world.min_num_food
