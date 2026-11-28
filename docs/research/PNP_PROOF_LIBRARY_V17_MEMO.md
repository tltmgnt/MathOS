# v17.9 — memoized proof retrieval

## Observed v17.8

PR #309 merged into the admission branch, not observed on main at
the new branch point. PR #305 merged into main. Both gates retained
the original 30-template library. Evidence CI passed:
https://github.com/tltmgnt/MathOS/actions/runs/46152616706.
All four expansion cohorts in each discovery epoch preserved coverage
but increased work. On 72 final heldout (30 UNSAT), original and gated
each verified the same 23 with 6,830,671 work ticks. Ungated 54-template
library verified 24 (one mixed gain, none lost), used newly admitted
entries in 12 verified recipes and spent 11,304,822 ticks. All arms
verified 1/6 ternary UNSAT. Aggregate search/replay time 4.814/4.822/
7.727 seconds for original/gated/ungated respectively. Selection
avoided extra cost but also missed a heldout gain. No iterative
learning success: neither epoch accepted knowledge.

## Hypothesis and method

Before expanding the library again, test whether repeated partial
signed embeddings consume retrieval work. In the existing matcher
different clause witnesses can lead to the same guard position and
signed partial injection. Given a fixed known-clause set, fixed
guard ordering and goal, the remaining search depends only on that
state (used variable identities are determined by the injection).
Cache a failed state only after exhaustive local traversal with
no witness satisfying the novel-goal condition. Never store a
failure at or after the local candidate cutoff. A thrown global
resource exception aborts search. Cache lives for a single matcher
call and is discarded before the next known-clause set or template;
no cross-formula negative learning. At most 4096 entries, further
limited by the cooperative cell cap. Lookup and insertion ticks
are charged; the local 4096 candidate transition cap is unchanged.
The order of candidate exploration remains the existing v17 order.
The proof route and replay are unchanged. A cache hit prunes only
a repeated complete failure; this informal invariant is not a Lean
formalization of implementation correctness or a guarantee of coverage
under finite budgets. Reduced duplicate exploration may allow a
later candidate within a limit; cache overhead can also hurt.

## Frozen experiment

Use v17.7 training only to rebuild its expanded snapshot, audit
lineage and compare 2x2: base/expanded x original/memoized search.
Same round and transfer limits, same cooperative 4M tick/15s/100k
cell cap per arm. Operation counts are coarse and not machine-level
costs; independent replay separately timed. New seed 17903: 72 cases,
equal binary, ternary and mixed width strata. Prior v17.7 holdout
72 cases retrospective only. Exclude exact normalized overlap
against known earlier splits including v17.8 seeds, not signed
orbits or external blinding. No selection or admissions on evaluation.
Report matched gains and losses, work, wall time, examined templates,
cache hits, stores, local cutoffs and use of added knowledge.
Tests cover repeated states, local cutoff, complete small search
agreement, resource exhaustion and independent replay. Report audit
rebuilds training provenance, checks all positive certificates and
counter arithmetic, not negative search or measurement authenticity.
No default changed; no novel theorem or unrestricted complexity
claim. Pending CI.
