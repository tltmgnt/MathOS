# PNP-F030 — Adaptive propagation, structural compression and search obstruction

Baseline F029 commit 61c30110117c1cf5a58439ac4e9b0a076e2d14b3;
dedicated strict CI run 45428442646 succeeded. Inherited work is
unchanged. **P versus NP remains open.**

## Track A: adaptive exact search with bounded work

Normalize occurring variable IDs using F029 sparse_input and preserve
the inverse map. Compress clauses using F027. At each node:

1. Restrict the clauses by the current assignment. Drop satisfied
   clauses; retain original indices of the other clauses.
2. Repeatedly assign units and pure literals, prioritizing empty-clause
   detection. A unit is forced; setting a pure literal to true preserves
   existence of a model (any prior model can change that variable
   without falsifying a remaining clause).
3. Recompute exact renamable-Horn recognition on the current residual.
   If successful, use Horn closure and map back the assignment. In
   fact, after complete unit propagation a nonempty-clause Horn
   residual with no units has the all-false model in its new orientation.
   The Horn conflict path is defensive, not required on that fixed point.
4. Otherwise split on the variable of greatest residual occurrence
   count, with deterministic ID and sign tie breaks. Recompute all
   simplifications on both branches. Visit the majority-sign branch first.

The iterative solver returns SAT, UNSAT, or UNKNOWN (node budget
exhaustion). It checks SAT witnesses against the original compacted
clauses, reporting a sparse witness with original IDs; omitted variables
are false. UNSAT evidence is a preorder tree: each node records unit
and pure assignments and then either a false original clause, Horn
conflict trace, or a split with both children. The independent replay
reconstructs residuals directly from original clauses, validates every
propagation and terminal step, and rejects missing or trailing children.
Soundness follows from restriction, pure-literal equisatisfiability,
Horn conflict soundness and both-branch exhaustion. Completeness
without a binding budget follows from strict decrease of unassigned
variables along splits and finite propagation. These are mathematical
arguments; the implementation is not kernel-refined to them.

## Cost and scope

Let r be the number of occurring variables, m the clause count, L the
node budget, and V the number of visited nodes. Sparse normalization
keeps r <= 3m, irrespective of the binary-encoded declared variable count.
At most r+1 residual passes per node, one 2-SAT recognition, and at
most r+1 Horn rule passes; each pass inspects at most m width-three
clauses. Sorting, indexing, SCC graph construction, branch ordering,
assignment copying, and output must also be charged. The abstract
per-node work and certificate record length are polynomial in r+m;
the full tree contains at most 2^(r+1)-1 nodes and V <= L. Replay
cost is polynomial in the formula plus the explicit tree size, not
necessarily polynomial in the formula alone. Actual bit-machine
refinement remains open. UNKNOWN is not a total SAT decision.

## Track B: two distinct obstructions

The F029 family contains all four clauses (±a_i, ±b_i, c) for each
disjoint pair. Pure c is set true at the root, eliminating the whole
formula: one visited node, zero splits, although the previous syntactic
minimum deletion was t. This is an exact family-specific improvement.

**Static obstruction after preprocessing.** For each of t disjoint
triples, include seven of its eight sign patterns, omitting the
all-negative clause. Connect consecutive triples by a positive
two-literal clause (represented by repeating one literal). The all-true
assignment satisfies the connected formula. Every variable occurs in
both polarities, every clause has at least two distinct literals, and
root unit/pure preprocessing makes no change. On any two surviving
variables of one triple, all four sign pairs occur, forbidding a
uniform renaming. At least two deletions per triple are necessary.
Deleting the first and third variable of each triple suffices,
including the connecting clauses, so the exact minimum is 2t.
This rules out universally logarithmic static deletion after these
preprocessing rules, not efficient adaptive search.

**Exponential lower bound for the implemented branching heuristic.**
Take t disjoint four-variable gadgets. For each of their four
three-variable subsets, include all six mixed-sign clauses.
Each gadget admits both uniform assignments (all true and all false).
Each untouched gadget variable has 18 occurrences, versus eight for
each variable of an additional disjoint UNSAT core (all eight signed
clauses on three variables). The core has no pure literal, no unit,
and cannot be renamed Horn. It is unchanged until a core variable
is assigned. Each untouched gadget likewise has no units or pure
literals. The heuristic must split in a gadget rather than in the
core whenever an untouched gadget remains, since 18 > 8.

For each of the 2^t vectors of desired first-split values, follow a
path as follows. The first split in an untouched gadget permits either
value, since both uniform assignments are models. After this split,
unit and pure simplification preserve satisfiability of that component;
whenever a later split is made there, choose a child preserving its
satisfiability. No gadget then supplies a conflict on this path. The
core cannot be discharged by renaming or propagation before a split.
Each first-core split node therefore has fixed a first-split value in
every gadget. All 2^t vectors are reachable in this way. They reach distinct nodes in the unbudgeted
UNSAT tree. Thus at least 2^t visited nodes are required. The input has
4t+3 variables, 24t+8 clauses and O(t log t) bits. This is a
superpolynomial lower bound on this deterministic search policy,
not on SAT or other branching policies. A component-aware algorithm
can solve the constant-size core first and avoid the obstruction.

Finite controls enumerate 4,418 formulas; check six sizes of both
static families and four sizes of the heuristic lower-bound family.
Tests also attack certificate completeness, pure/forced assignments,
sparse input and budgets. Five local Lean declarations cover
propagation identities and exhaustive binary refutation only.
Pinned strict CI is required; no claim of successful new replay
before actual results. No novelty or independent review is claimed.

## Next gate

F031: component-aware exact solving and total bit-complexity accounting,
including parsing, preprocessing, search-tree construction and replay.
Use the explicit exponential counterfamily as a regression. Analyze
remaining connected obstructions after decomposition. Do not promote
the resulting scoped bounds into a universal polynomial theorem.
F032–F036 remain open.

Reproduce:

    python -m unittest discover -s tests -p 'test_tga_proctor_adaptive_propagation.py' -v
    python -m mathos.research.tga_proctor_adaptive_propagation
    lean -DwarningAsError=true formal/ProctorAdaptivePropagation.lean
