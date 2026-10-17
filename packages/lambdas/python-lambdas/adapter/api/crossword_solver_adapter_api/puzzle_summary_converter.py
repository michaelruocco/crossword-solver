from crossword_solver_domain_entities.puzzle_summary import PuzzleSummary
from crossword_solver_domain_use_case.puzzle_summary_page import PuzzleSummaryPage

from .puzzle_summary_response import PuzzleSummaryPageResponse, PuzzleSummaryResponse


class PuzzleSummaryConverter:
    def to_response(self, summary: PuzzleSummary) -> PuzzleSummaryResponse:
        return PuzzleSummaryResponse(
            id=summary.id,
            name=summary.name,
            createdAt=summary.created_at,
            clueCount=summary.clue_count,
        )

    def to_page_response(self, page: PuzzleSummaryPage) -> PuzzleSummaryPageResponse:
        return PuzzleSummaryPageResponse(
            summaries=[self.to_response(summary) for summary in page.summaries],
            nextCursor=page.next_cursor,
        )
