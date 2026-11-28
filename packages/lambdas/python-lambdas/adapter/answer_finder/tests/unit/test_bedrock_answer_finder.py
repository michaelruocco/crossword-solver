from unittest.mock import Mock

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_use_case.answer_finder import AnswerFinder

from crossword_solver_adapter_answer_finder.bedrock_answer_finder import BedrockAnswerFinder
from crossword_solver_adapter_answer_finder.bedrock_conversation_config import DefaultBedrockConversationConfig
from crossword_solver_adapter_answer_finder.prompt_text_executor import PromptTextExecutor


def test_finds_candidates_and_filters_answers_that_do_not_match_clue():
    clue = Clue(Id.across(1), "Feline", [3], pattern="C??")
    prompt_factory = Mock()
    prompt_factory.to_prompt_text.return_value = "find candidates"
    executor = Mock()
    executor.execute.return_value = "1A|CAT|90\n1A|DOG|80\n1A|CATERPILLAR|70"
    finder = BedrockAnswerFinder(
        prompt_text_factory=prompt_factory,
        prompt_text_executor=executor,
    )

    candidates = finder.find_candidates(clue, 3)

    prompt_factory.to_prompt_text.assert_called_once_with(clue, 3)
    executor.execute.assert_called_once_with("find candidates")
    assert candidates.clue is clue
    assert list(candidates) == [Answer(Id.across(1), "CAT", confidence_score=90)]


def test_uses_math_prompt_and_filters_candidates_against_known_digits():
    clue = Clue(Id.across(1), "22 + 22", [2], type=ClueType.MATH, pattern="4?")
    executor = Mock()
    executor.execute.return_value = "1A|44|90\n1A|34|80"
    finder = BedrockAnswerFinder(prompt_text_executor=executor)

    candidates = finder.find_candidates(clue, 2)
    prompt = executor.execute.call_args.args[0]

    assert "digits, not spelled-out number words" in prompt
    assert "Pattern: 4?" in prompt
    assert list(candidates) == [Answer(Id.across(1), "44", confidence_score=90)]


def test_bedrock_finder_satisfies_answer_finder_protocol():
    finder: AnswerFinder = BedrockAnswerFinder(prompt_text_executor=Mock())

    assert isinstance(finder, BedrockAnswerFinder)


def test_builds_prompt_executor_from_client_and_default_configuration():
    client = Mock()

    finder = BedrockAnswerFinder(client=client)

    assert isinstance(finder.prompt_text_executor, PromptTextExecutor)
    assert finder.prompt_text_executor.client is client
    assert isinstance(finder.prompt_text_executor.conversation_config, DefaultBedrockConversationConfig)
    assert finder.prompt_text_executor.model_id == BedrockAnswerFinder.DEFAULT_MODEL_ID


def test_delegates_to_standard_prompt_for_standard_and_unspecified_clue_types():
    standard_factory = Mock()
    cryptic_factory = Mock()
    factories = _prompt_factories(standard_factory, cryptic_factory)
    standard_clue = Clue(Id.across(1), "Feline", [3], type=ClueType.STANDARD)
    unspecified_clue = Clue(Id.across(2), "Canine", [3])

    factories.to_prompt_text(standard_clue, 2)
    factories.to_prompt_text(unspecified_clue, 1)

    assert standard_factory.to_prompt_text.call_count == 2
    cryptic_factory.to_prompt_text.assert_not_called()


def test_delegates_to_cryptic_prompt_for_cryptic_clue():
    standard_factory = Mock()
    cryptic_factory = Mock()
    factories = _prompt_factories(standard_factory, cryptic_factory)
    clue = Clue(Id.down(3), "Insect in engine (3)", [3], type=ClueType.CRYPTIC)

    factories.to_prompt_text(clue, 4)

    cryptic_factory.to_prompt_text.assert_called_once_with(clue, 4)
    standard_factory.to_prompt_text.assert_not_called()


def _prompt_factories(standard_factory, cryptic_factory):
    from crossword_solver_adapter_answer_finder.delegating_find_answer_prompt_text_factory import (
        DelegatingFindAnswerPromptTextFactory,
    )

    return DelegatingFindAnswerPromptTextFactory(standard_factory, cryptic_factory)
