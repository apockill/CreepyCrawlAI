import random

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.critter.mixins.ai_mixin import AICritterMixin
from crawlai.grid_item import Turn


class RandomCritterMixin(BaseCritter):

	def get_turn(self, inputs) -> Turn:
		"""Super smart AI"""
		return random.choice(AICritterMixin.CHOICES)
