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

## Replay failures and targeted parser bridge repair

Initial head cbb738051736fcafb759895c3527a78df6168762 failed
[45530644979 / job 138924783750](https://github.com/tltmgnt/MathOS/actions/runs/45530644979/job/138924783750), artifact 14984436673.
Three elaboration errors: two unreduced nested matches in double_refines,
one recursive equation mismatch in nat_parser. No named zero-axiom
result or required executable marker was obtained.
Subsequent repository head 99abafce1e1203cf5d0e76d1be50b47058a3d247 corrected double_refines
and rewrote the recursive equations in nat_parser. It failed
[45531074276 / job 138926224059](https://github.com/tltmgnt/MathOS/actions/runs/45531074276/job/138926224059), artifact 14985226639.
Both double_refines and word_refines now print no axioms. A single
remaining error in nat_parser arises from unfolding advance globally,
including the transition passed to iterNat. The three dependent named
parser declarations report sorryAx transitively. Marker not reached.
The new correction keeps advance folded in the recursive transition,
proves its current-state result separately by cases on p ts, and uses
the induction hypothesis directly. No executable definitions, public
contracts, fixtures or strict gates changed. Exact new SHA needs replay.
PR #197 merged at 0683d7bbb680275be636776e20845e13e88bbb09;
PR #198 merged at cc33fe0873b0511b5d9d4f7ff32511baf3613848.
