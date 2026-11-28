# FV-10 — Concrete affine residual and operation-log refinement

Status: scoped mechanized verification PASS; executable audit PASS; universal implementation refinement and independent review OPEN.
Prior FV-09 scoped mechanized checkpoint a1288c6699c3abedda0378de956cd34794aa1c39 passed Proctor run 68.
PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Mathematical scope

ResidualRefinement.lean introduces bounded local tautology checks and exact removal, same-ordered-scope row intersection, merge semantics, row-set equality (independent of enumeration order or duplicates), factor-set comparison, composition with FV-09's local materialization, and zero-dimensional residual lifting with a dummy coordinate constrained false. It also states sound UNSAT transfer from a checked simplified residual Hall certificate. The implementation permits empty-scope factors and preserves constant contradictions instead of silently dropping them.

AffineReplay.lean checks equation proof claims against the existing FV-03 source, XOR addition and pair cancellation proof kernel, and states soundness of a checked contradiction. The concrete D7B exporter translates source masks, actual row additions and pivot substitutions into these proof trees. Reordering is justified by adding a reflexive pair and canceling the first two occurrences, not by an unproved permutation assumption. Actual source tables bind all proof checks. The translator is untrusted; Lean acceptance of generated claims is required. Proof trees can grow substantially and no polynomial certificate-size bound is claimed.

## Executed evidence

The exact committed JavaScript modules were loaded and executed in an independent JS runtime. The audit checked 128 deterministic small instances against exhaustive original model enumeration and five named concrete fixtures. Counts exclude the five named fixtures from the random-instance totals.

| Check | Result |
|---|---:|
| Random instances | 128 |
| Random contradiction outputs | 17 |
| Random equation claims | 496 |
| Equation/model evaluations (all fixtures and random inputs) | 3223 |
| Corrupted log rejection controls | 4/4 |
| Generated Lean fixture sources | 5 |

The generated fixtures cover duplicate-scope merging with signed substitutions, chain substitutions, zero-free padding, a contradiction with two actual row additions, and an empty source factor. The generator emits decidable source-log, affine map and local materialization checks where applicable. The contradiction cases emit source UNSAT theorems. The nonzero-free narrow cases emit pointwise residual equivalence theorems; the zero-free case emits existential equivalence. All five generated sources compiled successfully in Proctor run 85. Random semantic checks on UNSAT instances are vacuous for equation entailment, so they are not a substitute for proof checking.

## Verification gate

The Proctor workflow compiles the new modules and fixtures, runs the concrete executable audit, checks the five generated Lean sources and expands the strict static named theorem inventory from 111 to 132. Generated theorem sources are compiled and their dependency reports appear in the compile log separately from the static inventory. Proctor run 85 passed this build and the strict 132-theorem inventory.

## Mechanized verification result

Proctor run 85 completed successfully at exact checkpoint 87f61040754c5eb0ace8af518aaa803548812d83. All seven executable audit suites, the Lean build including the five generated fixtures, and the 132 named theorem axiom checks passed. F038_FV10_RESIDUAL_REFINEMENT_OK and F038_FV08_AXIOM_GATE_OK were emitted. The five generated theorem dependency reports separately show only the approved axioms. The generated chain fixture has a nonfatal unused-variable warning.

- Run: https://github.com/tltmgnt/MathOS/actions/runs/46096489544
- Evidence: https://github.com/tltmgnt/MathOS/actions/runs/46096489544/artifacts/15243588815
- Evidence ZIP SHA-256 reported by GitHub: ee6607782aef5cbe3f7bc9f68c1ba79b21d4474923f56fff0ca0b2313fa18f96

Proposed FV-11: checked relational operation-log translation, starting with actual semijoin deletion and exact table preservation.

## Remaining obligations

Universal correspondence of JS parsing, producer operations and typed proof inputs; relational operation-log translation; constant-conflict and wide fallback paths; complete physical compiler refinement, exact clock formula, selector semantics, total bit complexity, and independent human review remain open. This is not a proof of general solver completeness or P vs NP. No main or production promotion.
