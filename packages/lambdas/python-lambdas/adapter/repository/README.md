# crossword_solver.adapter_repository

Persists crossword puzzles, attempts, and answer candidates to Amazon DynamoDB.
Candidate records are keyed by the SHA-256 hash of clue text and pattern.
