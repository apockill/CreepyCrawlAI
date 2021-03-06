from abc import ABC, abstractmethod
from typing import Optional

from godot.bindings import Node

from crawlai.turn import Turn


class GridItem(ABC):
	def __init__(self):
		self.is_selected: bool = False
		self.instance: Node = self._load_instance()
		self.id: int = self.instance.get_instance_id()

	@abstractmethod
	def _load_instance(self) -> Node:
		pass

	@abstractmethod
	def perform_action_onto(self, other: 'GridItem'):
		pass

	@abstractmethod
	def get_turn(self, grid) -> Optional[Turn]:
		pass

	@property
	@abstractmethod
	def delete_queued(self):
		"""Whether the world should delete this object next"""
