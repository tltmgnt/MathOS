# Phase 6 — bounded matching audit and signed Hall subsystems

2026-11-28. PR #299 was already merged when inspected (merge a387265794f847e1f3db36da532b3e7bbee8a099). This follow-up is based on main 90e7ef32548a84c71e2c4d80377cfca846b591a7. Other work has advanced main through v22, including signed Horn, composite implication paths, positive Hall and partial XOR routes. This audit concerns the v18 line only, not a comparison against those newer architectures. No merge or solver promotion performed here.

## Actual bounded matching results

Run https://github.com/tltmgnt/MathOS/actions/runs/46137615889 passed evidence and formal jobs. Three bounded matching tests passed, plus the earlier 1180 oracle cases, 780 metamorphic controls, five scaling pairs and three tamper controls. Lean reported PnpHallCapacity.bucketCapacity and deficitContradiction axiom-free. These prove abstract cardinality facts, not Python refinement.

| Stratum | v18 decisions | Budgeted matching-first | v18 reported work | Candidate reported work |
|---|---:|---:|---:|---:|
| Matching | 2/12 | 12/12 | 991204 | 57240 |
| Pure3 | 12/12 | 12/12 | 133098 | 166218 |
| Overall | 14/24 | 24/24 | 1124302 | 223458 |

Total SAT/UNSAT/unknown: 7/7/10 vs 12/12/0. Single-run wall seconds 1.888802783 vs 1.423894303, about 24.6% lower. Reported work about 80.1% lower overall but 24.9% higher on pure3. Counters are route-specific proxies; do not claim equivalent CPU work or statistical runtime confidence. The 24 cases are the earlier archived development manifest, not a new independent holdout. Ten recovered cases are all matching-family; no coverage regressions.

Downloaded archive 15260900223 (221127 bytes), SHA256 1d026dc517398850229c4ae0520838280a4de51e61ec3067a65f7ce74268bbd1. Local independent standard-library checker verified ZIP digest and CRC, seven JSON hashes, upstream and manifest/library digests, regenerated all 24 references, checked all 48 verdicts and independently replayed all 38 credited decisions: 13 adaptive models, 13 trees (1143 nodes), six matching models and six Hall deficits. Checked candidate 25000 matching quota, 100000 total counter, remaining fallback allowance and report aggregates. No discrepancies. This does not authenticate timings, work counters or UNKNOWN search traces, nor prove implementation correspondence.

## Extension: signed Hall subsystem search

The strict matching recognizer refuses formulas that contain extra unit clauses or overlapping wide clauses, even when an entire Hall contradiction remains present. A separate positive-literal Hall subsystem exists in current main; this experimental route extends the signed matching line to arbitrary signed required groups, selecting greedily variable-disjoint clauses of width >=3, and partitioning their conflict graph into explicitly checked cliques. It is a heuristic, not a complete signed Hall detector. Neither it nor the existing positive Hall route has been benchmarked against the latest portfolios here.

Proof: choose disjoint original clauses G_i, then partition their signed literals into buckets B_j. For every distinct x,y in a bucket require the original clause (-x OR -y). If the number of buckets is strictly less than the number of required clauses, any satisfying assignment would pick a true literal from each G_i. Those literals are distinct because the variables are disjoint. They must occupy distinct buckets because the binary premises forbid any pair in a bucket. Contradiction by the capacity bound already proved in Lean. Unselected clauses cannot invalidate this proof. A successful matching of groups to buckets is only a necessary condition on arbitrary CNF; the route therefore NEVER claims SAT, only verified UNSAT or UNKNOWN. The independent checker examines the actual original premises and partition, without trusting the matching algorithm. This is a standard counting argument, not a new complexity theorem.

Search: deterministic greedy disjoint group packing, greedy clique partition, then alternating-path matching. A failed augmenting path yields a deficient reachable subsystem. Other edges can be ignored; no missing edge is assumed. Meter includes normalization, sorting proxies, traversal, clique checks, matching and certificate replay. Exceeding quota withholds the certificate. Polynomial bounded search on explicit inputs; no completeness claim outside the previously recognized matching class, and not even all Hall witnesses are found.

## Actual local development tests

Local module matched committed blob f2830a252da71ea8667e2a5518c5bc41d433ce61 after changing only import path for standalone execution. Fixed seed 185619, six hole counts 3..8, ten signed scrambled cases per SAT/UNSAT class per size. Each formula contains a unit and four overlapping wider clauses; SAT sibling deletes a specific binary conflict and has a directly checked planted model. All 120 formulas rejected by strict matching; new route certified all 60 UNSAT cases, returned UNKNOWN on all 60 SAT siblings (no SAT credit). Small cases also exhaustively cross-checked. Maximum observed route work 9688 of 25000.

500 further clause-removal/polarity perturbations of 12-variable mixed formulas, independently labeled by exhaustive bit-mask truth tables: 11 UNSAT certificates, 489 UNKNOWN, no incorrect positive. All exported witnesses independently checked. Three work-boundary controls passed (example boundary 1135); three forged report controls rejected. These are locally executed synthetic development tests with the same construction family, not blinded external evidence.

## Counterexample to search monotonicity

Seed 185620, first size-three UNSAT mixed case: verified Hall witness at 1135 reported units. Adding the single binary clause (x11 OR x12) makes greedy clique packing choose a different partition; search returns UNKNOWN at 759 units. The stronger formula remains UNSAT (independent exhaustive check), and the old explicit Hall witness successfully replays on it. This demonstrates that logical proof validity under strengthening does NOT imply monotonicity of heuristic proof discovery. Retain this exact counterexample in CI; do not reseed or silently reinterpret it. A future study can compare bounded partition strategies or reuse checked witnesses without guaranteeing general completeness. No such improved search is claimed now.

## Verification gate and limitations

New module, synthetic tests and separate CI staged. No changes to default portfolios, upstream libraries or existing gates. New CI has not been inspected as completed at the time of writing. No external blinded corpus, no fresh equal-budget comparison to the current main portfolios, no full implementation formalization. The abstract capacity lemmas are already verified, but the signed CNF extraction/search correspondence is still open. Future independent evaluation should freeze candidate hashes before third-party case selection, include mixed nonmatching controls and compare against current main's positive Hall, XOR, and adaptive routes. P versus NP remains unresolved.
