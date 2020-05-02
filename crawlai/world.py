from godot import exposed, export
from godot.bindings import Node2D, ResourceLoader


@exposed
class World(Node2D):
	min_num_critters = export(int, 10)

	def _ready(self):
		critter = ResourceLoader.load("res://Game/Critter/Critter.tscn")
		for i in range(0, self.min_num_critters):
			instance = critter.instance()
			print("Created", instance, instance.global_position)
			self.add_child(instance)
