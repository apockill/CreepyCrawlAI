from godot import exposed, export
from godot.bindings import Vector2, Input

from crawlai.critter.selectable_critter import SelectableCritter
from crawlai import keybindings

directions = {
	keybindings.MOVE_UP: Vector2(0, -1),
	keybindings.MOVE_DOWN: Vector2(0, 1),
	keybindings.MOVE_LEFT: Vector2(-1, 0),
	keybindings.MOVE_RIGHT: Vector2(1, 0)
}


class ControllableCritter(SelectableCritter):
	controller_speed = 300

	def _physics_process(self, delta: float) -> None:
		super()._physics_process(delta)

		if not self.is_selected:
			# Only process input if this critter is selected
			return

		direction = Vector2(0, 0)
		for key, vector in directions.items():
			direction += vector * int(Input.is_action_pressed(key))
		direction = direction.normalized()
		self.velocity = direction * self.controller_speed
