# MathOS bidirectional PNP convergence (v3 research extension)

Additive extension to the v2 outcome engine. Both E01 and E02 use the same
normalized signed CNF and graph. The shared question is whether there is a
uniform polynomial-time, polynomial-output, SAT-preserving transformation
with an efficiently generated logarithmic-width elimination certificate.
This unrestricted decision-reduction question is equivalent to P = NP:
the converse can output a constant yes/no instance after deciding SAT.
No universal transformation or obstruction is claimed.

## Execute

    python -m mathos.research.pnp_convergence --arena --checkpoint artifacts/pnp-convergence.json
    python -m mathos.research.pnp_convergence --input cnf.json --c 1
    python -m mathos.research.pnp_convergence --resume artifacts/pnp-convergence.json --seconds 30
    python -m unittest discover -s tests -p 'test_pnp_convergence.py' -v

JSON input: {"n":4,"clauses":[[1],[-1,2,3],[-2,4],[-3,4]]}.
The report contains certificates, monotone improvement history, fixed-width
threshold classifications, transformation trace, both proof plans, shared
background lemmas, barriers requiring manual assessment, and unresolved
universal obligations.

## Dual bounds and meeting criterion

For the same finite graph, L <= tw(G) <= U (empty graph width zero).
An elimination ordering is an upper certificate; replay explicitly constructs
fill edges. The lower agent certifies an induced subgraph of minimum degree d
(treewidth at least d: the first eliminated vertex of that subgraph has at
least d neighbors), or a clique minor on k disjoint connected branch sets
(treewidth at least k-1 by minor monotonicity and clique width). The greedy
contraction heuristic is not an optimal minor finder. Lower certificates are
checked against the original graph, including connectivity and pairwise edges.

For at most 10 vertices, bounded exact search asks whether an elimination
ordering of width <= k exists. For eliminated subset S the residual edge
relation is equivalent to an original path with all internal vertices in S.
Thus residual fill depends only on S, not the ordering. The search enumerates
reachable subsets, using original-path reachability for neighbors. Success
yields an order replayed against the graph. Failure yields a set of subsets
containing the empty subset, excluding the full subset and closed under every
legal elimination. Independent replay explicitly fills eliminated vertices
in canonical order and checks closure. By induction on legal elimination
steps no full order exists, so tw >= k+1. This is exponential finite
certification, not a polynomial-time lower-bound algorithm.

The orchestrator alternates bounds, using the midpoint threshold when a
remaining gap can be searched. It publishes only replayed bounds and never
uses a partial failed search to raise L. L=U establishes exact treewidth for
that graph, not complexity of SAT. L above the fixed logarithmic threshold
only rules out the width criterion on the current graph. Other algorithms
or representations can escape it.

## Constructive/obstruction feedback

The constructive agent simplifies by unit propagation. Each forced literal
must be a unit in the current residual; replay recomputes residuals from
the original normalized clauses and checks the final signed formula and
variable maps. A unit is forced in every model of the residual, and
substitution preserves SAT under projection, including empty clauses.
For small inputs an exhaustive decision cross-check is performed.
Both original and transformed graphs receive their own bound certificates;
bounds from different graphs are never subtracted as a convergence gap.

The adversarial arena reproduces the 8-variable complete primal graph with
all positive pair clauses and a second formula adding two negative units.
Both are 2-CNF, both have exact width 7, but their SAT decisions differ.
The decisions are checked with two independent algorithms. This refutes
unsigned primal graph as a sufficient statistic for satisfiability; it is
not a lower bound against every SAT solver. The shared result motivates
signed representations and alternative tractability criteria.

## Governance and remaining work

All universal proof obligations stay unresolved. Shared lemma entries
identify background facts and implications, not newly machine-checked
theorems. The proof barrier checklist (relativization, natural proofs,
algebrization) is explicitly unassessed; these are restrictions on specified
proof techniques, not automatic impossibility results.

The CLI is deterministic and offline. Budgets are cooperative and exact
state enumeration uses the existing logical cell cap, not a hard RSS cap.
Checkpoint resume restarts input, not a partially explored frontier.
The JSON evidence history can be used by a future dashboard. LLM hypothesis
synthesis, generalized transformations, arbitrary computational-model
obstructions, formal verification of the general Python implementation and arbitrary mathematical statements remain future work. No finite result closes a universal obligation.


## Independent finite Lean boundary and dashboard

    python -m mathos.research.pnp_formal_bridge
    python -m mathos.research.pnp_convergence_dashboard artifacts/pnp-convergence.json artifacts/pnp-convergence.html

The Lean 4.14.0 bridge checks the fixed, checked-in two-variable example:
identical unsigned primal adjacency, a witness for one formula, and false
evaluation for every assignment to the other. It requires an empty axiom
report for each named theorem and hashes the source. This is a separate
mathematical finite result, not a verification of Python, the eight-variable
arena, or general treewidth algorithms. It does not discharge O12 for novel
theorems. The dashboard renders a saved JSON report, escapes text and labels
it as a non-verifying view. It is static, offline and needs no external assets.
