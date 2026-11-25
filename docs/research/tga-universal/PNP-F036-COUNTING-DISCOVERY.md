# F036 — Discovering global counting certificates

PNP_RESOLUTION_STATUS = OPEN.

## New decision mechanism

The preceding bounded-scope counterexample is now handled by an
explicit certificate-discovery algorithm, without supplied demand
clauses, hole groups, gate maps, or a branching tree.

On an arbitrary signed-integer CNF, construct the graph of negative
binary clauses. Retain connected components that are complete graphs:
each is a capacity-one group. Starting from positive input clauses,
expand non-group literals through clauses of the form
(not v OR a) or (not v OR a OR b), with positive a,b, recording each
exact resolution step. Stop expanding a candidate if a pivot repeats
or a suitable clause is absent. Keep a greedily selected collection
of positive, pairwise variable-disjoint demands supported on the
recognized groups. Construct the demand/group incidence graph.

Augment a matching one demand at a time by breadth-first search.
If no augmenting path exists, collect reachable demands S and
reachable groups T. All neighbors of S lie in T, every member of T
is matched to a distinct reachable demand other than the new
unmatched root, and each reachable demand other than the root was
reached through its matched group. Hence |S|=|T|+1. Return the
resolution trace, the demands S and the groups T.

## Soundness and scope

The standalone checker replays each set-normalized resolution step,
checks that demands are nonempty, positive and variable-disjoint,
checks each group's complete negative-binary evidence in the original
formula, checks coverage, and checks the strict Hall deficit.
Every satisfying assignment would have to select a distinct true
variable from each demand, whereas each group can contribute at most
one true variable. This is impossible when |S|>|T|. Thus an accepted
certificate proves UNSAT. This is a mathematical soundness argument,
not a verified Lean refinement of the Python checker.

The search loops are bounded by the numbers of rows, occurring
variables, and incidence edges. Each input demand has at most n
expansions because each pivot is used at most once; intermediate rows
contain at most n distinct positive variables. The matching search
visits each demand and group at most once per augmentation. The
checker has at most a polynomial number of clause and pair checks.
This gives polynomial bounds on the abstract operations and
certificate entries of this particular construction. Full deterministic
bit-cost accounting for Python and a canonical wire format are not
supplied. Neither the greedy selection of disjoint demands nor
recognition of clique components is universally complete.

For the prefix-OR pigeonhole family of the preceding note, the
negative binary graph is exactly the disjoint union of hole cliques.
Backward resolution from each terminal positive unit recovers its
pigeon's placement demand. These demands are pairwise disjoint, and
their bipartite incidence graph is complete. When k+1 pigeons share
k holes the matching necessarily fails. This is an all-k argument
for the specified family (k>=2), not merely a fixture observation.

## A barrier to arbitrary clique-capacity discovery

One might attempt to improve the method by generating every violated
clique inequality rather than only recognizing clique components.
Even separation of these inequalities at an explicitly given feasible
point of the edge relaxation is NP-complete.

Given an undirected graph G and a CLIQUE threshold K>=3, encode each
edge uv as (not x_u OR not x_v). The all-zero assignment satisfies
this CNF. In the fractional relaxation 0<=z_v<=1 and z_u+z_v<=1
for every edge, set z_v=1/(K-1). This point is feasible.
For a clique Q, the valid capacity inequality sum_(v in Q) z_v<=1
is violated exactly when |Q|>=K. Therefore an exact polynomial-time
algorithm deciding whether any clique capacity inequality is violated
would solve CLIQUE. A clique is itself a polynomially checkable
witness; rational arithmetic is exact. This is a reduction from the
standard NP-complete CLIQUE problem, not an unconditional proof that
separation needs exponential time.

The result does not rule out selective clique discovery, other
constraints, or an efficient SAT decision algorithm. It excludes
assuming an unrestricted exact clique separator is an easy
polynomial-time primitive without already resolving P versus NP.

## Executed controls

The Python fixture passed locally: 57 shuffled UNSAT pigeonhole
instances (k=2..20, three shuffles each), 19 satisfiable equal-hole
controls, one proper Hall-subset deficit, three corrupted-certificate
rejections and one UNSAT input on which discovery returns None.
The latter is not a SAT answer. The Python CI replay is a separate
verification step; no new Lean theorem credit.

## Next research decision

Global counting detects the previous local-consistency obstruction
without exhaustive branching. General completeness remains open,
and discovering arbitrary strongest clique cuts already subsumes an
NP-complete problem. The next useful question is whether a different
uniform, efficiently discoverable global invariant can cover inputs
beyond this structural fragment, without relying on exact NP-hard
separation. Main unchanged.
