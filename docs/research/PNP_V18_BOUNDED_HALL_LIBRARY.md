# Phase 10 — bounded multi-record Hall library selection

## Repository and verification status

Parent PR #316 is still draft and open; dedicated rectangular CI 46154281035 and automatic CI 46154280991 were queued at inspection. No independent CI archive yet available for phase 9. This branch is stacked on its exact head 5a4c719a3a5e4db5f91abb7289f9c739662d6ca3; no merge or gate weakening. Main has advanced to 3e7961c7460aa75687788a8d101473e8db551928 (incremental XOR); this is not a comparison against current main portfolios.

## Candidate and mathematical scope

Library contains nine independently checked rectangular Hall witnesses for hole counts 2 through 10, in fixed order [9,7,4,10,2,8,5,3,6]. No target-specific record or embedding supplied. Each record is screened by rectangular shape, active-variable support, number of clauses of required width, total binary conflict clauses, and number of width-s candidate groups whose literals have conflict degree >= r-1. These are necessary conditions for exact signed embedding of an r-by-s rectangular witness: an injection preserves distinct variables and clauses; each bucket of r literals needs all r(r-1)/2 distinct binary conflicts; each image group has s literals, each with r-1 distinct conflict neighbors. For s=2, the width and binary counts are loose necessary conditions, not sufficient. Screening cannot establish a contradiction; successful retrieval still checks original target premises. Ranking by candidate-count slack, support and library index is a heuristic, not optimality or completeness. A four-attempt cap and resource exhaustion may miss valid witnesses. All selected records are revalidated by rectangular search; the profile is a hint, not a trusted proof. Pre-admission costs excluded. No persistent cache, no SAT credit or full SAT fallback: fallback is the previous signed Hall subsystem (UNSAT or UNKNOWN). Library size capped at 32 records.

All online screening, search and cold fallback consume one cooperative budget (25000 proxy units and 1.25 seconds). First 80% reserved for screening/retrieval, unused allowance carries to fallback. Candidate scan comparator has same envelope and attempt cap but uses fixed library order without screening. Cold-only comparator gets full allowance. These are not equivalent CPU instruction counts or hard process timing measurements. Policy chosen for this development test, not tuned after observed outcomes.

## Actual local experiment

Executed the new probe on the local phase-9 development report (not yet a verified CI archive). Exact local sources after import-path adjustment match repository blob hashes:
- router 897335973296eabded0d7edda8959994547b2d6c
- probe 0dae103512834b7615d6d1302b8151641367b991
- independent audit 453bd71742a32f0a2a350d57a81c4f80f8b1ae5c

290 formulas: 120 archived related UNSAT, 60 archived deletion SAT, 30 ambiguous strengthened UNSAT, 40 planted nonmatching SAT, 40 contradictory-unit UNSAT controls. The ambiguous targets add a disjoint satisfiable width-three decoy (one conflict removed, degree restored by two auxiliary false choices), so both a smaller false candidate and the real record pass screening; all 30 indexed runs attempt both candidates and certify the target. The 80 nonmatching controls use seed 189321. Related formulas intentionally share witness structures; no independent blind split. 

| Stratum | Cases | Cold | Ordered scan | Indexed |
|---|---:|---:|---:|---:|
| Related UNSAT | 120 | 37 | 65 | 100 |
| Ambiguous UNSAT | 30 | 9 | 11 | 30 |
| Deletion SAT | 60 | 0 | 0 | 0 |
| Nonmatching SAT | 40 | 0 | 0 | 0 |
| Unit UNSAT | 40 | 0 | 0 | 0 |
| Total positive | 290 | 46 | 76 | 130 |
| Unknown | | 244 | 214 | 160 |
| Reported work | | 832110 | 6364560 | 2462408 |

Indexed selection gains 54 decisions over ordered scan while reducing reported work 61.3%. It gains 84 decisions over cold search at about 2.96x work. It misses all twenty size-eight related targets: indexing work about 6500 units plus 80% cap leaves about 13500 for retrieval, insufficient. Prior preselected symmetry-reduced route solved 120/120 with the full 25000 allowance. This is a real coverage regression from that oracle-record comparison, and identifies selection/budget overhead. All forty unit contradictions remain UNKNOWN in all arms, demonstrating scope limits. No end-to-end superiority claim. All SAT controls remain UNKNOWN, not certified SAT by the router.

Separate standard-library-only audit actually ran: nine library records, 870 arm reports, 252 positive certificate occurrences, 100 explicit SAT models, retained reference linkage and shared budget arithmetic; no mathematical discrepancy. It does not authenticate negative search traces, actual timing or all individual operation counts. No new formal implementation proof. 

## Gates and next decisions

CI regenerates and audits predecessors, runs this probe and independent audit, hashes all six JSON reports. New CI not yet completed. Keep candidate experimental, not production. Next mathematical objective is a shared target index that avoids repeated normalization and structural scans, or a separately preregistered budget policy; preserve the 20 misses rather than changing this recorded experiment. Need external blinded evaluation, current-main comparisons, independent holdout, hard process timing and code-to-semantics refinement. P versus NP remains unresolved.
