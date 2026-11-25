# PNP-F035/F038 — Unbounded canonical wire completeness

PNP_RESOLUTION_STATUS = OPEN.

Candidate on envelope repair head 4fd3a57c03bf081e586c21307725dc2c0faea314.
Ordinary typed completeness independently passed all 19 zero-axiom
checks and 24 control groups at 83ca79f4fe5d89e23230a93226ad2a29e87678c6
(run 45636804423 job 139284339536, PR #240). Envelope completeness
initial run reported 16/19 zero-axiom declarations, with one root
rewrite error and two dependent failures; the positive-copy-pivot
repair uses Nat.succ_le_of_lt and needs fresh verification.

The new candidate constructs canonical ASCII decimal words using
division and remainder by ten, with structural fuel n+1. The Word
relation enforces a nonempty digit sequence, correct accumulated value
and no redundant leading zero. Appending one digit to a nonzero
completed prefix preserves the relation. Induction on fuel proves
arbitrary Nat digit correctness; induction over the token list proves
scan_encode and tokenize_encode. LF terminates every word.

The resulting expectedBytes and envelopeBytes constructors have
candidate exact roundtrip theorems for every typed expected formula
and envelope. The byte checker on canonical encodings equals the
typed boundCheck. Combined with input-bound envelope completeness,
for validFormula n f = true, there exists a finite accepted byte
certificate for the canonical encoding of f iff f is UNSAT.
The reverse implication uses existing unbounded byte soundness and
exact expected-input decoding.

This is ordinary serialized completeness, not polynomially bounded
proof size or discovery. Finite splitting may be exponential.
Structural fuel is not a bit-cost analysis, and the decimal encoder
is not yet proved polynomial in the encoded integer length. Neither
the old fixed-width resource bounds nor malformed-input cost bounds
are inherited automatically. No universal resolution claim.

12 candidate declarations, 1029 control groups (24 inherited
formula/envelope fixtures, 1004 decimal words including 129-, 257-
and 309-digit cases, one combined stream). Exact marker:
F035_UNBOUNDED_WIRE_OK pairs=16 singles=4 empty=2 sparse=1 zero=1 words=1004 stream=1.
Strict Lean 4.14.0, warnings as errors and explicit zero-axiom audit.
Main unchanged. Fresh exact-head CI required.
