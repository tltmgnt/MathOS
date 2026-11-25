# PNP-F034 — Checker padding and encoder resource accounting

PNP_RESOLUTION_STATUS = OPEN.

Independent candidate based on merged padding PR #222
(257e94f5355deabf5f8ad8a70333563ca27c8788). Does not depend on pending
binary reference validation or scanner composition PR #223.

Substitute the metered column constructor for both borrow circuits
of equality and identifier range testing. Substitute the metered
encoder at the Nat boundary. Preserve the entire existing
(optional Boolean, gate count) pair, including rejection.

For requested width w, equality has selected resources bounded by
(10*w+3, 2*w, 2*budget(w)), and identifier range testing by
(10*w+2, 2*w, 2*budget(w)). Coordinates are Boolean gates,
padding construction visits, and selected encoder events.
Encoder budget is the previously verified recurrence
budget(0)=1; budget(w+1)=budget(w)+(w+2)+w.
Both operand encoder costs are included even if either is rejected.
Gate and padding counts are zero on failed encoding; successful
result correctness still requires representability of both operands.

Thirteen candidate declarations and 2622 executable control groups
(961 raw pairs, 1641 checked adapters, 16 wide pairs, 4 wide adapters).
Both-side failed encodings and width zero are covered.
Marker F034_CHECKER_PADDING_ENCODER_OK pairs=961 adapters=1641 wide=16 wideAdapters=4.

Strict Lean 4.14.0 warnings-as-errors, exact executable marker and
explicit zero-axiom checks for all thirteen named declarations.
Fresh exact-head replay required before PR. No local Lean execution.
No actual allocation, full bit complexity, whole-checker bound,
certificate-size guarantee or P vs NP resolution claimed.
