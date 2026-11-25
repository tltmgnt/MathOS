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

## Replay failures and constructive reset-width repair

PR #210 merged at b0a977330d53a00f490f84a951922db0f0b07567.
Initial exact head 636f009ee0fa9179a4dd193380ed7b5cb0520e51 failed
[45545446115 / job 138973833528](https://github.com/tltmgnt/MathOS/actions/runs/45545446115/job/138973833528), artifact 14990414167,
on concrete reset-width elaboration recursion limits. Eight of ten
named declarations printed no axioms. An intervening commit
27736f6ce329a430f6aa7f7d652d99731f55c6a0 replaced concrete decide with symbolic List.length_replicate;
[45545843589 / job 138975137428](https://github.com/tltmgnt/MathOS/actions/runs/45545843589/job/138975137428), artifact 14991637193,
reported two unfinished reflexive inequalities and propext/sorryAx
on the two dependent bounds. Retain the intervening change's symbolic
approach but prove replicate length by structural induction locally,
and finish both inequalities with explicit Nat.le_refl. No increase
in recursion limit, no new axioms, no changed theorem statements,
executable definitions, fixtures or strict gates. Require exact-SHA
successful replay; neither failed run reached the executable marker.
