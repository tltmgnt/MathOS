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

Stage 3a passed pinned Lean 4.14.0 CI in PR #12.

## Stage 3b: raw candidate generation for finite AND/OR formulas

[FiniteCandidateGeneration.lean](FiniteCandidateGeneration.lean) introduces a
structurally recursive finite candidate-set generator for the `RouteFormula`
model. Assumed-true leaves produce the empty requirement, open leaves produce
singleton requirements, AND combines candidates by union and OR concatenates
alternatives. Structural recursion ensures termination for finite syntax.

Lean theorem `eval_iff_candidate` characterizes evaluation as coverage of
at least one generated candidate; the converse establishes soundness.
`minimalCandidateSets_sound` establishes minimality of every pruned output
relative to the formula semantics. `minimalCandidateSets_complete` proves
that every abstract minimal solution corresponds to an output up to mutual
predicate inclusion, while `minimalCandidateSets_antichain` reuses Stage 3a.

**Boundary:** a formula is an unfolded, finite, acyclic dependency tree.
This does not formalize a sharing-aware, indexed DAG, graph validity checking,
memoized recurrence, Python refinement, running-time guarantees or the
mathematical correctness of any authored proof-route edge. Accordingly the
broader `GRAPH1` claim remains open; the next milestone is an explicit
finite DAG representation with a proved refinement to this recurrence.

Build the new imported modules with the same pinned Lean 4.14.0 toolchain:

```sh
lean -o formal/BooleanRoutes.olean formal/BooleanRoutes.lean
lean -o formal/FiniteCompletionPruning.olean formal/FiniteCompletionPruning.lean
LEAN_PATH="$PWD/formal" lean formal/FiniteCandidateGeneration.lean
```

Stage 3b is a candidate until the above commands pass on GitHub Actions.

Stage 3b passed pinned Lean 4.14.0 CI in PR #13.

## Stage 3c: topologically indexed finite DAG semantics

[FiniteRouteDAG.lean](FiniteRouteDAG.lean) represents a finite directed
acyclic graph in topological insertion order. At each insertion, a node
can only refer to an earlier node (`Fin n`), allowing shared references
while ruling out cycles and forward edges by construction.

The forward interpreter computes Boolean truth at every node and separately
generates raw completion candidates. The `unfold` interpretation expands a
node into the already verified `RouteFormula` model. The two refinement
lemmas show Boolean evaluation and raw candidate lists coincide with those
of the unfolded formula. Stage 3b then gives soundness, completeness up to
mutual predicate inclusion, and an antichain property after pruning.

The scope is binary AND/OR nodes with an assumed-true or open leaf.
This model does not cover arbitrary-length OR-of-AND routes, string-index
validation, memoized Python execution, or runtime/resource bounds. The
broader `GRAPH1` and Python-refinement obligations remain open.

Reproduce the new check using pinned Lean 4.14.0 with
`LEAN_PATH="$PWD/formal"`:

```sh
lean -o formal/BooleanRoutes.olean formal/BooleanRoutes.lean
lean -o formal/FiniteCompletionPruning.olean formal/FiniteCompletionPruning.lean
lean -o formal/FiniteCandidateGeneration.olean formal/FiniteCandidateGeneration.lean
lean formal/FiniteRouteDAG.lean
```

Stage 3c is not kernel-verified until its CI check passes on the relevant
commit. Passing CI certifies only the precisely stated Lean theorems.
