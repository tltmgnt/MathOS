# PNP-F034 — Checked decrement and visited-bit ledger

PNP_RESOLUTION_STATUS = OPEN.

Start from merged verified research base 9366af5b3ac91e3f353fd030584debba4d9ba14d (PR #193).
The structural counter increment candidate 391325011a90c60607d167c35244e97033d63fae
is still in preflight 45527557169 at branch creation. No dependency on
or copied files from that candidate.

Candidate decrement on little-endian Boolean lists: propagate a borrow
across low zero bits until the first one, clear that one, share the
remaining tail. Reject if no one is found (including the empty word).
Successful output preserves input width and satisfies value(out)+1=value(in).
Success iff value(in)>0; rejection iff zero. No modulo wraparound.
The meter counts one visited bit per nonempty recursive case. It is
bounded by input width, with equality for zero words (underflow).
This is a selected visit ledger, not a complete gate/bit-machine cost:
allocation, stack, result construction, tail access and routing remain
unaccounted. No parser integration or proof of all structural bounds yet.

Seven named candidate declarations. Controls: 511 all words of widths
0..8, 15 structural boundaries at widths 8,17,20, four 512-bit controls.
Marker F034_CHECKED_DECREMENT_OK small=511 boundaries=15 wide=4.
Strict Lean 4.14.0, warning-as-error and zero-axiom gate preserved.
No local Lean execution; candidate requires exact-SHA successful replay
before opening PR. No independent review or resolution claim.
