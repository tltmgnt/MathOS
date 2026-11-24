# PNP-F034 — Polynomial selected sub-budgets

PNP_RESOLUTION_STATUS = OPEN. PR #177 merged at
fba934db02d5d563805f53f85f8de2fb672774f9. Initial CI run
45501724674 job 138826456298 failed:
artifacts/pnp-f030/f034-unified-meter-combined.lean:2848:8: error: unsolved goals
artifacts/pnp-f030/f034-unified-meter-combined.lean:2935:6: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-unified-meter-combined.lean:2935:47: error: invalid field notation, type is not of the form (C ...) where C is a constant
artifacts/pnp-f030/f034-unified-meter-combined.lean:2985:6: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Repository correction ceee99cef0211a1a8a1a5180cad2fa7caec84820
used explicit intermediate equalities and Boolean reflexivity.
Final CI 45502454422 job 138828959220 passed all 22 zero-axiom
declarations, 53 fixtures (19 accepted, 34 rejected) and four
hand controls. Actual aggregate selected count 1771562; additive
budget 2883685. Artifact 14972845240.
https://github.com/tltmgnt/MathOS/actions/runs/45501724674/job/138826456298
https://github.com/tltmgnt/MathOS/actions/runs/45502454422/job/138828959220

## New candidate polynomial inequalities

Rather than promote the previous analytical quartic estimate to
a formal claim, prove intermediate results against the existing
recursive budgets without replacing the actual meters.

* Uniform traversal: visitsBudget q xs <= length(xs)*(L+1)
  if each callback budget is at most L.
* Ordered-word traversal: wordsBudget <= W(g,k,L) for a leaf
  budget <= L on every word of length k. W(g,0,L)=L and
  W(g,k+1,L)=g*(W(g,k,L)+1). At k=3 this is
  g*(g*(g*(L+1)+1)+1). This is conditional on the leaf bound;
  it does not yet bound the complete capacity terminal.
* Sparse cancellation: U=sum of support occurrences. Prove
  intermediate support lengths, combineBudget <= |a|*B when
  |a|+|b|<=B, then sumBudget <= U^2 and the actual selected
  sumMeter charge <= U^2. No assumption of unique labels,
  valid blocks or valid certificate required.
* Chain: formulaMass counts row cells plus literal occurrences.
  chainMass B sums formulaMass over the initial formula and
  each batch's explicit tail frontier (including final frontier).
  chainSteps <= B by a strengthened induction. Each parent
  budget <= B+B*(B+1); the two-parent step budget is twice
  that. Summing over the chain yields the candidate unconditional
  chainMeter charge <= B*(2*(B+B*(B+1))) = 2B^3+4B^2.
  Empty batches need not contribute to B because this selected
  model charges neither batch dispatch nor empty traversal overhead.

21 candidate declarations, including actual meter inequalities.
The structural sizes B and U count encoded objects, not the
numeric variable bound. A formal inequality relating them to
the natural-token count of encExpected/encEnvelope remains to
be established. The previous analytical global quartic estimate
is not yet a kernel-proved global bound: remaining obligations
include capacity leaf budgets, aggregation over groups, complete
XOR blocks, binding/range costs, and unified encoded size.
No total machine-time, parser, allocator or bit-cost assertion.

## Validation

Static data runner tests all 53 existing chain budgets and
21 XOR sum budgets against the proposed closed bounds, plus
a hand-count ordered-word control (g=4,k=3,L=2 gives 212).
Exact marker F034_POLYNOMIAL_METER_OK chains=53 xor_sums=21 word_controls=1.
Strict Lean 4.14.0 zero-axiom gates added; previous gates
unchanged. New results pending CI, no local Lean.
No independent review, original scratch port, unrestricted SAT
result or main change. Next: formal capacity leaf and aggregate
bounds and complete XOR-block bound, then unified size bridge.

## First polynomial CI correction

Initial run 45503601628 job 138832955813 failed on seven
proof obligations. Representative exact errors:
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3112:11: error: type mismatch
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3223:11: error: tactic 'rfl' failed, the left-hand side
artifacts/pnp-f030/f034-polynomial-meter-combined.lean:3264:8: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
https://github.com/tltmgnt/MathOS/actions/runs/45503601628/job/138832955813
Base cases now use natural zero lower bounds rather than
definitional zero multiplication; parent case reduces its match
before rewriting. Local constructive multiplication identities
and monotonicity replace library lemmas to avoid axiom dependencies.
The corrected declarations still await strict CI; no gate relaxed.
