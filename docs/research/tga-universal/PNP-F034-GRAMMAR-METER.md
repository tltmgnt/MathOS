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

## Initial replay and boundary harness repair

PR #204 merged at f2d4061c8468c027e21eef56350aa79299858ada;
PR #205 merged at fd7580b3d8037547f4dc8ded96c84e94f9e38fdb.
Exact candidate 24c898d7d1cb4f6ae4ea00e497619c832a11afd6 failed
[45538838928 / job 138952058699](https://github.com/tltmgnt/MathOS/actions/runs/45538838928/job/138952058699), artifact 14988861026.
All 23 named declarations printed no axioms. The executable gate
failed in the non-tail-recursive reference serializer encItems on the
100000-row boundary fixture. Replace only the large-fixture comparison
with a tail-recursive, full structural check against independent
expected results for both metered and original parser outputs:
variable bound zero, exactly k empty rows, exact remainder [0] for
99999 and [] for 100000, rejection for 100001. Preserve the original
inputs, count, resource bound assertion, small fixture comparisons,
theorem source, strict warnings and zero-axiom gates. No stack limit
increase. New exact SHA must pass all controls before PR.
