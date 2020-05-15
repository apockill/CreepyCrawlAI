from godot import exposed, export
from godot.bindings import Node2D

from crawlai.grid import Grid
from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.critter.critter import Critter
from crawlai.items.food import Food


@exposed
class World(Node2D):
	min_num_critters = export(int, 100)
	min_num_food = export(int, 10)
	grid_width = export(int, 100)
	grid_height = export(int, 100)
	grid_spacing = export(int, 100)

	def _ready(self):
		self.grid = Grid(
			width=self.grid_width,
			height=self.grid_height,
			spacing=self.grid_spacing,
			root_node=self)
		for i in range(0, self.min_num_critters):
			self.grid.add_item(self.grid.random_free_cell, Critter())
		for i in range(0, self.min_num_food):
			self.grid.add_item(self.grid.random_free_cell, Food())
		print("Created", self.min_num_critters, "Critters")
		print("Created", self.min_num_food, "Foods")

	def _process(self, delta):
		# Run tick for all grid items
		for grid_item in self.grid:
			grid_item.tick()

		moves = {}
		# Process critter moves here, in the future in another thread
		for grid_item in self.grid:
			if isinstance(grid_item, BaseCritter):
				moves[grid_item.id] = grid_item.get_move(self.grid)

		# Actually move the critters here
		for grid_item in self.grid:
			if isinstance(grid_item, BaseCritter):
				self.grid.move_item_relative(moves[grid_item.id], grid_item)

	def _on_render_button_toggled(self, button_pressed):
		""" Enable and disable rendering
		Connected to: GUI.RenderButton """
		self.grid.rendering = button_pressed
