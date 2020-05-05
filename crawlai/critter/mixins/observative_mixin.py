from godot.bindings import Node

from typing import List


class ObservativeMixin:
	"""This critter is capable of keeping track of the objects around it's
	InputArea.

	Required Signals:
		_on_input_area_body_entered(*args) & _on_input_area_body_exited(*args)
			Emitted by an Area2D when a body enters (or exits) the collision
			bounds of a child CollisionShape2D.
	"""

	_objects_within: List[Node]
	"""A dict of {RID: [Actor, Actor} """

	@property
	def objects_within(self) -> List[Node]:
		return self._objects_within

	def _ready(self):
		super()._ready()
		self._objects_within = []

	def _on_input_area_body_entered(self, body):
		if body.get_instance_id() != self.get_instance_id():
			self._objects_within.append(body)

	def _on_input_area_body_exited(self, body):
		if body in self._objects_within:
			self._objects_within.remove(body)
		else:
			print("ERROR! Body not in objects within...")
