from crawlai.critter.mixins.observative_mixin import ObservativeMixin


class AICritterMixin(ObservativeMixin):
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

	def _process(self, delta):
		super()._process(delta)
		objects = self.objects_within_with_method(["velocity", "health"])

	def get_inputs(self):
		"""The inputs to the network are
		self.vx, self.vy and the nearest N_NEAREST_CRITTERS vx and vy.
		"""

	def process_inputs_and_move(self):
		pass
