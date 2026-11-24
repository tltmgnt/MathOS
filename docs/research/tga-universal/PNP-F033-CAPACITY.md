# PNP-F033 — Signed structural capacities and counting certificates

PNP_RESOLUTION_STATUS = OPEN. PR #158 merged at
d33aca15690c244648fc0a97c3e1f0b5bf8d70dc. Its actual CI run
45461192027 job 138683884541 passed six tests: 1600 paired sparse
formulas (3200 runs), eight certified UNSAT and 1592 UNKNOWN in
the original half, 64 exhaustive PHP2 polarity patterns, 18 signed
PHP and equal-size controls, six noisy negatives. Largest PHP
64 had 4160 variables, 133185 clauses, 6240 edge scans and zero
search nodes/pairs at both seeds. Artifact 14952074589.
https://github.com/tltmgnt/MathOS/actions/runs/45461192027/job/138683884541

## Certificate semantics

Select nonempty original demand clauses with disjoint variable
supports and no opposing pair inside a demand. Partition the union
of their signed literals into groups with explicit capacities c=1
or 2, no greater than group size. For each (c+1)-subset of a group
require an original CNF clause consisting of the complementary
literals, allowing duplicates/order normalization. Consequently at
most c signed literals can be true in that group. Every model needs
at least one true literal per demand, and disjoint supports make
these choices distinct. A total capacity strictly below the number
of demands proves UNSAT. This is a counting certificate on signed
literals; no orientation or matching assumption is needed. The
checker accepts mixed capacities and trivial groups of size c with
no conflict refs. It checks exact coverage and all original clause
references, not solver counters or discovery choices.

## Structural recognition

For fixed k in {1,2}, construct the (k+1)-uniform hypergraph on
signed literals from complements of normalized input clauses of
that width. Use a connected component as evidence only when its
distinct hyperedge count equals binom(size,k+1); this is precisely
completeness for a simple uniform hypergraph. For each variable
choose its sign only if it belongs to a strictly larger complete
component than the opposite sign (missing size zero). Drop clauses
containing any nonselected literal for demand discovery. Greedily
select variable-disjoint demands by width then absolute IDs. Match
each demand to k slots for each incident group using existing
augmenting paths. A failed augmentation identifies a deficient
subset. Restrict groups to used literals, lower capacities to group
size if smaller, and emit original (k+1)-clause references.
This policy is polarity-equivariant for fixed variable IDs; tied
components, incomplete components, overlapping demands and greedy
selection can defeat it. It is not complete for arbitrary capacity
encodings.

## Noisy signed PHP and capacity-two family

Use k*h+1 demands each over h resources, with one distinct
variable per incidence. Each resource forbids every (k+1) true
variables by explicit negative clauses. Add a shared fresh g and
all (x_v OR g) clauses, then shuffle sparse IDs and independently
complement variables. For k=1 the true resource-side components
remain complete with size h+1. The opposite-side noise star joins
the other signs into an incomplete component (even when h=2).
For k=2 binary noise is ignored in the uniform triple graph;
opposite demand-side components exist only for h=3 and have size
3, smaller than the resource groups of size 7. Thus the structural
policy selects precisely the demand signs on these families,
recovering the original disjoint demand clauses and capacities.
The noise clauses are not selected as demands (g is ineligible).
For k=2, this is a genuine capacity extension beyond the pairwise
Hall language: each group can accommodate two true literals.
Equal-size formulas with k*h demands are satisfiable by assigning
one resource per demand, k per resource and g=true. No generalized
Hall completeness for arbitrary hypergraphs is claimed.

## Integration and complexity

Try k=1 then k=2 before unchanged SIGNED_HALL/HALL/F032 fallback.
The CAPACITY route may terminate with zero pair and search budgets.
The matching graph has at most 2r slots and at most twice the
explicit demand incidence count; edge scans are at most d*e.
For fixed k, complete components can be detected by edge count
without enumerating absent edges. Checking certificates enumerates
at most O(r^3) triples; the actual conflict references must occur
in the input. Discovery/replay are polynomial in explicit bit length
with finite-list representations. No total transition bound claimed.

New tests: 1600 arbitrary small sparse CNFs at both capacities
with paired polarity runs (6400 total), 26 noisy signed PHP
fixtures (k=1 through 32 holes; k=2 through 16 holes, two seeds),
26 equal-capacity controls, mixed-capacity certificate, missing
triple/tie negatives, original-reference tamper and fallback.
New empirical results await CI. Prior seven Hall theorems only
cover capacity one on normalized positive demands; the generalized
counting theorem and signed certificate transport are paper
arguments, not new kernel results. No independent review, executable
refinement, original scratch port or global promotion. Main unchanged.
