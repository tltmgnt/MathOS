# PNP-F034 — Binary padding construction visits

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 5d5af78098c7918cf64db86e4aae1b6d70edc063 (PR #218). Independent of pending
value-projection, checker-binary-tests and binary-lookup replays.
Instrument the existing zero-padded column builder with one selected
construction visit per output column. Prove exact projection and
visit count equal to output column count; for two operands of width
<=w the count is <=w. Substitute the builder into the existing borrow
and ripple circuits. Preserve exact output and existing gate ledger,
and keep construction visits as a separate coordinate. Compare/add
candidate resource ceilings (5*w,w). For decimal shift-add with
accumulator width <=w and digit width <=4, candidate resource
ceilings (5*(w+3)+5*(w+4),(w+3)+(w+4)). At w=512: (5155,1031).
No cost for allocating a column, routing wires, executing Nat
arithmetic or full machine instructions is asserted. No production
substitution or total runtime claim.

Eleven candidate declarations and 3525 executable control groups
(961 pairs, 2560 decimal, 4 wide). Marker F034_PADDING_VISITS_OK pairs=961 decimal=2560 wide=4.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Exact preflight required before PR.
Independent review and resolution remain open.

## Initial replay repair

Exact head c5fed68a4396a7f39908f5311b3a8d6c86b99db6 failed [45556797014 / job 139010679709](https://github.com/tltmgnt/MathOS/actions/runs/45556797014/job/139010679709), artifact 14996317602. Nine independent declarations printed no axioms. decimal_projection rewrote both resource projections correctly but left a definitional equality against decimalMeter; close that residual goal with rfl. decimal_bounds depends on the repaired theorem. No public theorem statement, executable definition, fixture or gate changed. Initial executable marker not reached; require successful exact-head replay before PR.
