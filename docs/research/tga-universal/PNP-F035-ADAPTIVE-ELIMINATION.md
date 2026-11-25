# F035 — Factored adaptive variable elimination

PNP_RESOLUTION_STATUS = OPEN.

Rather than distribute all pairs of Shannon residual clauses, split each
input row according to its false/true restrictions. Keep clauses common
to both branches once, discard clauses satisfied on both branches, and
multiply only the two exclusive residual buckets. If C is the common
clause count and A,B are the two exclusive counts, the unsimplified
output count is exactly C+A*B, instead of (C+A)*(C+B). The candidate
proves pointwise equivalence to verified existential projection.
The executable choose function selects a locally minimum count among
the offered IDs; adaptive_local_bound states this exact local guarantee.

This is a Davis-Putnam-style elimination refinement, not a new
polynomial SAT algorithm. A local minimum is not a global complexity
bound; the verified parity projection stress illustrates why explicit
auxiliary-free CNF can still grow exponentially. The next gate is an
explicit adversarial all-orders or greedy-order stress family and
a precise global invariant, not more local optimization.

8 public theorem candidates, 4096 formulas, 12288 projected cases
and 98304 pointwise assignment comparisons. Strict replay required.
