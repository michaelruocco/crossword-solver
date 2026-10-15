from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.intersection import Intersection
from crossword_solver_domain_entities.word import Word

ACROSS_1 = Word(Id.across(1), 3, Coordinates(0, 2))
DOWN_2 = Word(Id.down(2), 3, Coordinates(2, 2))
OTHER = Word(Id.across(9), 3, Coordinates(0, 0))

# Crosses at the end of the across word and the start of the down word.
INTERSECTION = Intersection.of(ACROSS_1, DOWN_2, Coordinates(2, 2))


def test_of_works_out_each_words_index_from_the_crossing_coordinates():
    assert INTERSECTION.across_index == 2
    assert INTERSECTION.down_index == 0


def test_to_index_returns_index_in_the_word_of_that_direction():
    assert INTERSECTION.to_index(Direction.ACROSS) == 2
    assert INTERSECTION.to_index(Direction.DOWN) == 0


def test_to_intersecting_index_returns_index_in_the_word_of_the_other_direction():
    assert INTERSECTION.to_intersecting_index(Direction.ACROSS) == 0
    assert INTERSECTION.to_intersecting_index(Direction.DOWN) == 2


def test_to_intersecting_id_returns_id_of_the_other_word():
    assert INTERSECTION.to_intersecting_id(Id.across(1)) == Id.down(2)
    assert INTERSECTION.to_intersecting_id(Id.down(2)) == Id.across(1)


def test_to_intersecting_id_for_direction_returns_id_of_word_in_the_other_direction():
    assert INTERSECTION.to_intersecting_id_for_direction(Direction.ACROSS) == Id.down(2)
    assert INTERSECTION.to_intersecting_id_for_direction(Direction.DOWN) == Id.across(1)


def test_get_other_word_returns_the_word_that_is_not_given():
    assert INTERSECTION.get_other_word(ACROSS_1) == DOWN_2
    assert INTERSECTION.get_other_word(DOWN_2) == ACROSS_1


def test_contains_word():
    assert INTERSECTION.contains(ACROSS_1)
    assert INTERSECTION.contains(DOWN_2)
    assert not INTERSECTION.contains(OTHER)


def test_contains_id():
    assert INTERSECTION.contains_id(Id.across(1))
    assert INTERSECTION.contains_id(Id.down(2))
    assert not INTERSECTION.contains_id(Id.across(9))


def test_equal_intersections_are_deduplicated_in_a_set():
    same = Intersection.of(ACROSS_1, DOWN_2, Coordinates(2, 2))

    assert same == INTERSECTION
    assert len({INTERSECTION, same}) == 1
