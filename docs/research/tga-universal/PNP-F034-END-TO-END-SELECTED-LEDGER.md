# PNP-F034 — End-to-end selected resource ledger

PNP_RESOLUTION_STATUS = OPEN.

Separate integration branch from verified unified checker ledger head
fcc7c685bac71589c2ac83353e1514196056e7c5 (PR #236), incorporating
the exact repaired front-end ledger head
2ec90467652972fe26a459f750194c4274526d03. Front-end replay was pending
at integration time. PR #235 separately carries the verified capacity ledger.

Eight candidate declarations compose the two decoder results and
checker meter into one Bool result and nine selected resource
coordinates. Proposed exact byte acceptance equals the original
checker, with inherited conditional UNSAT soundness. Rejected
decoding retains the front-end reservation and zero checker reservation.

Let B be the sum of input and envelope byte lengths. Front-end
coordinate ceilings are (5235*B,1046*B+16,20*B,1047*B,21*B,1536*B,64*B+6).
Checker coordinates retain the verified recursive data-dependent
lookup and comparison budgets; no closed byte-length polynomial for
these two coordinates is established by this composition.

Independent conservative reservations are not a single execution trace.
The grammar meter and hoisted demand lookups are alternative projected
implementations. Abstract emission events do not establish constant
bit cost. Structural traversal, allocation, additional encoding,
arithmetic and other machine costs remain outside this ledger.
No total machine-cost refinement or certificate completeness claim.

Strict Lean 4.14.0, eight explicit zero-axiom checks and 218 control
groups (196 cross-pairs testing result and all nine coordinates,
6 positive and 5 negative fixtures, 11 typed checker ledgers).
F034_END_TO_END_SELECTED_LEDGER_OK pairs=196 positive=6 negative=5 ledgers=11.
Fresh exact-head replay required before PR.
