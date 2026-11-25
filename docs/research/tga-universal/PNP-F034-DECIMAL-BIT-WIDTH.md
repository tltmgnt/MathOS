# PNP-F034 — Decimal operand width and explicit Boolean addition primitive

PNP_RESOLUTION_STATUS = OPEN. End-to-end raw-pair candidate
8d22b6783a424243eaeeb8eca1ec495a914b0a8f passed exact-SHA
preflight 45523299397 job 138900306419 on the first attempt:
12 zero-axiom declarations, 67 custom pairs (19 accepts),
73 DIMACS pairs (22 accepts), eight hand controls.
Selected ledgers custom=3520120 DIMACS=3945528.
Artifact 14980772222. PR #190 opened only after preflight.
It remains unmerged at the creation of this independent branch.
Base is verified merged decoder PR #189,
01dd948ed45394ef4d1ea609124158e65f53d603.
No reliance on end-to-end candidate files.
https://github.com/tltmgnt/MathOS/actions/runs/45523299397/job/138900306419
https://github.com/tltmgnt/MathOS/pull/190

## Candidate first bit-level layer

Define radix(0)=1 and radix(k+1)=16*radix(k). For each valid
decimal digit, invariant v+1<=radix(k) implies
10*v+(b-48)+1<=radix(k+1), using b<=57.
The actual scanner additionally checks b>=48, leading-zero
and digit-count restrictions; the inequality uses a weaker
hypothesis. Word grammar induction and Wire grammar lift the
local invariant to every successfully tokenized natural.
The existing 128-digit guard implies v<16^128=2^512.
Natural and signed DIMACS word outputs inherit the same
magnitude bound. This is a width bound on decoded numbers
and the local accumulator transition, not a global bound on
all intermediate arithmetic values of the verifier.

A separate executable little-endian ripple adder over input
bit columns uses a full adder with two XOR, two AND and one
OR. Its ledger charges exactly five Boolean gate applications
per column, returns the final carry rather than discarding it,
and has candidate arithmetic value and length theorems.
At <=512 columns, <=2560 gate applications. The primitive
is not yet substituted for Lean Nat addition, does not
instrument actual machine instructions, and does not include
list construction, routing, memory, or conversion costs.
No connection between this gate ledger and the complete
selected-resource checker ledger is asserted yet.

13 candidate declarations, strict Lean 4.14.0 zero-axiom
gate. Existing 134 custom data files (127 lexical accepts,
7 rejects); 512 exhaustive four-bit addition/carry controls,
one 512-bit carry control and three decimal word boundaries.
Marker F034_DECIMAL_BIT_WIDTH_OK files=134 lexical_accept=127 lexical_reject=7 ripple=512 wide=1 word_controls=3.
Exact-SHA preflight required before PR, no local Lean.
No production or main change, no gate relaxation.

Next: explicit binary comparison and shift/add decimal
update, proof of representation/refinement of scanner operations,
then bounds on larger structural counters and checker
arithmetic. Complete parser control/reversal accounting,
allocation, machine/IO/compiler refinement and independent
review remain outstanding. No required proof-size or proof
discovery bound; no unrestricted SAT or P vs NP result.

## Initial preflight and correction

Exact candidate 2bf6604f3d59387c16cff2468d376fed820ad6dd
failed mandatory preflight 45523977318 job 138902598589,
exit 1, artifact 14981672372. Actual error headers:
```text
artifacts/f034-decimal-bit-width/combined.lean:7970:43: error: maximum recursion depth has been reached
artifacts/f034-decimal-bit-width/combined.lean:7996:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/f034-decimal-bit-width/combined.lean:8008:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
```
Eleven of thirteen declarations printed zero axioms, including
the digit invariant, wire/token bound and all ripple-adder
results. ceiling_bits and signed_width printed sorryAx
because of failed elaboration; no explicit sorry was added.
The run did not reach the fixture marker. The correction
replaces closed large-power decide with symbolic radix_pow
induction and reduces the cons match explicitly before
rewriting the sign condition. No theorem statement,
arithmetic implementation, fixture, recursion limit or
strict gate is changed. Corrected exact SHA requires replay.
PR #190 has merged at 4a2c3b20b05a9bf3b9fe85910d8008d4d32a5cc5.
https://github.com/tltmgnt/MathOS/actions/runs/45523977318/job/138902598589
