# F037 — Frozen-model barrier to universal bounded repair

PNP_RESOLUTION_STATUS = OPEN.

## Previous replay

The RUP repair audit passed at 3fc08138e3625339eb93a292b8c073606b6f3b2c
(run 45691797807, job 139478876147), including 2155 accepted
overwrites and 3826 model transports in its Python sample.

## A common SAT obstruction, not an UNSAT benchmark

Let G have a proper 3-coloring c in which each vertex has at
least two neighbors of each of its two alternate colors.
Suppose G has girth g (shortest cycle length). In any other
proper coloring c', let D be the vertices where c and c' differ.
If v is in D, both of its neighbors of old color c'(v)
must also be in D: otherwise c' would give an edge equal colors.
Thus the induced graph on D has minimum degree at least two.
If D is nonempty, it contains a cycle, and |D|>=g.

Encode 3-coloring by one positive triple and three negative
binary clauses per vertex, plus three same-color negative
binary clauses for each graph edge. Models are precisely
one-hot color assignments. Different colors differ in two
Boolean coordinates, so the distance from c to any other
model is at least 2g. This also applies to each of its six
global color permutations. For every Boolean coordinate,
at least one such permutation sets the coordinate true
and at least one sets it false.

Consequently ANY rule promising to transport EVERY model
to a model with a particular fixed bit, while changing fewer
than 2g Boolean coordinates per model, is impossible on
this satisfiable formula. Choose a frozen permutation whose
bit differs from the required value; its transported model
must differ and hence is at distance at least 2g.
In particular no nonempty constant overwrite with support
size less than 2g can preserve every model. The earlier
RUP overwrite test is sound for that universal model
transport requirement, so it must reject each such overwrite.
The statement is stronger than a limitation of RUP itself:
allowing arbitrarily strong entailment proofs for the same
bounded overwrite would not help.

It does NOT imply that no fixed bit is satisfiability-
preserving in the existential sense. In fact every bit value
is viable in this family, by color permutation. It also
does not exclude a repair changing many coordinates, or
a rule exploiting color permutations. The distinction
between universal bounded repair and existential choice is
essential.

## Self-contained existence at arbitrarily large girth

Start with the complete tripartite graph K_(2,2,2) colored
by its three parts. Every vertex has two neighbors of each
alternate color. Given a finite connected simple graph G,
choose a spanning tree and let q be the number of edges
outside the tree. Give every tree edge label zero in GF(2)^q,
and each other edge a distinct standard basis vector.
Construct a finite cover with vertices (v,a), a in GF(2)^q,
and for each base edge uv with label b join (u,a) to (v,a+b).
This projection is locally bijective. It preserves degrees,
simplicity and the two-neighbors-per-alternate-color property
under the lifted coloring. It is connected: tree paths reach
any base vertex without changing the fiber, and walking a
fundamental cycle toggles its corresponding basis bit.

A simple cycle in the cover projects to a closed nonbacktracking
walk in the base, including at the cyclic join (by local
bijectivity). A nonbacktracking closed walk in a simple
graph of length at most its girth must be a simple cycle
of exactly that girth: any repeated vertex would give a
shorter closed segment containing a cycle, since there
is no immediate backtracking. Every simple base cycle
contains at least one nontree edge, each used once, so the
sum of its labels is nonzero. Such a walk cannot close
in the cover. Hence the cover has strictly larger girth.
Iterating gives the desired family for every fixed repair
budget r: choose girth greater than r/2. No economical
size-vs-girth tradeoff is claimed; the cover can be huge.
The construction does not imply a superpolynomial time
lower bound in the size of the resulting formula.

## Other checked progress rules

The prior local GF(2) translation subgroup is zero: the
unique falsifying pattern of each positive triple forces
its translation to be zero. The linear-autarky cone is
zero by the positive triple and three pair inequalities,
as shown in the checked folding note. q-Horn is likewise
ineligible on a one-hot triple, and a syntactic deletion
backdoor to 2-CNF must hit all disjoint triples.

The earlier gadget-folding search also cannot eliminate a
vertex. For a fold from u to v by a permutation of its three
colors, take a neighbor w of u distinct from v. The image
of the original edge conflict is a negative binary clause
between v and w. No original units or empty clauses exist;
thus a subsuming original clause would have to be exactly
that binary clause. In particular v and w must be adjacent,
regardless of the color permutation. If u,v are adjacent,
such w gives a triangle, impossible at girth >4. If they
are nonadjacent, at least two distinct common neighbors give
a four-cycle, also impossible. The degree is four, so there
are enough neighbors. The recognized one-hot supports are
exactly the original vertex triples (each ternary clause
is such a triple). No accepted gadget fold exists.

This disproves a universal progress argument for the union
of these particular reduction rules on original inputs,
even when repairs may have any fixed constant support
budget. It does not exclude separate structural decision
procedures, color symmetry breaking, general retractions,
other types of autarky, or SAT solvers.

## Evidence and scope

Independent JavaScript evaluation built the first cover
of K_(2,2,2) (cycle rank 7, fiber size 128). It checked all
768 vertices for proper color and degree properties,
computed girth 6 with BFS from every root, checked connectedness,
and examined all 294528 unordered vertex pairs for
neighborhood inclusion. No fold was found.
The Python fixture repeats the construction, checks the six
global color permutations against the 2304-variable,
7680-clause CNF, and verifies both Boolean values occur at
each coordinate. Its exact-head replay is pending. The
finite fixture does not enumerate all models; the distance
bound and arbitrary-girth argument are mathematical proofs.
No new Lean credit.

## Research decision

Further increasing the bounded repair width does not give
a universal progress theorem. Nor does replacing RUP with
a perfect implication checker under the same bounded
universal-transport requirement. The viable next target
must abandon that sufficient condition, allow genuinely
nonlocal transport, or establish an existential branch
preservation invariant that is weaker than transporting
every original model. The verified single-path gate still
requires an actual polynomial selector for all inputs;
no such selector has been proved. Main unchanged.
