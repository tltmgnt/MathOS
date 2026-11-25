# F035 — Algebraic route and affine projection barrier

PNP_RESOLUTION_STATUS = OPEN.

A system of GF(2) affine equations is closed under the pointwise XOR
of any three satisfying assignments. Existential projection onto any
visible coordinates preserves this closure: XOR the three extension
assignments, and restrict the result. This applies regardless of
the number of auxiliary coordinates or the equation support sizes.

The positive three-literal clause is not closed under ternary XOR:
100, 010 and 110 satisfy it but their XOR is 000. Consequently no
exact encoding of its satisfying relation as a projection of affine
equations is possible, even with arbitrarily many auxiliary bits.
This is a relational encoding barrier, not a lower bound on algorithms
that use XOR reasoning plus nonlinear or other constraints.

A general clause does have an exact factored polynomial encoding
over GF(2): multiply (x_v + b) over all its literals (v,b), and
require the product to equal zero. For width-three clauses this
has syntactic degree at most three. The new module proves this
pointwise equivalence, including empty clauses and repeated literals.
The encoding is compact, but nonlinear equation solving is itself
the general SAT problem; Gaussian elimination alone cannot solve it.

The mathematical gap is an efficient exact nonlinear decision
operation with polynomial total resource bounds, not a compact
encoding. This also explains why simply replacing CNF by an affine
system cannot establish P=NP. No claim of new complexity separation.

15 public candidates, 32768 polynomial checks, 4096 closure checks
and one non-affine witness check. Strict replay required.
