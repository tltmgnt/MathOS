# PNP-F034 — Binary proof identifier range refinement

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged research head 03b9d7c80fb4f412df7227d2d59e09fe8da072e6.
Independent of pending chain, XOR and capacity refinements. Reuses verified
binary input binding, allGate composition, identifier checks and decoded
operand width. Covers all identifier occurrences checked by validProof:
step pivots and tails, demand/conflict reference rows, capacity group
literals, XOR supports and XOR reference rows. Does not add range checks
to reference/step indices or capacities, which retain their original roles.

The proposed proof meter projects exactly to validProof for representable
operands. A nested weight over the proof reserves (10*w+2) gates per
identifier occurrence, including each pivot. At w=512 this is 5122 per
occurrence. The weights count duplicates independently. The meter can
stop at failed list elements; the budget includes every occurrence.
This is a selected comparison gate ceiling, not total machine cost,
encoding, padding, allocation, Boolean combining or list traversal.

Decoded operand width discharges the proof range premises. The candidate
byte checker replaces original-input binding and proof range checks;
semantic chain and terminal checking remain original. The proposed exact
Boolean agreement and conditional UNSAT soundness theorems cover all
byte pairs, not certificate existence.

Twenty candidate declarations, 551 executable control groups:
96 steps, 288 terminals, 144 mixed proofs, 2 wide, 20 decoded pairs,
1 positive. Strict Lean 4.14.0 warnings-as-errors, exact marker
F034_BINARY_PROOF_RANGE_OK steps=96 terminals=288 mixed=144 wide=2 decoded=20 positive=1
and twenty zero-axiom checks. No local Lean execution. Fresh exact-head
verification required. Polynomial certificate completeness remains open.
