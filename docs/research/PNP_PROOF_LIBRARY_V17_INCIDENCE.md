# v17.10 — necessary signed incidence retrieval filters

## Basis

v17.8 evidence: https://github.com/tltmgnt/MathOS/actions/runs/46152616706.
Both gates retained 30 entries; the ungated 54-entry union added one
heldout refutation (24 vs 23 of 30 UNSAT) at roughly 65% extra ticks.
v17.9 memoization PR #313 was open and its evidence job queued at
inspection (run 46154141141). No outcome inferred. This is an
independent index experiment from main, not a successor requiring
memoization, and makes no default change.

## Necessary filter

Let K be the normalized known clauses, and w their minimum width.
For an injective signed map e, a guard g with |g|=w can only be
witnessed by a clause k in K satisfying k subset e(g) and |k|>=w.
Because |e(g)|=w, k=e(g). Distinct such guards have distinct
images. Consequently the count of tight guards cannot exceed the
count of minimum-width clauses in K.

For any pair of tight guards g,h, the signed injection preserves
both |g intersect h| and |g intersect (-h)|. It also injects distinct
unordered pairs into distinct unordered witness pairs. Thus the
histogram of those two counts for the tight guard set must be
componentwise bounded by the histogram for minimum-width target
clauses. Failure of either count condition excludes a match in
this context, not satisfiability or provability. These are
necessary conditions only; passing them does not establish a match.
When a stronger smaller-width premise becomes available, recompute
the tight width and target histogram. Never reuse a rejection after
a productive transfer. Pair histogram construction is skipped above
4096 pairs (not a rejection). Guard histograms are local to the
solver invocation. The filter assumes verified canonical templates
and normalized non-tautological known clauses, as in the existing
library. It does not establish a general graph isomorphism result.

## Evaluation

Same original v17 matcher, ordering, round/transfer limits and
certificate replay. Filter just before each match, not once at
the start of a round, because the known clauses can grow mid-round.
All filter ticks are charged. Count width, cardinality and pair
rejections, snapshot builds, cap skips, actual matcher calls and
filter work. A necessary condition cannot rule out an admissible
embedding, but finite budgets and additional overhead can alter
observed coverage. No speedup assumed. The cooperative cell cap
is not a hard process memory cap; guard cache and other allocations
are not fully accounted in bytes.

Rebuild v17.7 training-only base/expanded libraries. Four paired
arms: base/expanded x plain/indexed. 72 fresh instances, seed
171003, and 72 prior v17.9 instances (seed 17903) retrospective,
equally stratified binary, ternary and mixed widths. The v17.9
report is not used. Exact normalized input overlap checks, not
signed orbit disjointness or external blinding. Same per-arm 4M
ticks, 15s, 100k cells and separate independent RUP replay.
Independent audit reconstructs provenance and positive proofs,
checks aggregate and filter counter arithmetic, not authenticity
of timing, negative search or counters. Exhaustive signed
embedding checks on small random inputs, growth/invalidation,
cap and proof replay tests. No new Lean formalization or theorem
novelty; the counting argument is mathematical justification for
the filter. Pending CI. P versus NP remains unresolved.
