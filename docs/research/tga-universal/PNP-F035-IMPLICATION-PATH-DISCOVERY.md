# F035/F040 — Implication path certificate discovery

PNP_RESOLUTION_STATUS = OPEN. Exact-head verification required.

Base: binary-square branch verified at 9fa47c43769dafafee76ccb413df096b2d0ed94e
(run 45657067540, job 139356496301; eight zero-axiom declarations, 46 controls).
No changes to main or to the original checker.

For each binary row (a or b), emit arcs not a -> b and not b -> a.
For a unit row (a), emit not a -> a. Longer and empty rows are ignored by
the graph path. A formula model preserves truth across every arc and
path. If v reaches not v and not v reaches v, the formula is UNSAT.
The candidate includes the constructive semantic proof and a soundness
invariant for the executable reachability saturation.

For each source, repeatedly sweep the finite arc list and retain a route
only for a previously unseen destination. The bound is the number of arcs
(no iteration through the numerical variable bound). Retain forward path
witnesses. Formal saturation completeness, simple-path bounds, and a
machine cost theorem are still open. The current implementation is list-
based repeated sweeps, not Tarjan/Kosaraju or a linear-time SCC algorithm.

The compiler locates original or already derived rows contained in the
corresponding implication clause. Copy the first edge by weakening, then
resolve each successive edge against the last derived implication.
The endpoint clauses are duplicate-literal units [v,v] and [not v,not v].
Resolve them to the empty clause, retaining original-input binding.
The checked candidate uses the existing sequential-to-batch compiler
which copies frontier rows. The number of batches for two nonempty
paths of lengths p and q is p+q+1; total inference count is larger.
The local first, advance and close rules have explicit checker-acceptance
theorem candidates. A universal theorem that the whole path compiler
succeeds and produces an accepted envelope for any graph contradiction
is not claimed yet.

Missing or rejected candidates fall back to verified binary-square and
exhaustive proof-returning discovery. Combined completeness relies on
that fallback; it is not a standalone 2-SAT completeness theorem and
does not establish polynomial worst-case discovery.

Controls (299): 256 subsets of four binary and four unit clauses over
two variables, 16 subsets of reversed binary rows, 20 two-path chain
families, one sparse 128-digit identifier case, two empty cases, two
mixed-width fallback cases, two rejection cases. The graph-only checks
cannot be satisfied by the exhaustive fallback. Chain instances with r
internal variables per path have 2r+1 variables, 2r+2 binary clauses and
expected 2r+3 batches, versus 2^(2r+2)-1 for full distinct-variable
splitting. These are construction counts and fixture targets, not a
formal universal polynomial resource bound.

Twenty public theorem candidates; exact strict Lean 4.14.0 warning-as-
error and zero-axiom replay. Universal serialized completeness, general
polynomial certificate size, general polynomial discovery and P vs NP
remain open.
