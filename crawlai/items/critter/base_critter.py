from typing import Tuple
from abc import abstractmethod

from godot.bindings import ResourceLoader

from crawlai.grid_item import GridItem
from crawlai.position import Position

_critter_resource = ResourceLoader.load("res://Game/Critter/Critter.tscn")


class BaseCritter(GridItem):
	"""The base class for all critters"""

	def __init__(self):
		super().__init__()
		self.health = 100
		self.age = 0

	def tick(self):
		self.age += 1

	def _load_instance(self):
		return _critter_resource.instance()

	def perform_action_onto(self, other: 'GridItem'):
		pass
