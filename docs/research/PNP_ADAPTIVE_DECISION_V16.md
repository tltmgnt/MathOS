# MathOS adaptive decision v16 — research candidate, not default

## Regression diagnosis

The v15 report records v14 at 15/24 versus the v12 scheduler at
18/24: SAT 9/18 versus 14/18; UNSAT 6/6 versus 4/6; zero learned clauses.
The net loss is five SAT decisions minus two UNSAT gains. Inspection of
v14 shows a fixed first-third scheduler allocation, a separate third for
resolution, and small non-borrowing probe/final quotas. This is a plausible
resource starvation mechanism, not a causal ablation result. The new
paired report includes the baseline-decided / initial-third-unknown IDs.
A full factorial allocation ablation is still needed.

## Candidate

Add a bounded constructive search with shortest-clause branching, unit
propagation and residual literal frequency evidence. A model is replayed
against the original clauses; a contradiction tree must close both
branches at every split with a falsified original clause. Stop at a work,
time or depth limit. The first attempt uses half the budget for at most
16 active variables, one twentieth otherwise. Carry unused budget into
the unchanged v12 learned portfolio, including recursive separators,
decomposition and algebraic reduction. Dense inputs reserve a fraction
of residual budget for v13 resolution. If available, compact its proof
with v15; retain the original even when compression exhausts. If still
unknown, try two opposite singleton failed-assumption probes under a
bounded remaining share, and retry search only after a verified lemma.
There is no cross-formula lemma transfer. The existing v15 template
reuse API is unchanged, but not automatically invoked.

The v12/v14 APIs and tests are untouched. A fallback under the remaining
budget does NOT mathematically guarantee equal-budget baseline dominance.
The per-instance regression gate is therefore mandatory before adoption.
The known v14 benchmark is now development, not independent evidence.
The newly seeded suite has syntactic overlap checks, not independent
operators, semantic disjointness or representative SAT distributions.

## Replay and measurements

Use the existing v11/v12/v13 artifact generation commands, then:

    python -m mathos.research.pnp_adaptive_frontier --benchmark artifacts/source.json --scheduler artifacts/scheduler.json --failures artifacts/failures.json --checkpoint artifacts/v16.json
    python -m mathos.research.pnp_adaptive_frontier --benchmark artifacts/source.json --scheduler artifacts/scheduler.json --failures artifacts/failures.json --audit artifacts/v16.json --gate

Each arm has 100000 work steps and five cooperative seconds. The report
keeps per-case outcomes, attempted work, wall time for the solver call
(including in-call replay for v14/v16, not identical replay overhead),
and stored certificate payload bytes (original plus compact if stored;
not a minimal standalone proof size). Work counters are route-specific
and not CPU instructions. Independent report replay is outside the
search budgets; time and search counters are not authenticated.
The original 24-case seed 14014, v13's unresolved development targets,
and seed 16028 with 24 cases are separate strata. The gate requires at
least 18/24 and all six original UNSAT, zero v12/v14 per-case misses,
and strict held-out coverage improvement over both comparators. Failure
is evidence, not a reason to weaken tests. Reports are checkpointed and
uploaded even on failure. No empirical result is asserted in this note.

Lean checks the abstract Boolean split and conflict rule only, not
Python, runtime, full proof-system soundness, or P versus NP. Search
can be exponential, resolution can grow exponentially, fixed depth
and bounded template matching are incomplete, and no universal claim
is established. Recursive separator/algebraic strategies are reused
rather than newly optimized; separator-specific and learning ablations
remain open. Keep this branch separate until full evidence replay,
regression gates and review succeed.
