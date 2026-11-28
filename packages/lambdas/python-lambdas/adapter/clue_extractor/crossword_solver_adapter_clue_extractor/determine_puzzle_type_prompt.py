DETERMINE_PUZZLE_TYPE_PROMPT = """
Determine whether the following crossword clues are standard, cryptic, or mathematical.

Clues:
%CLUES%

Return exactly one of these values:
STANDARD
CRYPTIC
MATH

Use MATH when the clues predominantly require mathematical reasoning, such as
arithmetic, equations, sequences, or calculations, and their answers are numbers.
Use CRYPTIC when the clues predominantly use cryptic wordplay, such as anagrams,
hidden words, charades, containers, deletions, reversals, homophones, or double
definitions. Otherwise use STANDARD. Do not include commentary, markdown, or extra text.
"""
