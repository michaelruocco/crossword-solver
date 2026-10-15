class CellNotFoundForIdError(Exception):
    def __init__(self, cell_id: int):
        super().__init__(f"Cell not found for id {cell_id}")
        self.cell_id = cell_id
