# MathOS v16: frozen-engine stress and allocation ablation

## Confirmed predecessor evidence

GitHub Actions run 46132714203 (head 229bf872e243bf41b05962810b064d2454fce7a7)
passed the evidence gate and scoped Lean job before PR #278 was merged.
The paired original benchmark reproduced v12 18/24, v14 15/24 and
v16 24/24. The held-out suite was 15/24, 16/24 and 24/24 respectively;
prior unresolved targets were 0/2, 2/2 and 2/2. All 50 v16 decisions
were independently replayed in CI. These are finite synthetic data,
not independent third-party replication or general solver superiority.

## Why another experiment?

The previous results exactly match the standalone search route and
the integrated report does not identify which fallback stages contributed.
A strong simple DPLL-style route may explain all of the small-case gains.
The fixed-third scheduler hypothesis also needs a controlled ablation.
The new experiment freezes the existing solver and policy; no existing
test, threshold or production decision logic is changed.

### Manifest and arms

54 cases: original 24 retrospective cases, 16 independently seeded
10/12/14/16-variable random 3-CNFs, and 14 structured cases (chains
around the depth limit, SAT and UNSAT pigeonhole formulas). Exhaustive
bit-vector truth tables independently adjudicate small CNFs. Chain
and pigeonhole labels follow explicit generator structure and elementary
induction/injection arguments; they are not exhaustive enumeration or
a general reference solver. All credited solver certificates are
separately replayed on the original CNF.

Five arms: v12 full budget; the exact v14 initial scheduler's one-third
budget (diagnostic intervention, not equal-budget competitor); standalone
search full budget; standalone search at v16's initial quota; unchanged
v16. Full arms get 100000 steps/5 cooperative seconds. Rotate arm order;
record elapsed solver-call time, route-specific work, stored proof bytes,
per-stage attempted/exhausted/decisive counts, baseline misses and
all unresolved IDs. Replaying certificates is external to reported
solver-call time; v16 additionally audits inside its call, so wall
time includes different in-call overhead. Counters and time are
observations, not mathematically authenticated measurements.

No tuning on the new cases. The CI gate retains 24/24 original coverage;
stress-suite failures are retained explicitly, not counted as success.
A green stress job means the protocol and proof checks succeeded,
not that every stress case was decided or that adaptive routing beat
standalone search. No external solver comparator, independent operator,
representative distribution, or asymptotic result is asserted.
No new proof rules are introduced; prior scoped Lean results remain
unchanged. A dedicated test exercises real fallback after exhaustion,
failed-assumption lemma replay and compact resolution replay.

## Reproduction

Generate v11/v12/v13 evidence as in prior documentation, then run:

    python -m mathos.research.pnp_v16_stress --benchmark source.json --scheduler scheduler.json --failures failures.json --checkpoint stress.json
    python -m mathos.research.pnp_v16_stress --benchmark source.json --scheduler scheduler.json --failures failures.json --audit stress.json --gate

No new measured stress outcome is claimed before the workflow runs.
