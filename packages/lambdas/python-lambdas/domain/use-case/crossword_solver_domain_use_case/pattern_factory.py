from crossword_solver_domain_entities.attempt import Attempt
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues


class PatternFactory:
    def add_patterns_to_clues(self, clues: Clues, attempt: Attempt) -> Clues:
        return Clues([self.add_pattern_to_clue(clue, attempt) for clue in clues])

    def add_pattern_to_clue(self, clue: Clue, attempt: Attempt) -> Clue:
        return clue.with_pattern(self.build(clue, attempt))

    def build(self, clue: Clue, attempt: Attempt) -> str:
        pattern = [Clue.UNKNOWN] * clue.total_length
        for intersection in attempt.puzzle.intersections(clue.id):
            intersecting_answer = attempt.answers.find(intersection.to_intersecting_id(clue.id))
            if intersecting_answer is None:
                continue

            index = intersection.to_intersecting_index(clue.direction)
            letter = intersecting_answer.normalized_value[index : index + 1]
            if letter:
                pattern[intersection.to_index(clue.direction)] = letter

        return "".join(pattern)
