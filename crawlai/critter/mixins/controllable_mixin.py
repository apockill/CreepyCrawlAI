from godot.bindings import Vector2, Input

import numpy as np

from crawlai.critter.base_critter import BaseCritter
from crawlai import keybindings

directions = {
	keybindings.MOVE_UP: np.asarray([0, -1]),
	keybindings.MOVE_DOWN: np.asarray([0, 1]),
	keybindings.MOVE_LEFT: np.asarray([-1, 0]),
	keybindings.MOVE_RIGHT: np.asarray([1, 0])
}


class ControllableMixin(BaseCritter):
	"""This critter is capable of being controlled with the arrow keys. """

	speed_multiplier = 300
	"""How fast to move on keypress"""

	def get_move(self):
		if not self.is_selected:
			# Only process input if this critter is selected
			return super().get_move()

		direction = np.asarray([0, 0])
		for key, vector in directions.items():
			direction += vector * int(Input.is_action_pressed(key))
		return direction
