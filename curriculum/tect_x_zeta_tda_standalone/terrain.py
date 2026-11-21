"""Minimum connecting flood level for two marked cells on a finite terrain grid."""
import heapq
import json

# Heights in metres. Rows increase southward, columns eastward.
EXAMPLE = ((160, 155, 150, 155, 160),
           (100, 120, 140, 125, 110),
           (160, 150, 145, 150, 160))


def lowest_pass(grid, start, end, *, diagonals=False):
    """Return the minimum, over allowed paths, of the highest cell on each path.

    Heights are integer metres. None marks excluded cells. Return None when the
    endpoints cannot connect through observed cells. Coordinates are (row, col).
    """
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("expected a nonempty rectangular grid")
    if any(h is not None and type(h) is not int for row in grid for h in row):
        raise ValueError("expected integer metres or None")
    rows, cols = len(grid), len(grid[0])
    for r, c in (start, end):
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] is None:
            raise ValueError("endpoint outside observed terrain")

    steps = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    if diagonals:
        steps.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    best = {start: grid[start[0]][start[1]]}
    queue = [(best[start], start)]
    while queue:
        level, cell = heapq.heappop(queue)
        if level != best[cell]:
            continue
        if cell == end:
            return level
        for dr, dc in steps:
            r, c = cell[0] + dr, cell[1] + dc
            if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] is None:
                continue
            candidate = max(level, grid[r][c])
            if (r, c) not in best or candidate < best[r, c]:
                best[r, c] = candidate
                heapq.heappush(queue, (candidate, (r, c)))
    return None


if __name__ == "__main__":
    level = lowest_pass(EXAMPLE, (1, 0), (1, 4))
    print(json.dumps({"scope": "synthetic two-minimum grid", "heights_m": EXAMPLE,
                      "endpoints_row_col": [[1, 0], [1, 4]], "connectivity": 4,
                      "merge_level_m": level, "younger_persistence_m": level - EXAMPLE[1][4]}))
