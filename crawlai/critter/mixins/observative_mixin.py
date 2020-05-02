from godot.bindings import Node

from typing import List, DefaultDict
from collections import defaultdict

from crawlai.actor import Actor


class ObservativeMixin:
	"""This critter is capable of keeping track of the objects around it's
	InputArea.

	Required Signals:
		_on_input_area_body_entered(*args) & _on_input_area_body_exited(*args)
			Emitted by an Area2D when a body enters (or exits) the collision
			bounds of a child CollisionShape2D.
	"""

	objects_within: List[Node]
	"""A dict of {RID: [Actor, Actor} """

	def _ready(self):
		super()._ready()
		self.objects_within = []

	def _on_input_area_body_entered(self, body):
		if body.get_instance_id() != self.get_instance_id():
			self.objects_within.append(body)

	def _on_input_area_body_exited(self, body):
		self.objects_within.remove(body)
