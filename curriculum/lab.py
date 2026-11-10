"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")




def run():
    # Static source contract; no transformers, weights, credentials or model download.
    tree = ast.parse((ROOT/"experiments/internal_reasoning/activation_capture.py").read_text())
    fn = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "capture_activations")
    check("capture requests hidden states", any(isinstance(n,ast.keyword) and n.arg=="output_hidden_states" and isinstance(n.value,ast.Constant) and n.value.value is True for n in ast.walk(fn)), True)
    check("capture disables dropout via eval", any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="eval" for n in ast.walk(fn)), True)
    check("capture records last-token vector", "last_token" in {n.id for n in ast.walk(fn) if isinstance(n,ast.Name)}, True)
    # A hand-checkable representation baseline, not measurements from a model:
    vectors = [[1,0],[0,1],[-1,0],[0,-1]]
    def squared_distances(rows):
        return sorted(sum((a-b)**2 for a,b in zip(rows[i],rows[j])) for i in range(len(rows)) for j in range(i))
    rotated = [[-y,x] for x,y in vectors]
    check("orthogonal rotation preserves pair distances", squared_distances(rotated), squared_distances(vectors))
    check("synthetic distance multiset", squared_distances(vectors), [2,2,2,2,4,4])
    scaled = [[2*x,2*y] for x,y in vectors]
    check("scaling changes distance convention", squared_distances(scaled), [8,8,8,8,16,16])

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
