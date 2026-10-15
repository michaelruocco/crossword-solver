from uuid import UUID

import pytest

from crossword_solver_domain_use_case.clue_extractor_error import ClueExtractorError
from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_domain_use_case.puzzle_import_not_found_error import PuzzleImportNotFoundError


@pytest.mark.parametrize("error_type", [ClueExtractorError, ImageError])
def test_error_preserves_message_and_cause(error_type):
    cause = ValueError("cause")

    with pytest.raises(error_type, match="message") as error:
        raise error_type("message") from cause

    assert error.value.__cause__ is cause


def test_puzzle_import_not_found_error_removes_line_breaks_from_message_but_keeps_id():
    class IdWithLineBreak(UUID):
        def __str__(self) -> str:
            return "id\nFAKE LOG ENTRY\r"

    import_id = IdWithLineBreak(int=1)

    error = PuzzleImportNotFoundError(import_id)

    assert str(error) == "Puzzle import not found with id idFAKE LOG ENTRY"
    assert error.import_id is import_id
