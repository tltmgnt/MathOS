"""Outcome-driven PNP research CLI. Finite evidence never closes proof obligations."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from .pnp_structural_kernel import (
    Budget, Exhausted, analyze, brute, decide, duplication_example, validate,
)
from .pnp_outcome_registry import OBJECTIVES, decompose


def checkpoint(path, record):
    """Atomic replace; restart input, not an in-flight factor-table snapshot."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".pnp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(record, out, indent=2, sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class MathOSResearchEngine:
    def execute(self, objective, budget, *, n=0, clauses=(), c=1, checkpoint_path=None):
        plan = decompose(objective)
        # Validate before writing checkpoint; oversized data is not copied into it.
        record = {"schema": "mathos-pnp-outcome/2", "objective": plan,
                  "completion": "documented_unresolved_obligations",
                  "evidence": {}, "p_equals_np_established": False,
                  "p_not_equals_np_established": False,
                  "novel_theorem_verified": False,
                  "formal_verification": "not_performed"}
        try:
            f = validate(n, clauses)
            if type(c) is not int or not 1 <= c <= 16:
                raise ValueError("c must be an integer in 1..16")
            record["restart"] = {"objective": objective, "n": n, "clauses": f, "c": c}
            if checkpoint_path is not None:
                checkpoint(checkpoint_path, record)
            budget.tick()
            if objective == "E12":
                record["evidence"]["counterexample"] = duplication_example(budget)
                record["completion"] = "verified_finite_limitation"
                record["acceptance_scope"] = "only the exact raw-gap duplication claim"
            elif objective not in ("E17", "E19", "E20"):
                evidence = record["evidence"]
                evidence["analysis"] = analyze(n, f, c, budget)
                evidence["decision"] = decide(n, f, evidence["analysis"], budget)
                if n <= 12:
                    reference = brute(n, f, budget)
                    if reference != evidence["decision"]["sat"]:
                        raise AssertionError("independent SAT decision mismatch")
                    evidence["decision"]["independent_crosscheck"] = reference
                record["next_step"] = "discharge mathematical obligations independently; finite data are not proof"
            else:
                record["next_step"] = "no theorem or resource exhaustion inferred from objective selection"
        except Exhausted as exc:
            record["completion"] = "resource_exhausted"
            record["reason"] = str(exc)
        except AssertionError as exc:
            record["completion"] = "diagnostic_required"
            record["reason"] = str(exc)
        record["work_steps"] = budget.steps
        if checkpoint_path is not None:
            checkpoint(checkpoint_path, record)
        return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--objective", choices=sorted(OBJECTIVES), default="E12")
    p.add_argument("--input", type=Path, help="JSON with n and clauses")
    p.add_argument("--resume", type=Path, help="restart from saved input with a fresh budget")
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--c", type=int, default=1)
    p.add_argument("--seconds", type=float, default=10)
    p.add_argument("--max-steps", type=int, default=2_000_000)
    p.add_argument("--max-cells", type=int, default=100_000)
    args = p.parse_args(argv)
    if args.input and args.resume:
        p.error("choose --input or --resume")

    def read(path):
        if path.stat().st_size > 2_000_000:
            raise ValueError("JSON input exceeds 2 MB")
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        if args.resume:
            saved = read(args.resume)
            raw = saved["restart"]
            objective, c = raw["objective"], raw["c"]
        else:
            raw = read(args.input) if args.input else {"n": 0, "clauses": []}
            objective, c = args.objective, args.c
        budget = Budget(args.seconds, args.max_steps, args.max_cells)
        result = MathOSResearchEngine().execute(
            objective, budget, n=raw["n"], clauses=raw["clauses"], c=c,
            checkpoint_path=args.checkpoint)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["completion"] == "diagnostic_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
