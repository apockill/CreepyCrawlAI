from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from godot.bindings import Node

from crawlai.turn import Turn

if TYPE_CHECKING:
    from crawlai.grid import Grid


class GridItem(ABC):
    def __init__(self) -> None:
        self.is_selected: bool = False
        self.instance: Node = self._load_instance()
        self.id: int = self.instance.get_instance_id()

    @abstractmethod
    def _load_instance(self) -> Node:
        pass

    @abstractmethod
    def perform_action_onto(self, other: "GridItem") -> None:
        pass

    @abstractmethod
    def get_turn(self, grid: "Grid") -> Turn | None:
        pass

    @property
    @abstractmethod
    def delete_queued(self) -> bool:
        """Whether the world should delete this object next"""
