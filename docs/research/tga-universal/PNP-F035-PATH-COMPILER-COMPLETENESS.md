# F035/F040 — Exact route witnesses and path compiler completeness

PNP_RESOLUTION_STATUS = OPEN.

Base: implication-path discovery verified at aa7f8b0a818a88000885530d92c0c298374ceedb,
run 45658374268, job 139361129973 (20 zero-axiom declarations, 299 controls).

The previous reachability invariant proved existence of a semantic path
to the endpoint, not correctness of the actual returned vertex list.
The new indexed Walk relation records every consecutive arc and the
exact returned list. The candidate strengthens the route-table invariant
to this relation and lifts it through relaxation, sweeps and saturation.

The compiler completeness theorem targets every pair of complementary
walks in the arc list of a valid typed formula. Each local step is checked
by the existing checker. Trace induction retains the original clauses,
the last derived implication and the path length; the shifted lookup
lemma locates the first endpoint after the second path is compiled.
Both paths are then resolved to an empty clause and the existing
envelope theorem establishes original-input-bound acceptance.

The executable consequence is that if reach returns both complementary
routes, tryVar returns an accepted proof without any exhaustive fallback.
This does not yet show that reach finds all reachable vertices within
its fuel bound, that every unsatisfiable 2-CNF has a complementary
pair, or that the entire discovery pipeline has polynomial bit cost.
No change to the certificate format or checker.

14 public theorem candidates and 44 executable controls, including
20 chain instances, their 20 reversed-row/literal-order counterparts,
a unit contradiction, a sparse 128-digit identifier contradiction and
two malformed-route controls. The exact-head strict Lean 4.14.0 replay
is required before counting them as verified. No main changes.
