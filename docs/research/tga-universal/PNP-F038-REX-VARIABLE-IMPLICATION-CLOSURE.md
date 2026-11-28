# F038-REX-024D7I — Certified implication reachability and projected conflict closure

Parent D7H: 75f4612f92e1a8239f8f8485594eaa0984a85281. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4; Omega obligations 0/6.

## Exact binary implication graph

The input is the existing explicit Boolean factor instance, with distinct coordinates in each scope and arity at most three. Each forbidden row of a factor represents an exact clause on that scope. An empty allowed table immediately certifies UNSAT. For the unary and binary clauses only, construct a graph on the 2k signed literals. A binary clause (a or b) contributes arcs -a -> b and -b -> a; a unit (a) contributes -a -> a. Each arc records its original factor index. Higher-arity factors are not used as binary axioms, even if they imply additional binary consequences.

Run breadth-first search from each literal. A path p -> q entails (-p or q). A pair of paths p -> -p and -p -> p certifies contradiction, regardless of the other factors. The checker validates each edge by testing its exact falsifying row against the referenced original unary/binary factor, and checks complementary endpoints. Paths are simple and have at most 2k-1 edges. The implementation tests mutual reachability by BFS rather than a dedicated SCC algorithm.

The binary-part consistency test is complete. If no complementary pair lies in one strongly connected component, assign each literal true precisely when its component is later than the complementary component in a topological ordering of the condensation graph. The complementary arc property ensures every implication is satisfied: a true-to-false arc would imply rank(p) <= rank(q) < rank(-q) <= rank(-p) < rank(p), impossible. Thus the unary/binary clauses are satisfiable; this does not decide the higher-arity factors.

## Anchor projection theorem

Let A be the set of coordinates occurring in any original ternary factor, and let the binary part be consistent. The projected view preserves every ternary factor (with coordinates compactly renumbered) and contains every non-tautological unit/binary clause (-p or q) for which both endpoint coordinates lie in A and q is reachable from p. Duplicate clauses are stored once, each with an explicit original-edge path. The case q=-p gives a unit; q=p is a tautology and is skipped. No other original binary-only coordinates are kept.

**Claim:** the model set of this view is exactly the existential projection of the full model set onto A.

Necessity follows by following each implication path in any satisfying assignment. For sufficiency, fix an assignment of the anchors satisfying the view and add the unit clauses for its chosen literals to the consistent original binary part. If this augmented binary part is inconsistent, it has a closed directed walk through a complementary pair. The walk must contain an added unit arc. Between consecutive added arcs, cyclically, there is an original path from a chosen literal p to the negation of a chosen literal q. A zero-length path would mean two incompatible choices for one anchor, impossible. A nonzero path produces the stored clause (-p or -q), violated by the chosen assignment, also impossible. Therefore the anchor assignment extends to a model of the binary part, and the original ternary factors hold because all their coordinates were fixed. When there are no anchors, a consistent binary part projects to the single empty assignment. Empty-factor and binary-contradiction results are handled before projection.

This is an exact existential projection, **not** generally a bijection or a lexicographic witness transformation. D7I uses the view only for contradiction discovery. On UNKNOWN, the inherited D7H structural policy is also tried on the original residual, then unchanged D7D inference with the D7H sparse cardinality guard. If unresolved, return the exact original residual and identity expansion. A covering matching or a consistent binary component is never interpreted as a full SAT decision.

## Independent certificate verification

The projection certificate includes the sorted original anchor indices, source ternary factor indices, original path endpoints and edge factor references, and a nested D7H Hall certificate for the compact view. The verifier reconstructs the view independently using forbidden-row membership and validates all path clauses, then checks the nested Hall proof. It does not trust the producer's BFS, completeness claim, polarity votes, or matching heuristic. The verifier need not recompute reachability completeness for a refutation: omitted valid consequences only weaken the view, so an independently verified contradiction still implies original UNSAT. The oracle audit separately verifies full projection equality and independent reconstruction. Direct binary contradiction and empty-factor certificates use no nested Hall certificate.

