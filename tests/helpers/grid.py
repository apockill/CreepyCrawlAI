import numpy as np

from crawlai.grid import Grid


def validate_grid(grid: Grid) -> None:
    """Validate consistency in the grid datastructure"""
    id_to_obj_n_items = len(list(grid.id_to_obj.items()))
    id_to_pos_n_items = len(grid.id_to_pos.items())
    n_grid_nonzeros = np.argwhere(grid.array != 0).shape[0]

    assert id_to_obj_n_items == id_to_pos_n_items
    assert n_grid_nonzeros == id_to_obj_n_items

    for item in grid:
        assert grid.id_to_obj[item.id] == item
        pos = grid.id_to_pos[item.id]
        assert grid.array[pos.x][pos.y] == item.id
