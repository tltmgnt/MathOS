# F035/F040 — Constructive nonempty 2-CNF model extraction

PNP_RESOLUTION_STATUS = OPEN.

Integrates the exact path compiler from 1ce648a3 (14 zero-axiom declarations,
44 controls) and the unchanged reachability completeness module from
0ea47406 (23 zero-axiom declarations, 6208 controls).

For an occurring literal a, define its score as the little-endian bit
vector of all reachable literals, over a fixed list of both signs of
all occurring variables (duplicates harmless). Use the smaller score
of a and its complement as the true literal. Reachability is reflexive,
transitive and contrapositive because every graph arc has its
complement-reversed arc. Along an edge a->b, score(b)<=score(a) and
score(not a)<=score(not b). Equality of the two complementary scores
would imply mutual reachability, by bit-vector injectivity and
reflexivity. In the absence of conflicts the scores are distinct,
so every implication preserves truth. This satisfies every unit and
binary row. This ranking is an explicit alternative to SCC ordering.

The candidate noConflict_iff_sat is restricted to formulas whose rows
are all units or binary clauses; the empty formula is included, empty
clauses are excluded. discover uses the first complementary reachable
variable and checked path compilation, no exhaustive fallback. For
valid typed formulas in this fragment, discover_iff characterizes UNSAT,
and a missing conflict yields the executable satisfying assignment.

The rank integer has potentially exponential numeric magnitude but a
linear bit length in the literal occurrence list. A formal bit-cost
bound, efficient caching and support for empty-clause inputs remain
separate work. The method recomputes reachability and is not a
linear-time SCC implementation. No unrestricted SAT claim.

29 public theorem candidates; 535 controls: 256 subsets of four binary
and four unit rows, their 256 reversed versions, 20 implication-chain
SAT/UNSAT pairs (10 of each), two sparse identifier cases and one
empty-formula case. The UNSAT tests require the original bound checker
and cannot be satisfied by exhaustive fallback. SAT tests evaluate the
constructed model. Exact-head strict Lean replay is required.
