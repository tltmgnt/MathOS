# F036 — Common obstruction to a hybrid global invariant

PNP_RESOLUTION_STATUS = OPEN.

## Result: affine and binary domains cannot be combined for free

An exact joint satisfiability test for affine GF(2) equations and
2-CNF constraints is already NP-complete. For arbitrary graph G,
use three Boolean color bits per vertex. The parity equation
x_1+x_2+x_3=1 over GF(2), together with the three pairwise
at-most-one clauses, expresses exactly one color. For every edge,
forbid selecting the same color at its two ends by binary clauses.
The resulting mixed system is satisfiable exactly when G is
3-colorable. The reduction is polynomial and assignments are
polynomially checkable. See Garey, Johnson, Stockmeyer, Some
simplified NP-complete graph problems (1976),
https://doi.org/10.1016/0304-3975%2876%2990059-1 .
Gaussian elimination and 2-SAT are each polynomial separately;
a polynomial exact intersection oracle would imply P=NP.

## A stronger tractable hybrid and its invariant

Fix r>=3. Maintain an affine relaxation B and a binary-CNF
relaxation C. On every scope of at most r original Boolean bits,
retain local patterns satisfying every original clause wholly in
the scope, and extending separately to B and to C. Extract all
affine equations and all unary/binary clauses true of retained
patterns, adding them to the respective global systems. Allow
unrestricted Gaussian elimination and implication closure.
An empty retained set proves UNSAT. Terminate at a fixed point
or refutation. Every model remains in both relaxations.
For fixed r, the number of scopes is polynomial; at most n
independent affine equations and O(n^2) distinct unary/binary
clauses can be added, and each separate extendibility check
is polynomial. This is a specified algorithmic abstraction,
not an implemented full mixed solver or machine-cost theorem.

For any G of girth > r and chromatic number at least four,
encode its 3-coloring by the standard width-three CNF. Such
graphs exist by Erdos's high-girth high-chromatic theorem:
https://www.cs.yale.edu/homes/spielman/462/2007/lect11-07.pdf
(Theorem 11.7.1). Let P be the product of per-vertex odd-parity
planes, and Q the solutions of the original negative binary
clauses. Initially P is contained in B and Q in C. We show
these inclusions persist under the specified hybrid updates.

For a bit scope S, the touched graph vertices U number at most r,
so G[U] is a forest. Project any proper 3-coloring of G[U] to S.
The pattern satisfies the contained original clauses and extends
to P (choose arbitrary odd triples outside U) and separately to Q
(set all outside bits to zero). These patterns are retained.
The affine hull of proper forest colorings is the product of
odd-parity planes: from a 2-coloring, recolor each single vertex
to the unused third color, and repeat with swapped base colors.
The differences span both even-parity directions independently
at each vertex. Thus every learned affine equation holds on P.

For any one or two distinct bits, every setting allowed by Q
is attained by some proper coloring of G[U]. For two bits on one
vertex, the three possible patterns are exactly the one-hot
projections. For bits on different vertices, choose their colors
from the singleton or two-element sets specified by each bit.
Adjacent vertices can be assigned different colors unless both
bits demand the same color, precisely the excluded binary
conflict. Nonadjacent vertices may be prescribed independently.
In a forest, any proper prescription on at most two vertices
extends to a 3-coloring: if the two lie in the same component,
color their unique path, choosing the final interior color
different from both its predecessor and the prescribed endpoint;
then greedily color the branches. Length-one paths are already
proper, and disconnected components are independent.
Therefore every learned unary or binary clause holds on Q.

These arguments prove the inclusions by induction. No local
scope empties. With all scopes through size r present, the
fixed-point affine and binary solution sets are exactly P and Q:
original vertex triples yield their parity and original binary
scopes yield the conflict clauses. Both relaxations individually
have models but their intersection is empty. Even exchanging all
consequences of the permitted forms does not recover universal
completeness. This is a barrier to separate extendibility plus
local updates, not to a different mixed algorithm.

## A common obstruction to other investigated mechanisms

Take girth greater than max(r,4). The uniform rational point 1/3
satisfies all original clause, clique and odd-cycle inequalities
in the positive color-conflict graph, as in the coloring-gap note.
The same graph also defeats the witnessed odd closed-walk
recoloring language. At a walk occurrence v with distinct
predecessor u and successor z, its witness s must equal v:
otherwise u-v-z-s-u is a four-cycle. Thus every nonbacktracking
turn occurs at a neighbor of the apex w. Neighbors of w form an
independent set (no triangles). Any walk edge entirely outside
this set forces reversal at both ends forever, yielding an even
closed walk. If there is no such edge, the walk alternates
between neighbors and nonneighbors of w, also even. Therefore
no odd witnessed walk exists. This proves a common counterexample
for the separate specified inference mechanisms. It does not
prove that an arbitrary combination with additional derived
constraints, arbitrary extension variables, or branch learning
is incomplete. In particular it does not assert a lower bound
on unrestricted SAT algorithms.

## Concrete independently executed audit

Use the 21-vertex, 42-edge Brinkmann graph (girth five, chromatic
number four). Adjacency facts taken from SageMath's documented
BrinkmannGraph generator:
https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/generators/smallgraphs.html
and its source smallgraphs.py. Independently check the graph
has no triangle or quadrilateral, fails exhaustive 3-coloring
and admits a 4-coloring. The coloring CNF has 63 variables and
210 clauses. Independent JavaScript execution verified all
7546 nonempty vertex subsets of size at most four, 347445
proper local colorings, 446103 two-bit projection tests and
1764 recoloring parity-reachability start tests. Every local
affine hull has dimension twice the subset size; every pair
projection equals the binary conflict prediction; no recoloring
certificate exists. This is a test of the invariant, not a
run of the full proposed hybrid algorithm. The Python fixture
records these controls and checks the existing affine implementation.
Its exact-head replay remains pending.

The earlier global affine exact-head replay succeeded at
6fecd25a8c49ade27a417b534630ffe9d581fc42
(run 45684866791, job 139454670253), including 15 contradictions,
15 satisfiable controls, eight coloring gaps and three rejection
controls.

## Research decision

A portfolio of these individually tractable mechanisms is not a
generality proof. The common barrier and NP-complete joint
intersection rule out the naive strategy of treating exact
cross-domain consistency as a free operation. A new positive
route needs an explicit uniform inference principle that escapes
these limitations, together with a completeness and total-cost
argument. No such principle is established here. Do not count
fixture volume as a measure of proximity to resolution. No new
Lean credit. Main unchanged.
