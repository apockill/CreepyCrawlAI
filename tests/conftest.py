import random
import sys

# Do an import hack to replace the godot libraries with mocks for testing
import tests.godot_mock

sys.modules["godot"] = tests.godot_mock

from godot.bindings import Node2D
import pytest

from crawlai.grid import Grid


@pytest.fixture(autouse=True)
def each_test_setup_teardown():
	random.seed("3")

	# Reset instance ID count to 0 before each test
	import godot.bindings as bindings
	bindings.new_instance_id = 0

	yield
