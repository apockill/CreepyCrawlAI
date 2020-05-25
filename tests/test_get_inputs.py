import pytest

import numpy as np

from crawlai.model import extract_inputs
from crawlai.grid import Grid
from crawlai.items.critter.critter import Critter
from crawlai.position import Position

test_get_grid_around_parameters = [
	# # Basic checks at each corner-1 to check grid works normally without padding
	((1, 1), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((2, 3), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((2, 1), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
	((1, 3), 1, np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),

	# Check actual corners to see the grid applies padding correctl
	((0, 0), 1, np.asarray([[-1, -1, -1], [-1, 1, 0], [-1, 0, 0]])),
	((3, 4), 1, np.asarray([[0, 0, -1], [0, 1, -1], [-1, -1, -1]])),
	((0, 4), 1, np.asarray([[-1, -1, -1], [0, 1, -1], [0, 0, -1]])),
	((3, 0), 1, np.asarray([[-1, 0, 0], [-1, 1, 0], [-1, -1, -1]])),

	# Check the middles of each grid edge
	((0, 2), 1, np.asarray([[-1, -1, -1], [0, 1, 0], [0, 0, 0]])),
	((3, 2), 1, np.asarray([[0, 0, 0], [0, 1, 0], [-1, -1, -1]])),
	((1, 4), 1, np.asarray([[0, 0, -1], [0, 1, -1], [0, 0, -1]])),
	((1, 0), 1, np.asarray([[-1, 0, 0], [-1, 1, 0], [-1, 0, 0]])),

	# Check a radius of two near the center
	((1, 2), 2, np.asarray([[-1, -1, -1, -1, -1],
							[0, 0, 0, 0, 0],
							[0, 0, 1, 0, 0],
							[0, 0, 0, 0, 0],
							[0, 0, 0, 0, 0]])),

	# Check a large, off-center radius
	((1, 1), 4, np.asarray([[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, 0, 1, 0, 0, 0, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, 0, 0, 0, 0, 0, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1],
							[-1, -1, -1, -1, -1, -1, -1, -1, -1]]))
]


@pytest.mark.parametrize(
	argnames=('pos', 'radius', 'output_grid'),
	argvalues=test_get_grid_around_parameters)
def test_get_grid_around(pos, radius, output_grid):
	"""Creates a grid of shape:
	[[0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]
	 [0 0 0 0 0]]

	 and places a critter at position 'pos', then calls get_grid_around with a
	 radius of 'radius', and verifies the output grid is the same as
	 'output_grid'
    """
	grid = Grid(width=4, height=5)
	grid.add_item(pos=Position(*pos), grid_item=Critter())
	grid_around = extract_inputs.get_instance_grid(
		grid=grid,
		pos=Position(*pos),
		radius=radius)

	h, w = grid_around.shape
	assert h == w
	assert (grid_around == output_grid).all()
