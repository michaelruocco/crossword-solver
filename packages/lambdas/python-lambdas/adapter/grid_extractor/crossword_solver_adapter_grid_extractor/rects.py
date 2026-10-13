from collections.abc import Sequence

import cv2
import numpy as np


def contains(outer: Sequence[int], inner: Sequence[int]) -> bool:
    outer_x, outer_y, outer_width, outer_height = outer
    x, y, width, height = inner
    return x >= outer_x and y >= outer_y and x + width <= outer_x + outer_width and y + height <= outer_y + outer_height


def keep_outermost(contours: Sequence[np.ndarray]) -> list[np.ndarray]:
    boxes = [tuple(cv2.boundingRect(contour)) for contour in contours]
    return [
        contour
        for i, contour in enumerate(contours)
        if not any(_encloses(boxes, j, i) for j in range(len(boxes)) if j != i)
    ]


def _encloses(boxes: list[tuple[int, ...]], outer: int, inner: int) -> bool:
    # Of contours with identical boxes only the first is kept, so they don't remove each other.
    if boxes[outer] == boxes[inner]:
        return outer < inner
    return contains(boxes[outer], boxes[inner])
