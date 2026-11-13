from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.grid import Grid


class ClueLengthPopulationPolicy:
    def populate(self, clues: Clues, grid: Grid) -> Clues:
        return Clues([self._populate_clue(clue, grid) for clue in clues])

    @staticmethod
    def _populate_clue(clue: Clue, grid: Grid) -> Clue:
        if clue.lengths:
            return clue

        length = grid.count_contiguous_cells(clue.id)
        return Clue(id=clue.id, text=clue.text, lengths=[length], type=clue.type)
