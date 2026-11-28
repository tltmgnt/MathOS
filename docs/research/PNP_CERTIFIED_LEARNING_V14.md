# MathOS v14 — unified constructive/refutation learning

v13 passed its independent audit: both previous unresolved instances
(development_04 and holdout_01) were refuted by the selected min_product,
width-8 plan. The 30- and 39-clause inputs had minimized UNSAT subsets
of 9 and 13 clauses respectively. On the separate v13 24-instance
evaluation, selected and fixed baseline both refuted all four reference
UNSAT cases. This does not show an advantage on that evaluation.

v14 composes the frozen v12 scheduler with the v13 resolution route
without changing old benchmark manifests or route identifiers.

## Execute

    python -m mathos.research.pnp_learning_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --checkpoint artifacts/pnp-v14.json
    python -m mathos.research.pnp_learning_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --audit artifacts/pnp-v14.json

Generate upstream reports using their existing documented CLIs. Each
is audited before use. The hybrid API is pnp_certified_learning.solve.

## Constructive/obstruction exchange

Attempt the existing learned scheduler on the original input, then the
selected v13 refutation plan if unknown. If both fail, probe up to 24
single/pair assumptions on at most eight high-occurrence variables.
If F AND A refutes, F entails NOT A; append exactly the clause negating
the assumption conjunction. Each proof is a v13 resolution DAG on the
current formula plus unit assumptions. Independently replay these DAGs
and their exact assumption/blocking-clause relationship in order.
Subsequent probes may rely on already checked clauses. Finally run the
constructive/decision scheduler on the augmented formula. All appended
clauses are consequences, so satisfiability is preserved. No learned
clause is copied into an unrelated formula; only policies transfer.
This is bounded failed-assumption learning, not CDCL or unrestricted SAT.

## Budgets and evidence

Reserve one third of the work ceiling for each of the first two phases;
split the remainder between probes and final scheduler (or give it to
the final scheduler if probes disabled). No borrowing between phases.
Time fractions sum to the configured seconds, with separate cooperative
deadlines. External proof replay, Python overhead and input preparation
are not included in measured search work/time; no hard wall-clock or
RSS guarantee. An exhausted or unrecognized probe supplies no lemma.
A refutation is only credited after checking it. The verifier replays
the initial route, resolution phase, learned clauses, and final route
against the exact original input; it reconstructs work arithmetic but
does not authenticate search counters. Unknown never means UNSAT.

The default evaluation uses 24 new seeded 3-CNFs (seed 14014) with
independent exhaustive references; compare the hybrid against v12's
learned scheduler under the same configured total work/time. Neither
evaluation arm is tuned on these rows. The new seed does not prove
disjoint semantic instances or statistical representativeness.
Count SAT/UNSAT/unknown, learned clauses, direct refutation decisions,
paired coverage and work. No improvement is assumed. The baseline can
outperform the hybrid because of its different allocation of resources.
Lean checks the abstract failed-assumption consequence and equivalence
and Boolean pair negation, not the Python proof checker, full resolution
soundness, or asymptotic complexity. All universal obligations remain
unresolved.
