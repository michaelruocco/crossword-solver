import logging
from concurrent.futures import Executor, Future
from time import monotonic

from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.id import Id

from .candidate_loader import CandidateLoader

logger = logging.getLogger(__name__)

DEFAULT_CANDIDATES_PER_CLUE = 5
DEFAULT_CANDIDATE_TIMEOUT_SECONDS = 30


class CandidateBatchLoader:
    def __init__(
        self,
        candidate_loader: CandidateLoader,
        executor: Executor,
        timeout_seconds: float = DEFAULT_CANDIDATE_TIMEOUT_SECONDS,
    ):
        self.candidate_loader = candidate_loader
        self.executor = executor
        self.timeout_seconds = timeout_seconds

    def load_candidates(
        self,
        clues: Clues,
        candidates_per_clue: int = DEFAULT_CANDIDATES_PER_CLUE,
    ) -> dict[Id, Candidates]:
        futures: list[tuple[Clue, Future[Candidates], float]] = []
        for clue in clues:
            started_at = monotonic()
            future = self.executor.submit(self.candidate_loader.load_candidates, clue, candidates_per_clue)
            futures.append((clue, future, started_at))
        return {clue.id: self._get_candidates(clue, future, started_at) for clue, future, started_at in futures}

    def _get_candidates(self, clue: Clue, future: Future[Candidates], started_at: float) -> Candidates:
        try:
            timeout = max(0, self.timeout_seconds - (monotonic() - started_at))
            return future.result(timeout=timeout)
        except Exception as error:
            future.cancel()
            logger.warning("candidate lookup failed for clue %s", clue.id, exc_info=error)
            return Candidates(clue)
