# crossword_solver.puzzle_import_worker

Processes queued puzzle imports using the puzzle domain and extraction adapters.

The worker configures separate Bedrock model IDs for clue extraction
(`CLUE_EXTRACTOR_MODEL_ID`) and clue-type classification (`CLUE_TYPE_POLICY_MODEL_ID`).
