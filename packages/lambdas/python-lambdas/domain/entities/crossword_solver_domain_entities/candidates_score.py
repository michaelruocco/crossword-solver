from collections.abc import Collection
from dataclasses import dataclass


@dataclass(frozen=True)
class CandidatesScore:
    best_score: int
    alternative_scores: Collection[int]
    number_of_candidates: int
    known_letter_count: int
    total_letter_count: int

    def average_alternative_score(self) -> float:
        return sum(self.alternative_scores) / len(self.alternative_scores) if self.alternative_scores else 0

    def confidence_distribution_score(self) -> float:
        return (self.best_score - self.average_alternative_score()) / 100.0

    def count_score(self) -> float:
        return 1.0 / self.number_of_candidates**0.5 if self.number_of_candidates else 0

    def pattern_specificity_score(self) -> float:
        return self.known_letter_count / self.total_letter_count if self.total_letter_count else 0

    def evidence_score(self) -> float:
        return (
            0.4 * self.confidence_distribution_score()
            + 0.3 * self.count_score()
            + 0.3 * self.pattern_specificity_score()
        )

    def best_confidence_score(self) -> float:
        return self.best_score / 100.0

    def overall_score(self) -> float:
        return self.best_confidence_score() * self.evidence_score()

    def as_string(self) -> str:
        return (
            f"best_score {self.best_score}\n"
            f"alternative_scores {', '.join(map(str, self.alternative_scores))}\n"
            f"number_of_candidates {self.number_of_candidates}\n"
            f"known_letter_count {self.known_letter_count}\n"
            f"total_letter_count {self.total_letter_count}\n"
            f"average_alternative_score {self.average_alternative_score():.5f}\n"
            f"confidence_distribution_score {self.confidence_distribution_score():.5f}\n"
            f"count_score {self.count_score():.5f}\n"
            f"pattern_specificity_score {self.pattern_specificity_score():.5f}\n"
            f"best_confidence_score {self.best_confidence_score():.5f}\n"
            f"evidence_score {self.evidence_score():.5f}\n"
            f"overall_score {self.overall_score():.5f}\n"
        )
