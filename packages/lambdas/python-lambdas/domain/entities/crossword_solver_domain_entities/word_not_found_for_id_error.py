from .id import Id


class WordNotFoundForIdError(Exception):
    def __init__(self, word_id: Id):
        super().__init__(f"Word not found for id {word_id}")
        self.word_id = word_id
