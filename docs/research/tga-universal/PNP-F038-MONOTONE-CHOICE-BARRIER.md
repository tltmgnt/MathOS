# F038 — Monotone circuit barrier for existential branch choice

PNP_RESOLUTION_STATUS = OPEN.

## Verified starting point

The parity-complexity reduction and open resolution-gate audit
passed at 7433c8a2f74494beffb567226d05a7608aa4329b
(run 45697443075, job 139498417069). The replay reproduced 4096
core formula reductions, 256 full expansions and 76 graph controls.
No polynomial counting algorithm is assumed. Historical reported
verified declarations: 1603.

## A weaker target than exact branch recognition

Consider a candidate selector for a pair of 3-CNF branches with
fixed clause vocabularies. Let its output be one for the true
branch. The input coordinates are clause-presence flags on the
false branch and clause-ABSENCE flags on the true branch.
This orientation makes increasing a flag either constrain the
false branch further or relax the true branch. The candidate
need only choose a satisfiable branch when one exists. In
particular it need not recognize unsafe choices exactly or
distinguish two satisfiable branches, and it may output either
bit when both branches are unsatisfiable.

Investigate the proposed global invariant represented by a
polynomial-size monotone Boolean circuit (AND, OR, constants)
on these oriented flags. This is a syntactic restriction on
the computing circuit, not merely monotonicity of the computed
function. Sharing subcircuits and arbitrary circuit depth are
allowed. The following transfer of an established lower bound
rules out this candidate architecture, even nonuniformly.

## Graph-to-branch reduction

For graph G on n vertices and k>=2, make a fixed CNF template
with a selector z and two disjoint sets of witness variables:

* z=false activates the encoding of a proper (k-1)-coloring:
  each vertex has exactly one color, and for every present edge,
  its endpoints cannot share a color.
* z=true activates the encoding of a k-clique:
  each of k positions chooses exactly one vertex, no two
  positions choose the same vertex, and for every absent edge,
  neither orientation of its endpoints may occur in two
  different positions.

Use one-hot encodings. Guard all coloring clauses with z and
all clique clauses with not z. Split guarded long clauses by
fresh private auxiliary variables into clauses of width three:
replace a long disjunction (a OR b OR R) by
(a OR b OR u) AND (not u OR R), and repeat on the latter
clause as needed. Existential elimination of u recovers the
original disjunction. The graph-dependent clauses were binary
before guarding, so require no splitting. All fixed template
clauses, including the split clauses, are independent of G.
An inactive branch always has a satisfying extension, since
its guarded original clauses are true and the private split
auxiliaries can be chosen accordingly.

The resulting F_G satisfies

    SAT(F_G restricted by z=false) iff G is (k-1)-colorable;
    SAT(F_G restricted by z=true) iff G contains a k-clique.

The two cases cannot overlap, because vertices of a k-clique
must use k distinct colors in any proper coloring. Thus every
safe selector must output one for k-clique graphs and zero for
(k-1)-colorable graphs. On other graphs either branch may be
unsatisfiable; no correctness condition is imposed there.

For each graph edge indicator e_uv, wire it directly to all
coloring-clause presence flags associated with uv, and directly
to all clique-clause ABSENCE flags associated with uv. Fixed
clauses give constants. No negated graph input is needed in
these oriented coordinates. This is a monotone projection
by constants and repeated positive input wires. The template
has O(nk+n^2 k^2) clauses and polynomial bit length for k<=n;
the long one-hot clauses are split with only polynomially many
auxiliaries.

## Lower-bound transfer

The classical Razborov/Alon-Boppana monotone clique lower-bound
method in fact separates isolated k-cliques from complete
(k-1)-partite graphs, not just exact clique recognition.
In particular the Alon-Boppana bound n^Omega(sqrt(k)) holds
in the range k <= n^(2/3-delta) for fixed delta>0. For the
promise-distribution formulation and its parameter range see
Blasiok and Meierhofer, Hardness of Clique Approximation for
Monotone Circuits, CCC 2025, introduction and discussion after
Theorem 14:
https://drops.dagstuhl.de/storage/00lipics/lipics-vol339-ccc2025/html/LIPIcs.CCC.2025.4/LIPIcs.CCC.2025.4.html
The original lower bound is from Alon and Boppana, The monotone
circuit complexity of Boolean functions, Combinatorica 7 (1987).
Here only the earlier bound and its standard positive/negative
test sets are used, not the stronger recent random-graph bound.

Choose k=floor(n^(1/4)) for sufficiently large n. Substituting
the positive graph wires and constants above into a candidate
monotone selector circuit gives a monotone separator of the
two graph test sets: isolated k-cliques have only the true
branch viable; complete (k-1)-partite graphs have only the
false branch viable. Even arbitrary behavior outside these
test sets is allowed. Hence the selector circuit requires
n^Omega(n^(1/8)) gates, superpolynomial in its polynomial
template length. This is a transfer of an established theorem,
not a newly proved unrestricted circuit lower bound.

This obstruction applies to computing a safe choice, not just
exact SAT, counting, or recognizing all safe branches. It is
independent of the depth of the monotone circuit and allows
nonuniform circuits. It does not imply the same lower bound
for general circuits with negations or polynomial-time
algorithms. Nor does it rule out semantic monotonicity with
a nonmonotone implementation, adaptive selection of a different
variable, or using a different input representation with
nonmonotone preprocessing. If both positive and negative
graph input wires are supplied, the restriction can become
vacuous; the oriented flags above are essential.

## Independent validation

An independent JavaScript implementation built the guarded
one-hot templates, exhaustively enumerated every labeled graph
for (n,k)=(3,3),(4,3),(4,4),(5,3),(5,4), compared both branch
SAT results and whole-formula SAT against direct graph
enumeration, and checked both branch predicates under each
single-edge insertion. Across 2184 graphs, 1445 had only the
coloring branch viable, 727 only the clique branch and 12
neither. No graph had both viable. All 4368 branch checks and
2184 whole-formula checks agreed, and 10636 edge-insertion
checks passed. The largest template used 53 variables and the
largest instantiated formula had 231 clauses. These are
finite validation oracles using exhaustive enumeration/DPLL,
not polynomial SAT solvers. The Python regression also checks
the oriented input flags and the no-promise control C5 at k=3.
Its exact-head replay is pending.

## Decision

A purely monotone global selector over this natural oriented
clause template cannot establish universal progress, even
though the target need only preserve existential satisfiability.
This closes one restricted proposed architecture, not the
general problem. The next direct candidate must allow
nonmonotone global reasoning or use a materially different
representation; the universal algorithm, preservation and
polynomial bit-cost gates remain open. No new Lean credit,
no main change or PR, and no P versus NP resolution claim.
