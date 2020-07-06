from typing import Type, Optional
from multiprocessing.pool import ThreadPool
from collections import Counter

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
		self._spawn_items()
		self.pool = ThreadPool()

	def _process(self, delta=None):
		self.step(self.grid, self.pool)
		self._spawn_items()

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

	def _spawn_items(self):
		"""Spawns items until they meet the minimum requirements"""
		item_counts = Counter(type(item) for item in self.grid)

		for i in range(self.min_num_critters - item_counts[Critter]):
			self.add_item(self.grid.random_free_cell, Critter())
		for i in range(self.min_num_food - item_counts[Food]):
			self.add_item(self.grid.random_free_cell, Food())

	def add_item(self, pos: Position,
				 item: GridItem) -> Optional[GridItem]:
		successful = self.grid.add_item(pos=pos, grid_item=item)
		if successful:
			self.add_child(item.instance)
			return item
		else:
			item.instance.queue_free()
			return None

	@staticmethod
	def step(grid: Grid, pool: ThreadPool):
		"""Perform the logic for all items, using threading for get_move"""
		all_items = list(grid)

		# Get turns here, using a locked grid
		with grid as locked_grid:
			turns = pool.map(lambda gi: gi.get_turn(locked_grid), all_items)

		# Run the moves on the grid
		for grid_item, turn in zip(all_items, turns):
			if turn:
				if turn.is_action:
					grid.apply_action(turn.direction, grid_item)
				else:
					grid.move_item_relative(turn.direction, grid_item)

		# Delete any depleted objects
		for grid_item in all_items:
			if grid_item.delete_queued:
				grid.delete_item(grid_item)

	def close(self):
		self.pool.terminate()
