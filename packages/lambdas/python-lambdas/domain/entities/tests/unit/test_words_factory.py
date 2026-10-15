import pytest

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cell_not_found_for_id_error import CellNotFoundForIdError
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.words_factory import WordsFactory

CELLS = Cells(
    [
        Cell(Coordinates(0, 2), black=False, id=1),
        Cell(Coordinates(1, 2), black=False),
        Cell(Coordinates(2, 2), black=False, id=2),
        Cell(Coordinates(1, 1), black=True),
        Cell(Coordinates(0, 0), black=False, id=3),
    ]
)


def test_creates_a_word_per_clue_sorted_by_numeric_id():
    clues = Clues(
        [
            Clue(Id.down(2), "second down (3)", [3]),
            Clue(Id.across(3), "third across (3)", [3]),
            Clue(Id.across(1), "first across (3)", [3]),
            Clue(Id.down(1), "first down (1,2)", [1, 2]),
        ]
    )

    words = WordsFactory().to_words(clues, CELLS)

    assert list(words) == [
        Word(Id.across(1), 3, Coordinates(0, 2)),
        Word(Id.down(1), 3, Coordinates(0, 2)),
        Word(Id.down(2), 3, Coordinates(2, 2)),
        Word(Id.across(3), 3, Coordinates(0, 0)),
    ]


def test_word_length_is_the_total_of_the_clue_lengths():
    clues = Clues([Clue(Id.across(1), "split clue (2,1)", [2, 1])])

    assert [word.length for word in WordsFactory().to_words(clues, CELLS)] == [3]


def test_words_know_which_other_words_they_intersect():
    clues = Clues([Clue(Id.across(1), "across (3)", [3]), Clue(Id.down(2), "down (3)", [3])])

    words = WordsFactory().to_words(clues, CELLS)

    assert words.get_intersecting_ids(Id.across(1)) == [Id.down(2)]


def test_creates_no_words_for_no_clues():
    assert len(WordsFactory().to_words(Clues([]), CELLS)) == 0


def test_raises_error_when_no_cell_has_the_clue_number():
    clues = Clues([Clue(Id.across(9), "missing cell (3)", [3])])
    factory = WordsFactory()

    with pytest.raises(CellNotFoundForIdError, match="Cell not found for id 9"):
        factory.to_words(clues, CELLS)
