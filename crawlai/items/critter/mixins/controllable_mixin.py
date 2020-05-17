from godot.bindings import Input

from crawlai.items.critter.base_critter import BaseCritter
from crawlai import keybindings
from crawlai.position import Position
from crawlai.turn import Turn

directions = {
	keybindings.MOVE_UP: Position(0, -1),
	keybindings.MOVE_DOWN: Position(0, 1),
	keybindings.MOVE_LEFT: Position(-1, 0),
	keybindings.MOVE_RIGHT: Position(1, 0)
}


class ControllableMixin(BaseCritter):
	"""This critter is capable of being controlled with the arrow keys. """

	speed_multiplier = 300
	"""How fast to move on keypress"""

	def get_turn(self, inputs) -> Turn:
		if not self.is_selected:
			# Only process input if this critter is selected
			return super().get_turn(inputs)

		direction = Position(0, 0)
		for key, vector in directions.items():
			direction += vector * int(Input.is_action_pressed(key))
		return Turn(direction, False)
