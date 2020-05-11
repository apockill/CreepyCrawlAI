import random

from crawlai.items.critter.base_critter import BaseCritter
from crawlai.position import Position


class AICritterMixin(BaseCritter):
	"""
	Terms
		V: Velocity (x, y components)

	Inputs:
		self.vx
		self.vy
		self.health

		Nearest 10 critters:
			vx
			vy
			health
	Outputs:
		self.vx
		self.vy

	Desired Features:
		- Add a self.signal
		- Train each step on the outcome of the scenario after running
	"""
	CHOICES = [Position(*c) for c in [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1)]]

	def __init__(self):
		super().__init__()

	def get_move(self, inputs) -> Position:
		"""Super smart AI goes here"""
		return random.choice(self.CHOICES)
