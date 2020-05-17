import math

from godot import exposed, export
from godot.bindings import Camera2D, Vector2, Input, BUTTON_MIDDLE, \
	BUTTON_RIGHT, BUTTON_WHEEL_UP, InputEventMouseButton, BUTTON_WHEEL_DOWN
import numpy as np

zoom_signs = {
	BUTTON_WHEEL_UP: 1,
	BUTTON_WHEEL_DOWN: -1
}


@exposed
class PanZoomCamera(Camera2D):
	zoom_step = export(float, default=0.5)
	zoom_min = export(float, default=0.5)
	zoom_max = export(float, default=3.0)
	zoom_speed = export(float, default=2.0)

	zoom_target = 1
	last_mouse_pos = Vector2(0, 0)

	def _ready(self):
		self.set_process_input(True)
		self.set_process(True)

	def move_towards(self, current, target, max_delta):
		dist = target - current
		if abs(dist) <= max_delta:
			return target
		return current + math.copysign(max_delta, dist)

	def _process(self, delta):
		cur_mouse_pos = self.get_viewport().get_mouse_position()

		# mouse panning
		if (Input.is_mouse_button_pressed(BUTTON_MIDDLE)
				or Input.is_mouse_button_pressed(BUTTON_RIGHT)):
			if self.last_mouse_pos != cur_mouse_pos:
				offset = self.last_mouse_pos - cur_mouse_pos
				self.translate(offset * self.get_zoom())

		# smooth zoom
		new_zoom = self.move_towards(
			current=self.get_zoom().x,
			target=self.zoom_target,
			max_delta=self.zoom_speed * delta)
		self.set_zoom(Vector2(new_zoom, new_zoom))

		self.last_mouse_pos = self.get_viewport().get_mouse_position()

	def _input(self, event):

		if (isinstance(event, InputEventMouseButton)
				and event.is_pressed()
				and not event.is_echo()
				and event.button_index in zoom_signs):
			sign = zoom_signs[event.button_index]
			step = self.zoom_step * (1 / (1 + self.zoom_target))
			self.zoom_target += sign * step

		self.zoom_target = np.clip(
			self.zoom_target, self.zoom_min, self.zoom_max)
