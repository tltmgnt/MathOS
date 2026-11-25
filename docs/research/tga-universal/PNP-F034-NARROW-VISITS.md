# PNP-F034 — Checked narrowing structural visits

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base b0a977330d53a00f490f84a951922db0f0b07567 (PR #210). Independent of open
PR #211 (scanner arithmetic gate reservations, exact replay
45546413785 / job 138977004959 / artifact 14991698246 passed).

Meter zeroBits by one selected visit per inspected bit, with early
termination on true. Meter narrow by one visit per requested output
position (including padding), then the zero-test visits of the
remaining high bits. Result projection is exact even on rejection.
For input length <= w+extra, narrowing visits lie between w and
w+extra. Specialize to the checked decimal update (517 visits max)
and checked counter update (9 visits max, zero when guard rejects).
These are structural visit charges, not Boolean gate counts.
No claim of encoding cost, actual memory allocation, Nat projection,
byte classification, complete scanner composition or machine runtime.

Nine candidate declarations; 5917 executable controls (511 zero,
5110 narrow, 256 counter, 40 wide including decimal overflow).
Marker F034_NARROW_VISITS_OK zero=511 narrow=5110 counter=256 wide=40.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution; exact preflight required before PR.
Independent review and resolution remain open.
