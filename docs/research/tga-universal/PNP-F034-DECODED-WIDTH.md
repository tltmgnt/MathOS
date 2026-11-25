# PNP-F034 — Decoded explicit numeric field width

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged scanner resource PR #223
(0a405ad4376a9866e19d2ed12f9420bc6b106c03). Independent of the
pending binary reference and checker padding/encoder candidates.

Verified dependencies already establish exact token consumption and
a 512-bit ceiling for every successful decimal token. The new
candidate lifts those facts through the existing encoders, by
constructive list membership and append projections, to prove
representability of every explicitly decoded numeric operand:
variable bounds and all original literals; replay left/right
references, pivots and tails; capacity demand/conflict references,
group literals and capacities; XOR supports and reference rows.
The original and fuel-free decoders are covered. Boolean flags
are already Boolean. Structural tags and list counts remain covered
by the token-level bound.

This is a statement about successful decoding, not proof acceptance,
not a bound on values produced later by checker arithmetic, and not
a certificate existence or certificate-size theorem.

Twenty candidate declarations and 18 executable control groups
(6 expected, 8 envelope, 4 token), including successful 128-digit
operands in nested proof fields and rejection of 129-digit values.
Marker F034_DECODED_WIDTH_OK expected=6 envelope=8 tokens=4.
Strict Lean 4.14.0 warnings-as-errors, exact marker and explicit
zero-axiom checks for all 20 declarations. No local Lean execution.
Fresh exact-head replay required before PR; independent review open.
