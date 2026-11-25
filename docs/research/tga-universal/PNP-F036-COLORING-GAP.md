# F036 — An exact integrality gap surviving all clique and odd-cycle capacities

PNP_RESOLUTION_STATUS = OPEN.

The previous fractional capacity implementation passed exact-head replay:
0bd52fa816ee1bb6f140d59a18b94adda9ae265e,
run 45682398083, job 139446053831. No new Lean declaration credit.

## Scalable family

Take the odd cycle C_k, k odd and at least five. Build its Mycielski
graph G_k: original vertices v_i, shadows u_i and apex w. Keep the
cycle edges, connect each shadow to the two original neighbors of
its corresponding cycle vertex, and connect the apex to every
shadow. There are 2k+1 vertices and 4k edges. The graph is triangle-free:
a triangle cannot use two shadows (no shadow-shadow edges), an apex
triangle would require two adjacent shadows, and a triangle with one
shadow and two originals would require adjacent neighbors of a cycle
vertex. Original vertices also form no triangle.

The graph is not 3-colorable. If it were, call the apex color 3.
No shadow has color 3. Recolor every original vertex of color 3
with the color of its shadow. Each original edge still has distinct
colors: its endpoints could not both originally have color 3, and
a recolored endpoint's shadow is adjacent to the other original.
The result would 2-color an odd cycle, impossible. Conversely, a
3-coloring of the original odd cycle extends to the shadows using
their corresponding original colors, and a fourth color suffices
for the apex. In particular deleting the apex yields a 3-colorable
graph. These claims apply to every k, not just the finite audit.

Let n=2k+1. Encode a 3-coloring as a width-three CNF F_k:
variables x_(v,c), c in {1,2,3}; one positive triple per vertex;
three negative binary clauses per vertex enforcing at most one color;
three negative binary clauses per original graph edge forbidding a
shared color. Thus F_k has 3n=6k+3 variables and 4n+12k=20k+4
clauses. Satisfiability is equivalent to 3-colorability, so F_k is
UNSAT.

## All clique and odd-cycle cuts remain feasible

Let H_k be the conflict graph on the positive color literals,
with an edge exactly when the original binary CNF forbids selecting
both endpoints. It consists of within-vertex color triangles and
same-color edges induced by G_k. Every clique of size >=3 is
contained in a single vertex's color triangle: a pair of vertices
from distinct original vertices can be adjacent only for the same
color, and any additional common neighbor would require a triangle
in G_k. Thus every clique has size at most three.

Set every x-coordinate to exactly 1/3. All original clause
inequalities hold (positive triple sum=1; negative pair sum=4/3).
The variable bounds, at-most-one constraints, every clique inequality
and every odd-cycle inequality of H_k hold simultaneously. Indeed a
clique of size a has fractional sum a/3<=1, and an odd simple cycle
of length 2j+1, j>=1, has sum (2j+1)/3<=j. This argument covers ALL
cliques and simple odd cycles, not merely those enumerated by some
polynomial separation routine. It is an exact rational point.

Consequently no nonnegative linear combination of these inequalities
can derive a contradiction, even with unrestricted exact weights.
In particular fractional capacity covering of any subset of the
designated demands by arbitrary clique groups (or odd-cycle groups
with their valid integer capacities) cannot exhibit a strict
deficit. Summing the weighted coverage inequalities against this
feasible point directly proves this assertion. This is a limitation
of the given relaxation; further cuts, resolution or other
nonlinear inferences are not ruled out.

## Missing global inequality and its complexity

An independent set in H_k chooses at most one color per original
vertex, and is exactly a proper partial 3-coloring of G_k on the
chosen vertices. Therefore its maximum size is n-1: n would give
a 3-coloring of G_k, and n-1 is attained by the coloring after
deleting the apex. The valid full-set rank inequality is

    sum_(v,c) x_(v,c) <= n-1.

The fractional point has sum n; the demand constraints also imply
sum >= n. This single rank inequality would close the gap.

But for arbitrary graphs G the same 3-color conflict construction
H(G) has alpha(H(G))=|V(G)| if and only if G is 3-colorable.
Thus deciding whether the exact full-set capacity is at least
|V(G)| is NP-complete, and computing the strongest rank bound is
NP-hard. This standard reduction does not imply that finding some
useful rank inequality is NP-hard on every input, and does not
rule out other efficient mechanisms. In particular the family here
has an elementary known coloring obstruction.

## Evidence

Independent JavaScript execution checked k=5,7,...,19; all eight
graphs failed exhaustive 3-color search and admitted 4-colorings,
and all apex-deleted graphs admitted 3-colorings. Exact integer
checks of the 1/3 point, triangle and four-clique tests, and all
possible odd cycle lengths passed. Sizes range from 33 variables
and 104 clauses to 117 variables and 384 clauses. The Python
fixture repeats these checks; its repository replay is pending.
The finite search oracle is not a polynomial decision procedure.
The scalable result follows from the mathematical construction.

## Decision

The clique-plus-odd-cycle LP route is incomplete even if separation
and rational optimization are exact. Strongest unrestricted rank
capacity discovery already subsumes an NP-complete problem.
A future positive mechanism must generate a sufficient subset of
global consequences uniformly in polynomial time, rather than
assume a complete separation oracle. No unrestricted P vs NP
conclusion, new Lean credit, or main-branch change.
