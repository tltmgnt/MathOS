# F035 — Semantics-preserving normalization

PNP_RESOLUTION_STATUS = OPEN.

Normalize literals by retaining their last occurrence; delete tautological
clauses; process the formula from the right, dropping any row implied by
a retained subset row. This is one-direction subsumption, not a full
canonical antichain or semantic equivalence test. Normalize before and
after the verified factored elimination operation. Candidate theorems
prove pointwise normalization equivalence, nonincreasing clauses and
occurrences, and exact existential projection.

The raw multiplicity obstruction does not survive literal and clause
deduplication in its original form. In particular its repeated-literal
markers become units. This is not evidence of a universal polynomial
bound: even parity has an exponential exact auxiliary-free CNF
representation, and ordered elimination can still incur that barrier.

There is a more fundamental research boundary: normalization and
elimination belong to the resolution family. Known exponential resolution
lower bounds on some unsatisfiable CNFs are relevant to any algorithm
that extracts ordinary resolution refutations with polynomial overhead.
They do not exclude all polynomial SAT algorithms. No new universal
lower bound is claimed here. Before another positive-route attempt,
identify what inference or decision mechanism goes beyond this family,
or explicitly retain UNKNOWN when no bounded proof is found.

10 public candidate declarations, 4096 formula controls and 98304
pointwise assignment/projection checks. Strict exact-head replay required.
