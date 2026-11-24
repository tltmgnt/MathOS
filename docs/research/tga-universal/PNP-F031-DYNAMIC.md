# PNP-F031 — Dynamic residual components (native follow-up)

PNP_RESOLUTION_STATUS = OPEN. Stacked on draft PR #147 head
68058218ccd7c298fa45c01466fe2d4fb9480ed3, not on main. PR #147's adaptive
CI run 45440483366, job 138609891631, passed. The actual guarded-root
measurements for t=1,2,4,6,8 were 19,47,255,1279,6143 nodes; the
disconnected root-component control used seven nodes at every size.
These are repository-native results, not the original scratch measurements.

## Algorithm and certificates

Reuse F030's unit/pure simplifier and renamable-Horn recognition, F025's
partition routine and the native F031 sparse input contract (width <=3).
At every visited node, after propagation, partition the nonempty residual
by occurring variables. If more than one component exists, solve them in
ascending variable-count order. A SAT component contributes its witness;
one UNSAT component suffices to refute the parent residual. If there is a
single component, try renamable-Horn recognition, otherwise branch using
F030's highest-incidence rule. At a unit/pure fixed point an oriented
Horn clause has a negative literal, so all-false in the oriented variables
is a witness. A continuation stack avoids recursive Python search calls.
Budget exhaustion is UNKNOWN; the budget counts all visits, including
decomposition parents, but does not cap preprocessing or replay time.

The solver emits an original-ID sparse SAT witness, or an UNSAT preorder
tree with propagation events and one terminal: false original clause,
binary split with both children, or an original-clause subset with one
refutation child. The verifier starts from the original literal sets,
restricts at every step, checks forced units and pure assignments,
and rejects missing/trailing children. The subset proof checks membership
in the current residual, not graph connectivity: UNSAT of a subset
implies UNSAT of the residual by monotonicity. On SAT, independence is
needed for witness union; the implementation also directly checks the
original CNF. Tautologies and duplicate clauses may be dropped by the
solver; replay retains duplicates and checks original clause indices.
The verifier does not invoke partition, simplification or recognition,
but shares input helpers and is not an independent implementation review.

## Guarded obstruction

In PR #147's connected guarded family, unit g=true removes every added
bridge at the first visit. The resulting components are the t satisfiable
four-variable gadgets and the three-variable UNSAT core. Smallest first
selects that core; its F030 binary search takes seven visits, so this
implementation is expected to need eight total visits independent of t.
This is a family-specific derivation. New controls check exact counts
through t=32, a budget of seven, and corrupted subset/propagation proofs.
The previous lower bound applies to the root-only algorithm, not this
dynamic variant. No connected family forcing exponential dynamic search
has been established. The earlier guarded construction is intentionally
easy for propagation plus decomposition.

## Acceptance and scope

800 seeded sparse CNFs versus brute force, 800 zero-budget checks,
sparse witness gluing, malformed certificate tests, empty CNF/clause and
guarded controls are included in the CI suite. Actual results must come
from the CI log. The existing pinned Lean policy is unchanged. The F025
kernel-verified component semantics and UNSAT lifting support the paper
soundness argument, not executable refinement of this Python solver.
The prior root-only bit-cost analysis does not automatically certify this
dynamic algorithm. Search terminates without a binding budget: each
binary branch fixes a variable; each proper component child has fewer
active variables, and unit/pure simplification never increases them.
An unbudgeted finite search tree may still be exponential; no universal
small component theorem, total bit-machine refinement, or independent
review is claimed. The original six Claude modules remain unavailable.
