# F036 — Compact monotone circuit equivalence barrier

PNP_RESOLUTION_STATUS = OPEN.

A candidate exact global circuit-equivalence operation would not be
a routine normalization step: it would already decide general SAT.
For a CNF F, replace each literal by a separate positive input
rail r_(v,b). Define monotone circuits

    A(r) = AND_(C in F) OR_(l in C) r_l
    B(r) = OR_(v occurring in F) (r_(v,0) AND r_(v,1)).

Then A OR B equals B for every rail assignment iff F is unsatisfiable.
For a satisfying original assignment, enable exactly the true literal
rails; A=1 and B=0 distinguish the circuits. Conversely any
distinguishing rail assignment has A=1 and B=0. Decode x_v=r_(v,1).
Every selected positive literal is true, and every selected negative
literal is true because no pair of opposite rails is simultaneously
enabled. Missing rails may be assigned by that same decoding rule.
All clauses are therefore satisfied. Empty clauses and formulas are
included.

This is a polynomial-time reduction (linear in literal occurrences
and rows apart from copying the encoded identifiers). The actual
implementation keeps repeated variable occurrences; deduplicating
is unnecessary. The grouped unbounded-fan-in representation has
depth at most three; the formal executable uses binary trees, not
a bounded binary-depth representation. Inequivalence has a
polynomial-size witness, so equivalence is coNP-complete even for
these compact monotone circuits. This is a classical style reduction,
not a claim of novelty. A deterministic polynomial exact
equivalence oracle would already imply P=NP. No hardness claim is
made for syntactic hashing, individual gate rewrites, incomplete
identity checks, or all algorithms using circuits.

Since AND and OR translate to compact Boolean-ring expressions
ab and a+b+ab over GF(2), the same warning applies to universal
identity testing on the Boolean cube. Ordinary formal polynomial
identity testing over a field is not a substitute: x+x^2 is
zero at every Boolean point but is not the zero formal polynomial.

Independent JavaScript enumeration passed 4096 formulas and 262144
rail assignments, with 6384 distinguishing assignments decoded to
valid models (1280 SAT, 2816 UNSAT formulas). Eleven Lean theorem
candidates are submitted for strict replay; no new proof credit
until the exact head passes.

Strategic gate: do not assume efficient global semantic
canonicalization, exact equivalence, or exact zero-testing on
Boolean assignments. A local, sound incomplete rewriting mechanism
must prove universal completeness and polynomial total cost
separately. Compact circuit size by itself does not supply either.

This branch starts from the verified nonlinear-lift base; the
earlier F036 mathematical notes remain on their separate branches.
Main unchanged.
