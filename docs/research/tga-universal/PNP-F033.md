# PNP-F033 — Hall-deficiency certificates from CNF

PNP_RESOLUTION_STATUS = OPEN. Baseline PR #155 merged into the parity
research branch at c4c9e1f495c151a806da821acb169f65607c9b94.
CI run 45450598377 job 138646297848 passed five wide tests and 1000
random cases (609 UNSAT, 391 SAT). PHP h=2,3,4,5 used 3,11,47,239
search nodes and 22,75,280,1290 resolution lines. h=6,7 exhausted
1000 visits and returned UNKNOWN. Shared-selector odd q=4,8,16 used
31,127,2047 visits; matched even cases SAT in 4,6,10 visits.
Artifact 14947427380.
https://github.com/tltmgnt/MathOS/actions/runs/45450598377/job/138646297848

## Scope and certificate theorem

Select original nonempty all-positive demand clauses with pairwise
disjoint variable sets. Partition their union into disjoint groups
such that for every distinct pair a,b within a group the original
formula contains a clause with literal set {-a,-b}. Repeated literals
are allowed. Each group has capacity at most one true variable.
Every model must choose at least one true variable in each demand.
Disjoint demands force these choices to be distinct. Hence if the
number of groups is smaller than the number of demands there is
no model. This is a finite counting argument, or Hall deficiency
on the demand-to-capacity-group incidence graph. Other clauses
can only further constrain a model. The verifier checks original
demand indices, positive disjoint supports, exact group coverage,
strict deficiency, and original clause references for every
within-group conflict pair. It does not invoke matching or discovery.
This is a paper proof of soundness, not executable Lean refinement.

## Recognition and extraction

Deduplicate positive clause supports; greedily select disjoint
demands in order of width then lexicographic variable IDs. Build
the negative binary conflict graph restricted to their variables.
Use connected components only when complete, otherwise singleton
groups (deliberate conservative incompleteness). Build bipartite
adjacency from demands to groups. For each demand, attempt an
iterative BFS alternating-path augmentation. On the first failure
the reachable left set S has every neighbor reached and matched
to some other reached left vertex, so |N(S)|=|S|-1. Restrict groups
to the selected demand variables and emit their original conflict
references. Matching success returns UNKNOWN, not SAT; other
constraints may matter. This extracts a local Hall deficiency
even when the whole graph has at least as many groups as demands.

For canonical unary PHP and arbitrary nonempty restricted matching
CNFs, demands are already disjoint and conflict components are
cliques (one per nonempty resource). Thus this recognizer is
complete for contradiction on those encodings. Polarity-preserving
sparse renaming and clause/literal shuffling do not affect that
property. It is not invariant under arbitrary polarity flips;
nonclique conflict components or overlapping demands can defeat
the heuristic. Explicit negative controls demonstrate these gaps.

## Complexity and integration

Let d be selected demands, e distinct bipartite incidences,
r occurring variables and L the explicit input bit length.
The augmenting routine scans at most d*e edges because each left
vertex is dequeued at most once per attempt. Discovery and replay
are polynomial in L using ordinary finite list representations;
all demanded variable IDs and certificate clause references are
explicit. The proof needs at most d demand references, r grouped
variables and at most r(r-1)/2 conflict references (in fact at
most the input clause count for distinct pairs). The counter is
abstract edge scans, not total machine steps. It excludes graph
construction, matching bookkeeping, and replay. No n-sized array.

A new wrapper adds the HALL route before the unchanged F032
hybrid; zero pair and node limits do not disable Hall inference.
Other SAT/UNSAT routes and UNKNOWN semantics remain unchanged.
The old hybrid lower bound still applies to that old policy,
but its PHP family is no longer an obstruction to the wrapper.
No claim of a polynomial bound for unrestricted SAT or a new
lower bound on combined algebraic/combinatorial proofs.

## Controls and status

1500 arbitrary seeded small sparse CNFs checked against brute
force, 600 restricted matching formulas checked by independent
enumeration of injective choices, nine shuffled canonical PHP
sizes through 64 holes with zero search/pair budgets, nine equal
size negative controls, proper-subset deficiency, overlap and
nonclique negatives, complemented PHP negative, certificate
tamper, sparse IDs, direct XOR and SAT fallback. These are new
tests awaiting CI; counts and runtime must not be reported as
passed before the actual job succeeds. Existing Lean gates
unchanged. Next: formal finite counting soundness and explicit
polarity/capacity recognition boundaries. No original scratch
port, independent review or machine refinement. Main unchanged.