## Clean chain-family invariance theorem

In the clean ternary pigeonhole encoding of n+1 pigeons into n holes (n>=3), replace each exclusion (-x or -y) by an arbitrary positive-length directed binary chain x -> u1 -> ... -> ur -> -y, with distinct fresh auxiliaries for each exclusion; a length-one chain is the original exclusion. Independently complement any coordinates, including the occupancy, ternary-chain, and binary-chain auxiliary coordinates.

Every new binary-only auxiliary lies outside the anchor set, and every original occupancy and ternary-chain coordinate lies inside it. Eliminating each fresh chain recovers exactly the original exclusion: if x is true all intermediates must be true and y false; if x is false all intermediates may be false. The binary part is satisfiable (all original occupancies false in the uncomplemented representation). Its only nontrivial anchor implications, up to contraposition, are the original direct exclusions: the chain interior is fresh, and an implication ending at a negative occupancy cannot continue along another exclusion. Independent coordinate complementation simply relabels literal vertices. Consequently the compact view is the exact original clean encoding up to coordinate ordering and signs. D7H's clean-family polarity theorem recovers a checked Hall contradiction, with n+1 groups and n holes. This holds for arbitrary individual chain lengths and complement masks of this specified input family; it is not a theorem for arbitrary SAT formulas or arbitrary predecessor rewrites.

## Resource bounds

Let k be the explicitly represented coordinate count, f the number of bounded-arity factors, a=|A|, and e the number of implication arcs. There are O(f) arcs (at most eight forbidden rows per factor and at most two arcs per binary clause). Graph creation costs O(k+f) abstract operations. BFS from at most 2k vertices costs O(k(k+e)); recording one simple path per distinct non-tautological anchor clause costs O(a^2 k), plus O(k^2) for candidate opposite-literal paths. The view contains f3 original ternary factors and O(a^2) unary/binary factors, where f3 is the ternary factor count. A conservative bound for closure production is O(k(k+f)+a^2 k+f), with O(k+f+k^2+a^2 k) words of storage including explicit paths. The independent checker is polynomial in the original input and explicit certificate size; checking path edges is linear in total recorded path length with bounded-arity factor membership operations. Nested D7H structural discovery/checking remains polynomial in its explicit input and proof sizes, with its prior heuristic restrictions. These are abstract word-operation bounds with polynomial bit overhead, not measured host time, and do not bound unrestricted fallback or raw physical execution.

## Executed oracle evidence

- 1238 exhaustive small formula oracle comparisons, including all 276 local Boolean relation types, all 256 subsets of the eight possible unary/binary clauses on two coordinates, 256 seeded small binary formulas, 384 seeded mixed formulas, 64 complement masks of a mixed SAT fixture, and two constant-relation cases.
- 534 unary/binary-only and 704 higher-arity cases; 707 SAT, 531 UNSAT, 3093 satisfying model occurrences.
- 4 empty-factor and 496 mutual-reachability contradictions; 738 exact projected model-set and independently reconstructed view comparisons, 1830 distinct projected model occurrences. All consistent binary-only views matched the exhaustive oracle.
- 747 projected path clauses, 503 derived through multiple edges, 1490 total recorded edges in these views.
- D7H structural policy certified 416 cases on the identical corpus; D7I certified 511 (95 additional, 9 projected Hall and 2 inherited Hall in addition to 500 direct contradictions). Every positive certificate checked; zero observed false refutations. Remaining 20 UNSAT cases not claimed solved by structural inference alone.
- Six corrupted path/projection/nested proof certificates rejected.
- 32 heterogeneous-chain instances with lengths 1..5, random coordinate complements and permutations, reversed scope and factor order: all refuted, 2072 reconstructed exclusion paths and 6285 recorded edges. These were raw-input structural tests. The new ternary gadget's local 16-assignment oracle gives ten satisfying assignments and exactly the three allowed occupancy pairs of a mutual exclusion.

