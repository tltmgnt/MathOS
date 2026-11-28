# Phase 9 — rectangular Hall symmetry reduction

2026-11-28. PR #306 was already merged into main, and PR #311 was already merged into #306's branch, not main. At main 07e35a04275dfb26e2aa80a91617b95875716e30 (which includes parallel v25 complexity-barrier work), the automatic embedding module was absent; GitHub compare against 6924a9c31868870539ce39f12a5e8e88a4f38116 showed a diverged branch with five added files. This draft is based on current main and carries those five verified phase-8 files unchanged. No merge performed here; new branch requires full regression and review. No claim to compare against newer architectures.

## Phase 8 verification

Run 46152714478 passed. Downloaded artifact 15266054261, 115969 bytes, matched SHA256 34ed7046a4927d2a94806ebcd11d97116b324f7b97f17d9e189c4852d49dc7d8. ZIP CRC and both JSON hashes matched. Report SHA256 b6e1d0127acbff11af898011166f5c2b53a6c0595a0fd1e97dc296b163fc6f6f. Reran standard-library-only independent audit on downloaded report, reproducing archived audit exactly: 360 arm reports, 257 positive comparative certificates, 60 SAT control models, one counterexample; no discrepancy. Prior automatic 100/120, cold 37/120, supplied 120/120; automatic exhausted on all twenty size-eight cases. This verifies mathematical evidence, not runtime or negative-search completeness.

## Rectangular symmetry argument

Let a dense checked Hall witness contain r disjoint required groups and s incompatible buckets with r>s, exactly one literal per (group,bucket) cell. Guards are exactly the r group clauses plus all pairwise conflicts within each bucket. Independent permutations of rows and columns preserve those guards: each signed cell literal is relabeled bijectively, with its complement relabeled accordingly. Thus any valid signed embedding can be composed with a source automorphism so the image groups appear in ascending lexicographic order of their sorted target clauses and the first image row assigns target literals in ascending order to source columns. This eliminates redundant row and first-row column permutations without eliminating the existence of a solution. The implementation checks the rectangle condition before applying this reasoning.

For each subsequent image row, a literal in column j must lie in the intersection of the target conflict-neighbor sets of all already selected literals in column j. It must also belong to the current target clause, and all variable images must be disjoint. Enumerate bijections from columns to the current row using minimum remaining domain first, then intersect neighbor domains and recurse. The degree pruning threshold r-1 is necessary. By induction on rows, every symmetry-normalized valid embedding survives all pruning, and all feasible remaining assignments are enumerated absent resource exhaustion. On success, reconstruct signed injection and replay the transported witness against actual target clauses inside the allowance. This gives exact embedding existence for rectangular dense witnesses within support <=128 if the search finishes; it does NOT decide satisfiability on misses, recognize arbitrary Hall witnesses, or prove polynomial embedding discovery. Nonrectangular records return UNKNOWN; larger support and exhausted quotas also return UNKNOWN. Worst-case branching remains exponential. The symmetry proof is a paper argument, not a new Lean implementation correspondence result.

## Actual local regression

Exact local module matched committed Git blob b2f45c46f8f858a5b992bd3dec65204cb5303748 after changing only package import paths. Reused actual downloaded phase-8 evidence, same preselected records and target clauses, 25000 reported units and 1.25 cooperative seconds per query. No new holdout, no admission/selection cost, no common hard process/timing study.

| Holes | Previous auto decisions | Rectangular decisions | Previous work | Rectangular work |
|---:|---:|---:|---:|---:|
| 3 | 20/20 | 20/20 | 38551 | 29476 |
| 4 | 20/20 | 20/20 | 78083 | 56467 |
| 5 | 20/20 | 20/20 | 138831 | 94998 |
| 6 | 20/20 | 20/20 | 224718 | 148458 |
| 7 | 20/20 | 20/20 | 350450 | 220518 |
| 8 | 0/20 | 20/20 | 500000 | 315615 |
| Total | 100/120 | 120/120 | 1330633 | 865532 |

All twenty former misses recovered; zero coverage regressions on this manifest. Reported work fell 34.95%; this is a comparison of metered algorithmic proxy units, not a measured CPU-time speedup. All 60 archived SAT controls returned not_found without exhaustion; prior automatic had 10 not_found and 50 exhausted. Their aggregate work fell from 1302316 to 288004 (77.9%). Retained strengthened counterexample recovered in 1562 units (previous automatic 2087); budgets 1 and 1561 withheld credit, 1562 certified. One nonrectangular witness correctly rejected as out of scope. 60 additional related formulas with eight extra random binary clauses each all certified. No external generalization claimed.

Small exact-embedding test: 300 six-variable perturbed/signed CNFs, using a 3-by-2 rectangular guard; independent exhaustive enumeration of disjoint clause triples and both orientations per clause. 53 had embeddings, 247 did not; all matched the new search, no exhaustion. Absence of this embedding is not a SAT verdict. Separate standard-library-only audit (no MathOS imports) checked 334 positive certificate occurrences (220 old/new paired positives, 60 extra, 53 small, 1 counterexample), 60 explicit SAT models, all 300 oracle outcomes and report sums. No disagreement. Boundary/scope assertions are separate probe checks, not inferred from aggregate audit. Full per-case evidence emitted for paired, negative, extra and small controls.

## Verification gates

New workflow regenerates and independently audits phase-8 report before running symmetry regression; separate replay and four JSON integrity hashes required. Original production solvers and prior gates unchanged. Local test success is not CI success. Multi-record selection, indexing across records, independent external corpus, current-main portfolio comparison, replicated hard process performance, and full Lean implementation correspondence are still unresolved. P versus NP remains unresolved.
