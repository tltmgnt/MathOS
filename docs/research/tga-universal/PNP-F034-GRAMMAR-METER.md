# PNP-F034 — Complete token grammar selected meter

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base e755ef757c69dc2e9a67f03274a52b0a77e370c9 (PR #203). Four files copied byte-identically
from verified PR #204 head cac0acc36aee9efcd5b14e3578048e65c8e8daf7, exact preflight 45537358211/job
138947129693/artifact 14988016098, 11 zero-axiom declarations and 633
controls. Do not open this PR until #204 merges and exact replay passes.
PR #205 (exact iterator counts) independent, not required.

Contract packages pointwise equality and uniform selected resource bound.
Compose sequentially, through fuel-free list iteration and through
conditional grammar alternatives. Alternative budgets sum rather than
take max; pure constructors/rejection cost zero, Nat/Bool token attempts
cost one each, and nested list costs use verified listBudget. Cover
literal, clause, formula, reference, group, capacity, block, step,
terminal variants, proof batches, expected and envelope token parsers.
Candidate equality includes remainder and failure on arbitrary tokens.
Uniform bounds are deliberately loose, not input-length-sensitive.
No separate cost for conditional comparisons, constructor, binding,
reversal, boundary encoding, tokenizer, final remainder check, typed
checker, allocation or runtime; no whole-machine cost claim.

23 candidate declarations; 25 control cases: 8 expected, 12 envelope,
3 actual list-limit boundaries, 2 exact empty-grammar counts.
Marker F034_GRAMMAR_METER_OK expected=8 envelope=12 boundary=3 exact=2.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Independent review and resolution remain open.
