import pytest

from crossword_solver_domain_use_case.clue_extractor_error import ClueExtractorError
from crossword_solver_domain_use_case.image_error import ImageError


@pytest.mark.parametrize("error_type", [ClueExtractorError, ImageError])
def test_error_preserves_message_and_cause(error_type):
    cause = ValueError("cause")

    with pytest.raises(error_type, match="message") as error:
        raise error_type("message") from cause

    assert error.value.__cause__ is cause
