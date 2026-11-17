DETERMINE_PUZZLE_TYPE_PROMPT = """
Determine whether the following crossword clues are standard or cryptic.

Clues:
%CLUES%

Return exactly one of these values:
STANDARD
CRYPTIC

Use CRYPTIC when the clues predominantly use cryptic wordplay, such as anagrams,
hidden words, charades, containers, deletions, reversals, homophones, or double
definitions. Otherwise use STANDARD. Do not include commentary, markdown, or extra text.
"""
