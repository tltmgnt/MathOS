# PNP-F033 — Formal finite-counting and Hall CNF soundness

PNP_RESOLUTION_STATUS = OPEN. PR #156 merged into the parity research
branch at 7edd224fc5ce3a87e3c30b3fc2e5e3074c1b86a8. Actual CI run
45452755349 job 138653975538 passed six Hall tests: 1500 arbitrary
sparse CNFs (46 certified UNSAT, 1454 UNKNOWN), 600 restricted matching
controls (280 UNSAT, 320 UNKNOWN), all nine shuffled PHP sizes and
matching equal-size negative controls. At 64 holes: 65 demands,
4160 variables, 133185 clauses, 64 capacity groups, 133120 conflict
references, 6240 matching edge scans, zero search nodes and zero BVE
pairs. Artifact 14946939363.
https://github.com/tltmgnt/MathOS/actions/runs/45452755349/job/138653975538

## Candidate formal layer

ProctorHallDeficiency.lean is a self-contained constructive Init
module. The new strict audit requires Lean 4.14.0, warnings-as-errors,
and exact zero-axiom output for seven new declarations; existing
verification gates remain unchanged.

bounded_injection proves that a map of d bounded natural indices
into k bounded natural indices, injective on that domain, implies
d <= k. The proof inducts on k, handles the empty codomain, and
constructively removes the last domain point by replacing a possible
image k with the last point's image. The restricted map remains
injective and maps into k smaller codomain indices. This avoids
classical choice, quotient cardinality machinery, or a presumed
pigeonhole axiom.

finite_demand_choices constructs a finite family of true-variable
witnesses by induction on the demand count, not arbitrary choice.
capacity_injection shows that capacity-one groups and disjoint
demands force the group map of the selected true variables to be
injective. hall_deficiency rules out a model under strict deficiency.

positive_clause_demand transports an original normalized positive
clause into its true-variable demand. negative_pair_capacity proves
a normalized negative binary clause forbids both variables being
true. hall_cnf_unsat composes these with the counting result to
refute a CNF when the demand clauses and all required negative pairs
are present, each negative pair in either order. Additional clauses
are unrestricted. Demands are finite indexed lists; the owner
function and its coverage bound are supplied. No explicit group
partition object is required by the theorem: ownership is a function.

## Boundary of the proof

The theorem is a semantic statement on normalized clause lists,
not a checked implementation of matching, discovery or Python
certificate replay. Transport from original clause indices, repeated
literal normalization, arbitrary clause order within positive supports,
sparse signed integer labels and Python certificate data into these
hypotheses remains to be formalized. The theorem proves sufficiency
of a valid deficiency witness; not completeness of the recognizer,
matching algorithm correctness, or a universal SAT complexity bound.
The prior polynomial structural edge-scan bound is not a machine
transition count. The new declarations are candidates until CI
confirms the kernel and axiom gate; no local Lean executable available.
No independent review, original scratch port or main branch change.
Next: polarity-independent CNF recognition, further negative controls
and combined inference audit. No global promotion.
