"""Static formal-source guardrail (not a proof checker).

CI must ALSO compile both formal files using their independent kernels.
No use of trust bypasses in the small new policy examples is permitted.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "formal/MillenniumOmega.lean": (
        "theorem bounded_rejected", "theorem unreviewed_rejected",
        "#print axioms",
    ),
    "formal/coq/MillenniumOmega.v": (
        "Theorem bounded_rejected", "Theorem unreviewed_rejected",
        "Print Assumptions",
    ),
}
PROHIBITED = re.compile(
    r"\b(sorry|admit|Admitted|Axiom|Parameter|Parameters|"
    r"unsafe|opaque|native_decide)\b",
    flags=re.IGNORECASE,
)


def audit(root: Path = ROOT) -> dict:
    checks = []
    for relative, required in EXPECTED.items():
        path = root / relative
        source = path.read_text(encoding="utf-8")
        illegal = sorted(set(PROHIBITED.findall(source)))
        missing = [marker for marker in required if marker not in source]
        if illegal or missing:
            raise ValueError(f"{relative}: forbidden tokens {illegal}; missing {missing}")
        checks.append({"path": relative, "static_policy_check": "PASSED"})
    return {
        "schema": "mathos.millennium_omega.formal_source_audit/1",
        "checks": checks,
        "meaning": (
            "Static guardrail only; Lean and Coq compilation in CI check "
            "the limited Boolean policy lemmas, not Millennium theorems."
        ),
        "millennium_problem_formally_proved": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
