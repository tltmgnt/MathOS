# PNP-F034 — Checked structural counter primitives

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base f2d8f5722a97a0f981debdd8644a747cf64eaa76 (PR #192).
Copy four scanner files unchanged from exact head 241cab539339c994b1e4c4495182eb7e3879a1e0,
which passed [45527061220 / job 138912918806](https://github.com/tltmgnt/MathOS/actions/runs/45527061220/job/138912918806)
with 14 zero-axiom declarations and 9225 Lean controls.
Artifact 14983092135. PR #193 opened after preflight; do not open
this next PR until #193 merges and the exact new head passes replay.

Candidate counter capacities: digitLimit=128 < 2^8,
listLimit=100000 < 2^17, byteLimit=1000000 < 2^20.
These are inclusive representable limits, not claims about all
internal counters. An increment retains carry and uses checked
narrowing; a guarded increment accepts exactly below a representable
limit and preserves the exact value, with output <= limit.
An attempted guard and increment charges both Boolean circuits
as an upper bound: <=5w+5w for operands at most w bits, w>=1.
At 8, 17, 20 bits this is 80, 170, 200 gates respectively.
Encoding the limit, narrowing, allocation and memory are excluded.
No scanner counter substitution or whole length-pass refinement yet;
over-limit inputs and parser decrement require separate accounting.

14 candidate declarations, 510 increment controls, 1364 exhaustive
guard pairs (width 1..5), 15 structural-limit boundary controls.
Marker F034_STRUCTURAL_COUNTERS_OK increments=510 guards=1364 boundaries=15.
Strict Lean 4.14.0 warnings and zero-axiom gate unchanged.
New code awaits exact-SHA replay; no local Lean verification claimed.
No total machine-cost theorem, independent review or resolution claim.