## Previous policy obstruction eliminated, and larger executed instances

All six rows ran actual relational and affine preprocessing, independent affine verification, and independent D7I certificate verification. Every affine residual retained all coordinates with zero equations. No assignment enumeration was used for these structural decisions.

| holes | binary chain length | complemented | coordinates | factors | projected coordinates | paths | path edges | nested proof |
|---:|---:|---|---:|---:|---:|---:|---:|---|
|3|2|no|30|40|12|18|36|Hall|
|6|2|no|189|280|63|126|252|Hall|
|6|3|yes|315|406|63|126|378|signed Hall|
|8|2|no|405|630|117|288|576|Hall|
|12|2|yes|1209|2002|273|936|1872|signed Hall|
|20|2|no|4977|8778|777|4200|8400|Hall|

The second row is the exact D7H 189-coordinate obstruction. It reconstructs all 126 missing exclusions and a seven-group/six-hole Hall core, with 28 original ternary group-derivation axiom references and 126 derived binary exclusions. BFS counts: 378 searches, 1134 visited literals (with repetitions across searches), 756 arc scans, 252 recorded path edges. No D7D resolution or tree inference invoked.

The largest row verifies 21 groups and 20 holes, with 378 ternary group-derivation references and 4200 two-edge exclusion certificates. 9954 BFS searches, 35154 literal visits, 25200 arc scans. The original 4977-coordinate residual projects to 777 coordinates. These counters describe selected search operations and proof references, not full runtime or unique input bits.

## Physical replay

| fixture | affine residual worker | D7I worker |
|---|---:|---:|
|five-coordinate binary implication contradiction|312998|2092|
|mixed SAT|51371|51371|
|189-coordinate prior obstruction|not executed|2092|
|315-coordinate signed three-edge chain|not executed|2092|

Two paired fixtures: 364369 -> 53463 transitions, 310906 eliminated. Four original/minimized new-stream agreements, six exact clock checks and four one-short cutoffs passed. Mixed SAT least expanded witness 0,0,0,0,0,1 matches exhaustive oracle. Larger examples replay only the ten-symbol certified contradiction stream. No full unreduced physical runs for these larger fixtures, no incremental timing comparison to D7H's full pipeline, and no host computation included. Descriptor unchanged: 3683 minimized states, 180471 bits.

## New surviving policy obstruction — conditional ternary conflicts

Replace every binary exclusion (-x or -y) in the seven-pigeon/six-hole clean encoding by three ternary clauses with two fresh auxiliaries u,v:
    (-x or -y or u)
    (-x or -u or v)
    (-y or -u or -v)

If x=y=1 the first clause forces u=1 and the others force v and -v. If either occupancy is false, choosing u=0 satisfies the gadget. The 16-assignment local oracle confirms its exact existential projection. The formula is therefore UNSAT, with 63+252=315 coordinates and 28+378=406 factors. The three clause scopes differ, so no original binary forbidden-row clause is present. Actual integrated execution: 315 free coordinates, zero affine equations, zero unary/binary clauses and zero arcs in the implication graph, D7I UNKNOWN, indexed resolution exhausts 2000000 units (9111 generated records,17357 processed pairs), tree inference exhausts 2000000 units (5250 visited nodes,937 conflicts,1001 splits,3311 unit nodes). Exact residual retained. This is a limitation of the configured inference policy, not a proof of width-four non-refutability or a complexity lower bound on arbitrary SAT algorithms.

## Next

Investigate certified failed-literal and conditional propagation, with independently replayed resolution or unit-propagation traces for implied binary conflicts from ternary factors. Target the new 315-coordinate formula while preserving explicit polynomial discovery limits and independent verification. Direct raw-selector physical normalization, on-tape inference and end-to-end physical resource accounting remain open. Main and PR #248 untouched. Dedicated Proctor configured separately; remote completion not claimed.
