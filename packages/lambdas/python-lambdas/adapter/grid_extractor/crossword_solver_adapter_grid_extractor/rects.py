from collections.abc import Sequence


def contains(outer: Sequence[int], inner: Sequence[int]) -> bool:
    outer_x, outer_y, outer_width, outer_height = outer
    x, y, width, height = inner
    return x >= outer_x and y >= outer_y and x + width <= outer_x + outer_width and y + height <= outer_y + outer_height
