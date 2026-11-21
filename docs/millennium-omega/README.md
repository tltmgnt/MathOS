# Millennium Ω — research-only implementation

Millennium Ω is a **new orchestration and assurance layer** over MathOS's
existing seven-track hypothesis pipeline, proof graph and bounded experiments.
It does **not** constitute solutions to the Clay Millennium Prize Problems.

The framework exposes seven stable engine IDs:
bsd, hodge, navier_stokes, p_vs_np, poincare, riemann and yang_mills.
Each delegates bounded experiments to the existing audited MathOS probes,
rather than silently substituting a new conjecture for the official target.

## Run

From the repository root with Python 3.10+:

    python -m mathos.millennium_omega --output artifacts/millennium-omega/report.json
    python -m mathos.millennium_omega --engine bsd
    python -m unittest discover -s tests -p 'test_millennium_omega.py' -v
    python scripts/millennium_omega_audit.py
    python scripts/millennium_omega_benchmark.py --runs 3

Lean 4.14.0 and Coq are optional for local Python use, but checked
independently in the GitHub Actions workflow:

    lean formal/MillenniumOmega.lean
    coqc -q formal/coq/MillenniumOmega.v

Both files prove only toy Boolean acceptance-policy lemmas.
Their compilation does not discharge any Clay mathematical obligation.

## Hard boundaries

- Poincare is **externally solved**; MathOS's independent proof replay is still
  **blocked**, as recorded in the existing canonical register.
- The six other problem tracks remain open, without implied acceptance.
- Successful finite/numerical/conditional probes produce research evidence only.
- The TECT layer refuses missing engines, absent stage traces, altered fingerprints,
  false proof claims, and any attempted research-to-proof promotion.
- Agent steps are deterministic offline stages, not live self-directed AI agents.
- This code writes standalone reports, never the canonical obligation register.

See [architecture](ARCHITECTURE.md), [requirements](REQUIREMENTS.md),
[obligations](PROOF_OBLIGATIONS.md), [benchmarks](BENCHMARKS.md) and
[roadmap](ROADMAP.md). The existing
seven-hypothesis research lab remains the source of bounded experiments:
[SEVEN_HYPOTHESIS_LAB](../research/SEVEN_HYPOTHESIS_LAB.md).
