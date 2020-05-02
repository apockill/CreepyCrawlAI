from godot import exposed, export
from godot.bindings import Node2D, ResourceLoader


@exposed
class World(Node2D):
	min_num_critters = export(int, 100)

	def _ready(self):
		critter = ResourceLoader.load("res://Game/Critter/Critter.tscn")
		for i in range(0, self.min_num_critters):
			instance = critter.instance()
			self.add_child(instance)
		print(f"Created {self.min_num_critters} critters")
