# PNP-F034 — Scanner padding and encoder resource composition

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged padding PR #222, commit
257e94f5355deabf5f8ad8a70333563ca27c8788. Independent of the repaired
binary reference candidate (c685fa34); no new reference dependency.

For B input bytes, retain the three existing scanner coordinates and
add two selected reservations:
- Boolean arithmetic gates <= 5235*B.
- Scanner zero/narrowing visits <= 1046*B+8.
- Byte prepass decrement visits <= 20*B.
- Padding construction visits <= 1047*B (1031 for decimal shift-add,
  8 for the counter comparison, 8 for the counter increment).
- Four-bit digit encoder selected events <= 21*B.

The extra ledgers use the existing scanner's branch structure and
reserve digit work even if a guard rejects before the operation.
They are independent resource observations, not a claim of one
instrumented execution, actual allocation, or total machine runtime.
The encoder counts abstract Nat operations and append visits; it does
not refine their bit complexity. Byte prepass remains a specification.
Output Nat projection, reset construction, list allocation and other
unmetered operations remain open. No polynomial certificate-size claim.

Eight candidate declarations with 795 executable control groups
(781 small, 8 boundary, 6 exact). Marker:
F034_SCANNER_PADDING_COMPOSE_OK small=781 boundary=8 exact=6

Strict Lean 4.14.0 warnings-as-errors, explicit zero-axiom checks for
all eight declarations and exact executable marker are required.
No local Lean execution, no fresh kernel evidence yet. Do not open
a PR until the exact-head preflight passes. Independent review open.
