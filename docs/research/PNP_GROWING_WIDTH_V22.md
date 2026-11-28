# MathOS v22 — growing resolution width versus affine escape

v21 passed both jobs (46136410888): width-three first-step obstruction
and affine decisions on all twelve prism instances. v22 replaces the
constant first-step obstruction with a growing refutation-width bound.
This is a self-contained reproduction of a Tseitin width argument,
not a novelty claim.

## Family and claim

For every integer s >= 3 take the s by s toroidal square grid, with
horizontal and vertical cycle edges. It has V=s^2 vertices and N=2s^2
edge variables. At each vertex impose the XOR of the four incident
variables, with charge one at one vertex and zero elsewhere. Encode
each local relation as eight width-four forbidden-assignment clauses.
The odd-charge CNF is unsatisfiable by XOR cancellation. The zero-charge
twin is satisfied by all-zero variables and shares the graph and sizes.

**Claim:** every ordinary binary resolution refutation of the odd
formula from its original CNF axioms has a derived clause of width
at least 2s = sqrt(2N). No extension variables, extra axioms, or
arbitrary preprocessing are included in this proof model.

## Proof

Let mu(C) be the minimum number of vertex equations whose conjunction
entails clause C. This exists because the whole system is inconsistent.
Axiom clauses have mu <= 1; tautologies have mu=0. Every proper subset
of vertex equations is consistent: a nonempty subset of its rows has
a nonempty edge cut by graph connectivity, hence nonzero XOR sum.
Thus these rows are linearly independent over GF(2), so every
right-hand side is attainable. Consequently mu(empty)=V.
Resolution soundness gives mu(resolvent) <= mu(parent1)+mu(parent2):
the union of supporting equations entails both parents and therefore
the resolvent.

In a topological order of any refutation, the first clause with
mu > V/3 is derived, not an axiom, and both parents have mu <= V/3.
It has V/3 < mu <= 2V/3. Choose a minimum supporting vertex set U
for this clause, so its size lies in that interval.

For a non-tautological clause C, falsifying it fixes exactly its
support variables S. Restrict the equations in U to this assignment.
They are inconsistent, so Gaussian elimination gives a subset W of
these equations whose XOR has no unfixed variables and inconsistent
right-hand side. W already entails C. By minimum cardinality W=U.
The variables with odd multiplicity in the XOR of U are exactly
its cut edges delta(U). Since no unfixed variable survives,
delta(U) is contained in S, so width(C) >= |delta(U)|.

For a balanced set U on the torus (V/3 < |U| <= 2V/3), the cut has
at least 2s edges:

* If all rows are mixed, each horizontal row cycle has at least two
  crossings.
* If a full and an empty row exist, each vertical column cycle has
  at least two crossings.
* Otherwise complement U if needed to obtain a set with at least one
  empty row and no full row. Every nonempty row and column is mixed.
  With R nonempty rows and K nonempty columns, the cut is at least
  2(R+K). Since RK >= |U| (after possible complement) >= s^2/3,
  (R+K)^2 >= 4RK >= 4s^2/3, so R+K >= s.

Together these establish width(C) >= 2s. A strip of ceil(s/2) rows
lies in the strict support interval for every s >= 3 and attains the
balanced cut bound, but this does NOT prove tightness of
the resolution width bound. No matching resolution upper bound or
resolution-size lower bound is claimed here.

## Verification and scope

The structural verifier independently reconstructs vertex incidence,
checks each width-four parity block against all 16 local assignments,
checks twice-occurring variables and the odd-charge identity. These
are verified premises of the documented lower-bound proof, not a
machine-checked proof of the entire theorem. Lean checks only
abstract crossing arithmetic, inclusion and contradiction lemmas.
Small balanced cuts are exhaustively checked and larger cuts sampled;
neither finite test is used as the proof for all s.

The existing certified affine compiler and Gaussian elimination
decide the odd/zero twins with polynomial arithmetic/provenance
overhead. Input dimensions are N=2s^2 variables, 8s^2 clauses and
32s^2 literal occurrences; executable s<=16 due to 512-variable
input limit. Fixed arity means local compilation costs are bounded
per block. The growing width obstruction is therefore not a SAT
algorithm lower bound. No inference from observed failures to
complexity claims is made.

## Run

    python -m mathos.research.pnp_growing_width_frontier --checkpoint artifacts/pnp-v22.json
    python -m mathos.research.pnp_growing_width_frontier --audit artifacts/pnp-v22.json

Six side lengths (3,4,6,8,12,16), both charge controls; width-four
probes only for s<=6. All credited affine results and structural
premises replay independently. E01/E02/E08 registry obligations remain
unresolved. P versus NP remains unresolved.
