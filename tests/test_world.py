from crawlai.game_scripts.world import World


def test_basic_functionality():
	"""Basically, make sure things don't crash during normal use"""
	world = World()
	world._ready()
	N_TICKS = 100

	for i in range(0, N_TICKS):
		world._process(i)
