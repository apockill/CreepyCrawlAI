from godot.bindings import ResourceLoader

from crawlai.grid_item import GridItem
from crawlai.math_utils import clamp

_food_resource = ResourceLoader.load("res://Game/Food/Food.tscn")


class Food(GridItem):
    MAX_NUTRITION = 100

    def __init__(self):
        super().__init__()
        self.nutrition = self.MAX_NUTRITION

    def take_nutrition(self, amount):
        """Returns up to the amount requested, if available"""
        to_take = clamp(amount, 0, self.nutrition)
        self.nutrition -= to_take
        return amount

    def _load_instance(self):
        return _food_resource.instance()

    def perform_action_onto(self, other: "GridItem"):
        pass

    def get_turn(self, grid):
        pass

    @property
    def delete_queued(self):
        return self.nutrition <= 0
