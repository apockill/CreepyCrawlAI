from random import choice

from crawlai.grid import Grid
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.turn import Turn


class RandomMoveMixin(BaseCritter):
    def get_turn(self, grid: Grid) -> Turn | None:
        self._tick_stats()
        return choice(self.CHOICES)
