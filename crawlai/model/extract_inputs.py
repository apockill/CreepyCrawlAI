from collections.abc import Hashable
from threading import RLock

import numpy as np
import numpy.typing as npt

from crawlai.grid import Grid
from crawlai.position import Position

INPUT_DTYPE = np.int
"""The smallest int type accepted by tensorflow"""

# TODO: Implement caching
_generate_layered_grid_lock = RLock()
"""Because generating the full layered grid is a bit expensive, it's best for
one thread to process this and the rest of them to use the cached result. """
_instance_grid_cache: dict[Hashable, npt.NDArray[np.int8]] = {}
"""Holds a dictionary of a single value, of format
{hash(grid.array.data.tobytes(), ): instance_grid} """


def _generate_layered_grid(
    grid: Grid, layers: dict[str, int], radius: int
) -> npt.NDArray[np.int8]:
    """Converts the grid of shape (x, y) to (x, y, obj_layers)
    The 0th index of the grid always represents boundaries or walls.

    :param grid: The grid
    :param layers: A dictionary of {"GRID_ITEM_TYPE": LayerID}, where layer ID
           must be the index on obj_layer for that item ID to appear on
    :param radius: The radius that critters will have. This will pad the sides
    of the grid with walls on the 0 layer.
    """
    w, h = grid.array.shape
    full_grid = np.zeros(
        (w + radius * 2, h + radius * 2, len(layers) + 1), dtype=INPUT_DTYPE
    )

    for item in grid:
        layer = layers[type(item).__name__]
        pos = grid.id_to_pos[item.id]
        full_grid[pos.x + radius, pos.y + radius, layer] = 1

    # Fill in the "walls" around the radius
    full_grid[0:radius, :, 0] = 1
    full_grid[w + radius :, :, 0] = 1
    full_grid[:, 0:radius, 0] = 1
    full_grid[:, h + radius :, 0] = 1  # TODO: verify why this is different
    return full_grid


def get_instance_grid(
    grid: Grid, pos: Position, radius: int, layers: dict[str, int]
) -> npt.NDArray[np.int8]:
    """Get a numpy array of obj IDs surrounding a particular area.
    This function will always return an array of shape (radius, radius),
    where the value is the object ID.

    Shape: (x, y, object_layers)
               where object_layers is 3:
               0: walls
               1: critters
               2: food
    """
    global _instance_grid_cache
    with _generate_layered_grid_lock:
        key = (hash(grid), tuple(layers.items()), radius)
        if key in _instance_grid_cache:
            layered_grid = _instance_grid_cache[key]
        else:
            layered_grid = _generate_layered_grid(grid, layers, radius)
            _instance_grid_cache.clear()
            _instance_grid_cache[key] = layered_grid

    x1, y1 = pos.x, pos.y
    x2, y2 = pos.x + radius * 2 + 1, pos.y + radius * 2 + 1
    crop = layered_grid[x1:x2, y1:y2, :]
    return crop
