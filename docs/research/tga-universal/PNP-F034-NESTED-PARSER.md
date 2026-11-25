# PNP-F034 — Nested certificate parser substitution

PNP_RESOLUTION_STATUS = OPEN.

Start from verified merged research base cc33fe0873b0511b5d9d4f7ff32511baf3613848 (PR #198;
also contains #197). No dependency on the pending fuel-free candidate
c0079273a472b7875b9fa24af32ab7b7444c190c.

Abstract the list implementation by a pointwise refinement contract.
Substitute throughout clauses, formulas, referenced rows, groups,
capacity certificates, XOR blocks, proof steps, terminal variants,
batches, expected input and envelope. Specialize to the verified
17-bit checked list parser, then compose the verified binary byte
prepass and scanner. Candidate checkBytes equality preserves the
original soundness theorem for every pair of byte streams.
No production code change. Pointwise proofs avoid funext.

The concrete implementation retains explicit Nat recursion fuel,
Nat list-limit guard, Nat tokens and the original typed checker.
Fuel-free specialization can be added only after its independent
proof gate succeeds. No whole-machine cost theorem.

18 named candidate declarations and 117 executable controls:
8 expected decoders, 12 envelope decoders, 96 checker pairs, one
positive empty-clause control. Compare canonical encoded views for
typed decoder outputs, including none; check Boolean result directly.
Marker F034_NESTED_PARSER_OK expected=8 envelope=12 checker=96 positive=1.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution; all new claims await exact-SHA replay.
Independent review and PNP resolution remain open.
