from typing import NamedTuple


class Position(NamedTuple):
	x: int
	y: int

	def __repr__(self):
		return f"Position(x={self.x}, y={self.y})"

	def __iter__(self):
		yield self.x
		yield self.y

	def __eq__(self, other: 'Position'):
		return self.x == other.x and self.y == other.y

	def __add__(self, other: 'Position'):
		return Position(self.x + other.x, self.y + other.y)

	def __mul__(self, other: int):
		return Position(self.x * other, self.y * other)
