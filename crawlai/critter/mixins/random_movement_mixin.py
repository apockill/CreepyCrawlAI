import random

from typing import Tuple

from crawlai.critter.base_critter import BaseCritter
from crawlai.critter.mixins.ai_mixin import AICritterMixin


class RandomCritterMixin(BaseCritter):

	def get_move(self) -> Tuple[int, int]:
		"""Super smart AI"""
		return random.choice(AICritterMixin.CHOICES)
