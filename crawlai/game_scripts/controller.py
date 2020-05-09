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
	min_num_critters = export(int, 1000)
	grid_width = export(int, 100)
	grid_height = export(int, 100)

	def _ready(self):
		self.grid = Grid(width=self.grid_width, height=self.grid_height)
		for i in range(0, self.min_num_critters):
			self.create_item(*self.grid.random_free_cell, Critter())

	def create_item(self, x, y, grid_item):
		"""Add the child to the world node and register it in the grid"""
		self.add_child(grid_item.instance)
		self.grid.add_item(x, y, grid_item)
