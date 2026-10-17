from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary

from .puzzle_summary_response import PuzzleSummaryResponse


class PuzzleSummaryConverter:
    def to_response(self, summary: PuzzleSummary) -> PuzzleSummaryResponse:
        return PuzzleSummaryResponse(
            id=summary.id,
            name=summary.name,
            createdAt=summary.created_at,
            clueCount=summary.clue_count,
        )
