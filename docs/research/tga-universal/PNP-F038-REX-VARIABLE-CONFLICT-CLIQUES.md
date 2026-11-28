# F038-REX-024D7F — Certified robust conflict-clique decomposition

Parent D7E: 8a7d3fb44607a92b8e1562cfcb28d42334646337. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Exact interface and soundness

Keep D7E's certified same-polarity disjunction extraction and disjoint option groups. Let V be the retained signed options and g(v) their group. The conflict graph has an edge between options in different groups precisely when the source contains an explicit binary clause forbidding their joint truth. Same-group edges are not needed because only one true option is selected per group.

A proposed partition into nonempty holes is admissible iff it covers V exactly once and every pair of options in different groups within a hole has its original explicit exclusion. This is weaker than an ordinary clique when a hole has multiple options from one group. Ignore all other edges for this certificate: they can restrict models further, but cannot invalidate an already implied capacity-one condition. D7E's matching and independent Hall checker then apply unchanged. A deficient core is sufficient for original UNSAT; a covering matching is not proof of SAT.

The D7E Hall implementation on the D7F branch has an optional partition-proposal callback. The default behavior and default audit counters are unchanged. Every proposal, including callback proposals, is checked for exact option coverage and explicit cross-group exclusions before any matching. The independent checker replays source axioms and checks the final Hall certificate, not the producer's partition heuristic.

## Polynomial proposal portfolio

First try D7E connected components. For each conflict edge xy define its support s(x,y)=|N(x) intersect N(y)|, the number of common neighbors in the original conflict graph. Compute support once. For each distinct threshold of the form s+1 in increasing order, retain edges with support at least the threshold, and propose connected components of that filtered graph. The thresholds enumerate every distinct edge-deletion pattern after the unfiltered graph. Compute capacity checks using the original graph, never an assumed completion of the filtered graph.

If no threshold gives a Hall contradiction, try four greedy partitions in rank order, reverse rank order, ascending degree and descending degree (ties by rank). Insert each option in the largest existing compatible hole, or a new singleton if none is compatible. Compatibility means each cross-group pair has an actual exclusion edge. The greedy rules propose partitions but do not solve arbitrary optimal clique partitioning. Try both common polarities. If every proposal fails to certify Hall deficiency, continue through the unchanged D7D adapter. UNKNOWN preserves the residual and identity witness map.

### Support separation lemma
Suppose the conflict graph contains intended disjoint complete resource cliques, all with at least three vertices, plus cross-resource edges. If a threshold t exists such that every within-resource edge has support >=t and every cross-resource edge has support <t, the filtered graph recovers exactly the intended components. This threshold partition will be tried (or an equivalent deletion pattern will be tried). If the recovered matching graph is deficient, the producer obtains a valid Hall proof. In particular, a single bridge between two complete resource cliques has support zero, whereas original clique edges have support at least one. Threshold 1 recovers the original cliques, provided all intended resource cliques have size >=3. This is an extraction guarantee conditional on already having recovered the option groups, not a universal guarantee for arbitrary redundant clauses or all encodings.

### Resource bound
Let k be the explicit coordinate count, f the number of factors, v<=k the number of disjoint retained options, e<=v(v-1)/2 the conflict edge count. Edge support via adjacency-set intersections costs O(ev) abstract operations. There are at most v distinct support thresholds. Each proposal costs O(v+e) to construct, O(v^2) to check capacity and O(v^2) for augmenting-path matching (at most v option-derived edges). The four fixed greedy passes each use O(v^2) compatibility tests and O(v log(v+1)) sorting. Thus the additional portfolio costs O(k^3) abstract operations and O(k^2) graph/proposal storage, assuming bounded-cost set/map operations; coordinate keys and integer operations have polynomial bit cost. With D7E extraction, a conservative host bound is O(f k^2 log(k+1)+k^3). The independent Hall checker remains polynomial in explicit input and certificate size. These bounds cover Hall preprocessing only, not complete SAT fallback or physical implementation. Counters are not total host runtime.

