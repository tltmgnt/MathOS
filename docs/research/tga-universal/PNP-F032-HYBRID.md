# PNP-F032 — Integrated hybrid certificate routing

PNP_RESOLUTION_STATUS = OPEN. PR #153 merged into the formal research
branch at 1176bdbd502f797c0bf59396940f002a4d43470f (not automatically
into F030 or main). PR #153 CI 45447677029 job 138635823546 passed all
six blind tests: 1200 random projections (891 certified UNSAT,
309 UNKNOWN, 301 brute SAT, hence eight missed UNSAT), 36 blind
odd-charge recoveries, 36 even and 36 zero-budget controls, and 12
shared-selector negatives. At q=80, depth one/two required 320/640
pairs under the common 1000 budget. Artifact 14947610404.
https://github.com/tltmgnt/MathOS/actions/runs/45447677029/job/138635823546

## Interface and route semantics

Use the existing XOR recognizer first, then blind initial-degree-two
BVE with its global pair budget and width-five no-growth policy.
If either finds a contradiction, return its original-clause proof.
Otherwise, if search budget is positive, replay the BVE log and
prefer dynamic search on the reconstructed residual if every clause
has width <=3; if not, fall back to the original CNF when its raw
clause widths are <=3. Otherwise return UNKNOWN with an explicit
unsupported-width reason. Exhausted dynamic budget yields UNKNOWN.
The original input can be any finite signed CNF; the width-three
contract is complete only with sufficiently large search budget.

Four certificate routes: DIRECT_XOR, BVE_XOR, DYNAMIC_ORIGINAL,
DYNAMIC_PROJECTED. In the last route an UNSAT proof consists of the
exact projection log and the residual dynamic proof. The verifier
reconstructs that residual, rejects a SAT-labelled inner result,
and checks the dynamic certificate. In the first three UNSAT routes
it calls the corresponding existing checker against original clauses.
All SAT routes output an original sparse witness, checked directly;
UNKNOWN never has a valid certificate. Route labels and counters
are not evidence of complexity or of how a witness was found.

## Reverse projection witness extension

For projected SAT, start with the verified residual assignment and
default original non-eliminated variables absent from the residual
to false. Recover each pivot in reverse elimination order from
its recorded positive and negative active parents. If a positive
tail is false the pivot must be true; if a negative tail is false
it must be false. Both cannot happen: their non-tautological
resolvent would be false (a tautological resolvent cannot be false).
If neither constraint applies choose false. Inductively restore a
model at each stage, and finally check every original clause,
including duplicates and tautologies. The public SAT certificate
is just this original witness; it does not require trusting the
back-substitution routine. The existing kernel-verified
projection_iff supports the mathematical argument but is not
a refinement proof of the Python code.

## Budgets and limitations

Pair and search-node limits are separate nonnegative integers.
Every tested BVE pair (including rejected pivots) is charged;
dynamic search visits are charged once. Zero node budget disables
dynamic search, not the two algebraic routes. Zero pair budget
disables positive-cost BVE steps, not direct XOR inference.
Neither budget caps scanning, GF(2) work, preprocessing, proof
construction or replay. Direct XOR is attempted before BVE to
avoid erasing useful equations. This deterministic routing policy
is not asserted optimal. Dynamic search can still be exponential;
a stronger proof language avoids the earlier resolution-only
obstruction on recognizable parity, but no general lower or upper
bound for unrestricted SAT follows.

New controls: 1400 small seeded sparse formulas across widths <=3
and <=5, three budget settings each (4200 runs), brute-force checks
of every decisive result, nonbinding width-three completeness,
six cubic direct/hidden/shared-selector comparisons, four route
tests, SAT lifting, tamper and invalid-budget tests. The width-four
shared selector remains an intentional UNKNOWN control even with
positive search budget; this is a width-policy limitation, not
a universal hard instance. New CI must confirm the tests.
Existing Lean gates unchanged; original scratch files unavailable;
independent review, executable refinement and total machine-cost
analysis remain outstanding. No global promotion.
