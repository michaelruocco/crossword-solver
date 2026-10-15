from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.intersection import Intersection
from crossword_solver_domain_entities.word import Word

ACROSS_1 = Word(Id.across(1), 3, Coordinates(0, 2))
DOWN_2 = Word(Id.down(2), 3, Coordinates(2, 2))


def test_properties_come_from_id_and_coordinates():
    word = Word(Id.down(7), 4, Coordinates(3, 5))

    assert word.numeric_id == 7
    assert word.direction == Direction.DOWN
    assert word.x == 3
    assert word.y == 5


def test_has_id():
    assert ACROSS_1.has_id(Id.across(1))
    assert not ACROSS_1.has_id(Id.down(1))


def test_has_same_id():
    assert ACROSS_1.has_same_id(Word(Id.across(1), 9, Coordinates(5, 5)))
    assert not ACROSS_1.has_same_id(DOWN_2)


def test_finds_intersection_between_across_and_down_word():
    intersection = ACROSS_1.find_intersection_between(DOWN_2)

    assert intersection == Intersection.of(ACROSS_1, DOWN_2, Coordinates(2, 2))
    assert intersection is not None
    assert intersection.across.word == ACROSS_1
    assert intersection.down.word == DOWN_2
    assert intersection.across_index == 2
    assert intersection.down_index == 0


def test_finds_same_intersection_regardless_of_which_word_is_asked():
    assert ACROSS_1.find_intersection_between(DOWN_2) == DOWN_2.find_intersection_between(ACROSS_1)


def test_down_word_index_counts_downwards_from_its_start():
    across_3 = Word(Id.across(3), 3, Coordinates(0, 0))

    intersection = DOWN_2.find_intersection_between(across_3)

    assert intersection is not None
    assert intersection.across_index == 2
    assert intersection.down_index == 2


def test_no_intersection_between_words_in_the_same_direction():
    assert ACROSS_1.find_intersection_between(Word(Id.across(3), 3, Coordinates(0, 0))) is None


def test_no_intersection_between_words_that_do_not_cross():
    short_across = Word(Id.across(4), 2, Coordinates(0, 1))

    assert short_across.find_intersection_between(DOWN_2) is None
