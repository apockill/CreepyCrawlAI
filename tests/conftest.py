import random
from collections.abc import Generator

import pytest

from crawlai.game_scripts.world import World
from crawlai.model import extract_inputs
from tests import helpers, monkeypatch_godot_import


@pytest.fixture(autouse=True)
def each_test_setup_teardown() -> Generator[None, None, None]:
    random.seed("3")

    # Reset instance ID count to 0 before each test
    import godot.bindings as bindings

    original_start_instance_id = bindings.new_instance_id
    # Reset the cache before each test
    original_cache_state = extract_inputs._instance_grid_cache.copy()

    yield
    # Restore original values
    bindings.new_instance_id = original_start_instance_id
    extract_inputs._instance_grid_cache = original_cache_state
    helpers.verify_all_threads_closed()


@pytest.fixture
def world() -> Generator[World, None, None]:
    """Returns a world and closes threads after the test"""
    world = World()
    yield world
    world.close()
