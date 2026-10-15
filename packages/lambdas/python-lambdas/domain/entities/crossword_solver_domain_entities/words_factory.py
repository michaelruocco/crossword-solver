from .cells import Cells
from .clue import Clue
from .clues import Clues
from .word import Word
from .words import Words


class WordsFactory:
    def to_words(self, clues: Clues, cells: Cells) -> Words:
        words = [self._to_word(clue, cells) for clue in clues]
        return Words(sorted(words, key=lambda word: word.numeric_id))

    @staticmethod
    def _to_word(clue: Clue, cells: Cells) -> Word:
        return Word(
            id=clue.id,
            length=clue.total_length,
            coordinates=cells.force_find_coordinates_by_id(clue.numeric_id),
        )
