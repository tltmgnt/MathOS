# F038 — Uniform parity evaluation is a separate counting problem

PNP_RESOLUTION_STATUS = OPEN.

## Verified starting point

The affine fingerprint audit and open resolution gates passed at
ce8f8aa8259cfc491dd29cfa75ed2e80b738d951
(run 45696878758, job 139496478880). Its Python audit reproduced
273 model sets, 798 choices, 2048 hash-extension checks, and a
nonempty projected model set invisible to 17 fixed parity probes.
The polynomial advice existence argument does not construct that
advice uniformly or evaluate the parity queries efficiently.

## Exact parity reduction: even easy decision formulas retain the problem

For a 3-CNF F with n designated variables and m normalized clause
occurrences, construct a simple graph G. For each variable i create
two literal-choice vertices t_i,f_i joined by an edge, and a private
guard adjacent to both. For each clause create a guard adjacent to
the literal-choice vertices satisfying its literals. All guards are
independent of one another. The literal-pair edges are the only edges
between choice vertices.

Condition on the independent subset of literal-choice vertices.
For each unblocked guard the number of extensions multiplies by two;
each blocked guard contributes one. Thus modulo two only selections
blocking every guard contribute. The variable guards and pair edges
enforce exactly one choice per variable. The clause guards then
enforce satisfaction of every clause. There is one contributing
selection per satisfying assignment, including assignments to
designated free variables. Empty clauses give isolated guards and
parity zero. Tautologies may be dropped and duplicates retained.
Consequently

    #IS(G) mod 2 = #SAT(F) mod 2.

G has O(n+m) vertices and edges. This is a parity-preserving
reduction, not necessarily a count-preserving one over integers.

## Remove high degree and odd cycles without changing parity

Write the independent-set edge interaction matrix over GF(2) as

    B = [[1,1],[1,0]],

where bit 1 means selected. Summing the independent-set indicator
over internal vertices of a length-k path, while holding its
endpoints fixed, yields the entries of B^k. Direct multiplication
gives B^3=I, hence B^4=B and B^6=I.

For each vertex v of G with degree d, use max(1,d) clones, each
with its own incident original edge if d>0. Connect consecutive
clones by internally disjoint length-six paths. Each such path has
conditional parity equal to the equality relation. Replace each
original edge by a length-four path between its assigned clones.
All clone vertices lie on one side of a bipartition; alternate the
sides along each even-length path. All internal vertices have degree
two and every clone has degree at most three. Keep isolated vertices
as single clones.

For any fixed assignment to the clones, sum over all internal
vertices. The paths have disjoint internal vertices, so their
conditional counts multiply. Modulo two the equality paths force
all clones of a vertex to agree; the other paths implement the
original edge interaction. Summing over the clones therefore gives

    #IS(expand(G)) mod 2 = #IS(G) mod 2.

There are at most 2|E|+|V| clones, at most that many equality paths,
and one length-four path per edge. All graph sizes and construction
costs are linear in n+m (up to explicit binary identifier encoding).
The output is simple, bipartite and subcubic.

Write the independent-set relation on this graph as the all-negative
2-CNF (not x_u OR not x_v) per edge, with a designated variable for
each vertex. Complementing all variables yields an all-positive
2-CNF with the same model count. Isolated bits remain designated
free variables (or can be represented with tautologies when needed).
Thus the parity of satisfying assignments of subcubic bipartite
monotone 2-CNF already has the full difficulty of unrestricted
3-CNF parity. Every output decision instance is satisfiable: the
all-true assignment satisfies the positive formula.

Membership in parity-P follows from counting the parity of accepting
assignment guesses; ordinary parity-SAT is parity-P-complete via
the count-preserving circuit-to-3-CNF encoding of polynomial-time
witness verification. This gives an explicit parity-P completeness
reduction for the restricted output family. The broader bipartite
independent-set parity completeness result is established literature;
see e.g. https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/100307/Roth%20Counting%20Homomorphisms%20to%202021%20Accepted.pdf
and the modern parity-SAT context at
https://drops.dagstuhl.de/storage/00lipics/lipics-vol377-sat2026/html/LIPIcs.SAT.2026.20/LIPIcs.SAT.2026.20.html .
No novelty or priority claim for this gadget reduction.

## Consequences for the proposed resolution route

A deterministic polynomial-time evaluator for all the affine
fingerprint queries would in particular evaluate unrestricted
3-CNF parity (use the empty hash constraint, or an identically
true affine row). This would put parity-P in P. By the previous
random affine isolation proof it would give a randomized
polynomial SAT algorithm with one-sided error, hence NP=RP.
Derandomizing the isolation remains a separate missing ingredient.
P=NP alone is not known to imply polynomial parity evaluation.
We should not require a general parity-counting breakthrough as
though it were a routine implementation of an ordinary SAT solver.

The reduction above does NOT rule out polynomial parity algorithms;
it precisely identifies the complexity consequence of such an
algorithm even on an apparently easy structural class. It is not
a P versus NP lower bound. Decision tractability, graph bipartiteness,
bounded degree, and the polynomial number of fingerprints are not
proofs of parity tractability. Neither a fast finite audit nor
matrix multiplication on individual paths supplies an efficient
evaluation of the resulting global tensor contraction.

## Executed finite validation

Independent JavaScript execution checked the core reduction on all
4096 clause-subset formulas of the existing three-variable fixture:
1280 SAT, 2816 UNSAT, and 544 with odd model count. It independently
checked all 76 simple labeled graphs on 0..4 vertices under the
path-and-clone expansion, with exhaustive original independent-set
parity as the oracle. It also checked 256 fully expanded formula
instances using a generic GF(2) binary factor eliminator not given
the gadget contraction order. The largest expanded graph had 310
vertices, and the maximum observed elimination scope width was four.
All comparisons and degree/bipartition checks passed.

The Python implementation additionally checks all eight endpoint
cases of the length-four and length-six paths by enumerating their
internal assignments. Its factor eliminator is an exact finite
audit oracle with table size exponential in the elimination scope
width. It is NOT a proposed polynomial parity algorithm; the width
bound observed on small constructed inputs does not generalize.
Exact-head repository replay remains pending.

## Research decision

Deprioritize unrestricted parity evaluation as the next primary
positive-resolution route unless a specific independent insight
into parity computation or a direct uniform derandomization
mechanism is supplied. The prior fingerprint completeness result
has two genuine open subproblems; moving the problem to counting
does not close the universal selector obligation. The next
resolution-first target should avoid needing exact global counts
and focus on the weaker existential preservation gate. No new
Lean credit, no main change, no PR, and no resolution claim.
