from datetime import datetime
from typing import Any
from uuid import UUID

from crossword_solver_domain_entities.cell import Cell
from crossword_solver_domain_entities.cells import Cells
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_type import ClueType
from crossword_solver_domain_entities.clues import Clues
from crossword_solver_domain_entities.coordinates import Coordinates
from crossword_solver_domain_entities.direction import Direction
from crossword_solver_domain_entities.grid import Grid
from crossword_solver_domain_entities.id import Id
from crossword_solver_domain_entities.puzzle import Puzzle
from crossword_solver_domain_entities.word import Word
from crossword_solver_domain_entities.words import Words

Item = dict[str, Any]


class PuzzleItemConverter:
    def to_item(self, puzzle: Puzzle) -> Item:
        return {
            "id": str(puzzle.id),
            "name": puzzle.name,
            "format": puzzle.format,
            "hash": puzzle.hash,
            "clues": [self._clue_to_item(clue) for clue in puzzle.clues],
            "grid": self._grid_to_item(puzzle.grid),
            "words": [self._word_to_item(word) for word in puzzle.words],
            "created_at": puzzle.created_at.isoformat(),
        }

    def to_puzzle(self, item: Item) -> Puzzle:
        return Puzzle(
            id=UUID(item["id"]),
            name=item["name"],
            format=item["format"],
            hash=item["hash"],
            clues=Clues([self._item_to_clue(clue) for clue in item["clues"]]),
            grid=self._item_to_grid(item["grid"]),
            # Intersections are not stored, the Words constructor works them out from the word positions.
            words=Words([self._item_to_word(word) for word in item["words"]]),
            created_at=datetime.fromisoformat(item["created_at"]),
        )

    @staticmethod
    def _clue_to_item(clue: Clue) -> Item:
        return {
            "number": clue.id.number,
            "direction": clue.id.direction.value,
            "text": clue.text,
            "lengths": clue.lengths,
            "type": clue.type.value if clue.type else None,
        }

    @staticmethod
    def _item_to_clue(item: Item) -> Clue:
        # DynamoDB returns numbers as Decimal.
        return Clue(
            id=Id(int(item["number"]), Direction(item["direction"])),
            text=item["text"],
            lengths=[int(length) for length in item["lengths"]],
            type=ClueType(item["type"]) if item.get("type") else None,
        )

    @staticmethod
    def _word_to_item(word: Word) -> Item:
        return {
            "number": word.id.number,
            "direction": word.id.direction.value,
            "length": word.length,
            "x": word.x,
            "y": word.y,
        }

    @staticmethod
    def _item_to_word(item: Item) -> Word:
        return Word(
            id=Id(int(item["number"]), Direction(item["direction"])),
            length=int(item["length"]),
            coordinates=Coordinates(int(item["x"]), int(item["y"])),
        )

    @staticmethod
    def _grid_to_item(grid: Grid) -> Item:
        return {
            "column_width": grid.column_width,
            "row_height": grid.row_height,
            "cells": [
                {
                    "x": cell.coordinates.x,
                    "y": cell.coordinates.y,
                    "black": cell.black,
                    "id": cell.id,
                    "letter": cell.letter,
                }
                for cell in grid.cells
            ],
        }

    @staticmethod
    def _item_to_grid(item: Item) -> Grid:
        return Grid(
            cells=Cells(
                [
                    Cell(
                        coordinates=Coordinates(int(cell["x"]), int(cell["y"])),
                        black=cell["black"],
                        id=int(cell["id"]) if cell.get("id") is not None else None,
                        letter=cell.get("letter"),
                    )
                    for cell in item["cells"]
                ]
            ),
            column_width=int(item["column_width"]),
            row_height=int(item["row_height"]),
        )
