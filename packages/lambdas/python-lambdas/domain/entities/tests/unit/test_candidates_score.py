import pytest

from crossword_solver_domain_entities.candidates_score import CandidatesScore


def test_calculates_candidate_confidence_and_evidence_scores():
    score = CandidatesScore(
        best_score=90,
        alternative_scores=[70, 50],
        number_of_candidates=3,
        known_letter_count=1,
        total_letter_count=3,
    )

    assert score.average_alternative_score() == 60
    assert score.confidence_distribution_score() == pytest.approx(0.3)
    assert score.count_score() == pytest.approx(1 / 3**0.5)
    assert score.pattern_specificity_score() == pytest.approx(1 / 3)
    assert score.best_confidence_score() == pytest.approx(0.9)
    assert score.evidence_score() == pytest.approx(0.4 * 0.3 + 0.3 / 3**0.5 + 0.3 / 3)
    assert score.overall_score() == pytest.approx(score.best_confidence_score() * score.evidence_score())


def test_zero_denominators_produce_zero_score_components():
    score = CandidatesScore(
        best_score=0,
        alternative_scores=[],
        number_of_candidates=0,
        known_letter_count=0,
        total_letter_count=0,
    )

    assert score.average_alternative_score() == 0
    assert score.count_score() == 0
    assert score.pattern_specificity_score() == 0
    assert score.overall_score() == 0


def test_as_string_reports_inputs_and_computed_scores():
    value = CandidatesScore(80, [60, 40], 3, 1, 4).as_string()

    assert "best_score 80" in value
    assert "alternative_scores 60, 40" in value
    assert "average_alternative_score 50.00000" in value
    assert "overall_score " in value
