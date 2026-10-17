from crossword_solver_domain_use_case.puzzle_summary_lister import PuzzleSummaryLister
from pydantic import BaseModel, Field


class PuzzleSummaryQuery(BaseModel):
    limit: int = Field(default=PuzzleSummaryLister.DEFAULT_PAGE_SIZE, ge=1, le=PuzzleSummaryLister.MAX_PAGE_SIZE)
    cursor: str | None = None
