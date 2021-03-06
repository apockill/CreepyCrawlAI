import random

import tensorflow as tf

from tests import monkeypatch_godot_import
from tests.helpers import Timer
from crawlai.game_scripts.world import World


def main(ticks_per_report):
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
			for i in range(ticks_per_report):
				world._process()
			print(f"TPS: {round(ticks_per_report / timer.elapsed, 2)}")


if __name__ == "__main__":
	main(
		ticks_per_report=1000
	)
