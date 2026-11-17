from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.id import Id

from crossword_solver_adapter_answer_finder.default_find_answer_prompt_text_factory import (
    DefaultFindAnswerPromptTextFactory,
)
from crossword_solver_adapter_answer_finder.delegating_find_answer_prompt_text_factory import (
    DelegatingFindAnswerPromptTextFactory,
)


def test_populates_prompt_template():
    clue = Clue(Id.down(12), "Old vessel", [3], pattern="B??")
    factory = DefaultFindAnswerPromptTextFactory(
        "id=%CLUE_ID%; clue=%CLUE%; pattern=%PATTERN%; count=%NUMBER_OF_CANDIDATES%"
    )

    prompt = factory.to_prompt_text(clue, 5)

    assert prompt == "id=12D; clue=Old vessel; pattern=B??; count=5"


def test_default_prompt_factory_loads_standard_and_cryptic_templates():
    factory = DelegatingFindAnswerPromptTextFactory()
    standard = Clue(Id.across(1), "Feline", [3], type=ClueType.STANDARD)
    cryptic = Clue(Id.down(2), "Insect in engine", [3], type=ClueType.CRYPTIC)

    standard_prompt = factory.to_prompt_text(standard, 3)
    cryptic_prompt = factory.to_prompt_text(cryptic, 2)

    assert "standard (non-cryptic) crossword clues" in standard_prompt
    assert "1A" in standard_prompt
    assert "???" in standard_prompt
    assert "up to 3 plausible answers" in standard_prompt
    assert "cryptic crossword clue" in cryptic_prompt
    assert "wordplay" in cryptic_prompt
    assert "up to 2 plausible answers" in cryptic_prompt
