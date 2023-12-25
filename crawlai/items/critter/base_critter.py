from godot.bindings import Node, ResourceLoader

from crawlai.grid_item import GridItem
from crawlai.items.food import Food
from crawlai.math_utils import clamp
from crawlai.position import Position
from crawlai.turn import Turn

_critter_resource = ResourceLoader.load("assets/critter.png")


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

    def __init__(self) -> None:
        super().__init__()
        self.health: int
        self.age: int
        self._reset_stats()

    def _reset_stats(self) -> None:
        self.health = self.MAX_HEALTH
        self.age = 0

    def _tick_stats(self) -> None:
        self.age += 1
        self.health -= self.HEALTH_TICK_PENALTY

    def _load_instance(self) -> Node:
        return _critter_resource.instance()

    def perform_action_onto(self, other: "GridItem") -> None:
        if isinstance(other, Food):
            max_bite = clamp(self.BITE_SIZE, 0, self.MAX_HEALTH - self.health)
            self.health += other.take_nutrition(max_bite)

    @property
    def delete_queued(self) -> bool:
        return self.health <= 0
