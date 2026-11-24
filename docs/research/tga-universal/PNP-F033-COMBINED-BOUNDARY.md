# PNP-F033 — Combined inference boundary and mixed proof contrast

PNP_RESOLUTION_STATUS = OPEN. PR #160 merged at
f048146c7d0d70d06816734d7697868597a8b7c4. Actual Lean 4.14.0 run
45464629766 job 138696123642 passed warnings-as-errors and exact
zero-axiom checks for all fourteen new ProctorCapacityDeficiency
declarations; previous gates also passed. Artifact 14954228486.
This establishes local generalized capacity semantics, not Python
refinement.
https://github.com/tltmgnt/MathOS/actions/runs/45464629766/job/138696123642

## Obstruction to the existing policy

For unary PHP(h+1,h) with h>=4, replace every clause C by
(C OR g) AND (C OR NOT g) with one shared fresh selector g.
This is pointwise equivalent to C regardless of g. Each original
support appears once; guarded supports therefore have exactly two
forbidden assignments, differing only at g. Binary conflicts
become triples; demands become width h+1. No exact parity block
of width 1..5 is present (width three needs four forbidden
patterns). There are no binary clauses, so capacity one and
positive Hall cannot establish a deficiency. The capacity-two
hypergraph contains a single component on all conflict-oriented
original variables and both selector signs: each original variable
participates in a conflict, and each conflict connects to both
selector signs. This component is not complete because a triple
containing both selector signs is excluded as tautological. No
other triples exist. Thus capacity two selects no group. Each
original variable occurs twice on its demand side and 2h times on
the conflict side, while each selector sign occurs m times for
m original clauses. No unique once-occurring sign or opposite
degree-two variable exists. All shortcut failures remain true
under arbitrary polarity complementation and sparse renaming.
The original Hall route may choose positive demands but cannot
produce nontrivial conflict groups without binary clauses.

The wide combined solver consequently uses only its dynamic
resolution-simulable fallback, with identity BVE projection.
Restricting g=true in any ordinary resolution refutation gives
a refutation of original PHP of no greater line count (delete
satisfied lines; at a resolution step on a fixed pivot retain
the surviving parent, and otherwise resolve surviving subclauses
or retain one if its pivot is absent). Empty conclusion survives.
By Haken's classical lower bound, the guarded formula therefore
requires 2^Omega(h) resolution lines. The prior conversion bound
m'+V(m'r'+1) for m' guarded clauses and r' variables implies
2^Omega(h) dynamic visits on completed UNSAT runs. Since explicit
dense-label input length is O(h^3 log(h+1)), this is superpolynomial
for this particular fixed policy (and polynomial-size label
renamings). Finite budget exhaustion is UNKNOWN, not a proof of
asymptotic hardness. The width-three default has no search route
here. Source: A. Haken, The intractability of resolution,
Theoretical Computer Science 39 (1985), 297–308,
https://doi.org/10.1016/0304-3975(85)90144-6.
This is an application of existing resolution theory, not a new
resolution lower bound or a lower bound for the combined proof
language or unrestricted SAT.

## Short mixed proof, separate experiment

For each normalized original clause and each literal l in it,
index the remaining sorted tail together with l. When the same
tail occurs with opposite l, derive the tail by ordinary
resolution. Keep one representative pair per tail. No supplied
selector ID, graph, parity or auxiliary map; no saturation and
no full BVE cross-product. Then run the existing signed Hall
recognizer on the derived tails. Verify the original parent
indices and exact opposing-pivot tails, then replay the Hall
certificate against those derived clauses. Since every derived
clause is entailed, an UNSAT subset suffices. A proof can be
accepted without invoking either discovery or matching.

For the guarded PHP family the only opposing equal-tail pairs
are the two guard variants of each original clause: all original
supports are unique and all contain distinct variables. Therefore
exactly m resolution steps recover the original PHP up to signs
and order. Signed Hall gives a polynomial-size counting proof,
even for guarded formulas that require exponentially many
resolution-only lines. This separates the old search/recognition
policy from the expressiveness of a mixed proof language.
The experiment is deliberately not integrated into the default
combined router. The previous lower-bound statement remains
about the unchanged policy only. No general efficiency claim.

There are at most L literal-position signatures for L explicit
literal occurrences; storing a tail for each position can take
quadratic literal storage in L. Sorting and comparison, sparse
integer bit costs and Hall replay are additional polynomial work
under an explicit finite-list implementation. Signature count is
not total machine time. No executable refinement or independent
review.

## Validation

1600 small sparse random CNFs with brute-force soundness checks,
12 signed shuffled guarded PHP fixtures (h=4,5,6,7,16,32; seeds
11/29), six equal-size SAT controls, zero-budget and tamper
controls. Compare unchanged wide hybrid (100000 nodes for h<=5,
1000 for h=6,7, one for h=16,32 to bound CI cost) with separate one-round mixed inference. Extract
ordinary resolution proofs only when the old hybrid completes.
New empirical outcomes await actual CI. Existing strict Lean
gates unchanged. No original scratch port or main change.
Next: integrate bounded paired inference with explicit proof
routing and then audit the new policy rather than repeatedly
promoting scoped results to general claims.
