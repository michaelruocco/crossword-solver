from unittest.mock import Mock

import pytest
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id

from crossword_solver_adapter_clue_extractor.bedrock_clue_type_policy import BedrockClueTypePolicy
from crossword_solver_adapter_clue_extractor.determine_puzzle_type_prompt_text_factory import (
    DeterminePuzzleTypePromptTextFactory,
)


@pytest.mark.parametrize("response_text", ["STANDARD", "CRYPTIC", "MATH"])
def test_determines_clue_type_with_bedrock_converse(response_text):
    client = Mock()
    client.converse.return_value = {"output": {"message": {"content": [{"text": f" {response_text}\n"}]}}}
    clues = Clues([Clue(Id.across(1), "Feline (3)", [3])])
    prompt_factory = Mock()
    prompt_factory.to_prompt_text.return_value = "classify these clues"
    policy = BedrockClueTypePolicy(
        client=client,
        model_id="test-model",
        prompt_text_factory=prompt_factory,
    )

    result = policy.determine_clue_type(clues)

    assert result is ClueType(response_text)
    prompt_factory.to_prompt_text.assert_called_once_with(clues)
    client.converse.assert_called_once_with(
        modelId="test-model",
        messages=[{"role": "user", "content": [{"text": "classify these clues"}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 2048},
    )


def test_rejects_an_unrecognized_clue_type_response():
    client = Mock()
    client.converse.return_value = {"output": {"message": {"content": [{"text": "MIXED"}]}}}
    policy = BedrockClueTypePolicy(client=client)

    with pytest.raises(ValueError, match="MIXED"):
        policy.determine_clue_type(Clues([]))


def test_prompt_factory_includes_all_clue_ids_and_text():
    clues = Clues(
        [
            Clue(Id.across(1), "Feline (3)", [3]),
            Clue(Id.down(2), "Cryptic clue (4)", [4]),
        ]
    )

    prompt = DeterminePuzzleTypePromptTextFactory().to_prompt_text(clues)

    assert "1A|Feline (3)" in prompt
    assert "2D|Cryptic clue (4)" in prompt
    assert "STANDARD" in prompt
    assert "CRYPTIC" in prompt
    assert "MATH" in prompt
    assert "arithmetic, equations, sequences, or calculations" in prompt
