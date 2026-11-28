# MathOS v18 post-integration independent audit

2026-11-28 — release under examination: PR #285, candidate head da638106243128e8ad912230c2615c0b9145acb9, main merge 103991fbe57b808c042356aaa5e7058f48f616e8. GitHub reported this PR already merged at continuation start. No merge was performed by this audit. The independent external/blind benchmark obligation remains open despite that merge.

## Executed development evidence

Source: https://github.com/tltmgnt/MathOS/actions/runs/46134302576 . Both evidence and formal jobs passed; all 33 returned PR workflow runs reported success. Lean logs explicitly confirmed conflictBlocker, splitBlocker and rootBlocker do not depend on axioms. Those statements are abstract, not implementation-refinement proofs.

| Arm | SAT | UNSAT | Unknown | Reported work | Aggregate wall s |
|---|---:|---:|---:|---:|---:|
| v12 | 12 | 7 | 3 | 447202 | 1.18077 |
| v14 | 11 | 8 | 3 | 370576 | 1.15900 |
| v15+v12 | 12 | 7 | 3 | 452199 | 1.19111 |
| v16 | 14 | 8 | 0 | 118948 | 1.05251 |
| v17+v12 | 12 | 7 | 3 | 872473 | 1.52271 |
| v18 | 14 | 8 | 0 | 263945 | 1.20101 |
| v18-no-retrieval | 14 | 8 | 0 | 118948 | 1.07015 |

22 public development instances: 8 random 3-CNF, 8 random 2-CNF, 6 chain twins. Each arm used the same configured isolated process ceiling, not identical route-specific work units. All three random3 misses in v12 were solved by v16/v18; v18 did not improve v16 coverage. v18 attempted retrieval on six chain instances, all six exhausted the retrieval budget and no v18 decision came from the library. v17+v12 independently retrieved two valid proofs, but did not improve total coverage. In this run, v18 recorded about 2.22 times the work of v16 and took about 14.1% more aggregate wall time. Ablation equalled v16's work and coverage. Treat elapsed differences as single-run observations, not robust timing estimates. **Integrated performance superiority is NOT demonstrated.** Do not tune the next scored holdout or redefine success after seeing its results.

## Independent downloaded artifact audit

Artifact https://github.com/tltmgnt/MathOS/actions/runs/46134302576/artifacts/15259361528 ; 467407 bytes; SHA256 502b2bf515ff6e26e34e5ae023ffdabaeb6d318eb688c1d4cbcd509f8f361321. Actual downloaded bytes matched. ZIP CRC, eight JSON SHA256SUMS entries, upstream digests, frozen manifest and library hashes independently checked. Recomputed every reference (exhaustive truth tables for random cases; explicit indexed Horn chain proof for chain cases), all 154 arm verdicts checked against references, 142 decisions and 12 unknowns, no discrepancies. Independent direct replay of all 66 v16/v18/ablation positives: 36 direct SAT models, 18 complete contradiction trees (462 nodes), 3 fallback SAT assignments and 9 fallback unit-reduction traces; also replayed both successful v17+v12 retrieval proofs. No MathOS imports in this audit. This is not a separate replay of all v12/v14/v15 fallback proof systems; their own repository replay passed. Metrics and negative searches are not authenticated by positive mathematical replay.

## Restricted-class hypothesis and paper proof

Observed failure mode: the generic library spends its quota repeatedly on a family that admits a linear-time complete Horn procedure. The appropriate hypothesis is not that larger variable support predicts useful retrieval, but that structural applicability can screen generic proof search.

For every Horn CNF, after ignoring tautologies and duplicate literals, interpret clauses as implications from a conjunction of positive variable facts to one positive variable or false. Start with the empty fact set. Maintain the number of unproved body variables per clause and a reverse occurrence list. When a counter reaches zero, derive its head or report a contradiction. Inductively each derived fact holds in every satisfying assignment; a ready false head excludes all satisfying assignments. If the queue empties without conflict, set exactly the derived facts true. Any clause with true body has had its head derived, and any false-head clause has a false body, so the assignment satisfies every clause. Thus this computes the least model when satisfiable and is complete for Horn CNF.

