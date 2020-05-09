from godot import exposed, export
from godot.bindings import KinematicBody2D, Vector2, Sprite


@exposed
class Actor(Sprite):
	velocity = export(Vector2, default=Vector2(0, 0))

	def _ready(self):
		"""
		Called every time the node is added to the scene.
		Initialization here.
		"""

	def _process(self, delta: float) -> None:
		if self.velocity != Vector2(0, 0):
			self.position += self.velocity
