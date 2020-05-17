from godot.bindings import Node
from abc import ABC, abstractmethod

from crawlai.position import Position


class Turn:
	"""This describes a 'turn' that a grid item wants to perform in any given
	step. A turn consists of two things: A direction, and whether or not
	it is an 'action'. If a turn is not an action, then it implies the grid
	item would like to move in 'direction'. If it is an action, then it implies
	that the item would like to apply 'action' at 'direction'.
	"""

	def __init__(self, direction: Position, is_action: bool):
		self.direction = direction
		self.is_action = is_action


class GridItem(ABC):
	def __init__(self):
		self.is_selected: bool = False
		self.instance: Node = self._load_instance()
		self.id: int = self.instance.get_instance_id()

	@abstractmethod
	def tick(self):
		"""This is run on every instance once"""

	@abstractmethod
	def _load_instance(self) -> Node:
		pass

	@abstractmethod
	def perform_action_onto(self, other: 'GridItem'):
		pass

	@abstractmethod
	def get_turn(self, grid) -> Turn:
		pass
