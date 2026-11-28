# MathOS v12 — evidence-guided research optimization

This release adds a deterministic scheduler to the v10 certificate portfolio.
It consumes a complete, replayed v11 benchmark, learns from structured and
development cases only, and freezes a policy before running paired holdout
experiments. The purpose is to test a resource-allocation hypothesis, not
to claim a new SAT algorithm or settle a universal proof obligation.

## Run

    python -m mathos.research.pnp_evidence_benchmark --checkpoint artifacts/pnp-v11.json
    python -m mathos.research.pnp_evidence_scheduler --benchmark artifacts/pnp-v11.json --checkpoint artifacts/pnp-v12.json
    python -m mathos.research.pnp_evidence_scheduler --benchmark artifacts/pnp-v11.json --audit artifacts/pnp-v12.json
    python -m unittest discover -s tests -p 'test_pnp_evidence_scheduler.py' -v

## Policy

On the still-uncovered training rows, rank each remaining plan by marginal
certified decisions divided by observed attempted work (at least one step
per attempt). Use exact rational arithmetic, then greater marginal gain,
lower observed cost and original plan index as deterministic tie-breaks.
Remove the covered training rows and repeat. All 14 plans remain available
as fallbacks, even when no further training coverage is available.
The suggested per-plan cap is twice its maximum successful training work,
with a 32-step floor, or the baseline equal-share allowance when no
successful training observation exists. The total budget always truncates
each attempted cap. This is a chosen heuristic, not an optimal scheduling
theorem or a performance guarantee.

Only training plan verdicts and observed work enter the policy; neither
reference SAT labels, wall times, aggregate benchmark metrics nor holdout
rows enter the score. The source audit necessarily replays the entire
benchmark, but scoring does not use holdout results. The source digest
binds the evaluation report to its exact input artifact and the separate
training digest binds policy-relevant observations.

## Paired evaluation

Each holdout instance is executed afresh under two policies: original
fixed-order plans with equal per-plan work allowances, and the learned
order and suggested caps. Both use the same total work limit, shared
absolute deadline within each arm, logical cell cap, compiler settings
and first-certified-decision stopping rule. Unused work remains in the
parent budget; each attempt is bounded by its own cap. An arm may finish
with unknown or deadline exhaustion. The order of executing arms alternates
across cases. External proof replay is separately budgeted, not included
in measured schedule work/time. The comparison changes both ordering
and cap allocation; it does not isolate the causal effect of either.
The default total is 100,000 steps per case per arm, which is different
from the v11 per-plan allowance.

Paired counts distinguish both decided, learned only, baseline only,
and both unknown. Report totals include actual attempted work, attempt
counts, exhausted attempts and observed elapsed time. The research
queue preserves both-unknown cases first, then learned misses that the
baseline resolved. Their reference decisions are included for debugging,
not as hard-instance labels. No holdout feedback is fed into training.
A future policy tuned on this holdout must use a new evaluation set.

## Independent audit and limitations

The audit replays the source, reconstructs the frozen policy, checks
holdout ordering, replays every attempted route certificate and
reconstructs work-accounting arithmetic and aggregates. It rejects
unsupported universal claims, incorrect decisions, altered policies,
and omitted rows on completed reports. Unknown schedule prefixes may
reflect deadline stops; they are not proof that no route could succeed.
Wall times and observed search work are not authenticated by proof
replay. Cooperative limits are not hard RSS or CPU limits. The small,
public deterministic holdout is not a representative or blind benchmark,
and its known v11 results are not a new independent distribution.
No claim of improvement is justified without actual paired results.
No Lean changes: v12 changes experimental scheduling, not proof rules.
All universal P versus NP obligations remain unresolved.
