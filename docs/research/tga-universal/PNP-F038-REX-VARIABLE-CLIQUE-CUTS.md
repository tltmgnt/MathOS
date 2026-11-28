# F038-REX-024D7T — Certified signed clique cuts and nested aggregate composition

Parent D7S: c9e4899241b61f3db1a3a6749d5bd749e9ec43fc. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Signed clique theorem and cutting-plane construction

For each signed literal l on Boolean coordinate x, write its occupancy as y_l=x for l positive, or y_l=1-x for l negative. A forbidden binary tuple for distinct coordinates implies y_l+y_m<=1 for its two occupancy literals. Build a graph on signed literals with these edges, retaining an original factor reference for every edge. A clique of three vertices yields 2*sum y<=3 by summing its three edges, and hence sum y<=1 by integer division and flooring. A four-clique contains four triangles; summing those already derived cuts gives 3*sum y<=4, then sum y<=1. In original coordinates the RHS is shifted by the count of negative literals: sum sign(l)*x_l<=1-number_negative. Integer division is applied to the shifted RHS (including negative values) by the inherited exact floor operation. A pair cut is its edge inequality and a singleton occupancy has the trivial bound <=1. Every clique chosen has distinct underlying coordinates, since edges only join distinct coordinates.

The producer greedily partitions the graph's represented coordinates: traverse signed vertices in absolute-coordinate order, positive before negative, skipping a coordinate already chosen. At each pivot search the unused-coordinate neighbors for a four-clique, retain a triangle if one is found and no four-clique is found, otherwise choose a pair or singleton. Mark the chosen underlying coordinates and record their orientations. This is fixed-size local discovery, not maximum clique optimization or optimal clique partitioning. For each chosen clique emit a D7S source/sum/divide proof, caching edge nodes. The singleton box bound is certified by an incident original factor. Empty factors give immediate contradiction. The total clique upper bound is obtained by summing the disjoint clique inequalities. On every original factor wholly covered by the selected orientations compute the minimum sum of its signed occupancies across its allowed tuples; if positive, the corresponding lower inequality is a checked source. Group these by arity and minimum occupancy, sum and divide by the coefficient gcd, then combine each rounded lower bound with the upper bound; additionally try their combined group if multiple groups exist. A terminal row is contradictory exactly when its box minimum exceeds its RHS. Uncovered coordinates are not asserted absent from the formula; the selected subproof is a sound relaxation.

All certificate nodes use the existing D7S format. The new verifier entry delegates to the independently implemented D7S checker, which checks D7R source tables, strictly earlier dependencies, exact BigInt sums, divisibility, floor and terminal box minimum. No new unchecked clique axiom or trust in graph discovery is introduced. The adapter maps verified contradictions to the inherited empty unary factor and retains the original residual on UNKNOWN, optionally delegating to an inherited callback. No inherited source modified.

## Bounds and limitations

Default node cap 4096 (configurable 0..100000), default adjacency-membership-check cap 2000000 (nonnegative safe integer). Only completed proof nodes are retained, and no partial proof is returned as UNSAT. Sum/division metrics count attempted node operations when stopped by the node cap; successful certificates count completed operations. The membership counter excludes graph indexing, sorting, source generation, arithmetic, verification, fallback and physical execution. Worst-case fixed-size search O(k^4) adjacency tests on at most 2k signed vertices, with a tighter cap in the implementation. Graph construction O(k+f) abstract words and operations before sorting; ordering the vertices and neighbor lists costs at most O((k+f) log(k+1)). Each chosen four-clique uses 16 nodes (6 edges, 4 triangle sums and divisions, a four-clique sum and division), and smaller cliques use at most 4 nodes per covered coordinate. There are at most f lower sources and at most six nonempty lower groups for arity <=3, so O(k+f) nodes and explicit parent references in the uncapped proof, with O(k+f) sparse storage (only a constant number of global aggregate rows). Exact aggregate coefficients/RHS bounded in magnitude by O(k+f), polynomial bit overhead. Independent DAG checking polynomial in proof/input size. General SAT, arbitrary maximum clique, complete cutting-plane search and end-to-end physical polynomial execution are not established.

## Previous D7S obstruction eliminated

In the specified raw family of n disjoint K4 mutex groups, each coordinate appears in exactly three lower ternary occupancy constraints, one per group-layer cyclic position. The graph is exactly the disjoint signed K4s, so greedy selection recovers every group. Independently complementing any coordinate changes its literal sign but not this graph structure; the signed lower sources are restored automatically. The derived bounds are sum y<=n and sum y>=ceil(4n/3), impossible for n>0. This is a family-specific automatic discovery theorem within the proof/check budgets and distinct-scope encoding; arbitrary extra factors, alternate polarities and unrelated components can change the greedy result.

