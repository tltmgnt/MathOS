# PNP-F034 — Executable signed capacity terminal checking

PNP_RESOLUTION_STATUS = OPEN. PR #164 merged at
3a923690e74a423711e0bc9d9df26f9d5f8009e6. Its original PR run
45472256023 job 138728874079 failed:
Process completed with exit code 143.
A subsequent repository correction 939c23a681f907fb28af037adfdfae9048ace0b7
shared typed generated terms and bounded list-expression chunks.
The final run 45474211860 job 138729968630 passed the three Python
bridge tests, all nine executable replay declarations with zero
axioms and the exact F034_EXECUTABLE_REPLAY_OK cases=86 marker.
Artifact 14959555251.
https://github.com/tltmgnt/MathOS/actions/runs/45472256023/job/138728874079
https://github.com/tltmgnt/MathOS/actions/runs/45474211860/job/138729968630

## Candidate executable capacity checker

ProctorCapacityReplay.lean checks annotated original demand and
conflict row references using natural index lookup and exact list
equality. It checks distinct literals within each group, capacity
at most two, pairwise disjoint demand variable supports, coverage
of every demand literal and strict total capacity deficiency.
For each group it enumerates all ordered tuples of length cap+1
over its literals, ignoring repetitions, and checks that a cited
original clause uses only complementary literals from that tuple.
This is a stronger-clause test (not exact complementary-set equality).
The global referenced-clause pool need not be separated by group.
Groups may overlap, and capacity zero is allowed; overcounting
slots only weakens the bound. The Python capacity checker remains
unchanged and more restrictive. No equivalence claim.

Sixteen new candidate declarations establish Boolean universal and
existential check soundness, index and reference correctness,
distinctness, tuple enumeration completeness for checked words,
group evidence, demand selection/disjointness, full capacity
checker soundness and composition with the existing executable
paired chain. The end-to-end theorem is:
checkChainCapacity f bs c = true -> no satisfying assignment of f.
It has no assumed semantic terminal-refutation premise.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates are
extended, not relaxed.

## Cross-language data fixtures

Four actual signed capacity certificates (capacities one/two),
one actual two-round guarded PHP capacity certificate, a mixed
capacity example with duplicate literals, and a sound capacity-zero
example. Nine malformed certificate controls (indices, annotated
row, repeated demand, missing coverage, repeated group literal,
missing/incorrect/out-of-range conflict and excessive capacity),
and a satisfiable equal-capacity negative. Total 17. Python exports
typed data via existing chunked exporter; Lean independently executes
the chain plus capacity checker, compares frontier and expected
accept/reject results. Exact marker F034_CAPACITY_REPLAY_OK cases=17.
These are candidate results until CI. The proof is on typed
Lean data, not a mechanically verified Python or external parser
translation. The terminal XOR checker remains Python-only.

The enumeration has at most cubic tuples per group; scanning all
cited clauses per tuple, sparse bit costs, and checking coverage
and disjointness are additional work. No total machine transition
bound or independent review. No original scratch port or main
change. Next: typed executable GF(2) terminal checking with
original parity-block references, then audit the input binding
and trust boundary of the exported proof data.
