# F038-REX-024D7E — Certified Hall matching inference

Parent D7D: 23bf6ad2e6ed7f16c163546f94b15ba58002a23f. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4; Omega obligations 0/6.

## Sound extraction from explicit ternary Boolean relations

The input is the valid explicit binary-domain factor representation (distinct coordinates per scope, arity at most three). Use D7C exact forbidden-row clauses; an axiom's unique falsifying tuple must be absent from its referenced original factor.

For either common polarity, start with a nonempty clause containing only literals of that polarity. Resolve it with an axiom having exactly one opposite-polarity literal (the pivot) and at least one other literal. The result remains a same-polarity clause. Repeat while a unique continuation exists, refusing cycles or ambiguous continuations. This is an ordinary resolution derivation, possibly wider than four, with at most k distinct pivots per chain. The final clause implies that at least one of its options is true. Greedily retain only disjoint option sets, and store each full chain of original axiom references. Neither chain uniqueness nor greediness is necessary for soundness; these restrictions make extraction deterministic and polynomial, but incomplete.

Construct a graph on the retained options, joining options of different groups if an original binary axiom forbids both being true. Treat connected components as candidate holes; require every cross-group pair in each component to have an explicit exclusion axiom. If the condition fails, abandon this polarity's extraction rather than assume capacity one. Isolated options form singleton holes. The option groups and hole components define a bipartite graph. Every satisfying assignment allows selection of one true literal per group, and no two groups can select the same hole, by the verified cross-group exclusions. This implication does not require at most one true option within a group.

Use augmenting paths in the bipartite graph. If an unmatched group has no augmenting path, let S be the reachable groups and N the reachable holes. All neighbors of S have been visited, every reached hole is matched to a reached group, and the initial group is unmatched. Thus |N|<|S|. The certificate includes only these groups, all their options partitioned into the reached holes, group-derivation axioms, and every required cross-group exclusion. Hall deficiency gives an UNSAT certificate. If a covering matching is found, no SAT claim is made, because other original constraints may remain. Greedy extraction, same-polarity chains, and component-based hole identification can miss valid matching structures.

## Independent checker and exact fallback

The checker does not invoke the producer's graph construction, matching algorithm, or selection heuristic. It independently verifies each axiom against the factor, replays each group derivation as literal-set resolution, checks disjointness, verifies exact option coverage by nonempty disjoint holes, checks every cross-group exclusion within each hole, and requires fewer holes than groups. This directly certifies the pigeonhole contradiction.

On a checked Hall proof, use the one-coordinate empty unary contradiction stream. Otherwise call the unchanged D7D cardinality, bounded resolution, and budgeted tree adapter. If all stages return UNKNOWN, retain the original residual stream and its identity witness map. A matching is never interpreted as an original SAT witness.

## Polynomial host resource bounds

Let k be the explicitly represented coordinate count and f the number of factors. There are at most 8f forbidden-row clauses. For each polarity there are O(f) candidate starts, at most k distinct pivots per start, and at most k literals in each intermediate same-polarity clause. A conservative bound for chain construction including sorting is O(f k^2 log(k+1)) abstract operations. At most k disjoint options survive. Component construction uses O(f+k) records and cross-group checks use O(k^2) pair queries. The bipartite graph has at most k edges (each option contributes at most one edge), at most k groups and k holes; at most k augmenting searches cost O(k^2) abstract operations. Explicit certificate verification is polynomial in input and proof size; its chains replay by set operations and its pair coverage check uses at most O(k^2) comparisons. Map/set lookup and finite integer representation can be implemented with polynomial bit cost. No universal end-to-end time bound follows for the D7D fallback. Producer counters are counts of specified operations, not complete runtime measurements.

## Actual evidence

1263 exhaustive small-instance oracle comparisons (2784 satisfying models, 901 SAT and 362 UNSAT), including all 276 local relation types and all 343 three-group/three-hole labeled graphs with nonempty group neighborhoods. Hall recognized exactly the deficient graphs in that graph corpus; 114 total cases received verified Hall certificates, no satisfiable case was refuted. The remaining UNSAT cases are not claimed solved by Hall alone. Six deliberately damaged certificates rejected. Both common polarities were tested.

Sparse Hall example: four groups, five total holes. Three groups share only two holes; the remaining group has three private holes. The certificate isolates a three-group/two-hole core even though total holes exceed total groups. A two-group/two-hole satisfiable example remains UNKNOWN from Hall, with its original least witness preserved in the complete fallback.

| holes | coordinates | factors | deficient groups | group proof axioms | exclusion axioms |
|---:|---:|---:|---:|---:|---:|
|3|12|22|4|4|18|
|5|42|93|6|18|75|
|6|63|154|7|28|126|
|8|117|342|9|54|288|
|12|273|1066|13|130|936|
|20|777|4578|21|378|4200|

All six larger instances were executed through the actual relational and affine predecessors with independent affine checks and verified Hall certificates. Zero affine equations on these instances. No candidate enumeration used for those Hall decisions. PHP5 replaces the previous 6912-node tree proof with a 93-axiom Hall certificate (18 group axioms and 75 exclusions); these are different certificate units, not a direct bit-size or time comparison. PHP20 has 420 original occupancy variables and 357 chain auxiliaries. Its 4578 referenced axioms prove contradiction without enumerating 2^777 assignments.

## Physical replay

| fixture | D7B residual worker | D7E worker |
|---|---:|---:|
|small three-group/two-hole|943995|2092|
|sparse Hall core|13647854|2092|
|satisfiable two-group/two-hole|42197|42197|
|PHP5 (42 coordinates)|not executed|2092|
|PHP20 (777 coordinates)|not executed|2092|

The paired baseline is the predecessor affine residual worker, not D7D's already reduced worker. For three paired fixtures: 14634046 -> 46381 transitions, 14587665 eliminated. Five new-stream original/minimized replays, eight exact clock comparisons, five one-short cutoffs pass. In the paired satisfiable fixture, expanded least witness agrees with exhaustive oracle. Both larger replays use only the 10-symbol constant contradiction stream; unreduced physical replay was not attempted. No incremental physical savings over D7D are asserted, and host preprocessing/verification is excluded. The unchanged descriptor has 3683 minimized states and 180471 bits.

## New surviving policy obstruction

Take the six-hole/seven-pigeon ternary encoding (63 coordinates, 154 factors) and add the binary exclusion not x_{0,0} or not x_{1,1} between distinct groups and different original holes (zero-based coordinate indices 0 and 7). The base pigeonhole constraints remain present, so UNSAT follows immediately from the original pigeonhole principle. The added edge merges two hole components without providing every cross-group exclusion. The producer refuses this unsafe merging; it returns UNKNOWN across both common polarities.

Actual integrated execution: 63 free coordinates; no extracted affine equations; Hall UNKNOWN; inherited five-coordinate cardinality rule finds no certificate; indexed resolution exhausts 2000000 charged units (8429 generated records, 20970 processed pairs); tree inference also exhausts 2000000 charged units (16347 visited nodes, 1017 conflicts, 1030 splits, 14299 unit steps). The exact affine residual is retained. This is a concrete obstruction to the configured D7E policy, not a proof of width-four non-refutability for this instance, not an unrestricted resolution or SAT lower bound, and not a new mathematical pigeonhole theorem.

Next investigate robust clique partition or conflict-edge selection with independently checked capacity certificates, preserving soundness under redundant cross-hole exclusions. Direct physical raw-selector normalization remains outstanding. Main and PR #248 untouched. Dedicated D7E Proctor configured separately; remote completion not claimed.
