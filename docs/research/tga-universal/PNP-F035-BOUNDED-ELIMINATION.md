# F035 — Bounded elimination and the missing global invariant

PNP_RESOLUTION_STATUS = OPEN.

Counting clauses alone is inadequate: raw concatenation can increase
literal multiplicity without increasing clause count. Define weight
W(F) = number of clauses + number of literal occurrences.
For the three split buckets C,A,B, the proposed exact preflight is

    W(eliminate(v,F)) = |C| + |A||B| + L(C) + |B|L(A) + |A|L(B).

The preflight computes the size without materializing the product.
The capped decision routine follows a supplied finite elimination
schedule, delegates width-two leaves to the verified solver, and
returns none (UNKNOWN) before constructing an oversized residual.
It never turns exhaustion into SAT or UNSAT. Candidate theorems prove
soundness of every returned answer, and totality when the supplied
schedule satisfies the explicit ScheduleOK predicate and the input
identifier gate.

The positive route's outstanding hypothesis is substantive:
a uniform polynomial-time schedule generator, with polynomially
bounded length and full residual weight at every stage, that
reaches a width-two residual for every valid CNF. Existence of
some favorable schedule is not enough unless finding it is also
efficient. This condition is sufficient only together with full
bit-cost accounting for the bounded construction and leaf solver.
The module does not prove this hypothesis or imply P=NP.
It also does not cover arbitrary auxiliary-preserving representations.

12 public theorem candidates. 4096 formula controls, 12288 preflight
checks, 20480 decision/budget cases and two explicit UNKNOWN checks.
Strict replay required; upstream declarations are not counted again.
