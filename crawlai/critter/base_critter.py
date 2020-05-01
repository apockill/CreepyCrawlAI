from godot import exposed

from crawlai.actor import Actor


@exposed
class BaseCritter(Actor):
	"""The base class for all critters"""
	health = 100
	age = 0

	def _ready(self):
		"""
		Called every time the node is added to the scene.
		Initialization here.
		"""
		super()._ready()
