# PNP-F034 — Scanner digit counter integration

PNP_RESOLUTION_STATUS = OPEN.

Start from merged research base 3962227060ba877425aa21def239fe57fe2ccd83 (PR #194).
The decrement candidate passed preflight and is PR #195; this branch
does not depend on it.

Replace the scanner digit counter by an eight-bit little-endian word.
Use explicit zero detection and the verified guarded increment with
static limit word 128; no Nat conversion of the digit count in
the executable scanner. The decimal accumulator still uses checked
512-bit arithmetic. The generic proof abstracts reset and transition
operations, then specializes to the verified primitives. Candidate
tokenizer equality covers acceptance and rejection for arbitrary
List Nat, not just valid wire inputs. The byte-length prepass remains
Nat-based; byte classification and token projection also remain Nat.

Candidate local selected comparison-plus-addition ledger <=80 gates
per attempted digit counter increment on words of length <=8. This
is not a bound for the complete scanner, zero detection, narrowing,
allocation or conversion. No change to production parser.

Eight named declarations; 256 counter inputs, 781 short words
(lengths 0..4 over LF, 0, 1, 9, invalid 58), eight boundary controls.
Marker F034_SCANNER_COUNTERS_OK counter=256 short=781 boundary=8.
Strict Lean 4.14.0, warning-as-error and zero-axiom gate unchanged.
All new proofs await exact-SHA replay; no local Lean verification.
Complete cost, parser loop refinement, independent review and PNP
resolution remain open.
