# PNP-F034 — Executable sparse GF(2) terminal checking

PNP_RESOLUTION_STATUS = OPEN. PR #165 merged at
c653518afc2f681cc372bca48ede16c8d1798032. Its original PR run
45475719320 job 138735295506 failed:
artifacts/pnp-f030/f034-capacity-replay-combined.lean:996:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Repository correction c3b91e8ea5814b52969c8915702ca815212d222c
removed a redundant rewrite in distinct_complete. Final run
45477146881 job 138740262529 passed all 16 new declarations
with zero axioms, all three Python tests and exact
F034_CAPACITY_REPLAY_OK cases=17 marker. Artifact 14960476341.
https://github.com/tltmgnt/MathOS/actions/runs/45475719320/job/138735295506
https://github.com/tltmgnt/MathOS/actions/runs/45477146881/job/138740262529

## Candidate executable algebraic terminal

Each selected parity row contains a sparse variable list, a
Boolean right-hand side and explicit indexed original CNF rows.
The checker binds each referenced row exactly by index; for
every local bit pattern (support length at most five) of the
wrong parity it requires a referenced clause all of whose
literals are false on that pattern. Consequently any model
must satisfy the row parity. The checker allows stronger
clauses, duplicate support variables and width zero; it does
not require exactly the Python canonical forbidden block.
Even with repeated variables the actual model induces one of
the enumerated patterns and all its false literals are false.
This is a sufficient soundness test, not checker equivalence.

The sparse algebra folds Boolean XOR directly over Nat labels,
using a toggle that removes one matching occurrence or inserts
the label. A recursive combine has XOR-of-evaluations semantics
even for duplicate inputs. It computes the sum of selected
supports and right-hand sides. Acceptance requires an empty
sum support and true RHS (0=1), so a model is impossible.
The proof uses constructive Boolean case analysis and induction,
not an assumed GF(2) certificate or finite assignment search.
No dense array indexed by the declared variable bound is used.

Twelve candidate theorems cover local patterns, false literal
membership, parity, block soundness, Boolean algebra, sparse
toggle/combine/sum, checked terminal contradiction and its
composition with the existing executable paired chain:
checkChainXor f ps bs = true -> no satisfying assignment of f.
This is a new sparse representation, not a formal refinement
of the existing Python bitmask implementation.

## Cross-language fixtures

Five opposite-parity duals of widths one through five with
sparse labels, two signed cubic Tseitin duals, one actual
two-round guarded Tseitin dual, and one stronger-clause
example. Eight malformed dual controls and one SAT negative.
18 fixtures, 9 expected acceptances and 9 expected rejections.
The chunked exporter supplies typed original rows, paired
batches and parity blocks. Lean checks the complete chain
and terminal certificate and compares the reconstructed
frontier to the expected list. Exact marker:
F034_XOR_REPLAY_OK cases=18.
Pinned Lean 4.14.0, warnings-as-errors and twelve new exact
zero-axiom gates; prior gates unchanged. New CI pending.

The local truth-pattern test is bounded by 32 patterns per row;
clause scanning, list lookups, sparse toggle comparisons and
integer bit costs remain additional work. No full machine-cost
bound, verified external parser, Python translation refinement,
independent review or original scratch port. No main change.
Next: unified typed dispatch for empty/capacity/XOR terminals
and input binding audit before extending inference discovery.
