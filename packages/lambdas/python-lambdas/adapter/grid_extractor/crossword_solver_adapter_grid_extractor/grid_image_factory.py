import cv2
import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_use_case.grid_image_factory import GridImageFactory as GridImageFactoryPort


class GridImageFactory(GridImageFactoryPort):
    CELL_SIZE = 64
    BORDER_SIZE = 1
    FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX

    def to_png(self, grid: Grid) -> bytes:
        cells = {cell.coordinates: cell for cell in grid.cells}
        rows = [self._to_row(grid, cells, y) for y in range(grid.number_of_rows - 1, -1, -1)]
        image = np.vstack(rows)
        encoded, data = cv2.imencode(".png", image)
        if not encoded:
            raise ValueError("Failed to encode puzzle image")
        return data.tobytes()

    def _to_row(self, grid: Grid, cells: dict[Coordinates, Cell], y: int) -> np.ndarray:
        return np.hstack([self._to_cell(grid, cells, x, y) for x in range(grid.number_of_columns)])

    def _to_cell(self, grid: Grid, cells: dict[Coordinates, Cell], x: int, y: int) -> np.ndarray:
        coordinates = Coordinates(x, y)
        cell = cells.get(coordinates)
        if cell is None:
            raise ValueError(f"Grid is missing cell at ({x}, {y})")

        width = self.CELL_SIZE
        height = self.CELL_SIZE
        value = 0 if cell.black else 255
        image = np.pad(
            np.full((height, width), value, dtype=np.uint8),
            self.BORDER_SIZE,
            mode="constant",
            constant_values=0,
        )
        if cell.black:
            return image

        if cell.id is not None:
            self._draw_text(image, str(cell.id), (5, 4, width - 8, 14), scale=0.45, thickness=1)
        if cell.letter is not None:
            self._draw_text(image, cell.letter, (5, 23, width - 8, height - 28), scale=1.0, thickness=2, centred=True)
        return image

    def _draw_text(
        self,
        image: np.ndarray,
        text: str,
        bounds: tuple[int, int, int, int],
        scale: float,
        thickness: int,
        centred: bool = False,
    ) -> None:
        x, y, width, height = bounds
        while True:
            (text_width, text_height), baseline = cv2.getTextSize(text, self.FONT_FACE, scale, thickness)
            if text_width <= width and text_height + baseline <= height:
                break
            scale *= 0.9
            if scale < 0.01:
                raise ValueError(f"Text does not fit in grid cell: {text!r}")
        if centred:
            x += (width - text_width) // 2
            y += (height - text_height - baseline) // 2
        cv2.putText(image, text, (x, y + text_height), self.FONT_FACE, scale, 0, thickness, cv2.LINE_AA)
