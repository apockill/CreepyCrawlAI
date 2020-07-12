from godot.bindings import ResourceLoader

from crawlai.grid_item import GridItem
from crawlai.items.food import Food
from crawlai.math_utils import clamp
from crawlai.turn import Turn
from crawlai.position import Position

_critter_resource = ResourceLoader.load("res://Game/Critter/Critter.tscn")


class BaseCritter(GridItem):
	"""The base class for all critters"""
	HEALTH_TICK_PENALTY = 1
	MAX_HEALTH = 500
	BITE_SIZE = 20

	CHOICES = [
				  Turn(Position(*c), is_action)
				  for c in [(0, 1), (1, 0), (-1, 0), (0, -1)]
				  for is_action in (True, False)
			  ] + [Turn(Position(0, 0), False)]

	def __init__(self):
		super().__init__()
		self.health: int
		self.age: int
		self._reset_stats()

	def _reset_stats(self):
		self.health = self.MAX_HEALTH
		self.age = 0

	def _tick_stats(self):
		self.age += 1
		self.health -= self.HEALTH_TICK_PENALTY

	def _load_instance(self):
		return _critter_resource.instance()

	def perform_action_onto(self, other: 'GridItem'):
		if isinstance(other, Food):
			max_bite = clamp(self.BITE_SIZE, 0, self.MAX_HEALTH - self.health)
			self.health += other.take_nutrition(max_bite)

	@property
	def delete_queued(self):
		return self.health <= 0
