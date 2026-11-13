from .id import Id


class InvalidAnswerError(Exception):
    def __init__(self, answer_id: Id):
        super().__init__(f"Invalid answer for clue {answer_id}")
        self.answer_id = answer_id
