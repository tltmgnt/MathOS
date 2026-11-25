# F037 — Balanced separators and local backdoor leaves

PNP_RESOLUTION_STATUS = OPEN.

## Mechanism and exact promise

Normalize the 3-CNF and construct its primal graph, which has an
edge between every pair of variables in a clause. The decomposition
is computed before any truth assignment. At a region R, retain
structural clause projections obtained by deleting variables removed
by ancestor separators, regardless of whether those clauses might
eventually be satisfied. Consequently every actual residual clause
on R is among these projections. If the projected ternary clauses
have a hitting set of size at most k, make the region a leaf.
Otherwise enumerate separators of at most s variables and choose
one minimizing the largest remaining connected component, subject
to each component having at most 2|R|/3 vertices. Use deterministic
ties. Recurse on every nonempty component. If no eligible separator
exists or a recursive plan fails, return UNKNOWN rather than try
an unbounded search for alternative decomposition trees.

Given a successful plan, enumerate at most 2^s assignments to the
separator at each internal node. Restrict the clauses, reject an
empty clause, and solve the remaining components independently.
Their variable sets are disjoint and every surviving clause lies
in a single component, because its variables were a clique in
the primal graph. The conjunction is satisfiable iff every child
is satisfiable, and the parent is satisfiable iff at least one
separator assignment has satisfiable children. At a leaf use the
previous bounded-backdoor solver. A backdoor hitting the structural
projections hits every actual ternary residual, so leaf calls
are definitive. This proves exact decision by induction on the
plan. SAT witnesses combine across disjoint regions and are checked
against the original input. Local UNSAT checks are inherited; a
standalone global decomposition proof checker is not implemented.

The promise is that this deterministic planner succeeds; it is
not that some arbitrary decomposition exists. One sufficient
structural promise is that every induced region without a
size-k projected backdoor has an eligible separator. No claim
is made that every 3-CNF meets that promise.

## Uniform polynomial bound

Each child has at most 2/3 of its parent's vertex count. Thus
the depth H is at most ceil(log_(3/2)(n))+1 for n>=1. At any
depth the regions are disjoint, so at most n nonempty regions
occur at that depth, and there are O(n log(n+1)) plan nodes.
At a node, discovering the leaf backdoor costs 3^k poly(N);
enumerating separators costs O((n+1)^s) polynomial graph work.
Here N denotes encoded input length and n the occurring variable
count. Evaluation visits any region at most 2^(sH) times under
ancestor assignments, and the backdoor leaf solver costs
(3^k+2^k) poly(N). An overall upper bound is

    ((n+1)^s + (3^k+2^k)*2^(sH)) poly(N).

For fixed s and k<=c log_2(N+1) with fixed c, this is polynomial
in N. Unlike a proof using arbitrary logarithmic separators,
this bound accounts for discovering the separators by explicit
enumeration: s is fixed, not logarithmic. A logarithmic value
of s would generally give only quasipolynomial discovery by
this method. The implementation accepts explicit budgets;
the theorem is a mathematical resource bound, not a formal
Python bit-cost refinement.

## Strict improvement over block backdoors

Take t disjoint variable triangles (positive ternary clauses)
and join consecutive triangles by two binary clauses, one
linking their first variables and one linking their second.
For t>=2 the primal graph is biconnected: deletion of any
single vertex leaves connected nonempty triangles and at
least one surviving intertriangle link between consecutive
triangles. The minimum syntactic backdoor of the sole block
has size t because each disjoint ternary clause must be hit.

Every induced subgraph of this ladder has a separator of
at most two vertices leaving components of size at most
half the region size, except singleton regions which are
already leaves. Choose a column containing the weighted
median vertex, where columns are the original triangles and
weights are their surviving vertex counts. Remove the first
and second vertices of that column if present. The surviving
third vertex, if present, is isolated; regions to the left
and right contain at most half the vertices. Hence the
deterministic balanced planner cannot fail on this family
at s=2 and k=1, even with arbitrarily many ternary clauses
in its original biconnected block. This is a strict
improvement in the structural promise, not a general SAT
lower bound. The all-positive ladder itself is easy to satisfy.

## Evidence

The previous block-backdoor exact-head repository replay passed
at 7f7e574eb191654b3f9c85581432eed450cb97d6
(run 45686399171, job 139460025336).

An independent JavaScript implementation of the new plan and
separator evaluation, using an exhaustive local leaf oracle
instead of the Python backdoor implementation, passed all 4096
three-variable fixtures (1280 SAT, 2816 UNSAT). Six ladder sizes
2,4,8,16,32,64 were tested; the largest has 192 variables,
93 plan nodes and depth five in that implementation.
A two-variable separator contradiction, a budget rejection,
and an UNSAT ladder also passed. No discrepancy was observed.
The Python candidate uses the earlier certified-leaf procedure,
checks SAT reconstruction, and tests that the previous block
algorithm returns UNKNOWN on these ladders at budget one.
The Python replay is pending, not reported as completed.

## Remaining barrier

Graphs of large expansion can have no balanced constant-size
separator and also contain many disjoint ternary clauses.
The current architecture has no universal polynomial bound
or general completeness theorem. This note broadens a
standard structural promise; it makes no novelty claim
and gives no new Lean verification credit. Main unchanged.
