CRYPTIC_FIND_ANSWER_PROMPT = """
You are an expert at solving cryptic crossword clues.

Task:
Return up to %NUMBER_OF_CANDIDATES% plausible answers to the clue below.

Clue ID: %CLUE_ID%
Clue: "%CLUE%"
Pattern: %PATTERN%

Rules:
- You are an expert at solving cryptic crossword clues.
- Identify the most plausible definition (often at the beginning or end of the clue).
- Consider common cryptic wordplay types, including:
  - Anagram
  - Hidden word
  - Charade (word parts placed side by side)
  - Container/insertion
  - Deletion
  - Reversal
  - Homophone
  - Double definition
  - Cryptic definition
- If unsure, return multiple plausible synonyms.
- Confidence score must be an integer.
- Generate answers that plausibly satisfy BOTH the definition and a valid cryptic parsing.
- Do not rely on surface meaning alone; account for cryptic misdirection.
- Length must match the enumeration in the clue.
- Return uppercase A–Z only.
- Prefer common crossword answers and standard cryptic abbreviations.
- If multiple valid cryptic interpretations exist, return the strongest candidates first.
- Confidence score must be an integer reflecting how well the answer satisfies both definition and wordplay.
- If unsure, return multiple plausible cryptic interpretations rather than speculative synonyms.

Output format:
CLUE_ID|ANSWER|CONFIDENCE

If no plausible answers exist, return:
%CLUE_ID%|NO_MATCH|0

Do not include commentary, markdown, or extra text.
"""

STANDARD_FIND_ANSWER_PROMPT = """
You are an expert at solving standard (non-cryptic) crossword clues.

Task:
Return up to %NUMBER_OF_CANDIDATES% plausible answers to the clue below.

Clue ID: %CLUE_ID%
Clue: "%CLUE%"
Pattern: %PATTERN%

Rules:
- Return uppercase A–Z only.
- Length must match the enumeration in the clue.
- Prefer common crossword answers.
- If unsure, return multiple plausible synonyms.
- Confidence score must be an integer.

Output format:
CLUE_ID|ANSWER|CONFIDENCE

If no plausible answers exist, return:
%CLUE_ID%|NO_MATCH|0

Do not include commentary, markdown, or extra text.
"""

MATH_FIND_ANSWER_PROMPT = """
You are an expert at solving mathematical crossword clues.

Task:
Return up to %NUMBER_OF_CANDIDATES% plausible numeric answers to the clue below.

Clue ID: %CLUE_ID%
Clue: "%CLUE%"
Pattern: %PATTERN%

Rules:
- Solve the mathematical problem described by the clue.
- Return the answer using digits, not spelled-out number words.
- Match every known digit in the pattern.
- Length must match the enumeration in the clue.
- Do not include units, explanations, or extra text in the answer.
- Confidence score must be an integer.

Output format:
CLUE_ID|ANSWER|CONFIDENCE

If no plausible answers exist, return:
%CLUE_ID%|NO_MATCH|0

Do not include commentary, markdown, or extra text.
"""
