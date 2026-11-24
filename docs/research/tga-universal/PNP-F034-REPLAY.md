# PNP-F034 — Executable paired replay bridge

PNP_RESOLUTION_STATUS = OPEN. PR #163 merged at
6fdd96887d9d51fab2cdd1418f00f0df3c4d2b7a. The initial head
aaed853d134f468695f5237b4ace7d1852caf2b3 failed CI run
45469640829 job 138713783768:
artifacts/pnp-f030/f034-replay-combined.lean:622:2: error: too many variable names provided at alternative 'refl', #1 provided, but #0 expected
Process completed with exit code 1.
A repository correction dcb049fd830ab1a84f6a80ee48399b964acdeed4
removed the extraneous binder. Final CI 45470608995 job
138717237423 passed five tests, 3600 random budgeted runs
(495 UNSAT, 3105 UNKNOWN), 16 full-depth mixed refutations,
all 16 old and one-fewer-round cases UNKNOWN, four equal-size
controls, and all five replay lemmas zero axioms on Lean 4.14.0.
Largest PHP (16 holes, depth 3): 17544 clauses, 238646 signatures,
41667 steps; Tseitin32 depth3: 1024 clauses, 16896 signatures,
2432 steps. Artifact 14957137607.
https://github.com/tltmgnt/MathOS/actions/runs/45469640829/job/138713783768
https://github.com/tltmgnt/MathOS/actions/runs/45470608995/job/138717237423

## Executable checker, not merely supplied hypotheses

ProctorExecutableReplay.lean defines a recursive natural-index
lookup, literal membership, parent-shape check, per-step and
per-batch Boolean checks, finite chain check and terminal
empty-clause check. Nine candidate theorems prove lookup and
membership correctness, checked shape, step and batch evidence,
checked chain entailment and final UNSAT for an accepted
empty-clause terminal. The latter has an actual Boolean checker
premise, not an assumed semantic refutation of the terminal.

The checker accepts an explicitly annotated tail if every
literal of each parent is either its designated pivot or a
member of the tail. The other parent uses the opposite pivot.
This is sound even when the pivot is absent or the tail is
weakened, but intentionally weaker than Python exact equal-tail
replay. It does not implement Python sorting, tautology rejection,
positive pivot range checks or exact set equality. Its typed
Nat/Bool literals do not rely on a signed integer parser.
Empty batches and chains are allowed in the Lean checker;
soundness is unaffected (an empty formula has no empty clause).
The Python producer still rejects empty batches in actual proof
annotation. Do not claim equivalence of the two implementations.

## Cross-language execution

The Python exporter annotates real two-round PHP4 and Tseitin4
certificates with their reconstructed tails, preserves all parent
indices and uses signed sparse integer labels as Nat/Bool data.
It additionally emits a two-round empty-clause proof, invalid
parent-index and invalid-tail cases, a sound weakening example,
and 80 random one-round data cases. In total 86 fixtures.
Lean executes its own checker and compares accepted frontier
lists to the Python exported lists; it must reject both malformed
cases and check the expected empty-clause status. The workflow
requires an exact success marker, warnings-as-errors, pinned
Lean 4.14.0 and the nine new exact zero-axiom printouts. Existing
strict gates unchanged. The generated source uses only fixed
identifiers and checked numeric fields for this CI experiment.

The terminal capacity and XOR certificates for the real
two-round cases are still checked only by the existing Python
checkers. Lean independently checks their preceding resolution
chain, not those terminal certificates. The empty-clause route
is an end-to-end candidate within the typed Lean representation,
not verification of the full Python solver or its external parser.
The Python mirror is a same-author differential control, not
independent review. No machine-transition bound, general proof
complexity lower bound, original scratch port or main change.
New CI is pending. Next: executable signed capacity replay
with a checked bridge from original demand/conflict indices to
the formal generalized capacity evidence, before adding more
heuristics.
