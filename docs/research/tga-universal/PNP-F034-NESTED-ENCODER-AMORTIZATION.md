# PNP-F034 — Nested encoder amortization

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 6109ccc8c72f51bdbcdcc8682f3cfd828f9fbf3e (PR #214). Independent of pending
encoder-integration replay 45551505090 at 819bf3b4b7677934aab9d81f158c04ade880d481.

Lift the existing 64-token potential to 512 and keep the iterator's
two-unit success reserve and three-unit failure allowance. Define
chargedList as listMeter plus the actual selected 17-bit header
encoder event ledger when its list-limit guard passes. Empty header
has zero added charge. Success needs at most 35+3+307=345 of
the header's 512 units; rejection needs at most 55+307=362
plus the existing three-unit allowance. Thus candidate closure
under arbitrary finite nesting of charged lists, and nested Nat
list cost <=512*input.length+3. Projection to original nested
Nat parser is included. This is an accounting wrapper, not yet
the substituted encoder implementation from the pending integration
candidate; their pointwise equality and full grammar closure are
subsequent tasks. Selected mixed abstract events, not bit-machine
costs or full runtime. No production substitution.

Eleven candidate declarations and 1142 executable controls.
Marker F034_NESTED_ENCODER_AMORTIZATION_OK small=1122 nested=12 boundary=8. Strict Lean 4.14.0 warnings-as-errors and
zero-axiom gate unchanged. No local Lean execution. Exact preflight
required before PR. Independent review and resolution remain open.
