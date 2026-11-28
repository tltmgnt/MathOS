# MathOS v21 — cross-model complexity separation

v20 passed both CI jobs (46135311217): all nine chain depth witnesses
and six cube width witnesses met the bounds, and all nine chain cases
had a certified 2-SAT escape.

v21 reproduces a restricted first-step obstruction for linear-size
ternary parity CNFs (Tseitin-style systems), with an independent affine
escape. Unlike the v20 full sign cube, input size is linear in the
family parameter. This is not a new resolution lower-bound theorem.

## Family and exact first-step width

Take two simple cycles of length m >= 3, joined by m matching rungs.
Each edge is a Boolean variable; each vertex imposes a parity equation
on its three incident edges. Encode each equation by the four clauses
forbidding assignments of the wrong parity. There are 3m variables,
2m equations, 8m clauses and 24m literal occurrences. The graph is
simple, so different vertex scopes share at most one edge variable.
Each variable occurs in exactly two equations.

Within one scope all forbidden assignments have the same parity.
Two distinct ones differ in exactly two positions, so resolving on
one position leaves a complementary pair: the resolvent is tautological.
Across disjoint scopes no pivot exists. Across scopes sharing one
variable, a complementary pivot leaves four distinct literals, none
complementary. Such a pair exists since both signs of each variable
occur in each parity encoding. Thus the minimum width of a first
non-tautological resolution inference is exactly four. A resolution
system admitting only non-tautological derived clauses of width at
most three cannot start, regardless of depth or work budget.

This claim is about direct resolution from these original axioms,
without weakening, extension axioms or preprocessing. It does NOT
bound unrestricted resolution, proof size, CDCL, or all SAT algorithms.
It is not a growing width lower bound. Width four is sufficient for
a first inference, not necessarily a refutation.

## Algebraic escape and matched control

XOR all vertex equations. Every edge variable occurs twice, so the
left-hand side cancels to zero. Set exactly one right-hand side to
one to obtain 0=1, a contradiction; set all right-hand sides to zero
for a satisfiable twin (all-zero assignment). Both have the same
scope graph and first-step obstruction. Obstruction alone cannot
distinguish SAT from UNSAT.

A structural recognizer and independent verifier check each ternary
truth table, full scope coverage, pairwise linearity via a variable
pair index, twice-occurring variables and the XOR sum. Recognition
and checking take a linear number of dictionary/index operations in
the formula size (assuming unit-cost bounded-key operations; ordinary
bit encodings contribute logarithmic factors). On this family a
simple all-row XOR certificate is linear in the number of equations.
The experiment also uses the existing v7 affine compiler and
Gaussian elimination verifier, with polynomial arithmetic/provenance
overhead for fixed local arity, to certify both SAT and UNSAT without
depending on the first-step resolution obstruction. Odd parity
proves UNSAT, but even parity alone is not asserted to prove SAT
for arbitrary disconnected input; a separate witness is checked.

## Run

    python -m mathos.research.pnp_cross_model_frontier --checkpoint artifacts/pnp-v21.json
    python -m mathos.research.pnp_cross_model_frontier --audit artifacts/pnp-v21.json

Six sizes, both polarities, 9 to 192 variables; executable limits
m <= 64. The report replays bounded width-three search and affine
certificates, and independently checks the structural premises.
Search counters are observations, not complexity proofs. Tiny
instances are cross-checked by exhaustive assignments and explicit
first-step pair enumeration. Lean checks abstract Boolean
cancellation, parity flip and contradiction facts only; full
family and implementation are not formalized. E01/E02/E08 remain
open in the registry, with restricted evidence kept separate.
