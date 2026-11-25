# PNP-F034 — Selected binary iterator dispatch ledger

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 559b23059055305548a820386f89fd94ae5c99da (PR #200, includes #199).
Independent of open PR #201 (fuel-free nested decoder composition;
exact preflight 45533834634 passed). The meter follows the verified
iterWord control structure and charges one per base invocation and
one per doubled-transition wrapper invocation, with early failure.
Projection must equal the unmetered iterator on arbitrary optional
state transitions. For a uniform step-cost potential cost+1 <= K,
doubling yields potential <= K+K; iterating a word b costs at most
K*value(b). Unit base dispatch gives at most 2*value(b), hence at
most 200000 selected dispatches for a checked 17-bit list count
within the actual 100000 list limit. This includes rejecting runs.
Successful exact count 2*n-popcount is tested, not yet proved.
No claim about compiler function calls, closure construction, word
traversal, allocation, memory, parser transition work or total cost.
No production substitution. Seven candidate declarations; 2044
small controls and eight 17-bit boundaries. Marker F034_ITERATOR_DISPATCH_OK small=2044 boundary=8.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Exact-SHA replay required before PR.
Independent review and PNP resolution remain open.

## Initial replay and repair

Exact head f52600c57b1b4701e2559d9596d32e3429a86014 failed
[45534754083 / job 138938498919](https://github.com/tltmgnt/MathOS/actions/runs/45534754083/job/138938498919), artifact 14987315560.
Three elaboration errors: two projection branches retained an unreduced
let-bound match, and one potential rearrangement left an unsolved
commutation goal. Dispatch-bound declarations also printed propext
in addition to sorryAx. Replace the projection goal by its explicit
match, use typed associativity/commutativity equalities for potential,
and prove double_scale by structural induction instead of invoking
Nat.mul_assoc (a possible source of the unwanted dependency).
No executable definitions, theorem statements, controls, warning or
axiom gates changed. New exact SHA must pass replay, including the
strict axiom gate; no verification claim yet. PR #201 has merged at
 a60279a027a777996ca7f2eb5d60c27b0eaadbac.
