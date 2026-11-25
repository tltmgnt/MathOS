# PNP-F034 — Exact successful iterator ledger

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base e755ef757c69dc2e9a67f03274a52b0a77e370c9 (PR #203). Independent of pending
compositional parser meter candidate cac0acc36aee9efcd5b14e3578048e65c8e8daf7.
The joint ledger already has verified rejecting-run upper bounds and
exact structural overhead on success. Close the gap between tested
and proved dispatch counts. For a metered transition whose successful
invocations all have cost+1=K, a successful doubled invocation has
cost+1=2K. A successful word run has dispatch+popcount=K*value.
For unit base charges the joint selected cost plus popcount equals
2*value+2*width+1. A successful checked 17-bit count has selected
cost+popcount=2*k+35 (iterator only, excludes list header).
No subtraction in the statement. Failure remains covered by prior
upper bounds, not this equality. No actual machine, allocation,
list reversal or transition work accounting. Five candidate
declarations; 2044 small and eight 17-bit boundary controls.
Marker F034_ITERATOR_EXACT_OK small=2044 boundary=8.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution; exact replay required before PR.
Independent review and resolution remain open.
