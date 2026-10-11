import numpy as np

from .mat_converter import MatConverter


class GridFinder:
    CROP_EXPAND_PIXELS = 10

    def __init__(self, converter: MatConverter | None = None):
        self.converter = converter or MatConverter()

    def find_grid(self, image: np.ndarray) -> np.ndarray:
        warped = self.converter.warp_grid(image)
        return self.converter.crop(warped, self.CROP_EXPAND_PIXELS)
