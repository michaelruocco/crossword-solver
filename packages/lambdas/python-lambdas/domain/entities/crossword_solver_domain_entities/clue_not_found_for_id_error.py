from .id import Id


class ClueNotFoundForIdError(Exception):
    def __init__(self, clue_id: Id):
        super().__init__(f"Clue not found for id {clue_id}")
        self.clue_id = clue_id
