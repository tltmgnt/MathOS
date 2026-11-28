# F038-REX-024D7U — Complete signed conflict components and scalable prefix cuts

Parent D7T: f7ac4c83f3e42f2edefa70d1e73d953c02a0035c. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Arbitrary-size prefix theorem

Let y_i=x_i for a positive signed literal and y_i=1-x_i for a negative one. A complete signed conflict graph on distinct coordinates supplies a checked inequality y_i+y_j<=1 for every pair. The first two vertices give a prefix bound S_2<=1. Suppose a prefix of j>=2 vertices has S_j<=1. The j edges from the next vertex to that prefix sum to S_j+j*y_(j+1)<=j. Add j-1 copies of the prefix inequality. Then
    j*(S_j+y_(j+1)) <= 2*j-1.
Divide all coefficients by j and floor the RHS, obtaining S_(j+1)<=1. This works in original coordinates too: if the extended prefix has q negative literals, the shifted RHS is 2*j-1-j*q, whose floor after division is 1-q. Thus the entire explicitly complete clique has a proof with binom(w,2) source edges, w-2 sums and w-2 divisions. Reusing the prior prefix node through repeated parent indices keeps the total parent references O(w^2), not exponential. For width two the original edge suffices; the existing triangle construction is equivalent for width three. The independent unchanged D7S checker validates every original inequality, earlier parent dependency, integer sum and exact division/floor. There is no new trusted arbitrary clique axiom.

## Discovery

Build the signed graph from original binary forbidden tuples, storing one factor per edge. Find connected components by graph traversal; require distinct underlying coordinates and degree w-1 for each signed vertex, and explicitly check all pair memberships before accepting a component. Prioritize complete components in deterministic coordinate order; skip a component whose underlying coordinate is already assigned to another chosen orientation (opposite polarities can occur in distinct signed components). Then run the inherited D7T greedy bounded-size partition on remaining represented coordinates. Generate prefix cuts even for four-cliques; pairs and singletons use original source bounds. This is not a maximum clique algorithm. The producer inherits the lower-occupancy discovery: choose original factors wholly covered by the chosen orientations, compute the minimum signed occupancy count over their allowed rows, and create a checked inequality when that count is positive. Group by arity and minimum, aggregate and gcd-divide, combine with summed upper cuts; also try the combined lower group. The terminal box test works in original coordinates. Unknown results preserve the exact original residual, optionally delegating to inherited inference. Actual D7T fallback tested with zero node cap. No inherited source modified.

Node cap default 4096, configurable 0..100000, membership-check cap default 2000000. These caps exclude graph construction, sorting, other arithmetic, certificate checking, fallback and physical replay; sum/division counters can count attempted operations when capped. Exhaustion yields UNKNOWN. Completeness recognition requires O(k+f) graph traversal and degree checks, plus at most O(k^2) explicit pair membership tests on <=2k signed vertices (O(f) tests on accepted components because every pair is a source edge). Remaining fixed-size search has inherited worst-case O(k^4) tests. Sorting costs polynomial. On accepted disjoint cliques, the sum of w^2 is O(k+f) because their pair edges are explicit; prefix sparse row storage, sources, parent references and arithmetic work are O(k+f) abstract words/operations after recognition, apart from sorting and gcd bit costs. Constant-many lower aggregates are O(k+f). Coefficients and RHS are polynomially bounded (prefix intermediate O(w^2) RHS, coefficients O(w)); independent checker polynomial in explicit proof/input size. No complete proof search, general SAT, integer programming, or end-to-end physical bound follows.

## Prior obstructions eliminated and larger tests

For n disjoint signed K_w mutex groups, with w cyclic layers of ternary at-least-one factors at offsets 0,1,3 (distinct scopes), every coordinate occurs exactly three times among lower factors. The graph is exactly n complete signed components, regardless of global coordinate complements. The automatic producer finds sum y<=n and sum y>=ceil(n*w/3); for w>=4 and n>0 these conflict. The proof fits the configured resource caps in the executed cases; this is a theorem for the specified raw encoding, not arbitrary extra factors or predecessor rewrites.

