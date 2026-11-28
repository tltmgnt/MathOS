# Phase 12 — multi-family certificate routing

## Verified predecessor

PR #323 was already merged into main when inspected (merge 7d6d8eba599928d346b9953917019d00ec97bd43). Run 46157985319 evidence passed. Downloaded artifact 15268247977 (536440 bytes) matched SHA256 c5193fbdf955137fe2d8af3f68203d8deaf55a1f0beb8813c8cce10a1ca0afbb, ZIP CRC and all eight JSON hashes. Ran all four standard-library-only predecessor audit scripts locally against extracted reports, reproducing all four audit JSON objects exactly. This includes 150 new shared-index certificates, all 20 size-eight regressions recovered, zero lost decisions, and reported work 2029165 vs 2462408 on 290 cases. Earlier certificate occurrence counts overlap; do not sum as unique proofs. New branch based on main 07bf201843925374f80746832f643e25c8d00918, including parallel orbit-split work. No merge performed.

## Candidate and mathematical obligations

The experimental route order is quick empty/opposing-unit probe, shared Hall library, ordinary unit propagation plus renamable-Horn model completion, then existing partial XOR subsystem. The quick probe consumes at most 10% of the shared budget; its positive result must pass full input validation and original-clause unit trace replay. Hall receives the remainder (its existing internal 80% retrieval allocation and cold Hall fallback unchanged); if UNKNOWN with work/time left, propagation receives half of the remaining allowance and XOR gets the rest. No-Hall ablation removes the Hall route. Unused reported units carry forward. Hall can exhaust the remaining budget and prevent later routes; no guarantee of a fallback opportunity. The policy is a new experimental choice, not optimal. No existing route is replaced.

For a unit trace, each cited original clause is unsatisfied by the current partial assignment and has exactly one unassigned literal (or zero at the final conflict). Inductively all satisfying assignments must agree with each inferred literal; an empty residual proves UNSAT. Tautological clauses are skipped, duplicates normalized for the inference, and original indices retained. A direct SAT model is accepted only after checking the original formula.

A sign vector makes a formula Horn exactly when no pair of distinct literals in any normalized clause becomes simultaneously positive. This is a 2-SAT condition on the signs (implication graph and SCCs). Signed permutation preserves unit propagation. In a renamable Horn formula, if unit closure does not produce a conflict, assign unforced transformed variables false: a Horn clause with all body literals true would otherwise have forced its head or yielded a conflict. Hence this gives a satisfying completion on that restricted class if resources suffice. A failed recognition or candidate model yields UNKNOWN. The code follows the existing signed-Horn polarity criterion, adds direct model completion, and replays the original unit trace without relying on recognition. Pairwise constraints can cost O(sum of squared clause widths); no claim of general linear-time SAT. Existing affine route reconstructs small-width parity equations and uses GF(2) elimination; a dual is accepted only if each equation is implied by its cited original clauses and their XOR is 0=1. Models are checked directly. These standard mathematical arguments do not establish unrestricted completeness or implementation refinement.

## Local execution and reproducibility

Local new module/probe/audit matched exact committed Git blobs after import-path adjustment: 4b6cb7a79d0d56a9cc202e91653a08cc6ff2040d, fdb31ff67490f4882d247c03883a4206f99d92d8, 2dc28319c234188470aae4fa0da2fa1e28536d18. The copied affine module matched repository blob 877110bbb37fc624f84b3bf4a4df3a5e8b496e87. Local git clone was unavailable (DNS), so the affine module used local dependency slices of Budget/validate and the SAT branch of the existing Hall verifier; full package execution must be confirmed by CI. Local Python 3.13.5, CI configured for 3.11. Exact downloaded 290-case corpus plus 60 generated cases (seed 190207): 20 signed Horn chain twins, 16 signed affine prism twins, 24 balanced random width-three formulas (first four each truth-table SAT/UNSAT at each of n=8,10,12). All 60 distinct and zero exact normalized overlap with archived 290; no signed-orbit disjointness or blind selection claim. Post-run manifest digest ca28a31f32c5ed55137abd7c246b9ce794d7b5c9403b6fc285e01196c638bd3a and nine-record library digest 38183b12d698ccb6d4467b33a45dfc4620de6931d446b2ca69ace216848ffdf4 pinned for reproduction, not preregistration.

