from dataclasses import dataclass

from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary


@dataclass(frozen=True)
class PuzzleSummaryPage:
    summaries: list[PuzzleSummary]
    next_cursor: str | None
