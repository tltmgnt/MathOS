# PNP-F034 — Checked byte-length prepass

PNP_RESOLUTION_STATUS = OPEN.

Verified merged research base b3ea6b188b5635d4678d1a148976c54cf2c995f0 (PR #195).
Four scanner-counter files copied unchanged from exact verified head
b6bf1bbe19fff213dd957f5179bf4fad946f4b5c; [45528514794 / job 138917713849](https://github.com/tltmgnt/MathOS/actions/runs/45528514794/job/138917713849)
passed 8 zero-axiom declarations and 1045 controls. PR #196 open;
do not open this next PR until #196 merges and exact head replay passes.

The prepass starts with a static 20-bit remaining byte budget of
1000000. For each list cell, perform checked decrement, stopping
on underflow. Empty suffix succeeds even at zero budget. This is
tail recursive, rejects on the 1000001st byte, and does not compute
Nat length in the executable guard. Candidate equivalence is for
all lists, including malformed and over-limit byte inputs.
Composition replaces the Nat length guard of tokenizeCounted.

The selected decrement-bit visit ledger has candidate bounds
20*length and 20*(byteLimit+1), including the rejecting decrement.
No allocation, list-cell access, branching, accumulator arithmetic,
token conversion, parser loop or machine-cost theorem. The visit
specification is recursive and not run on the million-cell fixtures.

11 named declarations, 5715 exhaustive small guard cases,
six real byte-limit cases and ten tokenizer composition controls.
Marker F034_BYTE_PREPASS_OK small=5715 large=6 scanner=10.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
All new proofs await replay; no local Lean verification or resolution.
