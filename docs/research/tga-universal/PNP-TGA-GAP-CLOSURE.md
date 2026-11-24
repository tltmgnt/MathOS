# TGA-PNP — Constructive topological gap closure and universal proof obligations

Baseline: F030 b5ab1ae6d9c0e2fd0cae0ea6e13b69ac53689ab6;
strict run 45429725551 succeeded. This is a companion research branch
for F031–F036, not a renumbering or replacement of prior milestones.

## Audit and proof strategy

TGA-U001 section 3 derives the standard class-level bridge and identifies
the unrestricted polynomial algorithm as missing. PNP-B006 proves
tractability for disjoint AND blocks with affine coupling. F024 shows why
unrestricted SAT cannot simply be assumed to admit a polynomial reduction
to that tractable language. F025/F026 supply scoped decomposition and
F027–F030 supply backdoors, propagation and counterfamilies. No examined
source establishes unrestricted P=NP or P!=NP.

Use TGA as a mathematical proof strategy, with separate topology of SAT
constraints and topology of proof obligations. Neither graph bookkeeping
nor a closed modeled route by itself constitutes a proof.

## Constructive overlap gap theorem

After sparse normalization and tautology/duplicate removal, group clauses
by their variable scope. Let B_1,...,B_t be the distinct scopes (use an
empty bag for an empty formula). Each has at most three variables.
For every pair of bags assign weight |B_i intersect B_j|; include zero
weight edges. Define W* = sum_i |B_i| - |union_i B_i|. Compute a maximum
weight spanning tree T using deterministic descending Kruskal, and set
Delta = W* - w(T).

For each occurring variable v let d_v be the number of bags containing v.
The subgraph T[v] induced by those bags is a forest, hence its number
of edges is d_v - c_v where c_v counts its connected components.
Summing over v counts each edge exactly its overlap weight. Therefore
W* - w(T) = sum_v (c_v - 1) >= 0. Zero holds iff every variable has the
running-intersection property. Since T maximizes w, Delta=0 iff a
join tree on these exact scopes exists. This is a combinatorial overlap
deficit, not a claim that it equals homology of an arbitrary complex.

For Delta=0, F026 validates the constructed decomposition and computes
exact feasible assignment tables. Child and parent assignments agreeing
on their overlap glue to a global assignment because all occurrences of
each variable form a connected subtree. A feasible root entry exists
iff SAT. The inherited independent recurrence verifier checks UNSAT tables;
SAT witnesses are checked on the original compacted formula, including
the dropped tautologies. Thus the representation and decision are
constructive on this scoped class; topology alone does not decide SAT.
For Delta>0, invoke bounded F030 with explicit node_limit; UNKNOWN is
not a decision. The wrapper verifies the corresponding evidence.

Construction uses O(t^2) candidate edges of constant-width intersections
and polynomial sorting/union-find work. F026 tables have at most 8
assignments per bag, and its verifier examines at most 64 combinations per
tree edge, plus validation and clause placement. Sparse IDs require bit
length accounting. These finite-list operations admit polynomial
implementations on a standard machine on the zero-gap class, but this
code does not yet prove a bit-machine refinement. For positive gap the
fallback may require exponentially many nodes and output records. A
positive deficit does not exclude some other small-width decomposition.
A universal gap-closure algorithm remains open.

## Obstruction: local consistency and topology are not enough

For n>=3, take n binary constraints around a cycle; encode equality by
two signed clauses and pad with repeated literals. For the second
formula change the last edge to inequality. The unsigned scopes and
overlap graph are identical. Each bag intersects only neighboring
bags in a single variable, and every edge relation projects onto both
Boolean values at either endpoint. Thus both systems remain nonempty
under every pairwise semijoin pass, including the fixed point.
All equalities have a model. With one inequality, transitivity along
the equality path makes the last inequality impossible. Both formulas
have Delta=1: the maximum tree uses n-1 overlap-one edges while W*=n.
This is an all-n obstruction to unsigned topology or pairwise
compatibility as a complete SAT invariant. It is not a lower bound
on SAT; parity reasoning solves this family efficiently.

The new Lean declarations formalize endpoint support, the opposite
triangle outcomes and equality propagation only. The full forest
identity, Kruskal implementation, F026 refinement and bit-machine
complexity are not formalized by these declarations.

## Universal bridge and F031–F036 integration

The new executable obligation graph retains the TGA-U001 equality
and separation alternatives and adds a modeled TGA route. It is
fail-closed: all six new universal leaves are open.

- F031: component-aware recursion and constructive topology; charge
  all decomposition, gap transformations, witness and certificate work.
- F032: adversarial invariants and actual complexity barriers;
  distinguish graph topology, relation labels, parity and general SAT.
- F033: prove or refute a universal complete obstruction invariant and
  constructively efficient gap closure. Polynomial-size state space,
  termination and uniform total bit time require independent proofs.
- F034: refine the actual algorithm to standard SAT encoding and
  computational-machine semantics, not a self-defined cost counter.
- F035: independent mathematical reconstruction, literature comparison,
  and review of each assumption and dependency.
- F036: only an unconditional class theorem warrants resolution.

A possible universal TGA theorem would require a faithful representation
for all inputs, complete sound closure, total termination, and uniform
polynomial bit time including all intermediate representations. These
are not assumed axioms. An invariant whose computation requires solving
SAT is circular as an efficiency argument. Refuting one invariant does
not refute every TGA approach or prove P!=NP.

Reproduce:
    python -m unittest discover -s tests -p 'test_tga_pnp_gap_closure.py' -v
    python -m mathos.research.tga_pnp_gap_closure
    lean -DwarningAsError=true formal/ProctorTGAGapClosure.lean

New CI must establish the actual test and axiom outcomes. The 4,418
bounded decisions, small exhaustive spanning-tree comparisons, five
cycle sizes and 64-variable chain are controls, not universal complexity
proofs. No novelty or independent review is claimed.
