# PNP-F034 — Checked binary scanner gate reservation

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base f428f206eafefee3ef3b2136879eb1e17dfa9cdb (PR #209). Independent of open
PR #210 (combined mixed abstract byte ledger, exact preflight
45544266649 / job 138969961483 / artifact 14990677891 passed).

Instrument the actual binary scanCore control with arithmetic circuit
reservations. Every visited digit-classified byte reserves both
comparison and addition circuits of the eight-bit counter (<=80)
and both decimal accumulator additions at width 512 (<=5155).
Reservation may include skipped operations on a rejecting guard,
including the leading-zero check; this is deliberately conservative.
Each successful update preserves the required word widths, proved
using narrow_sound and bump_sound, so the entire scan reserve is
<=5235*byte length on all inputs. Projection to scanCounted, then
tokenizeBounded and the original tokenizer. Byte prepass does not
contribute to this gate reservation; its separate checked decrement
visit bound already exists. No claim of actual gate count on skipped
branches or of a complete bit-machine. Encoding, narrowing, zero
tests, byte tests, prepass visits, shifts/routing, Nat projection,
reversal, storage and allocation remain uncharged.

Ten candidate declarations; 795 executable controls (781 short words,
8 boundaries, 6 exact reservation checks). Marker F034_BINARY_SCANNER_GATES_OK small=781 boundary=8 exact=6.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate unchanged.
No local Lean execution; exact preflight required before PR.
Independent review and resolution remain open.
