# MathOS Lean verification — bounded stage 1

This directory contains a small Lean 4 source file for the Boolean logic underlying the
finite AND/OR dependency model in `mathos/proof_analysis/gap_analysis.py`.

## Scope

`ProofRouteLogic.lean` defines `Covers required available` as predicate-set
inclusion and `UnionNeeds` as union. The key theorem `covers_union_iff`
states that satisfying every obligation in the union of two dependency sets
is equivalent to satisfying each set separately. `covers_trans` establishes
monotonicity by inclusion. `alternative_route` constructs one side of an
OR alternative.

These are **small logical lemmas**, not the full correctness theorem `GRAPH1`.
The following remain open:

1. Formal definitions for finite acyclic DAGs and the actual completion-set recurrence.
2. Termination, soundness, completeness, and inclusion-minimality of recurrence.
3. A concrete refinement proof connecting Python implementation to abstract semantics.
4. Validation of authored mathematical inferences and external theorem references.
5. A Lean formalization of the SAT polynomial support theorem `SAT1`.

## Reproduction

Pinned toolchain: `leanprover/lean4:v4.14.0`.

```sh
lean --version
lean formal/ProofRouteLogic.lean
```

GitHub Actions runs the source under the pinned Lean toolchain in
`.github/workflows/proof-route-lean.yml`. Passing CI would certify only
the exact lemmas accepted by the Lean kernel under its trusted base, not
the broad MathOS or Millennium claims.

**At authoring time:** Lean was unavailable in the local execution environment.
The source is a candidate pending actual compiler replay. Do not mark it
`FORMALLY_VERIFIED` until the corresponding check succeeds and the
version and imports are recorded.

## Stage 2: finite Boolean formula semantics

[BooleanRoutes.lean](BooleanRoutes.lean) introduces inductive AND/OR syntax,
an assumed-true leaf and an open obligation leaf. It proves by structural
induction that satisfaction is monotone in the accepted-open-leaf set; it
also establishes invariance under mutual set inclusion, soundness of the
abstract minimal-completion predicate, and the antichain property of minimal
completions.

These theorems do **not** prove that Python enumerates all minimal completion
sets. This remains `GRAPH1` pending a finite DAG representation,
a formalized enumeration algorithm, termination and completeness proofs.

The source is a proof candidate until the Lean workflow actually passes on
the commit containing it.

## Stage 3a: finite candidate pruning

[FiniteCompletionPruning.lean](FiniteCompletionPruning.lean) gives a predicate-set
model of inclusion-minimality and proves that filtering a finite list of
candidates removes precisely the candidates strictly dominated by another
candidate. It establishes soundness relative to the supplied candidate list,
the antichain property, and exact membership characterization.

It does **not** prove candidate generation is complete or that the recursive
DAG implementation terminates for every abstract input under resource limits.
Predicate inclusion is decided classically (noncomputable), so this is a
proof-level model, not a verified extraction of Python's implementation.

The source remains a proof candidate until the pinned Lean CI job passes.
