# Phase 11 — shared metered target indexing

## Verified predecessor and repository status

PR #319 was already merged into #316, and #316 into main, when inspected. Final combined head ab933e3745eaad7cdd1cd92747ed830767995db0 passed the automatic, rectangular and library workflows (46157075366, 46157075385, 46157075164). Current base 22a826d7cd6665a64b594c15a742fd9e0b83fbdb also includes parallel v26–v30 work. No merge performed here. The new comparison is limited to the v18 line, not newer main portfolios.

Downloaded library artifact 15267948128, 388965 bytes, SHA256 d67d7f8ee7b4bec225dec84d369bd934ae01d141880eed046c1b547def170a33. ZIP CRC and all six JSON hashes verified independently. All three archived audit objects reproduced exactly by separately running the standard-library-only automatic, rectangular, and library checkers on the downloaded reports. They report respectively 257, 334 and 252 positive certificate occurrences; those counts overlap, not unique proofs. The library audit checks 870 reports and 100 explicit SAT models. No disagreement.

## Optimization and proof obligation

Previously each candidate attempt rebuilt the normalized target and conflict graph, and screening scanned clauses again. Build a private query-local target index once: normalized clauses, active support, width counts and lists for requested widths, and signed binary conflict adjacency. Compute and cache sorted degree-filtered candidate rows keyed by (r,s). Use the same index for ranking and subsequent symmetry-reduced search; the candidate set and sort key remain unchanged. Every valid embedding must satisfy the same necessary width/support/degree tests; cached lists are exactly those produced by the previous scans on the same immutable-in-use input. No change to symmetry completeness argument. Search may still miss because of resource limits or candidate caps.

Each selected record is rechecked in full; final target certificate checking still normalizes and checks the actual original target independently of the index. Internal cached data are not supplied by callers or persisted across queries. An incorrect candidate index can affect search availability but cannot authorize a false UNSAT without a valid original-clause witness. No SAT verdicts. Old solver and tests retained unchanged; the new candidate duplicates the small symmetry-search core to keep the comparison baseline intact (future refactoring may reduce maintenance risk). No implementation-level Lean refinement claim.

Keep the nine-record order, four-attempt cap, 25000 cooperative units, 1.25 seconds, and 80% retrieval reservation from phase 10. Index construction, screening, cached domain retrieval, record validation and proof replay are charged to the same Meter. Cold fallback gets remaining quota/time. Admission costs and common CPU-equivalent metrics still unavailable. Cooperative counters cannot authenticate actual runtime; no hard process timing comparison.

## Actual local paired experiment

Executed against the exact downloaded CI library report, not a reselected corpus. The locally executed search module matched Git blob ab96109bdc53d04519e93fedd4d61206cba9a613 after adjusting package import paths. New standard-library-only independent replay ran against the archived predecessor and newly generated per-case evidence. The candidate ranking was unchanged on all 290 inputs.

| Stratum | Old indexed certified | Shared index certified | Old work | Shared work |
|---|---:|---:|---:|---:|
| Related UNSAT (120) | 100 | 120 | 1334090 | 1032234 |
| Ambiguous UNSAT (30) | 30 | 30 | 326249 | 227917 |
| Deletion SAT (60) | 0 | 0 | 346829 | 329990 |
| Nonmatching SAT (40) | 0 | 0 | 227020 | 218952 |
| Unit UNSAT (40) | 0 | 0 | 228220 | 220072 |
| Total | 130 | 150 | 2462408 | 2029165 |

Recovered all twenty size-eight regressions (17635–17680 units including selection); no lost decisions. Overall reported work down 17.59%; screening/selection proxy fell from 889944 to 833276. All 100 SAT controls and all 40 unit UNSAT controls remain UNKNOWN; the Hall-only route is not a general SAT solver. Cold-only remains less aggregate work (832110) but far lower coverage (46); no end-to-end dominance claim.

New independent audit checked 580 paired reports, revalidated 252 prior certificate occurrences (all three old arms), replayed 150 new positive certificates and 100 explicit SAT models, and checked candidate ordering, quota arithmetic and verdict consistency. Zero detected discrepancies. Three retrieval-budget boundary tests passed (first representative retrieval succeeds at global budget 3169; smaller budgets do not credit retrieval); one corrupted selected record rejected. These boundary tests distinguish retrieval success from any fallback success. Local results are a retrospective regression, deliberately designed after the known failure, not fresh blind evidence.

## Gate and outstanding obligations

New workflow regenerates and audits prior reports, then performs shared-index regression, separate replay and eight JSON hashes. New CI pending at submission. No production route changed or prior gate weakened. Current-main comparisons, third-party blind holdout, multi-family fallback, replicated common hard-process timing, full formal correspondence remain unresolved. P versus NP remains unresolved.
