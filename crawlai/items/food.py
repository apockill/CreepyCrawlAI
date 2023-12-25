from godot.bindings import Node, ResourceLoader

from crawlai.grid import Grid
from crawlai.grid_item import GridItem
from crawlai.math_utils import clamp


_food_resource = ResourceLoader.load("res://Game/Food/Food.tscn")


class Food(GridItem):
    MAX_NUTRITION = 100

    def __init__(self) -> None:
        super().__init__()
        self.nutrition: int = self.MAX_NUTRITION

    def take_nutrition(self, amount: int) -> int:
        """Returns up to the amount requested, if available"""
        to_take = clamp(amount, 0, self.nutrition)
        self.nutrition -= to_take
        return amount

    def _load_instance(self) -> Node:
        return _food_resource.instance()

    def perform_action_onto(self, other: "GridItem") -> None:
        pass

    def get_turn(self, grid: Grid) -> None:
        pass

    @property
    def delete_queued(self) -> bool:
        return self.nutrition <= 0
