from godot import exposed, export
from godot.bindings import (
	Node2D,
	ResourceLoader,
	InputEventMouseButton,
	BUTTON_LEFT,
)

from crawlai.grid import Grid
from crawlai.critter.critter import Critter


@exposed
class World(Node2D):
	min_num_critters = export(int, 0)
	grid_width = export(int, 1)
	grid_height = export(int, 1)
	grid_spacing = export(int, 1)

	def _ready(self):
		self.grid = Grid(
			width=self.grid_width,
			height=self.grid_height,
			spacing=self.grid_spacing,
			root_node=self)
		for i in range(0, self.min_num_critters):
			self.grid.add_item(self.grid.random_free_cell, Critter())
		print("Created", self.min_num_critters, "Critters")

	def _process(self, delta):
		# Run tick for all grid items
		for grid_item in self.grid:
			grid_item.tick()

		moves = {}
		# Process critter moves here, in the future in another thread
		for grid_item in self.grid:
			if isinstance(grid_item, Critter):
				moves[grid_item.id] = grid_item.get_move()

		# Actually move the critters here
		for grid_item in self.grid:
			self.grid.move_item_relative(moves[grid_item.id], grid_item)
