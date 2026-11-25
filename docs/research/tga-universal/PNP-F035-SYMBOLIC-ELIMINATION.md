# F035 — Semantic summary width barrier

PNP_RESOLUTION_STATUS = OPEN.

For equality of two k-bit words, a deterministic representation that reads
all first-word bits before second-word bits and stores a state sufficient
to answer every possible second word must retain 2^k distinct attainable
states. If two different prefixes share a state, querying the first
prefix as the suffix must return both true and false. This excludes exact
state merging for that blocked order, even semantic rather than syntactic
merging. The Lean candidate constructs a list of 2^k pairwise distinct
states for any exact summary type, without assuming a particular encoding.

Equality has a linear-size 2-CNF representation: for each pair (x_i,y_i),
the clauses (not x_i or y_i) and (x_i or not y_i). The interleaved order
can check each pair immediately and retain only a mismatch flag between
pairs. The paired comparator is proved equivalent to equality in the
candidate module. Thus the lower bound is on the number of blocked-order
states, not their individual bit lengths, nor all variable orders,
circuits, branching programs, or SAT algorithms. A compact program that
stores the prefix itself is not ruled out. The result is relevant to
explicit state-table/DAG enumeration, not a universal time bound.

11 public theorem candidates, 87381 paired input checks for k=0..8.
Strict replay required. Next gate: investigate an explicit uniform
representation with bounded construction AND decision operations;
compact representation alone does not establish efficient SAT.
