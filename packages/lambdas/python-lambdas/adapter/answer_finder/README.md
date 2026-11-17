# crossword_solver.adapter_answer_finder

Answer finder adapter implementations belong in this package. The use-case contract is
`crossword_solver_domain_use_case.answer_finder.AnswerFinder`.

`BedrockAnswerFinder` uses the Bedrock Converse API. Its default model is the same Opus
inference profile used by clue extraction, with temperature `0` and a 2048-token limit.
Pass a Bedrock Runtime client, model ID, conversation config, prompt factory, or response
converter to override the defaults. The default standard and cryptic prompts request
one `clue-id|answer|confidence` candidate per line.
