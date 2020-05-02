from godot import exposed
from godot.bindings import Node2D


@exposed
class World(Node2D):

	def _ready(self):
		"""
		Called every time the node is added to the scene.
		Initialization here.
		"""
		pass
