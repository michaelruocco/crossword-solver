# crossword_solver.adapter_clue_extractor

Extracts crossword clues from puzzle images and classifies their type using Amazon Bedrock.
The use-case `CluesFactory` keeps classification separate from clue extraction and applies
the determined `STANDARD` or `CRYPTIC` type to every extracted clue.
