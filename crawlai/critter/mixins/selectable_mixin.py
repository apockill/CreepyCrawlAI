from godot.bindings import InputEventMouseButton, BUTTON_LEFT

global_selected_critter = None
"""Keep track of the (globally) latest selected critter"""


class SelectableMixin:
	"""This critter is capable of being selected or deselected via clicking.

	Required Signals:
		_on_critter_input_event(*args):
			Emitted by a KinematicBody2D when a mouse performs input in the
			collision bounds.
	"""

	def _on_critter_input_event(self, viewport, event, shape_idx):
		"""Keep track of when a critter has been clicked on or clicked away."""
		if (isinstance(event, InputEventMouseButton)
				and event.pressed
				and event.button_index == BUTTON_LEFT):
			global global_selected_critter
			global_selected_critter = self.get_instance_id()

	def _input(self, event):
		""" Handle when a user clicks away from the critter """
		if (isinstance(event, InputEventMouseButton)
				and event.pressed
				and event.button_index == BUTTON_LEFT):
			global global_selected_critter
			if global_selected_critter == self.get_instance_id():
				global_selected_critter = None

	@property
	def is_selected(self):
		global global_selected_critter
		return global_selected_critter == self.get_instance_id()
