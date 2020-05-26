import random

import pytest

from tests import monkeypatch_godot_import
from tests import helpers
from crawlai.game_scripts.world import World

@pytest.fixture(autouse=True)
def each_test_setup_teardown():
	random.seed("3")

	# Reset instance ID count to 0 before each test
	import godot.bindings as bindings
	original_start_instance_id = bindings.new_instance_id

	yield
	bindings.new_instance_id = original_start_instance_id
	helpers.verify_all_threads_closed()


@pytest.fixture
def world():
	"""Returns a world and closes threads after the test"""
	world = World()
	yield world
	world.close()