# MathOS v18 phase 4: matching certificates and frozen frontier audit

2026-11-28. PR #289 was already merged when this continuation began (main f95abf0a599bd755114de7f437392a2b273eefc8). No merge performed by this continuation.

## Actual frozen synthetic evaluation

GitHub run 46135424679 completed successfully. It includes separate positive replay and eight JSON integrity checks. Artifact 15259822431, 524892 bytes, SHA256 0fbffd282d4d08e83b1a86e7e58521c283f93726b0350d8b3a4eb0fbd437f61e. Downloaded archive hash, ZIP CRC, all eight JSON digests, frozen manifest and library digests, upstream hashes independently matched. The 30-case manifest was independently regenerated; analytic family references and bit-mask truth tables confirmed the reference labels. All 210 verdicts checked: 74 SAT, 32 UNSAT, 104 unknown. Independently replayed 69 positive v16/v18/ablation certificates and 32 legacy affine parity certificates (101 of 106 credited decisions). In total: 45 direct models, five direct trees with 461 nodes, 51 parity certificates (including fallback). The remaining five legacy positives were not independently replayed, but passed the repository replay. No false verdict detected. The audit did not authenticate timings, negative searches, or the full Python implementation.

| Arm | SAT | UNSAT | Unknown | Reported work | Aggregate wall s |
|---|---:|---:|---:|---:|---:|
| v12 | 5 | 4 | 21 | 2176966 | 2.35235 |
| v14 | 5 | 5 | 20 | 1749619 | 2.23976 |
| v15+v12 | 5 | 4 | 21 | 2179333 | 2.39293 |
| v16 | 18 | 5 | 7 | 834465 | 1.87983 |
| v17+v12 | 5 | 4 | 21 | 2401966 | 2.66974 |
| v18 | 18 | 5 | 7 | 1071032 | 2.12045 |
| v18-no-retrieval | 18 | 5 | 7 | 834465 | 1.96226 |

v18 and v16 tied (23/30); no per-case coverage gain. v18 attempted retrieval 16 times, all exhausted. Observed reported work increased 28.35%, aggregate wall time 12.8% versus v16. Not a statistically replicated timing result. Across the earlier 22-case and current 30-case suites, v18 and v16 each decided 45/52; all 22 v18 library attempts exhausted. No superiority established. All seven remaining cases belong to pigeonhole: php_4_0, php_5_0/1, php_6_0/1, php_7_0/1. Cycle coloring 8/8; random3 12/12, but random3 is SAT-only.

## Parameterized matching certificate

Recognized subclass: after tautology and duplicate removal, width >=3 clauses are variable-disjoint signed choice groups, width-two clauses are conflicts between the oppositely oriented choice literals (binary-only variables have consistent conflict polarity and can be set to make those literals true). The conflict graph induced by choice literals must be a disjoint union of cliques, including isolated vertices. Otherwise the recognizer returns UNKNOWN. Each group is a left vertex, each clique a right vertex, and an edge denotes at least one available choice literal in that clique. This is not a semantic recognition procedure for arbitrary SAT or arbitrary equivalent encodings.

Equivalence proof: a satisfying assignment selects one true literal from each group. Variable-disjoint groups ensure distinct choices, and every pair of literals in a common clique is forbidden simultaneously. Their clique indices thus define a matching saturating the groups. Conversely, a saturating matching picks one literal per group in distinct cliques; assign these true, all other choice literals false, and binary-only variables the consistent satisfying polarity. Every original wide clause and conflict clause is satisfied. Direct model verification is required.

If augmenting-path BFS fails, let S be the reachable groups and B their neighboring cliques. Every clique reached is matched to a distinct reached group other than the unmatched root; every reached group other than root arises this way. Hence |B|=|S|-1. The certificate consists of the actual required clauses in S and their literals partitioned into the corresponding buckets in B. The independent checker validates original clause membership, pairwise variable disjointness, exact partition, fewer buckets than groups, and every pairwise conflict from the original input. Even on an unrecognized formula, such a witness is a sound contradiction: selecting one true literal per group would inject more groups into fewer buckets. No reliance on the search trace or an UNSAT label.

The reduction and augmenting paths give polynomial time on this explicitly recognized family (O(gE) for g groups and E bipartite incidences, plus polynomial recognition and replay). The Python prototype uses hash containers, sorting and repeated minimum selection, so no worst-case linear implementation claim. The valid Hall certificate stores at most O(n) literal labels, with group and bucket boundaries; checking original binary conflicts is polynomial in the explicit input. This is a standard Hall/matching theorem application, not a new unrestricted SAT lower or upper bound, and not a Lean refinement proof.

## Executed local prototype

Standalone standard-library prototype, no MathOS imports, tested 780 exhaustive small bipartite neighborhood lists plus 400 random lists against enumerated distinct representatives (1012 SAT, 168 UNSAT), 780 signed-renaming/reordering controls, 10 analytic scaling cases up to 1056 variables and 16929 clauses, three forged certificates rejected, nonmatching input unknown. No discrepancy. On the already scored frozen suite, independently ran the standalone recognizer and checker: all ten pigeonhole cases solved, including all seven previously unresolved; the other 20 returned UNKNOWN. A hypothetical union with archived v18 decisions covers 30/30 retrospectively, NOT a measured integrated run or independent performance result. This route was developed after seeing the failure family and must not be presented as blinded evidence. No production solver has been changed.

## New controlled experiment

Frozen seed 184729, canonical digest 8fd7cf8eb5f2a24e814c62179d2dee71e8278d7cd3d9c153d7e3e7a28ca9692e. 24 cases: six SAT/UNSAT sparse matching twins with a deficient subset even when total global bucket count exceeds group count, and twelve pure 3-CNF instances (six SAT, six UNSAT; 12,14,16 variables; density 5; first two per truth class selected using exhaustive reference). Local check found 24 distinct normalized inputs with zero exact overlap against 201 archived rows. This does not certify orbit disjointness. Standalone recognizer already solved all twelve matching cases and returned UNKNOWN on all twelve pure3 controls. This is therefore a synthetic development/route test, not a third-party holdout; the unchanged v18 and candidate portfolio comparison has not been run locally.

New experiment compares unchanged v18 to matching-first then unchanged v18 fallback, with reference labels withheld from workers, frozen policy/library digests, same one-core, 512 MiB address-space and ten-second hard wall envelope, alternating run order, separate positive replay and evidence hashes. The matching route is not included in legacy cooperative work counters; do not claim equal step budgets, or promote this candidate from this experiment alone. Tests and comparison are staged in CI; no results asserted before completion. No changes to original v18 routes, verifier or gates. The new matching route needs a cooperative budget, independent external evaluation, code-to-semantics formalization and replay before any default integration.

## Obligations

- Integrated v18 verification: passed as scoped; original external blind holdout remains open.
- Superiority over v16: not demonstrated; both fixed suites tied and showed extra retrieval overhead.
- Matching certificate soundness and recognized-subclass completeness: paper proof above, computationally supported; formal Lean correspondence unresolved.
- Production matching route, equal-step comparability and integrated candidate results: unresolved.
- P versus NP: unresolved.
