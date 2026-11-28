# v17.3 — parameterized implication-path proof schema

## v17.2 outcome: negative optimization result

PR #286 merged (23c3fa664e576d1b089877fa9afd6377d69c8cc7).
CI https://github.com/tltmgnt/MathOS/actions/runs/46135269923 passed.
On 48 fresh cases (15 reference UNSAT), exact composition verified 7,
subsumption 8, adaptive exact 6, adaptive exact-first 6. The full
adaptive arm had 37 round-limit outcomes and took 6.544 s aggregate
search/replay wall time vs 3.539 s for subsumption and 2.625 s for exact.
It verified zero of eight fresh ternary UNSAT cases. The retrospective
48 cases showed 10/13 UNSAT for adaptive vs 9/13 for each legacy arm,
but that is not new holdout evidence. Retain existing defaults; do not
promote the adaptive agenda based on retrospective gains.

## Research move: parameterized schema rather than larger fixed templates

The known 2-SAT implication graph construction provides an elementary
length-parameterized proof schema. A clause (not a OR b) licenses a
directed edge a -> b, including unit clauses as duplicated literals.
A path licenses the implication between endpoints by induction on its
length. Opposite paths p -> not p and not p -> p are inconsistent
with any valuation. This is standard mathematics, not theorem novelty.

The implementation searches strongly connected components of the
original normalized binary and unit clauses, even if the input also
contains wider clauses. Only original edges qualify. Search returns two
simple signed paths as the certificate. A separate checker verifies
endpoints, dimensions and each original clause witness; no SCC label is
trusted. The paths imply unit clauses (not p), (p), then the empty
clause, all checked against the original formula by RUP and independently
replayed by the v17.1 residual-clause checker. An explicit input empty
clause is credited separately. A miss or exhausted budget is UNKNOWN,
not SAT. Binary-subset recognition is cross-checked against the
existing separately implemented 2-SAT reachability routine.

The mathematical schema is length-unbounded. The implementation has
the existing 512-variable, literal and clause caps, and a cooperative
budget. SCC and witness search on a materialized adjacency graph use
linear graph traversal work, apart from normalization and deterministic
sorting. No end-to-end linear runtime claim: certificate checking and
RUP have their own cost. The schema can handle paths too long for any
fixed-support whole-core template, but fixed fragments can also compose;
there is no separation theorem against arbitrary fragment composition.

Lean expresses the signed literal semantics and inductive path entailment
for all finite path lengths, then derives contradiction from opposite
paths. This is not a formal refinement proof of the Python checker or
SCC algorithm. Tests cover long chains, SAT twins, mixed formulas,
forged witnesses, random small 2-CNF and resource limits.

## Frozen experiment

Use audited, unchanged v17 expanded library. Compare exact composition,
subsumption composition and the parameterized route on the same input
with shared per-arm cooperative search/reconstruction budgets (4M ticks,
15s, 100k cells). Independent checking and report audit are timed or
performed separately. No hard process ceiling; operation counts differ.
The union statistic is an oracle-free set union of credited outcomes,
not a jointly budgeted portfolio performance result.

Fresh split seed 17303: 24 each random 2-CNF, random 3-CNF and mixed
binary/ternary CNF (72 total), generated without templates and with exact
normalized duplicate rejection against prior and upstream cases.
Controls: 12 explicit SAT/UNSAT chains of lengths 1 to 128, scored
separately. Fresh small references use exhaustive truth tables; larger
chain controls use the independent reachability decision routine.
No tuning or template admission on evaluation. Public seed, not an
external blind test, and no signed-orbit disjointness guarantee.
Do not count path-schema successes as empirical retrieval of learned
templates; this is a separate known algorithmic abstraction route.
Pure ternary formulas cannot benefit unless they contain original
short clauses after normalization; no new inference grammar is added.

Run:
    python -m unittest discover -s tests -p 'test_pnp_implication_paths.py' -v
    lean -DwarningAsError=true formal/PnpImplicationPaths.lean
    python -m mathos.research.pnp_implication_paths_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --v17 artifacts/pnp-v17.json --checkpoint artifacts/pnp-v17.3.json

Use --audit with the same upstream inputs to replay positive evidence,
references and summaries. Negative search and timing observations are
not authenticated. New experimental and Lean results are pending CI.
No claim of unrestricted generalization, novelty or P versus NP.
