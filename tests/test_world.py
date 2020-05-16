import mock
import pytest

from godot.bindings import Node

from crawlai.game_scripts.world import World
from crawlai.position import Position
from tests.helpers import validate_grid


def test_basic_functionality():
	"""Basically, make sure things don't crash during normal use"""
	world = World()
	world._ready()
	n_ticks = 100

	for i in range(0, n_ticks):
		world._process(i)


def test_add_item():
	world = World()
	world._ready()

	validate_grid(world.grid)

	class FakeItem:
		def __init__(self):
			self.instance = Node()
			self.id = self.instance.get_instance_id()

		id = 29

	with mock.patch.object(Node, 'queue_free'):
		assert not Node.queue_free.called

		# Put an item in a location
		item = world.add_item(pos=Position(0, 0), item_type=FakeItem)
		validate_grid(world.grid)
		assert isinstance(item, FakeItem)
		assert not Node.queue_free.called

		# Try to put another item in the same location
		item = world.add_item(pos=Position(0, 0), item_type=FakeItem)
		assert Node.queue_free.called
		assert item is None
		validate_grid(world.grid)
