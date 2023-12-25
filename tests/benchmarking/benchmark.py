import os
import random
from pathlib import Path
from time import time

import tensorflow as tf
from progress.bar import IncrementalBar

from crawlai.game_scripts.world import World
from crawlai.items.critter.critter import Critter
from tests import monkeypatch_godot_import  # noqa: F401
from tests.helpers import Timer


def main(min_num_critters: int, n_ticks: int) -> None:
    tf.random.set_seed(1)
    random.seed("benchmark")

    """Set up benchmark parameters"""
    world = World()
    world.min_num_critters = min_num_critters
    world.min_num_food = 500
    world.grid_width = 250
    world.grid_height = 250
    world.rendering = False

    # Disable critters dying, to have more consistent benchmarks
    Critter.HEALTH_TICK_PENALTY = 0

    print("Initializing Creatures...")
    world._ready()

    # Sometimes the first few ticks take a while as tensorflow JIT compiles
    # various different ops.
    # This loop will run until ticks are consistently within 20% the same TPS
    # at which point it will call world._process one last time, and break
    print("Warming up", end="", flush=True)
    last_time = float("inf")
    for _ in range(100):
        with Timer() as timer:
            world._process()
            if abs(1 - timer.elapsed / last_time) < 0.2:
                world._process()
                break
            last_time = timer.elapsed
        print(".", end="", flush=True)

    print("\nBeginning Benchmark...")
    start = time()
    for _ in IncrementalBar().iter(list(range(n_ticks))):
        world._process()
    tps = round(n_ticks / (time() - start), 3)

    with Path("tests/benchmarking/benchmark.txt").open("a") as f:
        cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES", None)
        critters = [c for c in world.grid if isinstance(c, Critter)]
        print("Critters", critters)
        steps = int(critters[0].steps)
        avg_total_reward = round(
            sum(float(c.total_reward) for c in critters) / steps, 1
        )
        avg_total_deaths = round(sum(c.deaths for c in critters) / steps, 1)
        report = (
            f"\n{tps=}, "
            f"{avg_total_reward=}, "
            f"{avg_total_deaths=}, "
            f"{n_ticks=} "
            f"{world.min_num_critters=}, "
            f"{world.min_num_food=}, "
            f"{world.grid_width=}, "
            f"{world.grid_height=}, "
            f"{world.rendering=}, "
            f"{Critter.INPUT_RADIUS=}, "
            f"{Critter.TRAIN_BATCH_SIZE=}, "
            f"{Critter.REPLAY_BUFFER_CAPACITY=}, "
            f"{cuda_devices=}"
        )
        f.write(report)
    print(report)


if __name__ == "__main__":
    main(20, 100)
