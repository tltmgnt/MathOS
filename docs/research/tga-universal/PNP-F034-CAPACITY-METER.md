# PNP-F034 — Executable capacity-terminal structural metering

PNP_RESOLUTION_STATUS = OPEN. PR #174 merged at
09f875c80b58fc86603d2d257ac2310b1271eaa1. Initial CI run
45497351652 job 138811249813 failed (representative exact messages):
artifacts/pnp-f030/f034-chain-meter-combined.lean:1841:6: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-chain-meter-combined.lean:1870:59: error: tactic 'rfl' failed, the left-hand side
artifacts/pnp-f030/f034-chain-meter-combined.lean:1870:11: error: unsolved goals
Process completed with exit code 1.
Repository correction 4a4d391508ff3f9a901ebbb7046472e1337ebbd2
added definitional simplification and explicit Bool.and_false.
Final CI 45498144501 job 138814014438 passed all fourteen
zero-axiom declarations, 53 fixture checks and five hand controls.
Actual aggregate selected counts: chain=53207 refs=14667.
Artifact 14969997204.
https://github.com/tltmgnt/MathOS/actions/runs/45497351652/job/138811249813
https://github.com/tltmgnt/MathOS/actions/runs/45498144501/job/138814014438

## Metered capacity verifier

ProctorCapacityMeter composes previous indexed-reference and
membership meters with eager all/any traversals (one count per
visited list element plus callback charge). Distinctness counts
membership comparisons; wordsMeter enumerates the original ordered
words including repetitions, charging one visit per tree edge
and the selected leaf predicate charge. For an alphabet of size g
and depth k, this is sum(g^j,j=1..k) edge visits and g^k leaves.
Group checking rejects capacity >2 before enumeration, so k<=3.
Tuple distinctness is metered before conflict scanning, and repeated
tuples skip conflict scanning. Conflict scanning charges all
reference, clause-literal and tuple-literal visits plus one per
opposite-literal comparison. Eager folds can visit more items than
the production short-circuit predicates.

Demand-pair checks charge one index comparison, two indexed demand
lookups for unequal indices (hoisted once), and all pairwise literal
variable comparisons and their list visits. Coverage charges nested
demand, literal, group visits and membership comparisons. Final
capacity arithmetic is represented only by one final comparison;
totalCapacity arithmetic and lengths, construction of indices and
tuples, allocation, recursion overhead and bit cost are excluded.
The prior reference meters count only their selected operations.
The production checker remains unchanged.

Twenty-four candidate declarations prove Boolean result projection
and structural upper bound for generic folds, distinctness, ordered
word traversal, conflicts, tuples, groups, indexed demand lookup,
different-demand checks, coverage and whole capacity terminal.
The budgets are recursive input-structure expressions, not yet a
kernel-proved polynomial in bytes. In particular wordsBudget
traverses the full tree and charges all leaf budgets, including
conflict work skipped for duplicate words. Guard checks avoid
unbounded depth for invalid capacities. This meter is a
value-equivalent algorithm candidate, not a formal bound on the
precise production trace (notably demand lookups are shared).

## Validation

Static fixture runner loads all 53 prior typed input/proof file
pairs, measures the 24 capacity-terminal cases (17 original
capacity fixtures plus seven input-binding controls), checks
Boolean correspondence and budget, and prints individual counts.
Six direct controls exercise distinctness, two-level word
enumeration, conflict scanning, demand lookup/pairing, coverage and
oversized capacity. Required marker:
F034_CAPACITY_METER_OK cases=24 hand_controls=6.
Terminal acceptance is not whole-envelope acceptance: invalid
binding, chain or range checks are deliberately outside this
local comparison. New results pending CI; no local Lean.
All previous exact zero-axiom gates retained, 24 added.
No total runtime theorem, parser costs, compiler/IO refinement,
independent review, unrestricted SAT claim or main change.
Next: sparse XOR terminal metering, then unified typed composition
and an explicit polynomial bound for the selected charge model.
