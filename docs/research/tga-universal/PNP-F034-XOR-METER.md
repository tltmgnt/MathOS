# PNP-F034 — Sparse GF(2) terminal resource metering

PNP_RESOLUTION_STATUS = OPEN. At submission, PR #175 was open,
not merged, with adaptive CI run 45499880801 job 138820033867
in progress. This work is independent of that unverified
capacity-meter branch and starts at the verified #174 merge
09f875c80b58fc86603d2d257ac2310b1271eaa1. A separate additive
CI workflow avoids modifying #175's existing workflow changes.
https://github.com/tltmgnt/MathOS/pull/175
https://github.com/tltmgnt/MathOS/actions/runs/45499880801/job/138820033867

## Selected charge model

ProctorXorMeter composes the verified membership and indexed
reference meters with local eager all/any folds. These folds
charge one per element plus callback charges. Each parity
pattern charges one per pattern literal and one RHS comparison.
Wrong-parity patterns also scan all annotated references and
their literals with metered membership; correct patterns skip
that scan. The binary pattern tree charges one per internal
node. With support width k<=5 the tree has at most 32 leaves
and 31 internal nodes. Invalid widths reject before enumeration.

Sparse toggle charges one equality per examined label and
returns the resulting support list. Combine and sum recursively
accumulate actual toggle charges. The corresponding additive
budgets use intermediate support lengths, not the numeric
variable bound. RHS metering charges one Boolean XOR per block;
the terminal empty-support comparison adds one charge. The
outer block fold counts all block visits. Algebra may still
run in the eager meter for a rejected block. The production
checker is unchanged.

Twenty candidate declarations prove value correspondence and
selected additive bounds for generic folds, local patterns,
pattern trees, block checks, sparse toggle, combine, sum,
RHS sum and complete XOR terminal. The pattern count bound
above is analytical, not a new kernel theorem about 2^k.
Likewise if U counts all support occurrences, intermediate
support lengths are at most U and the selected toggle charge
is at most U^2 analytically; the formal budget is recursive.
Counts exclude construction, lengths, allocation, arithmetic
bit costs, closure invocation and parser costs. No total
runtime or exact short-circuit trace theorem is asserted.

## Validation

A separate workflow uses Lean 4.14.0, warnings as errors,
exact zero-axiom gates and static fixture runner on the
53 existing data pairs, selecting 21 XOR terminal cases
(18 prior XOR, two augmented controls and one invalid range).
Six hand controls check toggle cancellation/insertion, combine,
binary enumeration, wrong-pattern reference scans and width guard.
Local terminal acceptance is not envelope acceptance.
Required marker F034_XOR_METER_OK cases=21 hand_controls=6.
The new CI is pending; no local Lean. Prior gates unchanged.
The local fold definitions deliberately duplicate the pending
capacity-meter fold interface so there is no unverified dependency;
unify them only after both CI results are confirmed.

Next: reconcile the two metering branches once both pass,
compose a unified typed meter and derive a formal polynomial
bound in encoded structural size for the selected charges.
No machine refinement, independent review, unrestricted SAT
result or main change.
