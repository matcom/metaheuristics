from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, Iterable, List, Set, Tuple, Union

import numpy as np

Board = List[List[bool]]
Cell = Tuple[int, int]

DX = [-1, -1, -1, 0, 0, 1, 1, 1]
DY = [-1, 0, 1, -1, 1, -1, 0, 1]


class GameOfLife:
    def __init__(self, cells: Iterable[Cell]) -> None:
        self.initial_cells: Set[Cell] = set(cells)
        self.alive_cells: Set[Cell] = set(cells)
        self._center_cells()

    def _center_cells(self):
        si, sj, _, _ = self.bounds()
        bi, bj = self.board_size()
        i_offset = bi // 2
        j_offset = bj // 2
        cells = [
            (ci - i_offset - si, cj - j_offset - sj) for ci, cj in self.initial_cells
        ]
        self.initial_cells = set(cells)
        self.alive_cells = set(cells)

    @staticmethod
    def from_random(size: Tuple[int, int]) -> GameOfLife:
        si, sj = size
        board = [[random.random() < 0.5 for _ in range(sj)] for _ in range(si)]
        return GameOfLife.from_board(board)

    @staticmethod
    def from_board(
        board: Board,
    ) -> GameOfLife:
        cells = set()
        for i, row in enumerate(board):
            for j, v in enumerate(row):
                if v:
                    cells.add((i, j))
        return GameOfLife(cells)

    @staticmethod
    def from_str(
        str_board: str,
        sep="\n",
        alive="O",
        remove_spaces: bool = True,
    ) -> GameOfLife:
        cells = set()
        if remove_spaces:
            str_board = str_board.replace(" ", "")
        for i, row in enumerate(str_board.strip().split(sep)):
            for j, v in enumerate(row):
                if v == alive:
                    cells.add((i, j))
        return GameOfLife(cells)

    @staticmethod
    def str_to_boolean_board(
        str_board: str,
        sep="\n",
        alive="O",
        remove_spaces: bool = True,
    ) -> List[List[bool]]:
        if remove_spaces:
            str_board = str_board.replace(" ", "")

        rows = str_board.strip().split(sep)
        assert all(
            len(r) == len(rows[0]) for r in rows
        ), "All rows must have the same length"

        board = [[False for _ in range(len(rows[0]))] for _ in rows]

        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                if v == alive:
                    board[i][j] = True
        return board

    def reset(self):
        self.alive_cells = self.initial_cells.copy()

    def __hash__(self) -> int:
        return hash("|".join(f"{c[0]}|{c[1]}" for c in sorted(list(self.alive_cells))))

    def __getitem__(self, index):
        assert (
            isinstance(index, tuple) and len(index) == 2
        ), "Index must be of the form (i, j)"
        i, j = index
        for cell in self.alive_cells:
            if cell == (i, j):
                return True
        return False

    def bounds(self) -> Tuple[int, int, int, int]:
        cells = iter(self.alive_cells)
        first = next(cells, None)
        if first is None:
            return 0, 0, 1, 1
        min_i, min_j = first[0], first[1]
        max_i, max_j = min_i, min_j
        for cell in cells:
            i, j = cell
            min_i = min(i, min_i)
            min_j = min(j, min_j)
            max_i = max(i, max_i)
            max_j = max(j, max_j)
        return min_i, min_j, max_i, max_j

    def _neighbor_idxs(self, cell: Cell):
        ci, cj = cell
        for dx, dy in zip(DX, DY):
            yield ci + dx, cj + dy

    def alive_neighbors_count(self) -> Dict[Cell, int]:
        ans: Dict[Cell, int] = defaultdict(int)
        for cell in self.alive_cells:
            for ni, nj in self._neighbor_idxs(cell):
                ans[ni, nj] += 1
        return ans

    def next_step(self):
        new_alive_cells = set()
        alive_neighbors_count = self.alive_neighbors_count()

        # Check alive cells
        for cell in self.alive_cells:
            alive_nb = alive_neighbors_count.get(cell, 0)
            if 2 <= alive_nb <= 3:
                new_alive_cells.add(cell)

        # Check for new cells
        new_alive_cells.update(
            [cell for cell, count in alive_neighbors_count.items() if count == 3]
        )

        self.alive_cells = new_alive_cells

    def get_board(self, margin: int = 0) -> Board:
        si, sj, ei, ej = self.bounds()
        size_i = ei - si + 1 + margin * 2
        size_j = ej - sj + 1 + margin * 2
        board = [[False for _ in range(size_j)] for _ in range(size_i)]
        for cell in self.alive_cells:
            i = cell[0] - si + margin
            j = cell[1] - sj + margin
            board[i][j] = True
        return board

    def get_str_board(self, sep="\n", alive="O", dead=".", margin: int = 0):
        board = self.get_board(margin=margin)
        return sep.join(["".join([alive if c else dead for c in row]) for row in board])

    # ---------------------------------------
    # Stats functions
    # ---------------------------------------

    def cell_array(self) -> np.ndarray:
        return np.array([[i, j] for i, j in self.alive_cells])

    def alive_cells_count(self) -> int:
        return len(self.alive_cells)

    def board_size(self) -> Tuple[int, int]:
        si, sj, ei, ej = self.bounds()
        return ei - si + 1, ej - sj + 1

    def board_centroid(self) -> Union[Tuple[float, float], None]:
        cell_arr = self.cell_array()
        if len(cell_arr) == 0:
            return None
        mean = np.mean(cell_arr, axis=0)
        return mean[0], mean[1]

    def board_std(self) -> Union[Tuple[float, float], None]:
        cell_arr = self.cell_array()
        if len(cell_arr) == 0:
            return None
        std = np.std(cell_arr, axis=0)
        return std[0], std[1]
