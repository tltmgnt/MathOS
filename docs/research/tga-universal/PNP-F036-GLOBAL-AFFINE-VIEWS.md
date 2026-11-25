# F036 — Compact global affine views

PNP_RESOLUTION_STATUS = OPEN.

## Inference mechanism

Maintain an affine space B over GF(2) on all n occurring Boolean
variables, represented by an independent basis of equations.
Initially B is the full Boolean space. For each selected scope S
of size at most r, enumerate its patterns satisfying every original
clause wholly contained in S. Retain only patterns that extend to B,
testing this by Gaussian elimination after adding the fixed bits.
If none remain, report UNSAT. Otherwise extract all affine equations
holding on every surviving pattern and adjoin the independent ones
to B. Repeat until no rank increases. At a fixed point without
contradiction report UNKNOWN.

Inductively every original satisfying assignment lies in B:
its restriction is one of the retained patterns, so every inferred
equation is necessary. A local void therefore proves UNSAT.
The trace checker replays the equations against the prior affine
space and rechecks the final local void using exact integer
arithmetic. No numerical tolerance, global SAT oracle, or complete
semantic equivalence test is needed.

At most n independent equations can be added; at most n+1 passes
are needed. Each scope has at most 2^r patterns and 2^r-1 nonzero
linear forms. Every extension test is ordinary elimination on n-bit
rows, polynomial in n. For fixed r the number of possible scopes
is O((n+1)^r), so even processing all of them is polynomial in
the explicit encoded input after dense renaming of occurring
variable identifiers. The implemented version processes distinct
original clause supports and all clauses contained in each support.
It expects dense indices 1..n; a general sparse-ID front end and
formal bit-machine refinement are not supplied. Global combinations
of learned equations can have support n, even for r=3.

## Constructive positive family

Encode three independent XOR chains computing the same parity of
k input bits, with respective terminal bits a,b,c. Each XOR gate
has four width-three CNF clauses. Add (a OR b) and (not b OR not c).
Each pair clause by itself has full affine hull on its two bits.
The learned gate equations globally imply a=b=c. Under that space
the first pair requires a=b=1 and the second requires b=c=0.
The local void test detects the contradiction. Replacing the second
pair with (b OR c) gives a satisfiable control. No branching or
expanded monomial representation is used.

## Universal obstruction for any fixed local scope

Let G be a graph of chromatic number at least four and girth greater
than r. Such graphs exist for every fixed r by the classical
Erdos girth-chromatic-number theorem; see the formalized theorem
at https://isa-afp.org/entries/Girth_Chromatic.html .
Use the standard three-color CNF from PNP-F036-COLORING-GAP.md.
It is UNSAT. Let P be the affine space given by the single parity
equation x_(v,1)+x_(v,2)+x_(v,3)=1 for each graph vertex v.

Claim: every inferred equation is valid throughout P. Suppose
inductively P is contained in B. For a scope S of at most r bits,
let U be the original graph vertices touched by S. Then |U|<=r,
so the induced graph G[U] is a forest and is bipartite.

The affine hull of all proper three-colorings of any bipartite
graph, represented by one-hot triples, equals the entire product
of the odd-parity planes on its vertices. To prove this, take a
proper two-coloring using colors 1 and 2. Recolor any single vertex
to the unused color 3; this is still a proper coloring. The
difference of the corresponding vectors is supported just on
that vertex's triple and equals e_old+e_3. Swap colors 1 and 2 in
the base coloring and repeat. The second difference at that vertex
is the other independent even-parity vector. Thus the direction
space of the affine hull contains the two independent directions
for every vertex, spanning the product direction space. Every
coloring lies in the product affine space, so equality follows.
This proof also covers isolated vertices and the empty graph.

Project these proper colorings of G[U] to S. Each projection
satisfies every original clause wholly contained in S and extends
to P by setting arbitrary odd-parity triples outside U. Hence it
extends to B and is among the retained patterns. Projection
commutes with affine hull, so the affine hull of these retained
witnesses contains the entire projection of P. Any extracted
equation therefore holds on P, and the invariant P subset B
persists. In particular no local scope becomes empty.

Thus for every fixed r, even taking ALL scopes of size at most r
and allowing unrestricted global combinations of their affine
equations fails to refute some unsatisfiable width-three CNFs.
When all vertex-triple scopes are processed, the learned system
is exactly P at the fixed point: those scopes yield their parity
equations, and nothing stronger can be learned. This is a
restriction of the proposed affine-hull procedure, not a lower
bound for arbitrary algebraic inference or SAT algorithms.

For the previous odd-cycle Mycielski family, all touched graphs
on at most three vertices are bipartite because the graph is
triangle-free. The same proof applies for r=3 even though these
graphs are not arbitrary-high-girth examples. The experiment uses
this explicit family. The high-girth generalization is a
mathematical existence argument, not inferred from finite tests.

## Evidence

The earlier Boolean-view implementation passed its exact-head
replay at 8ce8627fabdd8e0153fa1226a37c64a756acb62e
(run 45684109237, job 139452042515), including 48 accepted random
certificates checked against exhaustive truth evaluation.

Independent JavaScript exact GF(2) computation passed all 15
contradictory parity chains (k=2..16), 15 satisfiable controls,
and eight coloring-gap instances (odd cycle lengths 5..19).
All eight coloring instances stabilized at precisely one
independent parity equation per graph vertex. In developing the
experiment, grouping only clauses with identical supports failed
to extract the one-hot parity equations; the corrected grouping
includes every clause contained in the scope. The Python trace
checker, three corruption tests and repository replay are pending.

## Decision

This establishes a compact global affine mechanism and an
obstruction that survives global linear combinations. Enlarging
scope by any fixed constant does not recover completeness.
A subsequent general mechanism must introduce genuinely
non-affine global inference or a different decision principle;
merely adding more affine views is insufficient. No new Lean
credit or unrestricted P vs NP claim. Main unchanged.
