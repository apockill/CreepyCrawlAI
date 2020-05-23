import random
from pathlib import Path
from time import time

from tests import monkeypatch_godot_import

from crawlai.game_scripts.world import World
from crawlai.items.critter.critter import Critter
from crawlai import model

def main():
	random.seed("benchmark")

	N_TICKS = 10000

	"""Set up benchmark parameters"""
	World.min_num_critters = 1000
	World.min_num_food = 500
	World.grid_width = 250
	World.grid_height = 250
	World.rendering = False
	model.extract_inputs._INPUT_RADIUS = 30

	# Disable critters dying, to have more consistent benchmarks
	Critter.HEALTH_TICK_PENALTY = 0

	world = World()
	world._ready()

	start = time()
	for i in range(N_TICKS):
		world._process(0)
	tps = N_TICKS / (time() - start)

	with Path("tests/benchmarking/benchmark.txt").open("a") as f:
		f.write(f"\nBenchmark: {tps} Ticks per second")


if __name__ == "__main__":
	main()
