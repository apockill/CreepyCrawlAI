import random
import itertools
from pathlib import Path
from time import time

import tensorflow as tf
from progress.bar import IncrementalBar

from tests import monkeypatch_godot_import
from crawlai.game_scripts.world import World
from crawlai.items.critter.critter import Critter


class Timer:
	def __init__(self):
		self.start, self.end = None, None

	def __enter__(self):
		self.start = time()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.end = time()

	@property
	def elapsed(self):
		if self.end is None:
			return time() - self.start
		return self.end - self.start


def main():
	tf.random.set_seed(1)
	random.seed("benchmark")

	N_TICKS = 30

	"""Set up benchmark parameters"""
	world = World()
	world.min_num_critters = 1000
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
	for _ in IncrementalBar().iter(list(range(N_TICKS))):
		world._process()
	tps = round(N_TICKS / (time() - start), 3)

	with Path("tests/benchmarking/benchmark.txt").open("a") as f:
		report = \
			f"\nBenchmark: {tps} TPS. " \
			f"N_TICKS: {N_TICKS} " \
			f"world.min_num_critters: {world.min_num_critters}, " \
			f"world.min_num_food {world.min_num_food}, " \
			f"world.grid_width {world.grid_width}, " \
			f"world.grid_height {world.grid_height}, " \
			f"world.rendering {world.rendering}, " \
			f"Critter.INPUT_RADIUS {Critter.INPUT_RADIUS}, " \
			f"Critter.TRAIN_BATCH_SIZE {Critter.TRAIN_BATCH_SIZE}, " \
			f"Critter.REPLAY_BUFFER_CAPACITY {Critter.REPLAY_BUFFER_CAPACITY}"
		f.write(report)
	print(report)


if __name__ == "__main__":
	main()
