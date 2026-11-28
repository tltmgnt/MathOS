# MathOS v13 — failure-directed resolution synthesis

v12 CI observed 11/12 learned decisions versus 7/12 baseline, with
180945 versus 286733 work steps on the small holdout. holdout_01 was
UNSAT by the independent reference but both schedulers were unknown.
v13 consumes audited v11/v12 artifacts, investigating their union of
unresolved benchmark cases and scheduler queue. The old holdout is
now development evidence, not an independent evaluation set.

## Run

    python -m mathos.research.pnp_evidence_benchmark --checkpoint artifacts/pnp-v11.json
    python -m mathos.research.pnp_evidence_scheduler --benchmark artifacts/pnp-v11.json --checkpoint artifacts/pnp-v12.json
    python -m mathos.research.pnp_failure_synthesis --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --checkpoint artifacts/pnp-v13.json
    python -m mathos.research.pnp_failure_synthesis --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --audit artifacts/pnp-v13.json

## New refutation route

Unlike v4's non-growth bounded elimination, this Davis-Putnam route
permits controlled clause growth. Choose a pivot by positive-times-negative
occurrences, neighbor degree, or ascending label. Resolve each positive
and negative parent; ignore tautologies and duplicate retained clauses.
Eliminate the pivot and continue. Stop on derived width, record, work
or time caps. If the empty clause is derived, trim the proof DAG to its
ancestors. A verifier reconstructs every resolvent from normalized input
axioms or earlier steps, checks pivot polarity, derived clause and limits,
and requires an empty root. The original formula is UNSAT by resolution
soundness. If no refutation is found, report unknown, even when the
elimination would otherwise permit a SAT conclusion. This is a bounded
implementation of known resolution, not a new proof system.

## Failure-directed synthesis

Try nine combinations (three pivot orders, width caps 3/5/8) on the
original unresolved cases with equal per-attempt quotas. Select the plan
with the most verified refutations, then lowest observed attempted work,
then grammar order. No evaluation cases enter selection. Also minimize
reference-UNSAT cases by greedy deletion and exhaustive reference checks,
up to 128 trials. The minimized formula is deletion-minimal only after a
completed final pass. This preserves UNSAT, NOT the old portfolio failure;
it is diagnostic, not a minimized hardness witness.

Evaluate the frozen plan against a fixed min_product/width-5 baseline
on 24 new seeded random 3-CNFs (5–9 variables). Each uses identical
per-attempt quotas. This is not a comparison to the full v12 scheduler
on the new suite. A SAT formula is correctly unrefuted but remains
unknown to this UNSAT-only route. Reference-UNSAT counts are the relevant
denominator for refutation coverage. The seed and small synthetic dataset
do not provide representative or blind evaluation.

Audit verifies both upstream reports, target selection, all credited
resolution certificates, deterministic minimization, plan selection,
fresh reference labels and aggregates. Search work is observed, not
independently authenticated; absence of a proof cannot prove a lower
bound. Cooperative caps and input dimensions limit the experiment.
No new formal theorem or universal P versus NP claim.
