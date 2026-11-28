# Phase 8 — bounded automatic Hall guard embedding

2026-11-28. Parent PR #306 remains open and draft at head 0878a687227f5e450ae0a85e0dea55e9cbab0668. Its dedicated run 46151936749 passed. Downloaded artifact 15266470385 (624 bytes) matched SHA256 678d4029e997fd1b955d28c1ee3a9634f1f265d15b9bcb75e9c39bb6be9b5b66; ZIP CRC and report.json SHA256 a1eb6994992ef3ab45a6a9add7bb206a3eff1374212b5ba55adc12d108700510 matched. Confirmed 300 supplied transfers, cold 78/300, 3910 guard deletions, 110 SAT deletion controls, 90 tamper controls, boundary 1109, and retained counterexample. This archive contains aggregate counts, not every individual witness; no independent replay of every archived certificate claimed. Other parent PR checks were not all complete at latest inspection. This new branch is stacked on the unmerged parent rather than merging it or copying unreviewed changes onto main.

## New bounded search

Given one preselected, checked Hall record, index normalized target clauses by width and binary incompatibility adjacency. Search variable-disjoint target clauses of the same width as the source required groups. Within each clause, try signed literal bijections, preferring source literals with already mapped conflict neighbors. Prune any variable reuse, insufficient target conflict degree or missing conflict against a mapped neighbor. A successful assignment of all source literals defines a signed injection. Transport the witness and recheck its original target premises within the same Meter; return no certificate if the quota is exhausted. Offline replay revalidates the record and explicit signed embedding using the separate transfer checker. The source label map is not used by automatic search.

Soundness: an accepted mapping preserves the original required clauses and all binary conflict clauses; distinct source variables map to distinct target variables. Thus the transported witness is a Hall obstruction on the actual target and entails UNSAT. This is also checked directly, independent of the search. For dense validated records of support at most 128, absent resource exhaustion, enumeration covers all exact signed injections satisfying these guards: every possible image clause appears in its width bucket, all within-group bijections are considered, and each pruning predicate is necessary for a valid injection. The finite enumeration may be exponential/factorial; this is not an efficient general subgraph-embedding theorem. Support cap, exact guard membership and one preselected record are explicit scope limits. Larger targets up to existing input limits are permitted; witness support above 128 returns UNKNOWN. The method does not choose a record from a library or discover arbitrary UNSAT structures. The meter is a cooperative work proxy, not a hard instruction count. No production route or existing gate changed.

## Executed local experiment

Exact search module matched committed Git blob 8fca46f472e740e1f69209fc2cb98b82b5662b47 after changing only package imports for standalone execution. Fixed seed 187102; one admitted signed pigeonhole record per hole count 3..8. Twenty related, signed-injected targets per record with three added random clauses, 120 total. Automatic arm receives record and target only, not correspondence; supplied arm receives the generator's known mapping; cold arm receives target only. All three use 25000 cooperative units and 1.25 seconds per query. Initial admission costs excluded; no common hard process envelope or replicated timing. This is related synthetic development, not a new external holdout or comparison with newer MathOS portfolios.

| Holes | Cold | Automatic | Supplied |
|---:|---:|---:|---:|
| 3 | 17/20 | 20/20 | 20/20 |
| 4 | 4/20 | 20/20 | 20/20 |
| 5 | 2/20 | 20/20 | 20/20 |
| 6 | 6/20 | 20/20 | 20/20 |
| 7 | 5/20 | 20/20 | 20/20 |
| 8 | 3/20 | 0/20 | 20/20 |
| Total | 37/120 | 100/120 | 120/120 |
| Reported work | 325822 | 1330633 | 721020 |

Automatic search recovered 66 cold misses but lost three cold successes. All twenty size-eight automatic searches exhausted their quota; do not hide this scaling limit. The retrospective union of cold and automatic decisions is 103/120, not a measured integrated portfolio. Automatic work was about 4.08x cold and 1.85x supplied. More coverage is demonstrated conditional on a preselected record, not an end-to-end computational gain or equal-information comparison. No library indexing or record selection cost measured.

Sixty guard-deletion SAT controls: ten not_found, fifty resource_exhausted, no false UNSAT; explicit models independently replayed (size-three controls additionally truth-table checked). Three budget boundaries passed (1 and 1803 UNKNOWN, 1804 verified), four tampered record/report controls rejected. The exact previously retained strengthened 12-variable example was automatically recovered without a supplied embedding in 2087 units (cold UNKNOWN at 759; supplied transfer 1247 previously). No claim that the cold heuristic itself is monotone.

## Independent local replay and new CI

The new report exports all 120 comparison rows (360 arm reports), 60 SAT controls with models, and the retained counterexample, rather than only aggregates. Separate standard-library-only audit imports no MathOS modules. Locally executed it against the generated report: independently replayed all 257 positive comparative certificates, all 60 negative-control models, the automatically recovered counterexample, checked automatic signed embeddings and source/target guard certificates, and recomputed comparison counts/work sums. No disagreement. It cannot authenticate actual search expenditures, timings or negative search completeness. The workflow now requires independent replay and hashes of both report and audit. New CI results pending at submission; no assertion of completed CI. No new Lean theorem or full implementation refinement; abstract Hall capacity from prior phases applies.

## Outstanding obligations

Automatic multi-record selection, resource-bounded portfolio fallback, third-party blind evaluation, comparison with current main portfolios, replicated hard-process cost study, and code-to-semantics formalization remain unresolved. Parent and new stacked PR remain subject to review. P versus NP remains unresolved.
