# v17.13 — failure-directed resolution-cone abstraction

PR #320 merged, evidence workflow 46158758877 passed. On 72 fresh
signed-orbit-disjoint cases (23 UNSAT), base verified 19 and
expanded/compacted 20; one mixed gain, none lost. All arms verified
2/5 ternary UNSAT, so three ternary refutations remain unresolved.
Expanded compaction reduced ticks 12,283,674 -> 11,244,375 with
identical coverage (~8.46%). Memoization added no fresh coverage and
increased work on both tested snapshots. The expanded compacted
snapshot used admitted entries on 10 verified proofs, but that is
not proof that every use was necessary. Screening recorded 1,028
distinct exact prior keys, three unresolved and 12 out-of-support
inputs, two duplicates. All 72 selected inputs passed. No claim of
independent local guards or logical inequivalence.

## Design

Explicitly retire the v17.12 evaluation set to development. Regenerate
and audit its report, rebuild the expanded compacted library from
prior training only. Treat its observed non-verified outcomes as a
failure cohort, verified outcomes as a success cohort. A miss is
not evidence of satisfiability or a diagnosed root cause. Run the
same bounded offline Davis-Putnam resolution generator on every
development case, without supplying reference labels. Independently
verify the DAG, compress with checked embedding, extract existing
dependency-cone templates, replay each fragment and independently
check the guarded entailment by RUP under its negated goal.
No new inference rule or proof-system complexity claim.

Build separate candidate pools from failure and success sources,
prefer short nonempty goals then cores, cap each at 12, remove
known exact guarded-orbit or fallback structural duplicates.
Unknown orbit keys do not prove inequivalence. Each candidate
binds source and DAG digests. Match additions by the smaller
pool cardinality, permitting zero if one pool is empty. Keep
original compact-expanded library unchanged in every arm. Equal
template counts do not equalize proof sizes, source distribution,
or computational cost. A successful prior source may supply
unseen cones, and a failed prior source may be SAT and yield no
proof. This tests a source selection policy, not a causal diagnosis
of every failure. Offline resolution is never run on target cases.

## Evaluation

Register the declared prior corpus and all 288 prior orbit-pool
inputs before label-free selection from seed 171303 (288 candidates).
Require exact orbit-disjoint keys and quarantine unresolved
buckets. Freeze three snapshots (baseline, failure additions,
success additions) before evaluating 72 selected cases, 24 per
family, 216 paired evaluations. Identical original matcher,
shared cooperative 4M tick/15s/100k cell caps, independent RUP
and exhaustive truth reference. Compare paired gains/losses,
work and actual added-template use. Audit prior report, all
positive source DAGs, deterministic candidate pools and provenance,
matched size, selected orbit manifest and positive target proofs.
Report development resolution cost separately; negative search
observations and timings are not authenticated. Public seeds,
explicitly scoped whole-formula signed orbits, not external
blinding or semantic separation. No new Lean implementation
refinement, hard process caps or default changes. Pending CI.
P versus NP remains unresolved.