|n|w|coordinates|factors|complemented|predecessor|pair checks|nodes|divisions|terminal RHS|
|---:|---:|---:|---:|---|---|---:|---:|---:|---:|
|5|5|25|75|no|yes|50|109|16|-4|
|7|5|35|105|yes|yes|70|151|22|-5|
|7|4|28|70|yes|yes|42|102|15|-3|
|11|9|99|495|yes|yes|396|653|78|-22|
|41|13|533|3731|yes|raw|3198|4637|452|-137|
|5|31|155|2480|yes|raw|2325|2774|146|-47|

All six independently verified; no complete assignment enumeration for these decisions. The first four actually run relational and affine predecessor processing (all free, zero affine equations). Last two raw structural input only. The 533-coordinate case requires an increased node cap of 20000; default stops at 4096 nodes and reports budget. Largest individual clique size 31. For the n,w family the generated DAG has n*(binom(w,2)+2*(w-2)+w)+4 nodes and n*(w-2)+1 divisions. The previous 25/35-coordinate manually verified nested certificates had 238/332 nodes; the new automatic prefix proofs need 109/151 (different equivalent sign encoding in the second case). The 28-coordinate K4 regression decreases from D7T's 144 nodes to 102.

## Executed oracle and physical replay

503 exhaustive formula comparisons: 323 SAT,180 UNSAT,1484 satisfying model occurrences. All 276 local relation tables,192 seeded mixed formulas, a K5 contradiction with every triple requiring one, all 32 independent complement masks, reversed factor/scope order, and a pure K5 SAT control with six models. 142 independently certified refutations,361 UNKNOWN (323 SAT and 38 UNSAT),1117 certificate nodes and136 division nodes. Six corrupted proofs rejected, no false refutations observed. The 29-node K5 proof stops at 28-node cap; nine pair checks insufficient for its ten explicit edges; zero-node adapter preserves exact residual. Actual inherited D7T produces 104 nodes on a K4-family fixture when D7U is capped at zero. These are stage-specific outcomes, not incremental improvements on the entire inherited solver.

Actual D7U adapter on the 25-coordinate previous obstruction maps to ten-symbol stream. Original/minimized machines agree UNSAT at 2092 transitions; independent clock 2092, one-short timeout 2091. Descriptor unchanged:3683 states,180471 bits. No unreduced physical replay or new paired physical savings; host costs excluded.

## New limitation: bridges between otherwise complete cliques

Add n-1 explicit binary exclusions linking the first coordinate of consecutive K5 groups. All original constraints remain, so UNSAT persists; the old nested proofs still verify on the strengthened original input without referencing the extra factors. However the signed conflict graph is now one connected noncomplete component. Complete-component recognition rejects it. The inherited bounded partition chooses K4 plus singleton per original group, and the bounds are insufficient: sum x<=2n versus sum x>=ceil(5n/3). The all-one-third rational point still satisfies every local convex support, including the added exclusions.

|n|coordinates|factors|components|complete|automatic bounds|automatic nodes|fractional support checks|verified manual nodes|tree nodes|
|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
|5|25|79|1|0|9<=sum<=10|84|3314|238|118|
|7|35|111|1|0|12<=sum<=14|116|4646|332|118|

Actual predecessor runs retain all coordinates and no affine rows. Both D7U results UNKNOWN; independently checked inherited tree proofs take 4243/5101 charged units. These are limitations of the complete-component and bounded partition policy, not of all clique cuts or an unresolved full-pipeline barrier. Extra valid constraints can disrupt discovery without invalidating prior certificates.

## Next

D7V: certified sparse-bridge and noisy conflict-component decomposition. Investigate bridge deletion and supported-edge filtering (or biconnected decomposition with disjoint coordinate selection), exact verification of recovered complete subgraphs on original source edges, and composition across noisy components. Bridge deletion is a sound relaxation for UNSAT inference; arbitrary maximum clique search remains out of scope. Test the two bridged K5 fixtures, then investigate overlapping clique structures and denser cross-edge noise that do not separate by bridges. General SAT, raw-selector normalization, on-tape inference and full physical accounting remain open.

All five new audit sections executed in the connector JS runtime against committed source; the large section was rerun after adding the default cap regression. Main and PR #248 untouched. Remote Proctor completion unconfirmed.
