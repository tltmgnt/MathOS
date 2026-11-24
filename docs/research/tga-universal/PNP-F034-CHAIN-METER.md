# PNP-F034 — Compositional replay and reference meters

PNP_RESOLUTION_STATUS = OPEN. PR #173 merged at
e7b0dbe946c0144b839042c463417eb9762f554b. Initial run 45494896210
job 138802656135 failed:
artifacts/pnp-f030/f034-cost-combined.lean:971:12: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-cost-combined.lean:975:12: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Repository correction a62782c9571669983471ed02dfe2d0ef6cb11e58
removed rewrites already performed by cases. Final run 45495709789
job 138805504493 passed all six zero-axiom primitive declarations
and four Python cost-ledger tests (53 fixture and nine family
estimates). Artifact 14967684309.
https://github.com/tltmgnt/MathOS/actions/runs/45494896210/job/138802656135
https://github.com/tltmgnt/MathOS/actions/runs/45495709789/job/138805504493

## Metered layer

ProctorChainMeter extends the previous lookup/contains/shape meters.
Each parent meter adds visited lookup cells and shape comparisons.
Each step checks both parents; each batch checks all steps; each
chain checks all batches using exactly the prior frontier construction.
The meter deliberately evaluates all conjunction operands, including
those the production short-circuit checker can skip. It returns the
same Boolean result if the candidate value theorems hold, but not the
exact production execution trace. The charge counts exclude conjunction
operations, batch dispatch, tails construction, allocation, Nat
arithmetic, recursion overhead and final frontier construction.

Reference equality charges one per compared literal pair and one
end-marker comparison when comparison reaches the end of either row.
An indexed reference meter adds lookup cells and row equality counts.
Reference-list composition checks every reference, not just those
reached before failure. These meters can be used by both terminal
types; terminal enumeration itself is not yet metered in Lean.

Fourteen candidate declarations: paired value equality and additive
budget bound for parent, step, batch, chain, row equality, indexed
reference and reference list. Parent budget is formula row count
plus shapeBudget on the looked-up row if present. Step budgets sum two
parent budgets; batch and chain budgets sum the corresponding step
budgets on the exact intermediate frontiers. Reference budget is
formula row count plus referenced row length+1 if present. These
budgets are expressed in input structures, not yet a formal global
polynomial in byte size. No exact bit-machine model is asserted.

## Validation and boundary

Static Lean fixture runner reads the existing 53 data pairs (including
invalid certificates), checks metered Boolean projections against
production chainCheck and every refCheck and checks their additive
bounds. Five direct hand-count controls cover valid and invalid step
references, valid row equality, wrong row and missing index. Emits
per-case chain/ref counts and aggregate totals, then
F034_CHAIN_METER_OK cases=53 hand_controls=5.
Tests are not proof of total production cost; the candidate theorems
are about the explicit meters. Strict Lean 4.14.0 warnings-as-errors
and all previous exact zero-axiom gates remain; fourteen new exact
gates. New CI pending, no local Lean.

No solver-discovery cost, complete terminal cost semantics, parser
cost, machine refinement, independent review or unrestricted SAT
claim. Main untouched. Next: executable capacity terminal metering
for distinctness, bounded tuple enumeration, conflict scanning and
demand coverage, then XOR and unified typed composition.
