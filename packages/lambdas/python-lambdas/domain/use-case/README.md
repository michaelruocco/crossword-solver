# crossword_solver.domain_use_case

Domain use cases for the crossword solver python lambdas.

`CandidateLoader` loads candidates for one clue from the repository or answer
finder. `CandidateBatchLoader` loads multiple clues concurrently using an
injected executor, with a 30-second per-clue timeout and empty candidates for
individual lookup failures.
