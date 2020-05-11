import random

from typing import Tuple

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.critter.mixins.ai_mixin import AICritterMixin


class RandomCritterMixin(BaseCritter):

	def get_move(self, inputs) -> Tuple[int, int]:
		"""Super smart AI"""
		return random.choice(AICritterMixin.CHOICES)
