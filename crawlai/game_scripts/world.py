from typing import Type, Optional

from godot import exposed, export
from godot.bindings import Node2D, Vector2

from crawlai.grid import Grid
from crawlai.grid_item import GridItem
from crawlai.items.critter.critter import Critter
from crawlai.items.food import Food
from crawlai.position import Position


@exposed
class World(Node2D):
	min_num_critters = export(int, 0)
	min_num_food = export(int, 0)
	grid_width = export(int, 100)
	grid_height = export(int, 100)
	spacing = export(int, 100)
	rendering: bool = True

	def _ready(self):
		self.grid = Grid(
			width=self.grid_width,
			height=self.grid_height)
		for i in range(0, self.min_num_critters):
			self.add_item(self.grid.random_free_cell, Critter)
		for i in range(0, self.min_num_food):
			self.add_item(self.grid.random_free_cell, Food)
		print("Created", self.min_num_critters, "Critters")
		print("Created", self.min_num_food, "Foods")

	def _process(self, delta):
		self.step(self.grid)

		# Render all sprites
		if self.rendering:
			for grid_item in self.grid:
				pos = self.grid.id_to_pos[grid_item.id]
				grid_item.instance.set_position(
					Vector2(pos.x * self.spacing, pos.y * self.spacing))

	def _on_render_button_toggled(self, button_pressed):
		""" Enable and disable rendering
		Connected to: GUI.RenderButton """
		self.rendering = button_pressed

	def add_item(self, pos: Position,
				 item_type: Type[GridItem]) -> Optional[GridItem]:
		item = item_type()
		successful = self.grid.add_item(pos=pos, grid_item=item)
		if successful:
			self.add_child(item.instance)
			return item
		else:
			item.instance.queue_free()
			return None

	@staticmethod
	def step(grid: Grid):
		"""Perform the logic for one full grid step"""

		# Run tick for all grid items
		for grid_item in grid:
			grid_item.tick()

		turns = {}
		# Get turns here, in the future this will be threaded
		for grid_item in grid:
			turns[grid_item.id] = grid_item.get_turn(grid)

		# Actually run the turns
		for grid_item in grid:
			turn = turns[grid_item.id]
			if turn.is_action:
				grid.apply_action(turn.direction, grid_item)
			else:
				grid.move_item_relative(turn.direction, grid_item)

