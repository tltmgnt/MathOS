# F037 — Common obstruction to the structural/semantic portfolio

PNP_RESOLUTION_STATUS = OPEN.

## Construction

Fix the previously audited 21-vertex Brinkmann graph B (girth five,
not 3-colorable, and biconnected as checked in this fixture).
For t>=3 subdivide each edge of K_t into a path of length three,
with distinct new internal vertices. This core has t^2 vertices.
Take a disjoint copy of B and join two distinct branch vertices
of the core to two distinct vertices of B by internally disjoint
paths of length three. The resulting G_t has n=t^2+25 vertices.
It has no triangles or quadrilaterals: the core has girth nine,
B has girth five, and a cycle using the joins has length at least
eight. It is biconnected: both pieces are biconnected and the
two joins have distinct endpoints in each piece, so deleting
a single vertex leaves a connection. In the subdivided clique,
deleting an internal vertex only removes one clique path;
deleting a branch vertex leaves the other branches connected
and each remaining internal path attached to a surviving branch.
G_t contains B, so it is not 3-colorable.

Encode 3-coloring as in F036: one positive triple and three negative
binary clauses for each vertex, and three negative binary clauses
per graph edge. The result is an unsatisfiable width-three CNF
F_t with 3n variables. Its primal graph consists of one triangle
per graph vertex and matching edges between same-color bits.
It is biconnected: all vertex triangles retain connectivity after
deletion of a bit, and every graph edge retains at least two of
its three links.

## Simultaneous parameter lower bounds

Every strong syntactic deletion backdoor to 2-CNF must hit all n
disjoint positive triples. Thus its size is at least n, also
within the sole primal block. More strongly, q-Horn recognition
fails on each untouched vertex gadget. With doubled weights a,b,c,
its constraints require a+b+c<=2 and a+b>=2, a+c>=2, b+c>=2.
Summing the last three yields a+b+c>=3, impossible, even with
real weights. Hence a strong deletion backdoor to q-Horn must
also hit all n disjoint triples: if none of a gadget's variables
is assigned, its clauses survive every literal restriction.
This assertion is about syntactic residual class membership,
not preprocessing by arbitrary inference or an early UNSAT exit.

For any s Boolean variables deleted from the primal graph,
at most s original graph vertices are touched. At least t-s
core branch vertices are untouched. At most s length-three paths
between surviving branches can be blocked by touched internal
vertices. If t>=2s+2, these branches remain connected: deleting
at most s edges from a clique on at least t-s vertices cannot
disconnect it, since any nontrivial cut has at least t-s-1>s
edges. The connected untouched core includes at least

    (t-s) + 2*(binom(t-s,2)-s) = (t-s)^2-2s

original vertices. Each of their three-bit triangles is intact,
so a connected primal component has at least
3*((t-s)^2-2s) Boolean vertices. A 2/3-balanced separator must
therefore satisfy

    (t-s)^2-2s <= (2/3)*(t^2+25)

or s>(t-2)/2. In particular for t>=40 and s<=t/10,
the left side is at least .81 t^2-.2t, strictly greater
than the right side. Thus balanced separators require
Omega(t)=Omega(sqrt(n)) variables. For any fixed separator
budget and any logarithmic backdoor budget the F037 root
plan fails on sufficiently large members of this family.

## Earlier mechanisms

Girth five and non-3-colorability also place F_t in the scope
of the previously derived F036 hybrid obstruction for scopes
through size four. The per-vertex odd parity space and original
binary conflict relaxation remain invariant under the specified
local affine-binary exchange. The uniform 1/3 point satisfies
all clique and odd-cycle constraints in the positive conflict
graph. No witnessed odd recoloring walk exists, by the absence
of triangles and four-cycles. These are mathematical consequences
of the earlier derivations, not executions of every solver on
the expanded family.

Consequently there is no completeness argument for the portfolio
consisting of the specified root structural promise, q-Horn
recognition, fixed-scope (<=4) affine-binary exchange, clique and
odd-cycle capacities, and witnessed recoloring. This statement
concerns the union of the specified mechanisms on the original
input, not arbitrary iterative combinations or general SAT
algorithms. In particular the construction contains a fixed
small UNSAT subgraph, so finding that subgraph is an obvious
possible bypass. It is not a family of proven hard SAT inputs.
The purpose is to refute a particular coverage argument; there
is no new complexity lower bound for SAT.

## Evidence

Previous q-Horn replay passed at a0a951742486696783250956d8427b58d2eb47df,
run 45687186149, job 139462765103. Its random sample contained
92 SAT, 52 UNSAT and 112 UNKNOWN cases.

Independent JavaScript execution checked five family sizes
t=8,12,16,24,32. Across the five graphs, all 2189 single-vertex
deletions preserved connectivity, all triangle/four-cycle tests
passed, all 27 possible local doubled q-Horn weight assignments
were rejected, and 736 sampled primal deletion sets satisfied
the quantitative connected-component lower bound. The largest
formula has 3147 variables and 8804 clauses. The general bound
is proved analytically, not inferred from sampling. Python
exact-head replay of the new fixture is pending.

## Research decision

Do not continue treating a larger union of tractable promise
classes as a route to universal completeness without a proof
of coverage. The remaining direct gate is a uniform decision
algorithm for unrestricted encoded 3-SAT with both a total
correctness proof and a polynomial bit-cost proof, or a
universal deterministic lower-bound argument. Neither is
available. Prior theorem and test counts are not a progress
percentage toward resolving P vs NP. No new Lean credit.
Main unchanged.
