import numpy as np

from crawlai.grid import Grid
from crawlai.position import Position
from crawlai.math_utils import clamp

_INPUT_RADIUS = 30
INPUT_SHAPE = (_INPUT_RADIUS * 2 + 1,
			   _INPUT_RADIUS * 2 + 1)
INPUT_DTYPE = np.int_


def get_instance_grid(
		grid: Grid,
		pos: Position,
		radius=_INPUT_RADIUS) -> np.ndarray:
	"""Get a numpy array of obj IDs surrounding a particular area.
	This function will always return an array of shape (radius, radius),
	where the value is the object ID. """

	x1, y1 = pos.x - radius, pos.y - radius
	x2, y2 = pos.x + radius + 1, pos.y + radius + 1

	crop = grid.array[
		   clamp(x1, 0, grid.width):clamp(x2, 0, grid.width),
		   clamp(y1, 0, grid.height):clamp(y2, 0, grid.height)]
	w, h = crop.shape
	if x1 < 0:
		concat = np.full((abs(x1), h),
						 fill_value=-1, dtype=INPUT_DTYPE)
		crop = np.vstack((concat, crop))
	if x2 > grid.width:
		concat = np.full((x2 - grid.width, h),
						 fill_value=-1, dtype=INPUT_DTYPE)
		crop = np.vstack((crop, concat))

	w, h = crop.shape
	if y1 < 0:
		concat = np.full((w, abs(y1)),
						 fill_value=-1, dtype=INPUT_DTYPE)
		crop = np.hstack((concat, crop))
	if y2 > grid.height:
		concat = np.full((w, y2 - grid.height),
						 fill_value=-1, dtype=INPUT_DTYPE)
		crop = np.hstack((crop, concat))
	return crop
