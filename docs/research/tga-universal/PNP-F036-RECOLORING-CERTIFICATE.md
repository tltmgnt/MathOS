# F036 — Selective global rank inference by recoloring walks

PNP_RESOLUTION_STATUS = OPEN.

## Exact new certificate

For a simple undirected graph G, specify an apex w, an odd closed
walk v_0,...,v_(L-1), and a witness s_i for every occurrence v_i.
Require every consecutive pair of walk vertices to be adjacent,
and require s_i adjacent to w, v_(i-1), v_(i+1), with cyclic indices.
The vertices and witnesses need not be distinct. The checker checks
only the parity, bounds, and these original graph edges.

If G had a 3-coloring, rename the apex color to 3. Every witness
has color 1 or 2. Replace each walk occurrence of color 3 by its
witness color, retaining the other occurrences. Consecutive original
vertices have distinct colors, so at most one is recolored. If
one is recolored, its witness is adjacent to the other vertex,
which retains its color. Thus consecutive new colors differ,
including the closing edge. This is a 2-coloring of an odd closed
walk, a contradiction. Repeated vertices cause no difficulty:
the colors are assigned to occurrences in this argument.

Equivalently this certificate establishes a global capacity bound
alpha(H(G)) <= |V(G)|-1 for the standard three-color conflict graph
H(G) defined in PNP-F036-COLORING-GAP.md. It is not a computation of
the strongest possible capacity. The certificate proves UNSAT for
the standard graph-coloring CNF encoding, whose at-least-one and
at-most-one color clauses plus edge constraints exactly express
3-colorability.

## Complete polynomial discovery for this certificate language

For each candidate apex w, build a directed transition graph whose
states are ordered adjacent pairs (u,v). Put an edge from (u,v)
to (v,z) if N(w) intersect N(u) intersect N(z) is nonempty. Store one
witness from that intersection. A certificate for w exists exactly
when this transition graph has an odd directed closed walk.
Use a parity-expanded graph, with two copies of every state;
every transition flips the parity. For each state a, run a BFS
from (a,0) to (a,1). If a path exists, its projected walk and
stored edge witnesses give the checked certificate. Conversely,
any certificate induces such a path starting at one of its
ordered adjacent pairs. Therefore discovery is complete for this
specific certificate language.

There are 2m states, at most 4m parity-expanded states, and at
most n^3 transitions per apex. Using explicit adjacency tables,
testing candidate transitions costs O(n^4) per apex; BFS from
all states costs O(n^2 * (n^2+n^3)) per apex. Overall O(n^6)
abstract adjacency and graph operations suffices. A shortest
parity path has at most 4m-1 edges, so the encoded certificate
has O(m log(n+1)) bits. These are mathematical polynomial bounds
for the described graph algorithm, not a formal bit-cost theorem
for the Python implementation. They do not cover the separate
NP-hard problem of finding arbitrary rank inequalities.

## All-family improvement

For every nonbipartite simple base graph B, an odd cycle in B
gives a certificate in its Mycielski graph: choose the new apex,
use the original cycle vertices, and choose the corresponding
shadow as each witness. The algorithm requires neither the cycle
nor the Mycielski decomposition as input. The same certificate
survives any additional graph edges. For bipartite B, its
Mycielski graph admits a 3-coloring (copy the base colors onto
the shadows and use a third color on the apex), so soundness
implies discovery returns UNKNOWN. This gives a full decision
criterion on the promised Mycielski family, and sound UNSAT
certification on arbitrary simple graphs.

This directly closes the preceding exact clique-and-odd-cycle
relaxation gap on its entire odd-cycle family, without evaluating
maximum independent sets. The relevant extra inference is
conditional recoloring, not another inequality of that relaxation.

## Evidence and limits

The previous coloring-gap audit passed at 7876cb4075949d030bc2276b94207681775d4439
(run 45683196872, job 139448832384).
An independent JavaScript implementation of the new search and
checker was executed: 42 relabeled odd-cycle Mycielski instances
(including 14 with an extra edge), 14 even-cycle controls, and
256 random seven-vertex graphs. The 43 returned random certificates
were independently checked against exhaustive 3-coloring search;
none was a false positive. Largest returned walk length was 31.
The Python fixture additionally checks three malformed certificates.
Its exact-head replay is pending. Different random generators may
produce different random acceptance counts.

The implementation starts from an explicit graph, not arbitrary
CNF structure discovery. The underlying recoloring principle is
the classical Mycielski argument generalized to witnessed odd
closed walks; no novelty claim is made. Discovery is not complete
for arbitrary non-3-colorable graphs and returns UNKNOWN on
failure. Universal polynomial SAT decision remains open.
No new Lean declaration credit. Main unchanged.
