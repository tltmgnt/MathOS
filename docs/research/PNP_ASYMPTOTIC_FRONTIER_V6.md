# MathOS v6 — asymptotic family convergence and certified parity reduction

This extension addresses a specific v5 counterexample rather than expanding
a finite training set and calling it a theorem. It recognizes a signed
triple-block class, reduces it to 2-CNF, checks local equivalence and an
independent decision certificate, and supplies a Lean theorem for arbitrary
finite lists of abstract signed blocks. Neither P = NP nor P != NP is proved.

## Run

    python -m mathos.research.pnp_asymptotic_frontier --checkpoint artifacts/pnp-v6.json
    python -m mathos.research.pnp_asymptotic_frontier --sizes 4 8 16 24 --c 1
    python -m mathos.research.pnp_asymptotic_frontier --input cnf.json
    python -m unittest discover -s tests -p 'test_pnp_triple_parity.py' -v

Input is JSON with n and clauses, signed nonzero literals 1..n.
The recognizer returns no candidate outside its explicit grammar.
Finite family probes are capped at n=24 and use cooperative resource limits.

## Constructive route and proof

Group normalized clauses by their three distinct variables. Require exactly
six distinct clauses per group. A ternary clause forbids one Boolean triple.
Require the two unexcluded triples to be complementary. Let one allowed
triple be (s,t,u). Exactly the same assignments are described by the pair
constraints x XOR y = s XOR t and x XOR z = s XOR u: choosing x determines
both remaining bits, leaving precisely the two complementary assignments.
Each pair constraint is expressible as two binary clauses. Thus the
conjunction of all blocks is pointwise equivalent to a 2-CNF, even when
blocks overlap, and SAT can be decided in polynomial time on this class.
The reduction emits at most four binary clauses per six distinct input
clauses before deduplication. Grouping, local enumeration, normalization
and implication-graph solving have polynomial overhead. The verifier
independently checks all eight assignments of each block, assembly, and
the v5 2-SAT witness or contradiction certificate. A satisfying assignment
also gets checked against the original normalized formula. The constant
decision output has width zero; the intermediate 2-CNF need not have
low treewidth.

Lean proves the local equality, pointwise equivalence for all finite lists
of abstract signed blocks, existential SAT equivalence, and satisfiability
of all lists seeded by a common assignment. It does not formalize the
Python recognizer, complexity bounds, binary encoding, or v5 obstruction.
CI enforces the same axiom-free policy as v5.

## Infinite family obstruction to v5 grammar

For every n>=4, let the seed assign x1=true and all other variables false.
For every triple of distinct variables, include the six clauses excluding
all assignments except its seed restriction and complement. There are
6*C(n,3) clauses, and the primal graph is K_n, hence treewidth n-1.
Every pair belongs to a triple, so any model has the same pair parity as
the seed on all pairs; hence models are exactly the seed and complement.
Neither is uniform. The formula is ternary, so not 2-CNF. For any fixed
pair in a triple, the six forbidden patterns project onto all four
possible pair patterns: deleting two complementary triples cannot delete
both extensions of any one pair pattern. Under any sign renaming those
four patterns remain. In particular some clause has both literals
positive, so no renaming makes the formula Horn. A satisfiable formula
has no contradictory core. These facts rule out all five v5 routes, for
this family only. The v6 parity route solves it.

For the input proxy N=n+m+L=n+24*C(n,3)=Theta(n^3), every fixed c gives
floor(c log2 N)=O(log n), whereas width is n-1. Thus the family eventually
violates the original logarithmic-width criterion for every fixed c,
yet admits the polynomial semantic reduction above. This is an asymptotic
counterexample to treating the original width condition as necessary
for polynomial solvability, not a new complexity separation.

For an UNSAT companion, flip the local seed at x1 only in block (1,2,4).
Its constraint on x1 XOR x2 contradicts block (1,2,3), so every such
family member is UNSAT. The same polynomial reduction yields a checked
opposing-path contradiction. No hardness claim is made for either family.

The asymptotic family, width and running-time arguments above are written
mathematical arguments, not machine-checked complexity theorems. Finite
probes do not establish universal obligations. The CLI explicitly records
formal verification as not performed; the separate CI Lean check covers
the stated abstract theorems only. The next frontier is broader relation
grammars, mixed residual constraints, and formalized complexity accounting.
