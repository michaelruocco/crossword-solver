from unittest.mock import Mock

from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id

from crossword_solver_domain_use_case.clues_factory import CluesFactory


def test_extracts_clues_determines_type_and_returns_typed_clues():
    image = Mock()
    clues = Clues([Clue(Id.across(1), "Feline (3)", [3])])
    clue_extractor = Mock()
    clue_extractor.extract_clues.return_value = clues
    clue_type_policy = Mock()
    clue_type_policy.determine_clue_type.return_value = ClueType.CRYPTIC
    factory = CluesFactory(clue_extractor, clue_type_policy)

    result = factory.build(image)

    clue_extractor.extract_clues.assert_called_once_with(image)
    clue_type_policy.determine_clue_type.assert_called_once_with(clues)
    assert result is not clues
    assert [clue.type for clue in result] == [ClueType.CRYPTIC]
