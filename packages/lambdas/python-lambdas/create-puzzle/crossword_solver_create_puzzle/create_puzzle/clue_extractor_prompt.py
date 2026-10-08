CLUE_EXTRACTOR_PROMPT = """
You are an expert at extracting structured crossword data from images.

Analyze the attached image of a crossword puzzle and output all clues in structured JSON format.

Instructions:

* Identify and extract every clue visible in the image, including both Across and Down clues.
* For each clue, capture:

  * "id" — the exact clue number printed next to the clue in the image. Do not infer, generate, renumber, or substitute a sequential number.
  * "text" — the complete clue text, including its enumeration.
  * "direction" — either "ACROSS" or "DOWN".
  * "lengths" — an array of integers representing the enumeration. For example, "(3,4,3)" → [3,4,3].
* The clue number must be read directly from the image. It is the number printed next to the clue, not the position of the clue in the extracted results.
* Ensure every visible clue is included.
* Across and Down clues often share the same clue numbers. If the same number appears in both directions, include both as separate entries.
* In cases where Down clues appear in a second column or wrap to additional columns, carefully preserve all clues and their correct directions.
* Double-check that every clue has the correct printed number and direction, particularly where clues wrap to another column.
* Ignore any crossword grid data. Only extract the text clues.

Text transcription:

* Transcribe the clue wording exactly as it appears in the image.
* Do not add, remove, correct, or substitute words.
* Do not correct spelling based on what you believe the clue should say.
* Do not add, remove, or change accented characters.
* Preserve accented characters exactly as they appear in the image.
* Do not infer or add diacritics that are not visibly present.

Formatting:

* The only formatting normalisations permitted are the following:

  1. Within an enumeration, always use exactly one space after each comma.
     Examples:
     "(3,6)" → "(3, 6)"
     "(4,2)" → "(4, 2)"
     "(1,1,1)" → "(1, 1, 1)"

* Do not otherwise alter, correct, normalise, or reformat the clue text.

* These formatting rules apply only to the clue text. Do not apply them to other punctuation.

Ordering:

* Return all Across clues first, followed by all Down clues.
* Within each direction, list clues in ascending numerical order.

Output:

* Your entire response must consist ONLY of the JSON array.
* Do not include explanations, comments, or any other text.
* Do not use Markdown.
* Do not use code fences.
* The first character of the response must be "[".
* The last character of the response must be "]".

Return the JSON array in this format:

[
  {
    "id": 1,
    "text": "Pacific republic (4)",
    "direction": "ACROSS",
    "lengths": [4]
  },
  {
    "id": 2,
    "text": "Gold bar (5)",
    "direction": "DOWN",
    "lengths": [5]
  }
]
"""