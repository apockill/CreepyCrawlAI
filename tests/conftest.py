import random

from tests import monkeypatch_godot_import
import pytest


@pytest.fixture(autouse=True)
def each_test_setup_teardown():
	random.seed("3")

	# Reset instance ID count to 0 before each test
	import godot.bindings as bindings
	original_start_instance_id = bindings.new_instance_id

	yield
	bindings.new_instance_id = original_start_instance_id