|coordinates|factors|complemented|predecessor|four-cliques|membership checks|proof nodes|division nodes|terminal RHS|
|---:|---:|---|---|---:|---:|---:|---:|---:|
|20|50|no|yes|5|15|104|26|-2|
|28|70|no|yes|7|21|144|36|-3|
|28|70|yes|yes|7|21|144|36|-3|
|404|1010|yes|raw|101|303|2024|506|-34|
|804|2010|yes|raw|201|603|4024|1006|-67|

All five automatic certificates independently checked, no complete assignment enumeration for these structural decisions. The first three run actual relational and affine predecessors (all coordinates free, zero affine rows). Last two are raw structural inputs, not full preprocessing or physical replay. For n K4s, emitted proof has 20n+4 nodes, five divisions per clique plus one lower aggregate division. Both prior structural obstructions eliminated.

## Executed oracle, budgets and physical replay

487 exhaustive formula comparisons:322 SAT,165 UNSAT,1382 satisfying model occurrences. 276 local relation tables,192 seeded mixed formulas, a four-clique contradiction plus its 16 coordinate-complement masks, reversed factor/scope order, and a pure four-clique SAT control (5 models). 124 certified contradictions,363 UNKNOWN (322 SAT and 41 UNSAT),524 total proof nodes and108 division nodes. Six corruptions rejected, zero observed false refutations. This is stage-specific coverage, not incremental gains over the full inherited solver. Zero-node cap preserves original residual, 22-node cap on the 23-node K4 fixture reports budget; zero membership-check cap reports budget. Actual D7S delegation succeeds on the previous 31-coordinate rounding fixture, producing 67 proof nodes. Actual adapter on the 20-coordinate prior obstruction yields UNSAT in 2092 physical transitions on the ten-symbol stream, original/minimized agreement, independent clock 2092, one-short timeout 2091, unchanged descriptor 3683 states/180471 bits. No unreduced paired replay or physical savings claimed; host costs excluded.

## New automatic-discovery limitation: five-clique extension

Replace each K4 with K5, keeping five cyclic layers of ternary at-least-one factors. Every coordinate still occurs three times in lower factors. All models must satisfy sum y>=ceil(5n/3), but the K5 groups each permit at most one, giving sum y<=n. The local convex hull relaxation admits x_i=1/3; the audit checks every support at that point. The configured producer instead partitions each K5 into a K4 and singleton and obtains upper 2n, insufficient for contradiction. This is a limitation of the fixed-size disjoint partition, NOT of all size-four clique cuts (the latter can overlap), all cutting-plane proofs, or the full pipeline.

The general D7S verifier already accepts a manually constructed stronger proof: derive all triangle cuts, all five four-subclique cuts with shared triangle nodes, then sum the five four-subclique cuts and divide by four to get sum over K5<=1. Combine with the rounded lower aggregate. Explicit DAGs checked against original input. No claim about minimum rank.

|coordinates|factors|automatic bounds|automatic nodes|fractional source checks|manual nodes|manual divisions|manual terminal RHS|inherited tree nodes|
|---:|---:|---|---:|---:|---:|---:|---:|---:|
|25|75|9<=sum<=10|114|3250|238|81|-4|128|
|35|105|12<=sum<=14|158|4550|332|113|-5|128|

Actual predecessor runs keep all coordinates and no affine rows. Automatic stage UNKNOWN in both. Separate inherited tree proofs pass (4388 and 5228 charged units, respectively). Not an unresolved full-pipeline obstruction.

## Next

D7U: certified arbitrary-size explicitly complete conflict components and scalable clique aggregation. Detect complete signed conflict components without enumerating all subsets or optimizing maximum clique; verify every required pair edge independently and certify the general at-most-one rule (or use a polynomial-size checked cutting-plane derivation). Compose with existing lower bounds and test the five-clique fixtures. Investigate limits of incomplete and overlapping conflict graphs and weighted clique covers. General SAT, raw-selector normalization, on-tape inference and complete end-to-end physical accounting remain open.

All five new audit sections executed successfully against committed source in connector JS. Adapter originally passed the support producer rather than source checker to the nested verifier; corrected and all five sections rerun. Main and PR #248 untouched. Remote Proctor completion unconfirmed.
