# PNP-F034 — Complete encoder-aware grammar

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base d7cc6fb7f34ac1a88b311e2c55c0ca9b48bde19f (PR #215). Its exact preflight
45551676519/job 138994059868/artifact 14994637360 passed 11
zero-axiom declarations and 1142 controls. Independent of pending
encoder-integration replay 45552942447 at 3e590eb984d6c12c2f8708aa9c7c9ce64bc53894.

Reuse the existing generated complete token grammar and replace each
listMeter application with chargedList, including every nested list
in formulas, references, capacity certificates, XOR blocks and proof
batches. Pointwise original-parser equivalence follows from the
existing sequence and choice projections and charged list projection.
Uniform contracts additionally reserve 307 events per header.
The reusable 512-unit amortized token potential closes under all
grammar constructions: expected and envelope parsers each cost at
most 512*input.length+3, on arbitrary token streams. The accounting
wrapper still uses the original list parser plus a separate encoder
event calculation; equivalence to substituted encoder implementation
is a separate pending stage. No actual Nat bit-cost, allocation,
production substitution or complete machine-cost claim.

43 candidate declarations and 131 executable potential controls
(8 expected, 12 envelope, 3 boundary, 108 short).
Marker F034_ENCODER_GRAMMAR_OK expected=8 envelope=12 boundary=3 short=108. Strict Lean 4.14.0 warnings-as-errors and
zero-axiom gates unchanged. No local Lean execution. Require exact
preflight before PR. Independent review and resolution remain open.
