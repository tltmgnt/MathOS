# PNP-F034 — Binary accumulator value projection

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base ee03c935217ac0488fe35c0809164fcd9df224be (PR #217). Independent of pending
encoder-aware byte-checker candidate 6a43b49555c769b25b5a2b924a20e9870359e4a3.

Instrument the existing little-endian bitsValue recursion with one
bit traversal visit and two abstract Nat arithmetic events per bit
(multiplication by two and addition). Exact result projection and
selected event count 3*width; result value < cap width. Width <=512
implies <=1536 selected events per emission. Substitute valueMeter
at successful LF token emission in the checked binary scanner,
retaining emissions before subsequent rejection in the charge.
Candidate tokenization projection to original tokenizer and bound
1536*byte length on arbitrary byte inputs including malformed
ones. EOF/invalid bytes and skipped emissions have zero selected
value conversion charge. This is deliberately a coarse byte bound,
not a bound on actual Nat bit operations. BitVal evaluation,
arithmetic implementation, allocation, scanner reset/reversal and
other runtime costs remain outside this ledger. No production
substitution or total machine-cost claim.

Ten candidate declarations and 1310 executable controls (511 words,
4 wide, 781 scanner, 8 boundary, 6 exact). Marker F034_VALUE_PROJECTION_OK words=511 wide=4 scanner=781 boundary=8 exact=6.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Require exact preflight before PR.
Independent review and resolution remain open.
