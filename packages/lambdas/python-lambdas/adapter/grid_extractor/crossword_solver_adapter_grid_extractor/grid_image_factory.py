import cv2
import numpy as np
from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_use_case.grid_image_factory import GridImageFactory as GridImageFactoryPort


class GridImageFactory(GridImageFactoryPort):
    BORDER_SIZE = 7
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

        width = grid.column_width * 4
        height = grid.row_height * 4
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
            self._draw_text(image, str(cell.id), scale=3.0, thickness=15, x=int(image.shape[1] * 0.05), y_offset=0.1)
        if cell.letter is not None:
            text = cell.letter
            text_size = cv2.getTextSize(text, self.FONT_FACE, 7.0, 20)[0]
            x_position = (image.shape[1] - text_size[0]) // 2
            y_position = (image.shape[0] + text_size[1]) // 2
            cv2.putText(image, text, (x_position, y_position), self.FONT_FACE, 7.0, 0, 20)
        return image

    def _draw_text(self, image: np.ndarray, text: str, scale: float, thickness: int, x: int, y_offset: float) -> None:
        text_height = cv2.getTextSize(text, self.FONT_FACE, scale, thickness)[0][1]
        y = int(image.shape[0] * y_offset) + text_height
        cv2.putText(image, text, (x, y), self.FONT_FACE, scale, 0, thickness)