A derivation needs at most n distinct positive heads followed by one conflict; each body occurrence is processed once. With indexed array counters/occurrence lists, input normalization by array stamping, and unit-cost indexed operations, time and space are O(n+m+L), where n is variables, m clauses, L total literal occurrences. The standalone Python prototype uses sets/dicts (expected rather than worst-case constant hash operations), and is not yet wired into production v18 or its resource checker. The proof is a standard Horn-SAT result, not a novelty claim, and no new Lean theorem for it is asserted.

The local standalone prototype executed: exhaustive 256 canonical two-variable Horn formulas (56 SAT, 200 UNSAT), 500 independent seeded Horn formulas (157 SAT, 343 UNSAT), 500 metamorphic relabel/reorder/tautology/duplicate-literal checks, 18 analytic chain twins (sizes 20 to 5120), three malformed proof/model controls rejected; non-Horn input returned UNKNOWN. Zero disagreements. Chain refutation trace length exactly n+1 clause indices, model length n bits. This is separate synthetic development evidence; it is not a benchmark of the production solver, nor external holdout. The source is tests/independent_pnp_v18_horn_probe.py. This prototype deliberately remains standalone.

## Frozen synthetic evaluation of the unchanged release

The follow-up experiment freezes existing v12 policy, old and new template-library digests, and resolution plan from the verified release. A regenerated upstream library must match exactly or scoring stops. No changes to the candidate solver, certificate kernels, resource allowances or prior gates. Independently generated seed 180831 specifies 30 new cases: 10 pigeonhole SAT/UNSAT twins (12–56 variables), 8 odd/even cycle 2-colouring cases (17–128 variables), and 12 random pure 3-CNFs (12–16 variables). The generator uses analytic references for larger structural cases and bit-mask exhaustive truth tables for small cases, and randomized signed bijections/clause order. The independent reference labels, family and case ID are withheld from workers. Exact normalized input overlap against available prior splits is rejected; this does not establish full signed-isomorphism disjointness. The seven unchanged arms run under the original hard process/cooperative envelope. Full route replay, manifest/aggregate audit and artifact hashes required. This is a new fixed synthetic benchmark, **not a third-party blinded external corpus**. Its results are not asserted until execution. No policy training/admission occurs on this manifest.

## Obligation ledger update

- V18-05: completed upstream positive certificate checks as previously scoped; new integrated positive certificate audit passed as scoped above.
- V18-06: development coverage tied v16; no retrieval gain, higher observed work. Universal/held-out improvement conjecture remains unresolved; current development data do not support superiority.
- V18-07: integrated CI and three abstract Lean statements passed. Implementation refinement, external/blind benchmarks, hard-resource comparability beyond common process ceilings remain open.
- V18-08: standard Horn-SAT completeness/linear restricted bound proved by paper argument; standalone empirical validation passed. Formal implementation correspondence and production routing remain open.
- V18-09: P versus NP remains unresolved.

No verified solver is to be replaced solely on these results. Keep this follow-up PR draft until the new experiment completes and is reviewed; preserve all failure and unknown outcomes.

### Pre-scoring independent manifest verification

The local standalone generator executed and produced 30 distinct normalized inputs (21 SAT, 9 UNSAT), with no exact normalized overlap against 171 archived prior rows. Canonical manifest SHA256 a3d6c722f83619950b5255014991cf9e9402e2ec80e782506a2b928a2c9a561f is now enforced in CI. Pigeonhole 5 SAT/5 UNSAT; cycle2 4 SAT/4 UNSAT; random3 12 SAT/0 UNSAT. The random3 seed happened to contain no UNSAT reference cases; preserve it rather than reseeding. This suite cannot evaluate random3 UNSAT coverage. Future separately preregistered pure-3-CNF obstruction strata are required. No solver outcomes were observed when freezing this manifest.
