import numpy as np


class Position(np.ndarray):

	def __new__(subtype, x, y):
		obj = super(Position, subtype).__new__(
			subtype, shape=(2,), dtype=np.int)
		obj[0] = x
		obj[1] = y
		return obj

	@property
	def x(self):
		return self[0]

	@property
	def y(self):
		return self[1]

	def __repr__(self):
		return f"Position(x={self.x}, y={self.y})"

	def __eq__(self, other):
		return super().__eq__(other).all()
