# PNP-F034 — Round-depth boundary and set-normalized replay semantics

PNP_RESOLUTION_STATUS = OPEN. PR #162 merged at
f1153692d7ef2efd9bfa3c5e179536fe2b3dc541. Actual CI run 45468062622,
job 138708197686: six tests, 3000 budgeted runs (2101 UNSAT,
592 SAT, 307 UNKNOWN), all 12 mixed fixtures certified (PHP
through 32 holes, Tseitin through 80 vertices) with zero BVE
pairs and dynamic nodes. All five composition declarations
passed strict zero-axiom Lean 4.14.0. Artifact 14955906695.
https://github.com/tltmgnt/MathOS/actions/runs/45468062622/job/138708197686

## Round boundary

For each original clause C use every one of the 2^t sign
patterns on t shared fresh guards: C OR G_pattern. For any
assignment exactly one guard pattern is false; thus the
expanded formula is pointwise equivalent to the original.
The generator caps t at five and is exponential in t, not
a succinct reduction. For distinct original supports and
no same-support opposing-tail pairs in the original formula,
a full paired-resolution round removes exactly one guard
from each derived clause. After j<=t full rounds the frontier
contains C joined with every sign pattern on every subset of
t-j guards, for each original C. This follows by induction:
two equal-tail parents differ on one remaining guard only;
two different guard subsets cannot share an equal-tail pivot
pair. Distinct original supports preclude cross-clause
pairs. For the same-support Tseitin blocks, original sign
patterns differ in an even positive number of positions,
so no cross-original paired resolution occurs either.

This is a frontier-depth statement for the paired policy,
not a proof-complexity lower bound. The existing one-round
router also tests augmented scopes and other inference
engines; the new tests check their failure for specified
multi-guard PHP and Tseitin fixtures. No assertion that
all arbitrary guard encodings or all inference policies
require t rounds. No new universal lower bound claimed.

## Experimental bounded chained route

Keep existing F034 mixed router unchanged. New UNSAT-only
experiment applies its bounded paired derivation repeatedly
to the immediately preceding frontier, with global round,
signature and distinct-step limits. Attempt the same four
sound UNSAT engines at each new frontier. On exhaustion
return UNKNOWN unless an already-derived prefix yields a
checked refutation. A certificate contains a nonempty list
of parent-index batches and a final inner proof. Replay
each batch against the immediately preceding frontier and
check the inner proof; no solver/discovery required.
Derived SAT is never promoted. This is not a general
saturation policy: cross-frontier parent pairs are excluded.
Counters omit normalization, inference and checking costs.

## Formal bridge

The verified F034 paired_sound theorem used pivot-at-head
lists. New ProctorPairedReplay uses membership-based
ParentShape: every literal in a parent is either the pivot
or a member of the proposed tail. The other parent uses
the complementary pivot. This weaker sufficient condition
covers duplicate/reordered original clauses after set
normalization without requiring list equality. It proves
one-step soundness, batch entailment, finite chain entailment
and UNSAT lifting, using the prior signed literal conflict
theorem. Five new declarations are subject to strict Lean
4.14.0 zero-axiom CI. Actual Python index/normalization
replay is not formally refined: the transport to the
ParentShape premises remains to be established mechanically.

## Controls and scope

1200 arbitrary sparse formulas at three budget sets (3600
runs), eight guarded PHP and eight guarded Tseitin cases
at depths two and three; compare original one-round policy,
one-fewer-round budget and full-depth budget. Four equal
size SAT controls, exact single-clause frontier counts,
pointwise equivalence, budget and corrupt-parent/batch
tests. New outcomes await CI; no independent review,
machine transition theorem, original scratch port or main
change. Next: independently check actual executable
certificates against formal premises, and benchmark
structural depth and total cost without extrapolating
to unrestricted SAT.
