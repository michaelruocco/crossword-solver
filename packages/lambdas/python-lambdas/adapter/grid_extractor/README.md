# crossword_solver.adapter_grid_extractor

Extracts the crossword grid from puzzle images using OpenCV.

Puzzle imports use `CellClassifier` to classify black/white cells and
`GridNumberer` to assign consecutive IDs at across/down answer starts,
top-to-bottom and left-to-right. This avoids OCR of small, faint printed numbers.
It assumes conventional blocked crosswords with answers at least two cells long.
Barred grids, nonstandard numbering, and single-letter entries are not supported
by this strategy; a mistaken black/white classification can affect later IDs.

`DefaultGridExtractor` accepts a `CellClassifier` and an optional `GridNumberer`.
The import worker explicitly selects structural numbering. No OCR engine or trained
language model is required. Without a numberer, the classifier's cells remain unnumbered.

Integration tests compare all cells against fixed JSON fixtures for nine puzzles,
including the web puzzle.
