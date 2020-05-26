import random
from pathlib import Path
from time import time

import tensorflow as tf
from progress.bar import IncrementalBar

from tests import monkeypatch_godot_import
from crawlai.game_scripts.world import World
from crawlai.items.critter.critter import Critter


def main():
	tf.random.set_seed(1)
	random.seed("benchmark")

	N_TICKS = 30

	"""Set up benchmark parameters"""
	World.min_num_critters = 1000
	World.min_num_food = 500
	World.grid_width = 250
	World.grid_height = 250
	World.rendering = False
	Critter.INPUT_RADIUS = 30

	# Disable critters dying, to have more consistent benchmarks
	Critter.HEALTH_TICK_PENALTY = 0

	print("Initializing Creatures...")
	world = World()
	world._ready()

	# Sometimes the first tick takes a while (tensorflow allocating memory, etc)
	print("Warming up...")
	world._process()
	world._process()
	world._process()

	print("Beginning Benchmark...")
	start = time()
	for _ in IncrementalBar().iter(list(range(N_TICKS))):
		world._process()
	tps = round(N_TICKS / (time() - start), 3)

	with Path("tests/benchmarking/benchmark.txt").open("a") as f:
		report = f"\nBenchmark: {tps} Ticks per second. Samples: {N_TICKS}"
		f.write(report)
		print(report)


if __name__ == "__main__":
	main()
