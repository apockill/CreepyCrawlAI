from crawlai.critter.base_critter import BaseCritter


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

	n_nearest_critters = 10
	"""How many critters to include in the inputs for the network"""

	def get_move(self):
		print("AICritter calculating move... Yes, do nothing!")
		return 0, 0
