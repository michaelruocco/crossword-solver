from uuid import uuid4

import pytest
from pydantic import ValidationError

from crossword_solver_adapter_api.puzzle_import_message import PuzzleImportMessage


def test_parses_import_id_from_message_body():
    import_id = uuid4()

    message = PuzzleImportMessage.model_validate({"importId": str(import_id)})

    assert message.import_id == import_id


@pytest.mark.parametrize("body", [{}, {"importId": "not-a-uuid"}], ids=["missing", "invalid"])
def test_rejects_message_without_a_valid_import_id(body):
    with pytest.raises(ValidationError):
        PuzzleImportMessage.model_validate(body)
