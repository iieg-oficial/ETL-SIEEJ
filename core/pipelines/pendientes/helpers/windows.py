from __future__ import annotations

from rasterio.windows import Window


def core_tile_windows(shape: tuple[int, int], tile_size: int) -> list[Window]:
    if tile_size <= 0:
        raise ValueError("Tile size must be positive")
    height, width = shape
    return [
        Window(column, row, min(tile_size, width - column), min(tile_size, height - row))
        for row in range(0, height, tile_size)
        for column in range(0, width, tile_size)
    ]
