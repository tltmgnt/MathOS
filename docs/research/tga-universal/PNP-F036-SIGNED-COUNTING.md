# F036 — Signed counting with grounded support

PNP_RESOLUTION_STATUS = OPEN.

This is a broader constructive UNSAT fragment, not a general SAT
decision procedure. The previous counting discovery passed its exact
head replay (b11e7e1, run 45681378005, job 139442496745).

## Mechanism

Treat every signed literal as a separate vertex. A binary clause
(a OR b) certifies that its complementary literals -a and -b cannot
both be true. Retain graph edges that lie in a triangle, form connected
components, and independently require every pair in a component to
have its original binary conflict evidence. This recognizes capacity-one
groups without knowing which signs encode selection, and can ignore
isolated cross-group edges. It does not solve arbitrary clique search.

Seed the literals in these groups with rank zero. In synchronous
rounds, mark a new signed literal p if an input clause contains -p
and at least one other literal, and every other literal already has
a rank. Record that original clause as the rule for p. Each new rank
is strictly larger than the ranks of all its rule dependencies.

For each original nonempty clause whose literals are ranked, resolve
away a highest-ranked nonterminal literal using its recorded rule.
Every new literal has strictly smaller rank. A pivot cannot reappear
after it is eliminated, because subsequent pivots have no higher rank.
Thus at most twice the number of occurring variables are eliminated
per candidate. Process unit clauses first, greedily retain pairwise
literal-disjoint demands, and discover a deficient Hall subset by
bipartite augmenting paths. Resolution traces and original pairwise
binary-clause evidence are checked independently.

## Soundness

Any model satisfies all replayed resolvents. Each selected demand
contains at least one true literal. Literal-disjoint demands require
distinct true literals, even if their underlying variable sets
overlap: opposite signs of one variable cannot both be true.
Each capacity group contains at most one true literal because
every pair has original binary evidence. Coverage and the strict
deficit therefore contradict the existence of a model. Groups may
contain opposite signs; this causes no soundness problem. The
checker accepts only the exact signed resolution steps and the
required coverage and deficit. Failure to find a certificate is
UNKNOWN, never SAT.

The graph triangle pass takes polynomially many abstract operations
(for example, O(V^3) adjacency tests). Grounding requires at most
V productive rounds, where V is the number of signed vertices
occurring in the CNF, and each expansion uses at most V steps.
Each normalized row contains at most V literals. Matching and
checking are polynomial in these explicit structures. This is not
a formal Python bit-machine refinement or a universal completeness
proof. A deterministic representation can use sorted lists instead
of assuming constant-time hash operations.

## Scalable family

In the prefix-OR pigeonhole encoding with k+1 pigeons and k>=2
holes, the signed conflict graph contains one clique of size k+1
per hole. The gate binary edges do not belong to triangles: the
negative prefix literals attach only to the previous positive
prefix and the current placement literal, which are not adjacent,
or to the first placement literal. The reverse first-gate edge is
isolated. Adding a single edge between placement literals for two
different holes of the same pigeon (as in the test) introduces
no triangle. Therefore triangle filtering still finds the hole
cliques. All placement literals start at rank zero. The intended
positive prefix literals become ranked in chain order, and their
backward OR clauses recover the disjoint placement demands from
the terminal units. Negative rails do not become grounded in this
family: every rule for such a rail would require another ungrounded
negative rail. Unit-first processing recovers all demands, and the
matching fails. Arbitrary consistent polarity flips and renaming
preserve these graph and rank properties. Thus the family is handled
without a known polarity, known gate map, or fixed variable IDs.

The new Python fixture covers k=2..20, three transformed UNSAT
instances per k (one with an extra cross-group edge), one transformed
satisfiable control per k, 512 random small signed CNFs with brute-force
soundness checks for each accepted certificate, and a known unsupported
UNSAT input. Independent JavaScript calculation already found
contradictions on 57 transformed UNSAT instances, including 19
bridged cases, and none on 19 untransformed satisfiable controls.
The Python fixture and independent certificate checks await exact
repository replay; they are not reported as passed prematurely.

## Remaining gate

Triangle components, greedy demand packing and grounded clause
expansion are deliberately incomplete. Variable polarity and a
single bridge no longer obstruct the specified family, but overlapping
triangle cliques can still defeat this recognizer, and signed
grounding need not recover all valid demands. Exact arbitrary
clique-capacity separation remains NP-hard. The next substantive
target is a different polynomially discoverable global invariant
or a sharply stated completeness theorem that can be falsified
without silently invoking an NP-hard subroutine.

No new Lean declaration credit. Main unchanged.
