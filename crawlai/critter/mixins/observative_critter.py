from godot import exposed, export

from typing import Set, DefaultDict
from collections import defaultdict
from godot.bindings import Node

from crawlai.actor import Actor


class ObservativeMixin:
	"""This critter is capable of keeping track of the objects around it's
	InputArea.

	Required Signals:
		_on_input_area_body_entered(*args) & _on_input_area_body_exited(*args)
			Emitted by an Area2D when a body enters (or exits) the collision
			bounds of a child CollisionShape2D.
	"""

	objects_within: DefaultDict[int, Set[Actor]]
	"""A dict of {RID: Set(Node, Node, Node)} """

	def _ready(self):
		self.objects_within = defaultdict(set)
		super()._ready()

	def _on_input_area_body_entered(self, body):
		print("Entered", body)

	def _on_input_area_body_exited(self, body):
		print("Exited", body)
