# PNP-F034 — Reusable amortized parser contract

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 9af7c618d8eeb467c3ee7d0d6a4a990b202b72af (PR #206). Four files copied byte-identically
from verified PR #207 head 3753b09b809a67dea0f7fea65b318a9b7cda2153, exact preflight 45540672200/job
138958115532/artifact 14989710918, seven zero-axiom declarations and 1131
controls. Do not open next PR until #207 merges and new exact replay passes.

Use potential 64*remaining tokens. Success requires selected cost+2
plus remaining potential <= initial potential; failure requires
selected cost+2 <= initial potential+3. The two reserved units pay the
base transition and its doubling potential. The verified iterator
success theorem preserves residual potential; overhead <=35 for the
17-bit list count. A header pays the 35 overhead, one header attempt
and two reserved units (38<=64). On rejection the verified iterator
bound adds 3+17+35=55; the header potential covers this and the list
header/reserved units with slack. Thus the identical contract is
closed under listMeter, with no multiplicative list-limit factor.
Nested Nat lists have candidate uniform-in-depth linear bound
64*input.length+3 (selected events; not a claim for arbitrary
recursive grammar). This stage establishes reusable list closure;
sequential/conditional grammar closure remains. Costs of actual
allocation, encoding, reversal, Nat comparison and complete machine
execution still excluded.

Eight candidate declarations; 1142 control cases: 1122 small,
12 nested and 8 boundaries. Marker F034_AMORTIZED_PARSER_OK small=1122 nested=12 boundary=8.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution. Independent review and resolution remain open.