Ran 1050 isolated local arm processes (rotated execution order), each with 25000 cooperative units, 1.25 cooperative seconds, one CPU affinity, 512 MiB RLIMIT_AS, 3-second RLIMIT_CPU and parent 3-second response poll. No process-resource outcomes observed. Reported work counters have heterogeneous units; not exact CPU instruction equality. Timings are single runs and include fork overhead, not statistically robust. No training/admission cost charged. No existing production routes altered.

| Family | Cases | Hall only | Multi-family | No Hall |
|---|---:|---:|---:|---:|
| Related Hall UNSAT | 120 | 120 | 120 | 3 |
| Ambiguous UNSAT | 30 | 30 | 30 | 0 |
| Unit UNSAT | 40 | 0 | 40 | 40 |
| Deletion SAT | 60 | 0 | 0 | 0 |
| Nonmatching SAT | 40 | 0 | 0 | 0 |
| Signed Horn (10 SAT, 10 UNSAT) | 20 | 0 | 20 | 20 |
| Affine (8 SAT, 8 UNSAT) | 16 | 0 | 16 | 16 |
| Random3 (12 SAT, 12 UNSAT) | 24 | 0 | 0 | 0 |
| Total | 350 | 150 | 226 | 79 |
| SAT | | 0 | 18 | 18 |
| UNSAT | | 150 | 208 | 61 |
| UNKNOWN | | 200 | 124 | 271 |
| Reported work | | 2227203 | 2633188 | 1580990 |

All 150 prior Hall decisions preserved, +76 new decisions relative to Hall alone (58 UNSAT and 18 SAT). All forty unit contradictions recovered (35160 units vs 220072 Hall-only); all fresh Horn and affine twins certified. No-Hall ablation loses 147 decisions compared to full candidate, solves three related Hall cases by propagation. Multi-family work increases 18.2% versus Hall-only; there is no efficiency dominance claim. Critically all 24 random3 and all 100 archived SAT controls still UNKNOWN. The 124 unknown include 112 SAT and 12 UNSAT. Ten full-candidate propagation attempts exhausted quota, though no process limit was hit. This indicates the need for general adaptive fallback and better gating, not further specialization alone.

Independent standard-library-only audit replayed 455 positive certificate occurrences (150 Hall, 226 multi, 79 no-Hall), all 350 reference labels (190 archived UNSAT premises, 118 explicit SAT models, 24 exhaustive random3, 10 fresh unit contradictions and 8 fresh affine duals), nested Hall/route quota arithmetic for 1050 reports and the prior shared-index evidence. Four deliberately corrupted proof controls rejected (unit, SAT model, affine RHS, Hall bucket). Separate 700 random signed-Horn development tests (seed 120920, n<=8) agreed with exhaustive bitset truth tables, 143 SAT/557 UNSAT. The latter are probe-level checks, not exported per-case evidence. No detected incorrect verdict. Independent audit cannot authenticate actual execution expenditure, negative search completeness or timings.

## Gates and limitations

New CI regenerates predecessor reports, runs the full package experiment, pins the manifest/library digests, runs independent replay and hashes ten JSON files. Separate formal job recompiles existing CompositePaths, SignedHorn, HallCapacity and XorSubsystem abstract lemmas and checks all twelve named theorems axiom-free. No new Lean proof of Python implementation; local Lean unavailable. New CI pending, no completed-run claim. General adaptive fallback remains to be connected; current-main adaptive/native-XOR and other v26–v30 comparisons, external independently selected blind holdout, repeated hard-process performance study, and code-to-semantics refinement remain outstanding. This is archived regression plus fresh synthetic development, not unrestricted SAT. P versus NP remains unresolved.
