from random import choice
from typing import Optional

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.turn import Turn


class RandomMoveMixin(BaseCritter):
    def get_turn(self, grid) -> Optional[Turn]:
        self._tick_stats()
        return choice(self.CHOICES)
