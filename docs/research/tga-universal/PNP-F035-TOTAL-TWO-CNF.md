# F035 — Total typed 2-CNF interface

PNP_RESOLUTION_STATUS = OPEN.

Integrates the independently verified nonempty-clause solver
(d119286a, 29 public zero-axiom declarations) and path resource bounds
(32e9f3c6, 20 public zero-axiom declarations). The existing checker
and certificate representation are unchanged.

The interface returns invalid for out-of-range identifiers, unsupported
for rows wider than two, sat with a constructive assignment, or unsat
with an original-input-bound proof. Empty rows produce the existing
zero-batch empty terminal; no pivot or positive variable bound is
needed. The empty formula is satisfiable. Invalid inputs are prioritized
over unsupported, and unsupported over empty-row detection.

The candidate solve_spec gives a specification for every result
including the two rejection cases, and makes internalError impossible.
For valid width-two input, SAT and UNSAT completeness follow without
exhaustive fallback. Each returned certificate has at most 2L+1
batches and (m+2L+1)*(2L+1) total inferences (L literal occurrences,
m original clauses). These are structural counts, not bit-cost bounds.
Assignment is a function; finite materialization and serialization
are separate tasks. No general SAT or P versus NP conclusion.

12 public theorem candidates. 1033 controls: 512 subsets including the
empty clause and 512 reversals, 3 zero-bound cases, 2 sparse cases,
4 invalid/unsupported cases. Strict exact-head replay required.
