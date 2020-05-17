from crawlai.grid_item import GridItem

from godot.bindings import ResourceLoader

from crawlai.grid_item import GridItem

_food_resource = ResourceLoader.load("res://Game/Food/Food.tscn")


class Food(GridItem):
	def __init__(self):
		super().__init__()
		self.nutrition = 100

	def tick(self):
		pass

	def _load_instance(self):
		return _food_resource.instance()

	def perform_action_onto(self, other: 'GridItem'):
		pass

	def get_turn(self, grid):
		pass
