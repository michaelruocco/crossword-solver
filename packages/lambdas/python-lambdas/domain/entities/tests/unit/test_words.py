import pytest

from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.word_not_found_for_id_error import WordNotFoundForIdError
from crossword_solver_domain_entities.words import Words

# A 3x3 grid with a black centre: across words on the top and bottom rows, down words on the left and right columns.
ACROSS_1 = Word(Id.across(1), 3, Coordinates(0, 2))
DOWN_1 = Word(Id.down(1), 3, Coordinates(0, 2))
DOWN_2 = Word(Id.down(2), 3, Coordinates(2, 2))
ACROSS_3 = Word(Id.across(3), 3, Coordinates(0, 0))


@pytest.fixture
def words() -> Words:
    return Words([ACROSS_1, DOWN_1, DOWN_2, ACROSS_3])


def test_iterates_and_counts_words(words):
    assert list(words) == [ACROSS_1, DOWN_1, DOWN_2, ACROSS_3]
    assert len(words) == 4


def test_find_by_id_returns_word_with_id(words):
    assert words.find_by_id(Id.down(2)) == DOWN_2


def test_find_by_id_raises_error_when_no_word_has_id(words):
    with pytest.raises(WordNotFoundForIdError, match="Word not found for id 9A") as error:
        words.find_by_id(Id.across(9))

    assert error.value.word_id == Id.across(9)


def test_works_out_every_intersection_between_crossing_words(words):
    assert len(words.get_intersections_by_id(Id.across(1))) == 2
    assert len(words.get_intersections_by_id(Id.down(1))) == 2
    assert len(words.get_intersections_by_id(Id.down(2))) == 2
    assert len(words.get_intersections_by_id(Id.across(3))) == 2


def test_get_intersecting_ids_returns_ids_of_crossing_words(words):
    assert words.get_intersecting_ids(Id.across(1)) == [Id.down(1), Id.down(2)]


def test_get_intersecting_ids_raises_error_when_no_word_has_id(words):
    with pytest.raises(WordNotFoundForIdError):
        words.get_intersecting_ids(Id.across(9))


def test_get_intersecting_words_returns_crossing_words(words):
    assert words.get_intersecting_words(DOWN_1) == [ACROSS_1, ACROSS_3]


def test_get_intersections_returns_those_containing_the_word(words):
    intersections = words.get_intersections(DOWN_2)

    assert [intersection.get_other_word(DOWN_2) for intersection in intersections] == [ACROSS_1, ACROSS_3]


def test_get_intersections_by_id_returns_those_containing_the_id(words):
    intersections = words.get_intersections_by_id(Id.down(2))

    assert [intersection.to_intersecting_id(Id.down(2)) for intersection in intersections] == [
        Id.across(1),
        Id.across(3),
    ]


def test_words_in_the_same_direction_do_not_intersect(words):
    assert Id.across(3) not in words.get_intersecting_ids(Id.across(1))


def test_uses_given_intersections_instead_of_working_them_out():
    words = Words([ACROSS_1, DOWN_2], intersections=[])

    assert words.get_intersections(ACROSS_1) == []


def test_equal_when_values_and_intersections_match(words):
    assert words == Words([ACROSS_1, DOWN_1, DOWN_2, ACROSS_3])


def test_not_equal_when_values_differ(words):
    assert words != Words([ACROSS_1, DOWN_1])
    assert words != "not words"


def test_repr_includes_values_and_intersections(words):
    assert repr(words).startswith("Words(values=[Word(")
    assert "intersections=[Intersection(" in repr(words)
