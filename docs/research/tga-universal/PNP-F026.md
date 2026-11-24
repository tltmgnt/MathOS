# PNP-F026 — Supplied tree decomposition and bounded-width SAT

Stacked on F025 corrected head 08f0593178ba495fa8caac5745b681ba0bd56789.
F025's first kernel replay failed, while its five tests and 74 finite
controls passed. Its correction is subject to a new strict kernel replay.

## Scope and mathematics

Given a signed 3-CNF and a supplied tree of variable bags, validate tree
connectivity, acyclicity, clause coverage and running intersection.
Unused variables may be omitted and assigned false; this corresponds to
adding isolated singleton bags if a full primal-graph decomposition is
required. Assign each clause to its first covering bag. Root the tree
at bag zero. For each bag assignment, require its assigned clauses
to hold and at least one feasible child entry agreeing on the intersection.
A feasible root entry exists iff a global assignment exists: the
forward direction restricts a witness; the reverse direction glues entries
using running intersection. The Lean kernel establishes the two-region
semantic join, boundary-preserving join and equality along an agreement
path. The full tree recurrence and its executable refinement are not
formalized in this milestone.

## Executable reference and independent recurrence checker

Enumerate each bag's assignments once, in reverse breadth-first tree order.
Index feasible child assignments by their shared coordinates with the parent.
Reconstruct a SAT witness by following those indices and verify it directly
against the original formula. For UNSAT return all feasible-entry tables.
A separate verifier checks exact leaf and internal recurrences with full
child table scans (not the solver's projection index) and empty root.
It independently recomputes validation and clause placement using the
same preparation routine. No claim of an independent implementation of
the decomposition validator. This is not a compact general UNSAT proof
system; certificates may be exponential in width.

For t bags, max bag size b, and m clauses, the exact number of candidate
table assignments is sum_i 2^|bag_i| <= t*2^b. The solver's child lookups
are at most (t-1)*2^b and its indexed child projections at most the same.
Per-entry predicate, key and allocation costs are additional. Under
ordinary dictionary assumptions the table computation has a 2^b times
polynomial schedule in the explicit formula/decomposition size. The
independent verifier's naive full scans allow a 2^(2b) times polynomial
schedule. These are algorithmic bounds, not a verified Turing-machine
transition theorem. Width is b-1. Logarithmic b in the combined input size
is sufficient for polynomial table work, not universally guaranteed.
The decomposition is supplied; no cost-free construction assumption.
Space includes all tables and projection indices, potentially exponential
in b. No general SAT polynomial bound or Millennium resolution.

## Acceptance

Run python -m unittest discover -s tests -p 'test_tga_proctor_tree_decomposition.py' -v
and python -m mathos.research.tga_proctor_tree_decomposition_audit --output-dir artifacts/pnp-tree-decomposition.
The strict kernel gate audits six declarations without axioms.
35 bounded cases compare the DP decision with brute force and test
certificate tampering; the structured 64-variable chain is checked
without brute force, with 252 candidate table entries. Six tests cover
invalid trees, invalid clause coverage, running intersection, empty bags,
isolates and corruption. Actual CI report determines acceptance.

Next: full formal tree induction and executable recurrence refinement,
then decomposition construction/cost and affine-backdoor optimization.
No universal small-width or small-backdoor theorem is assumed.
