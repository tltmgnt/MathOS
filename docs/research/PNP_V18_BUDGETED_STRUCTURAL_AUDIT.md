# Phase 5 — bounded structural routing and matching-frontier audit

2026-11-28. PR #294 was already merged on inspection (main 190ef18e4e7d17197c969317d7b624bae48970dc); no merge performed by this continuation.

## Actual matching-first experiment

Run https://github.com/tltmgnt/MathOS/actions/runs/46136498391 passed, including the 1,180 oracle tests, 780 metamorphic cases, five scaling pairs, three rejection controls, separate replay and SHA256SUMS. Artifact 15260366235 (219017 bytes) downloaded locally and matched SHA256 5924222b7221ce4e1fd5571efdbf9cafdfc3e1f66c794c642a3bb5fcb864c106. ZIP CRC, all seven JSON hashes, upstream and frozen library hashes, independently regenerated manifest, all 48 decisions/unknowns and all 38 positive certificates independently checked with standard-library Python and no MathOS imports: 13 direct adaptive models, 13 contradiction trees (1143 nodes), six matching models and six Hall deficit certificates. No disagreement. This checks positive mathematical evidence, not timing or implementation refinement.

| Stratum | v18 | matching-first |
|---|---:|---:|
| Matching | 2/12 | 12/12 |
| Pure 3-CNF | 12/12 | 12/12 |
| All | 14/24 | 24/24 |
| SAT | 7 | 12 |
| UNSAT | 7 | 12 |
| Unknown | 10 | 0 |
| Observed aggregate wall s | 1.70862 | 1.25434 |

All ten gains were matching cases. No pure3 regressions or gains; matching route returned UNKNOWN on each, then unchanged v18 decided it. Single-run aggregate wall time fell 26.6%, matching stratum 45.1%, pure3 increased 6.1%. Not statistically replicated. Matching work was not charged to the legacy cooperative allowance in that experiment, so the result establishes coverage gain under the common hard process ceiling, not equal metered work or external generalization.

## Candidate revision

New standalone metered matching route (mathos/research/pnp_bounded_matching.py) bounds input dimensions as v18, charges normalization, recognition, sorting proxies, graph traversals, augmenting paths, model construction, and original-clause certificate replay. A positive answer is only returned after in-budget replay; on exhaustion it returns UNKNOWN, no certificate, and charges the entire allocation. Offline replay rejects impossible reported costs below the cost of positive certificate checking, but does not authenticate search measurements or negative outcomes. This is cooperative operation accounting, not a proof of CPU-instruction equality or a hard deadline for each Python operation.

New experimental portfolio (mathos/research/pnp_budgeted_structural_v18.py) reserves 25% of the total cooperative work and time for matching; unused allowance carries into unchanged v18 fallback. With standard 100000 reported steps and five cooperative seconds, matching is capped at 25000 and 1.25s; fallback receives remaining reported steps and wall allowance. Production entrypoints and previous gates are unchanged. The outer benchmark still uses one core, 512 MiB address space and ten-second hard process timeout, including external verification. Legacy fallback bookkeeping/replay and wrapper fingerprint/digest overhead are not all metered; the new counters use different proxy units from legacy routes. Thus the configured total cooperative counter is shared, not a universal exact cost model.

## Local verification actually executed

The exact committed matching module blob 023a5d52ddf3729d713e4c315788b6b62a023215 matched the local Git blob hash. Tested 780 exhaustive neighborhood lists and 780 signed metamorphic variants plus 400 independent seeded matching lists against an enumerated distinct-representative oracle: 1960 decisions/replays, no discrepancy. Five work-boundary checks passed: a representative 30-variable contradiction needed 2114 proposal units and 3066 including replay; budgets 1, 2113, 2114, 3065 returned UNKNOWN, budget 3066 certified UNSAT. Three corrupt report controls rejected. Additionally ran 1000 randomly perturbed small matching CNFs against independent exhaustive bit-mask truth tables: 229 SAT, 27 UNSAT, 744 UNKNOWN, zero false positives. This tests scope soundness, not completeness outside the recognized subclass.

Retrospectively ran the bounded route alone on both previous archives (54 cases): all 22 matching/pigeonhole cases certified with the 25000-unit quota; all 32 others returned UNKNOWN. On the recent 24-case manifest, maximum successful route cost 10422 units; pure3 misses 2238–3222 units. These are archived tests, not new independent holdouts or measurements of the integrated fallback.

## New paired regression and formal obligations

The frozen 24-case manifest, policy, library and old templates remain fixed. The new comparison scores unchanged v18 against budgeted-matching-first and records combined reported work, decisions, elapsed wall, separate replay and integrity hashes. It is an archived regression, not an external test; no outcome asserted before execution. New Lean file formalizes the numeric occupancy bound and deficit contradiction from abstract hypotheses. This does not formalize CNF extraction, matching algorithm or Python implementation; local Lean unavailable, CI required. Do not promote candidate before results and independent review. No changes to baseline solver, library or gates.

Third-party blinded evaluation, implementation correspondence and robust repeated runtime measurement remain open. P versus NP remains unresolved.
