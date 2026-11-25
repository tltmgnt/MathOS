# PNP-F034 — Fuel-free binary parser iteration

PNP_RESOLUTION_STATUS = OPEN.

Start from verified merged research base 9662fc2772432f20ebcb4d11a36fff4fb9a8002f (PR #196).
Independent of PR #197 byte prepass and PR #198 parser-counter candidate
with explicit Nat recursion fuel. Both have passed exact-SHA preflight
but remain open at branch creation.

Alternative implementation: structurally recurse on a little-endian
word, doubling an optional state transition by composition after each
bit; execute it once for a set bit. No Nat recursion fuel or decoded
remaining counter is used in this iterator. The reference iterNat is
proof/specification only. Preserve failure propagation and order for
arbitrary optional state transitions, including parsers that do not
consume tokens. Reverse the accumulated list only at completion.
The boundary Nat list-limit guard and checked encoding remain.
Pointwise congruence enables nested parser substitution without funext.

Five candidate declarations and 2160 executable controls:
1533 generic iteration, 612 small lists, 6 malformed, 3 real list-limit
boundaries, 6 nested. Marker F034_FUEL_FREE_PARSER_OK words=1533 small=612 malformed=6 boundary=3 nested=6.
Strict Lean 4.14.0 warnings and zero-axiom gate unchanged.
No local Lean execution; exact-SHA replay required. This is a different
iteration architecture, not the decrement loop with a ghost fuel.
Closure construction, calls, allocation, memory, selected and full cost
composition still require proofs. No complete machine-cost or PNP claim.
