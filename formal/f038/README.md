# F038 formal verification — semantic kernel, initial proof layer

This branch extends D7I in isolation. Lean 4.19.0 and Mathlib v4.19.0 are selected for reproducible dependency versions. The new Lean source contains proof scripts for coordinate complement involution, factor/model preservation, signed resolution, binary edge soundness, implication paths, implied exclusions, Hall deficiency, and UNSAT transfer through relaxation.

These are semantic theorem statements and proof scripts, not a mechanically verified JavaScript implementation. No local Lean binary or network access was available in the execution environment. The Lean build must actually pass before claiming any mechanically checked theorem. The Proctor compiles the source, prints theorem axioms and rejects admitted proofs. The first remote run is unconfirmed.

Open obligations: formal concrete table/forbidden-row decoding and certificate checker refinement; affine and relational reduction proofs and their implementation correspondence; structural extractor and beam/budget resource accounting; original D7A–D7I composition; raw-selector normalization and physical worker simulation, lexicographic witness and exact clock; bit-level time and space; independent review. No P vs NP resolution, no promotion, no claim of complete formal verification. Main and PR #248 unchanged.

Reproduce from formal/f038 with: lake update; lake exe cache get; lake env lean F038Formal.lean; lake build.

## FV-02 — concrete certificate checker

The new `F038Formal/Certificate.lean` implements a finite, executable Lean reference checker for explicit Boolean row tables, forbidden-row source references, resolution trees, clause weakening, implication paths, and Hall deficiency. Source indices and row lengths are checked against the original tables; a source row must be absent from the allowed rows. Resolution computes its own clause. Path checking validates each step against a derived clause and the final signed endpoint. Hall checking requires a proved group disjunction, placement of every option, a conflict proof for every cross-group pair sharing a hole, and strictly fewer holes than groups. The list-backed entry point additionally rejects out-of-range natural-number hole indices before constructing the typed certificate.

The central theorem `checkHallLists_sound` states that for all coordinate counts, original tables and finite certificates, Boolean acceptance by this reference checker implies that no assignment satisfies the original tables. The theorem uses the FV-01 semantic kernel. It is not a claim that the current JavaScript D7E–D7I certificate schema has been formally refined into this format, that every valid UNSAT certificate is accepted, or that all UNSAT formulas are efficiently refutable. The reference checker permits proof-tree resolution and sound weakening; it does not reproduce the JS producer's policies.

`F038Formal/CertificateTests.lean` contains 16 Boolean acceptance/rejection examples and two fixture UNSAT theorem scripts. It includes an actual two-hop source-path contradiction on a three-coordinate table instance, resolution, malformed source references/rows, truncated/wrong paths, omitted conflicts/placements, invalid hole indices and nondeficient cores. These are authored compile-time tests, not executed evidence until Lean compilation succeeds.

The Proctor now builds the semantic kernel, compiles the checker and fixture scripts, prints theorem axioms and rejects admitted proofs. Run from `formal/f038`:
```sh
lake update
lake exe cache get
lake build F038Formal
mkdir -p .lake/build/lib/lean/F038Formal
lake env lean F038Formal.lean
lake env lean -o .lake/build/lib/lean/F038Formal/Certificate.olean F038Formal/Certificate.lean
lake env lean F038Formal/CertificateTests.lean
```

Status: FV-02 source and proof scripts committed; local Lean unavailable, remote Proctor unconfirmed. No mechanically checked theorem or full verification is claimed yet. Next: verify FV-01/FV-02 compilation, then FV-03 (relational and affine model-preserving reduction certificates), followed by concrete signed-literal/JSON decoding and checker refinement, composition, resource bounds and physical simulation. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## FV-03 — certified relational and affine reduction

`F038Formal/Reduction.lean` extends the concrete table semantics of FV-02. The reference semijoin filters rows using equality of overlapping coordinate bindings, with a proof script that the model set is preserved whenever the supporting factor belongs to the original instance. A finite sequence of support-factor indices is replayed, rejecting invalid indices. Every successful replay preserves the model predicate pointwise, not merely satisfiability. This is a conservative whole-list semijoin reference, rather than a direct implementation/refinement of D7A's pair-specific deletion log, quotienting, or derived permutation factors.

The GF(2) reference equation checker derives equations from original allowed rows (validating the mask length and checking every listed row), adds equations, and cancels two explicitly present occurrences of a coordinate. Reflexive equations permit free coordinates without imposing any original constraint. The soundness scripts establish that accepted equations hold in every original model, and that a checked 0=1 equation implies UNSAT. The affine reconstruction map requires a checked equation for every original coordinate and uses the designated free coordinates as a projection; each source model reconstructs exactly. The residual is an executable exact pullback predicate evaluating the original tables on the expanded assignment, not yet a materialized width-three reduced table set. Any accepted residual witness expands to an original model; every original model projects to an accepted residual witness, provided the map certificate checks. No claim of arbitrary reduced assignments being canonical, lexicographic preservation, rank optimality, or correspondence to the D7B producer.

Main proof scripts:
- `relationalReplay_exact`: pointwise model equivalence after certified semijoin replay.
- `eqDerive_sound`, `affine_contradiction_sound`: equation and contradiction certificate soundness.
- `affineMap_reconstruct`, `affine_reduction_exact`: reconstruction and equisatisfiability.
- `relational_affine_compose`: equivalence of original satisfiability and accepted pullback witnesses after both stages.

`F038Formal/ReductionTests.lean` supplies 17 Boolean/equality examples and two fixture theorem scripts, including pruning, invalid indices, GF(2) contradiction, malformed masks, invalid cancellation, and accepted/rejected reconstruction maps and residual witnesses. These are authored tests, not executed Lean evidence. The Proctor now compiles the reduction module and its fixtures, reports theorem axioms, and checks for admissions. After the FV-02 build commands, run:
```sh
lake env lean -o .lake/build/lib/lean/F038Formal/Reduction.olean F038Formal/Reduction.lean
lake env lean F038Formal/ReductionTests.lean
```

FV-03 is committed as a reference implementation and proof layer. Lean is not installed locally, and remote workflow completion is not confirmed; no theorem is claimed mechanically checked. Remaining: obtain a successful Lean build, formalize concrete D7A/D7B log and raw certificate decoding/refinement, quotient/pivot correspondence and materialized residual checks, then algorithm/resource and physical-machine correspondence. FV-04 is the implementation-to-specification refinement stage. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.
