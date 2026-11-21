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



def investigate_omissions(grid, start, end, *, diagonals=False):
    """Rank all single observed-cell omissions, holding endpoints and adjacency fixed."""
    baseline = lowest_pass(grid, start, end, diagonals=diagonals)
    report = {"baseline": baseline, "ranking": [], "review_cells": []}
    if baseline is None:
        report["review_question"] = "Which missing observations could connect the endpoints?"
        return report

    trial = [list(row) for row in grid]
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value is None or (r, c) in (start, end):
                continue
            trial[r][c] = None
            level = lowest_pass(trial, start, end, diagonals=diagonals)
            trial[r][c] = value
            report["ranking"].append({
                "cell": [r, c], "value": value, "threshold_after": level,
                "increase": None if level is None else level - baseline,
            })

    def severity(result):
        return (result["threshold_after"] is None, result["increase"] or 0)

    ranked = report["ranking"]
    ranked.sort(key=severity, reverse=True)
    if ranked and severity(ranked[0]) > (False, 0):
        report["review_cells"] = [item["cell"] for item in ranked
                                  if severity(item) == severity(ranked[0])]
        report["review_question"] = (
            "What independent measurement supports the listed cells, and are their "
            "assumed neighbour connections justified?"
        )
    else:
        report["review_question"] = "No single omission changed the threshold. Which joint omission is plausible?"
    return report


if __name__ == "__main__":
    level = lowest_pass(EXAMPLE, (1, 0), (1, 4))
    print(json.dumps({"scope": "synthetic two-minimum grid", "heights_m": EXAMPLE,
                      "endpoints_row_col": [[1, 0], [1, 4]], "connectivity": 4,
                      "omission_study_m": investigate_omissions(EXAMPLE, (1, 0), (1, 4)),
                      "merge_level_m": level, "younger_persistence_m": level - EXAMPLE[1][4]}))
