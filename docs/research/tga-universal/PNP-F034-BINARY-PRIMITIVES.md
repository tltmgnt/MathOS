# PNP-F034 — Unsigned comparison and decimal shift-add gate primitives

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 4a2c3b20b05a9bf3b9fe85910d8008d4d32a5cc5
contains end-to-end PR #190. Bit-width PR #191 exact head
f7a0ca95999615b92d5bd2ba6aa93c169234377a passed preflight
45524779172 job 138905293199, artifact 14980773718:
13 zero-axiom declarations, 134 raw files (127 lexical accepts,
7 rejects), 512 four-bit add/carry controls, one wide carry,
three word boundaries. Intermediate candidate 267c6704 failed
preflight 45524299852 job 138903681742, exit 1:
artifacts/f034-decimal-bit-width/combined.lean:7982:2: error: exponent 512 exceeds the threshold 256, exponentiation operation was not evaluated, use `set_option exponentiation.threshold <num>` to set a new threshold
'ProctorDecimalBitWidth.ceiling_bits' depends on axioms: [propext]
Repository correction replaced library power addition with
constructive equality induction and scoped exponentiation.threshold
512 at the theorem and runner. No strict gate changed; this is a
local elaboration/evaluation setting, not a new axiom. PR #191
opened after replay and was unmerged at this branch's creation.
This branch starts from the merged verified base and copies its
four exact preflight-verified bit-width files unchanged.
Do not open the new PR before #191 merges and exact-SHA replay passes.
https://github.com/tltmgnt/MathOS/actions/runs/45524779172/job/138905293199
https://github.com/tltmgnt/MathOS/actions/runs/45524299852/job/138903681742

## Candidate semantics

Little-endian unsigned bit lists, zero-padded to the longer
operand. The borrow circuit per column computes na=!a,
(na AND b) OR ((na OR b) AND carry). One NOT, two AND,
two OR, five Boolean gate applications. The final borrow
with initial false equals numeric strict less-than, using
a local radix-two arithmetic equivalence and induction.
Unequal widths and empty lists are included. Candidate
comparison cost <=5K for input lengths <=K.

Padded ripple addition reuses the verified full adder.
The numeric value of the sum is exact, with final carry
retained; no truncation. Output length <=K+1, gate cost <=5K.
The decimal update adds shifted v (one and three low zero
bits), then adds d. For numeric values V,D it gives
10V+D. With input length <=w and digit length <=4 the
untrimmed output length is <=w+5, gate count <=5(w+3)+5(w+4).
For w=512 this is 5155 gates, 517 output bits maximum.
The local digit theorem connects the update's value to the
scanner's invariant V+1<=radix(k) when D=b-48 and b<=57.
It does not prove fixed-width representation conversion or
fit of the untrimmed output into 512 bits. No wraparound.

All counts are gate ledgers; zero padding, shift wires,
routing, list construction, memory and conversion are
not counted. The circuits have not replaced production
Nat operations. No total bit-cost or runtime theorem.

14 candidate gated declarations. 961 exhaustive comparisons
and 961 additions for widths 0..4 independently, 2560
eight-bit decimal updates, four 512-bit boundary operations.
Marker F034_BINARY_PRIMITIVES_OK comparisons=961 additions=961 decimal=2560 wide=4.
Strict Lean 4.14.0 warning and zero-axiom gates, mandatory
preflight before PR; no local Lean. Main and production unchanged.
Next: binary representation conversion, trimming or checked
fixed-width fit, scanner refinement and counter width bounds.
Complete parser control/reversal and memory/IO/compiler
costs and independent review remain open. No proof-size,
discovery or unrestricted SAT claim.
