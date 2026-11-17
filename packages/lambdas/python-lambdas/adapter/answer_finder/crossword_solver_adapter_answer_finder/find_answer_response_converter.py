import logging
import re
from collections.abc import Collection

from crossword_solver_domain_entities.answer import Answer
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.id import Id

logger = logging.getLogger(__name__)
_ANSWER_ID_PATTERN = re.compile(r"([1-9]\d*)([AD])")


class FindAnswerResponseConverter:
    def to_answer(self, answer_and_score: str) -> Answer:
        logger.debug("Converting answer and score: %s", answer_and_score)
        return self._convert(answer_and_score)

    def to_candidates(self, answers_and_scores: str) -> Collection[Answer]:
        logger.debug("Converting candidate answers and scores")
        answers = [self.to_answer(line) for line in answers_and_scores.splitlines() if line and line.count("|") == 2]
        return self._remove_duplicates(answers)

    def _convert(self, line: str) -> Answer:
        last_line = line.splitlines()[-1] if line.splitlines() else line
        parts = last_line.split("|")
        answer_id_text = parts[0].strip()
        match = _ANSWER_ID_PATTERN.fullmatch(answer_id_text)
        if match is None:
            raise ValueError(f"Invalid answer id: {answer_id_text}")

        answer_id = Id(number=int(match.group(1)), direction=Direction(match.group(2)))
        answer_value = "".join(parts[1].split()).upper()
        try:
            confidence_score = int(parts[2].strip())
        except ValueError as error:
            logger.debug("Invalid answer confidence score %r: %s", parts[2], error)
            return Answer.no_match(answer_id)

        return Answer(id=answer_id, value=answer_value, confidence_score=confidence_score)

    @staticmethod
    def _remove_duplicates(answers: Collection[Answer]) -> list[Answer]:
        by_value: dict[str, Answer] = {}
        for answer in answers:
            existing = by_value.get(answer.value)
            if existing is None or existing.confidence_score <= answer.confidence_score:
                by_value[answer.value] = answer
        return sorted(by_value.values(), key=lambda answer: answer.confidence_score, reverse=True)
