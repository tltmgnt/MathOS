# PNP-F032 — Formal local parity and elimination bridge

PNP_RESOLUTION_STATUS = OPEN. PR #151 merged into the bit-cost research
branch at e685a301bff10bea0641ade7beb535f6e4b1cee1. CI run 45444713969,
job 138625170319, passed six BVE tests and 1500 random projection
comparisons: 1067 certified UNSAT, 433 UNKNOWN, 431 brute-force SAT
(two undetected UNSAT). All twelve hidden odd-charge fixtures were
recovered with the supplied auxiliary schedule; all corresponding
even-charge and zero-pair-budget controls returned UNKNOWN.
At 80 vertices both seeds had 440 variables, 640 hidden clauses,
zero directly recognized parity rows, 80 recovered rows and 320
resolution-pair tests/derived lines. Evidence artifact 14945667051.
https://github.com/tltmgnt/MathOS/actions/runs/45444713969/job/138625170319

## Candidate Lean declarations

The new module is replayed together with the unchanged F002 GF(2)
source. Its statements are local semantic theorems, not a proof of
Python refinement. The strict audit requires exact zero-axiom output
for all ten new declarations and the four inherited F002 gate names,
with Lean 4.14.0 and warnings as errors.

- resolution_sound: (v OR a) and (NOT v OR b) imply a OR b.
- all_true_or_false_member: constructive finite Boolean list dichotomy.
- projection_iff: for any finite lists of positive/negative clause-tail
  truth values under a fixed nonpivot assignment, the conjunction of
  every cross-resolvent holds exactly when a Boolean pivot value exists.
  Includes empty lists, hence pure pivots. Unaffected clauses can be
  conjoined on both sides; their truth does not depend on the pivot.
- clause_split_iff: the private-auxiliary clause splitting construction
  is existentially equivalent to the original clause.
- block_self and block_false_eq: the local clause represented by a
  forbidden Boolean pattern is false exactly on that pattern.
- parity_block_iff: a complete, sound list of forbidden patterns of
  the supplied support width is equivalent to the specified XOR parity.
- parity_select: parity of selected assignment coordinates equals the
  padded coefficient-list GF(2) dot product from F002.
- row_block_sound: completeness alone suffices to entail the affine row.
- parity_blocks_unsat: complete blocks and zero-coefficient, odd-RHS row
  sum rule out an assignment satisfying all those blocks and widths.
  Reuses ProctorGF2.certificate_sound rather than reimplementing GF(2).

The statements allow arbitrary finite local widths; the Python detector
uses only widths 1–5. Block semantics are defined over ordered Boolean
patterns; length mismatches evaluate true, and the soundness bridge
explicitly assumes selected support width. The extraction of ordered
patterns from signed sparse CNF, normalization and checking completeness,
construction of projection batches and deletion/deduplication,
and the transport from Python proof objects to these hypotheses are
not formally refined by these theorems. The projection theorem concerns
clause-tail truth values, not a concrete list-of-literals implementation.

## Acceptance

The prior BVE evidence is verified by actual CI, not extrapolated from
scratch data. New Lean declarations remain candidates until the pinned
kernel run and exact axiom gate succeed; no local Lean executable is
available. No independent review or total bit-machine refinement claimed.
Original six scratch modules remain unavailable. No change to main or
existing strict gates; a new gate is appended to the adaptive workflow.
Next: blind recovery experiments with shuffled sparse IDs and stronger
adversaries, then integrated certificate-routing audit. No global promotion.
