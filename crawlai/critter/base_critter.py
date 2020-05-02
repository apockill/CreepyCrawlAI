from godot import exposed, export

from crawlai.actor import Actor


@exposed
class BaseCritter(Actor):
	"""The base class for all critters"""
	health = export(int, default=100)
	age = export(int, default=0)
