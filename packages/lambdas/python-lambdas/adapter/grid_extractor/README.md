# crossword_solver.adapter_grid_extractor

Extracts the crossword grid from puzzle images using OpenCV.

Grid PNGs use 64x64-pixel cell interiors with a one-pixel border on each side,
independent of the source image's cell dimensions. IDs occupy a small upper-left
label region, with answer letters centred in a separate region below. Text is
shrunk to fit its region when needed. Stored source dimensions are unchanged.

Puzzle imports use `CellClassifier` to classify black/white cells and
`GridNumberer` to assign consecutive IDs at across/down answer starts,
top-to-bottom and left-to-right. This avoids OCR of small, faint printed numbers.
It assumes conventional blocked crosswords with answers at least two cells long.
Barred grids, nonstandard numbering, and single-letter entries are not supported
by this strategy; a mistaken black/white classification can affect later IDs.

`DefaultGridExtractor` accepts a `CellClassifier` and an optional `GridNumberer`.
The import worker explicitly selects structural numbering. No OCR engine or trained
language model is required. Without a numberer, the classifier's cells remain unnumbered.

Integration tests compare all cells against fixed JSON fixtures for eleven puzzles,
including the Web, Math, and Zen puzzles.

Grid location searches nested dark contours for multiple enclosed cells, so a
worksheet's page frame does not hide its crossword. If no such candidate exists,
the largest external outline is used, preserving support for undivided outlines.
Grid-location snapshots also cover the Math and Zen images. Dimension detection
enlarges grids whose shorter side is below 800 pixels for thresholding, denoising,
and line extraction, then maps boundaries and intersections back to the original
image coordinates. Larger images and the extracted grid images are unchanged.
Detected boundaries must span at least half of each axis of the cropped grid,
so isolated noise cannot be treated as a small grid elsewhere in the image.

Intersections are assigned to their nearest detected row and column within half
the local line spacing. Extra candidates are ranked using the median offset between
line bounding-box origins and unambiguous intersection centroids. Missing matches
and equally plausible candidates raise explicit errors instead of shifting later
cell crops. Math and Zen also have boundary-count regressions at multiple resolutions.
