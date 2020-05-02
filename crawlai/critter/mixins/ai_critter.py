class AICritterMixin:
	"""
	Terms
		V: Velocity (x, y components)

	Inputs:
		self.vx
		self.vy

		Nearest 10 critters:
			vx
			vy

	Outputs:
		self.vx
		self.vy

	Desired Features:
		- Add a self.signal
		- Train each step on the outcome of the scenario after running
	"""

	n_nearest_critters = 10
	"""How many critters to include in the inputs for the network"""

	def _physics_process(self, delta):
		super()._physics_process(delta)

	def get_inputs(self):
		"""The inputs to the network are
		self.vx, self.vy and the nearest N_NEAREST_CRITTERS vx and vy.

		"""

	def process_inputs_and_move(self):
		pass
