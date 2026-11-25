# PNP-F034 — Compositional selected parser resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 6135f07bd8b524e34b80366a966bb41a1c979dff (PR #202). Four files copied byte-identically
from verified PR #203 head dd43a116db6675b8d008955e643dc64d3354cfd5, exact preflight 45536750594/job
138945118070/artifact 14987074520, six zero-axiom declarations and
2052 controls. Do not open next PR until #203 merges and new exact
candidate replay passes.

Generic metered parsers return an optional parsed value and remainder
plus selected charges, also on failure. Sequential composition adds
child charges with short-circuit rejection. Metered list base transition
includes the child cost plus one dispatch; the verified joint iterator
ledger propagates these costs through doubled transitions and structural
overhead. Charge one per list header attempt, including missing/invalid
headers. Projection targets actual fuel-free list parsing and then the
original list parser. If each child invocation costs <= B, a permitted
list call costs <= (B+2)*k+36, hence <= listBudget B =
(B+2)*100000+36. This coarse uniform bound is compositional, includes
failed children and does not imply logarithmic parsing. Two nested
Nat lists illustrate the bound listBudget (listBudget 1) = 30003800036.
This is deliberately loose and not an input-length-sensitive bound.
No complete nested certificate grammar meter yet; no guard/encode bit
cost, list reversal, constructor/bind or allocation cost (beyond
selected charges), actual compiler/runtime, total cost or PNP claim.

11 candidate declarations and 633 control cases: 612 small list,
6 malformed, 3 actual boundary, 6 nested with explicit reference
totals [36,73,118,54,4,111], 6 sequential. Marker F034_PARSER_METER_COMPOSE_OK small=612 malformed=6 boundary=3 nested=6 sequence=6.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution; independent review remains outstanding.
