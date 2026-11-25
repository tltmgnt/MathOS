# PNP-F034 — Checked binary representation and scanner accumulator

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on verified merged research base 41a181566e692a35c64fad5a433b57afcf51cf85 (PR #191).
The four binary-primitives files are copied byte-for-byte from exact
head 9fd2fef7a0ec3badae645f5dbe8c464007c6dec5, whose strict preflight passed
[45525367117 / job 138907240232](https://github.com/tltmgnt/MathOS/actions/runs/45525367117/job/138907240232)
with 14 zero-axiom declarations and 4486 controls. PR #192 is open,
not presumed merged. Do not open a new PR until #192 is merged and
the exact new head passes mandatory preflight.

Candidate semantics: little-endian fixed-width lists, checked
Nat-to-binary quotient conversion, zero-padding for short inputs,
and explicit rejection of nonzero discarded high bits. Soundness and
completeness are separate theorems, not a modulo-truncation contract.
Use recursive capacity cap(0)=1, cap(w+1)=2*cap(w). A candidate
bridge identifies cap(w)=2^w. The admissible scanner step uses
the prior decimal invariant to show that its retained-carry output
fits into exactly 512 bits after checked narrowing. A general
512-bit input need not fit after multiplication by ten.

Candidate scanBits uses the checked accumulator and a Boolean
zero test for redundant leading zero; byte classification,
digit counters, byte-limit check, Nat token projection and
list reversal remain outside bit-level cost accounting.
Candidate scan/tokenize equivalence covers rejection as well as
acceptance. No production change.

14 named declarations, strict warning and zero-axiom gates.
Candidate controls: 4608 encodes (width 0..8, n 0..511), 4599
narrowing cases (all representations of widths 0..8 against each
target width), five full-width controls and 13 scanner controls.
Marker F034_CHECKED_BINARY_SCANNER_OK encode=4608 narrow=4599 wide=5 scanner=13.
No local Lean execution available; all new statements and controls
await exact-SHA replay. No total cost, conversion cost, independent
review, proof discovery or unrestricted SAT claim.
