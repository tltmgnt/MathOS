import itertools
from terrain import investigate_omissions
import unittest

from terrain import EXAMPLE, lowest_pass


def flood_oracle(grid, start, end):
    # Independent definition: at each threshold, flood only submerged cells.
    for level in sorted({z for row in grid for z in row if z is not None}):
        wet = {(r, c) for r, row in enumerate(grid) for c, z in enumerate(row)
               if z is not None and z <= level}
        if start not in wet:
            continue
        seen = {start}
        stack = [start]
        while stack:
            r, c = stack.pop()
            for p in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
                if p in wet and p not in seen:
                    seen.add(p)
                    stack.append(p)
        if end in seen:
            return level
    return None


class TerrainTests(unittest.TestCase):
    def test_known_pass_and_persistence(self):
        level = lowest_pass(EXAMPLE, (1, 0), (1, 4))
        self.assertEqual((level, level - 110), (140, 30))
        # Closing the original pass leaves a distinct, higher route.
        changed = [list(row) for row in EXAMPLE]
        changed[1][2] = None
        self.assertEqual(lowest_pass(changed, (1, 0), (1, 4)), 150)

    def test_corner_contact_depends_on_connectivity(self):
        grid = ((100, None), (None, 110))
        self.assertIsNone(lowest_pass(grid, (0, 0), (1, 1)))
        self.assertEqual(lowest_pass(grid, (0, 0), (1, 1), diagonals=True), 110)

    def test_all_small_grids_against_independent_oracle(self):
        for heights in itertools.product((None, -1, 0, 2), repeat=6):
            if heights[0] is None or heights[-1] is None:
                continue
            grid = (heights[:3], heights[3:])
            self.assertEqual(lowest_pass(grid, (0, 0), (1, 2)),
                             flood_oracle(grid, (0, 0), (1, 2)), grid)

    def test_invalid_grid_and_endpoint(self):
        for grid in ((), ((1,), (1, 2)), ((True,),), ((None,),)):
            with self.assertRaises(ValueError):
                lowest_pass(grid, (0, 0), (0, 0))


class OmissionStudyTests(unittest.TestCase):
    def test_all_ranked_omissions_against_flood_oracle(self):
        for values in itertools.product((None, -1, 2), repeat=4):
            grid = [[0, values[0], values[1]], [values[2], values[3], 1]]
            start, end = (0, 0), (1, 2)
            baseline = flood_oracle(grid, start, end)
            expected = {}
            if baseline is not None:
                for r, c in ((0, 1), (0, 2), (1, 0), (1, 1)):
                    if grid[r][c] is not None:
                        masked = [row.copy() for row in grid]
                        masked[r][c] = None
                        expected[(r, c)] = flood_oracle(masked, start, end)
            before = [row.copy() for row in grid]
            result = investigate_omissions(grid, start, end)
            self.assertEqual(grid, before)
            self.assertEqual(result["baseline"], baseline)
            ordered = sorted(expected, key=lambda cell: (
                expected[cell] is None, expected[cell] or 0), reverse=True)
            self.assertEqual([tuple(item["cell"]) for item in result["ranking"]], ordered)
            for item in result["ranking"]:
                level = expected[tuple(item["cell"])]
                self.assertEqual(item["threshold_after"], level)
                self.assertEqual(item["increase"], None if level is None else level - baseline)
            top = [list(cell) for cell in ordered if expected[cell] == expected[ordered[0]]
                   and expected[cell] != baseline]
            self.assertEqual(result["review_cells"], top)

    def test_diagonal_control(self):
        grid = [[1, None], [None, 2]]
        self.assertIsNone(investigate_omissions(grid, (0, 0), (1, 1))["baseline"])
        result = investigate_omissions(grid, (0, 0), (1, 1), diagonals=True)
        self.assertEqual(result["baseline"], 2)
        self.assertEqual(result["ranking"], [])
