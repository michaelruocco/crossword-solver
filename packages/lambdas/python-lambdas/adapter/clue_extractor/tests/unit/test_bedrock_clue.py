import pytest
from crossword_solver_domain_entities.id import Id

from crossword_solver_adapter_clue_extractor.bedrock_clue import BedrockClue


@pytest.mark.parametrize(
    ("direction", "expected_id"),
    [
        ("ACROSS", Id.across(1)),
        ("DOWN", Id.down(1)),
        ("across", Id.across(1)),
        ("A", Id.across(1)),
        ("D", Id.down(1)),
    ],
)
def test_to_clue_parses_direction(direction, expected_id):
    bedrock_clue = BedrockClue.model_validate(
        {"id": 1, "text": "Pacific republic (4)", "direction": direction, "lengths": [4]}
    )

    assert bedrock_clue.to_clue().id == expected_id


def test_rejects_unknown_direction():
    with pytest.raises(ValueError):
        BedrockClue.model_validate({"id": 1, "text": "text", "direction": "SIDEWAYS", "lengths": [4]})