## Executed finite oracle and robustness evidence
1452 small-instance exhaustive oracle comparisons: 2797 satisfying models, 966 SAT cases, 486 UNSAT cases; 138 D7E Hall refutations vs 233 D7F Hall refutations on the same corpus (95 additional). Every positive Hall result checked independently; no false refutations. 276 local relation types, all 343 nonempty-neighborhood three-group/three-hole graphs, 192 noisy graphs (64 exhaustive extra-edge patterns on three groups/two holes plus 128 seeded mixed matching graphs), and both polarities. The small oracle comparisons verify Hall soundness, not completeness of general SAT. Greedy recovered 66 cases in the total corpus. Four corrupted certificates rejected; two malformed partition proposals ignored. All 32 deterministic coordinate relabelings, reversed factor ordering and reversed scope ordering of the six-hole bridge fixture refuted independently. The inherited D7E audit was re-executed with the optional hook present and default behavior; its complete output matched the previous checkpoint.

The 64 exhaustive noisy three-group/two-hole graphs all refute:
| strategy | count |
|---|---:|
| unfiltered components |2|
| support threshold 1 |17|
| support threshold 2 |6|
| greedy rank |33|
| greedy reverse |4|
| greedy ascending degree |2|

## Prior 63-coordinate policy obstruction eliminated

All listed instances passed relational/affine predecessor checks (zero equations, all coordinates free); baseline D7E Hall returned UNKNOWN, D7F independently verified a deficient core.

| holes | noise | coordinates | factors | threshold | required exclusions |
|---:|---|---:|---:|---:|---:|
|3|single bridge|12|23|1|18|
|5|single bridge|42|94|1|75|
|6|single bridge|63|155|1|126|
|6|two edges forming cross-resource triangle|63|156|2|126|
|6|cycle of cross-resource edges|63|160|1|126|
|6|30 cross-resource edges|63|184|1|126|
|8|cycle|117|350|1|288|
|12|cycle|273|1078|1|936|
|20|single bridge|777|4579|1|4200|

Each needed two partition attempts (unfiltered then one threshold). The prior obstruction's certificate uses 28 group-derivation axioms and 126 mutual exclusion axioms, ignores the extra bridge, and proves seven groups need six holes. Actual support computation: 127 edge scores, 763 common-neighbor probes and 254 adjacency visits during filtered traversal. For 777 coordinates, 4201 edge scores, 84021 support probes and 8402 adjacency visits. No candidate enumeration or adaptive inference required for these Hall decisions. No new claim of general polynomial non-affine decision.

## Physical replay
|fixture|D7B residual transitions|D7F transitions|
|---|---:|---:|
|greedy small noisy UNSAT|945051|2092|
|noisy satisfiable matching|47419|47419|
|63-coordinate bridge|not executed|2092|
|777-coordinate bridge|not executed|2092|

Two paired fixtures: 992470 -> 49511 worker transitions, 942959 eliminated. Four original/minimized new-stream agreements, six exact clock comparisons and four one-short cutoffs passed. The noisy satisfiable case preserved the lexicographically least expanded witness by exhaustive oracle. The two larger instances replay only the ten-symbol constant contradiction stream; no unreduced worker timing or incremental D7E physical saving asserted. The inherited descriptor is unchanged (3683 minimized states, 180471 bits). Host costs excluded.

## New surviving policy obstruction — ambiguous disjunction chains

Take the original six-hole/seven-pigeon ternary encoding (63 coordinates,154 factors). Add the binary implication not u or x, where u is the first auxiliary (zero-based index 42), and x is original occupancy coordinate index 2. The original pigeonhole contradiction remains intact. This gives the first positive extraction chain an additional continuation, which D7E's unique-continuation rule refuses. D7F only changes partition proposals; it cannot recover the lost option group. Actual integrated run: 63 free coordinates, 0 affine equations, 155 factors, Hall UNKNOWN after 11 partition attempts across both polarities, cardinality UNKNOWN, 2,000,000-unit indexed resolution budget exhausted (8541 generated records,21944 processed pairs), and 2,000,000-unit tree budget exhausted (17065 visited nodes,998 conflicts,1004 splits,15062 units). Exact residual retained. This is a policy-specific obstruction, not a proof of width-four non-refutability, a complexity lower bound for all inference strategies, or an unrestricted SAT lower bound.

## Next
Investigate certified alternative disjunction derivations and deterministic bounded branching or dominance selection for auxiliary-chain ambiguity; preserve polynomial resource accounting and independently verify every derived group. Robust partition discovery remains heuristic outside the separation condition. Direct physical raw-selector normalization and end-to-end physical accounting remain open. Main and PR #248 untouched. Dedicated D7F Proctor configured separately; remote completion not claimed.
