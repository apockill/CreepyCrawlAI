from tests import monkeypatch_godot_import  # noqa: F401 # isort: skip
import random

import tensorflow as tf

from crawlai.game_scripts.world import World
from tests.helpers import Timer


def main(ticks_per_report: int = 1000) -> None:
    tf.random.set_seed(1)
    random.seed("benchmark")

    """Set up benchmark parameters"""
    world = World()
    world.min_num_critters = 1
    world.min_num_food = 50
    world.grid_width = 25
    world.grid_height = 25
    world.rendering = False

    print("Initializing world...")
    world._ready()
    print("Starting simulation...")
    while True:
        with Timer() as timer:
            for _ in range(ticks_per_report):
                world._process()
            print(f"TPS: {round(ticks_per_report / timer.elapsed, 2)}")


if __name__ == "__main__":
    main()
