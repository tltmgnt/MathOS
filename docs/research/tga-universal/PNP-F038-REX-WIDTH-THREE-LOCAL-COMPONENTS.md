# F038-REX-024D6F — Component-local factor execution and separator conditioning

Parent D6E 8074ec9c2e934ed61dfd0092384d86734d33f8e0. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6E exact-head Proctor 46034968120](https://github.com/tltmgnt/MathOS/actions/runs/46034968120): all 15 jobs completed successfully, including both connected-UNSAT physical jobs, both native descriptors and all original/quotient/cutoff jobs.

## Physical component-local materialization
Retain D6E propagation, active-scope graph discovery, component order and witness projection. After selecting a nontrivial component, reuse V1 and V2 (tapes 17,18) as a compact mask stream and scope directory. Clear these tapes and scan the immutable Q/D originals once. For an active scope, copy its exact directory record and all run-coded field tokens (including terminator) if its first coordinate is in the current component; otherwise skip. Universal fields do not enter the local directory. No sorting, decoding into a host array, or externally supplied index is involved. D6E closure guarantees every active scope is wholly contained in exactly one component. Thus the selected subsequence is precisely the active local factors in original prefix order. No candidate validation, last-coordinate extension, or conflict retry reads Q/D thereafter; it operates on the compact tapes. Retry restores only their heads. Component success preserves selected ranks, and the next nontrivial component replaces the compact tapes. Singleton bypass is unchanged.

On genuine normalized streams, the copied records have identical order, scopes and mask tokens to those evaluated by D6E. Thus every local trial, conflict, direct extension, reset and carry is identical, with the same exact lexicographic witness or UNSAT. A connected instance materializes all active factors, eliminating repeated scanning of inactive fields and headers even without decomposition. This is a source-level correctness argument; finite original/quotient replay corroborates it. Malformed normalization is not covered.

## More precise conditional macro accounting
Let S bound the original canonical stream length, S_i be the sum of the run-coded token lengths (including terminators) of active local factors in component i, C_i the number of complete trials there, and p the number of GAC passes actually executed. Sum S_i <= S. A compact directory has at most 36*9+84*13=1416 cells. Each copied factor uses its original token representation; the total compact tape length never exceeds S plus the sentinel/blank. Tape allocation may retain the maximum length of a previously cleared compact tape; include that high-water length, not just live contents. The reused graph has at most 1632 bits. The local scratch therefore preserves N=O(S+m+1) segmented span, not the old D6E numeric bound.

For fixed nine variables, building all local streams takes O(S+m+1) logical primitives (at most nine builds, including clearing). Each trial/retry uses O(S_i+m+1) logical primitives under the inherited cursor/extension macro bounds: a run token covers at most four rows; rank loading and resetting cost O(m) per fixed number of scopes/coordinates, and the local directory is bounded by a constant. Rewinding compact heads costs O(S_i+1). GAC costs O(p(S+m+1)) and p<=4 bounded, p<=9(m-1)+1 full on genuine nonempty domains, because each changed pass deletes at least one rank. The fixed-size graph closure costs O(S+m+1) including its initial stream scan. Thus
T=O((p+1)(S+m+1)+sum_i C_i(S_i+m+1)).
Segmented physical work is O((S+m+1)T), conditional on inherited primitive lowering and producer/projector bounds. In particular with S=O(L), m=O(L^(1/3)), total is O(L^2(p+1)+L sum_i C_i(S_i+m+1)); this preserves the earlier O(L^(2+k/3)) conditional envelope for k>=2, and O(L^2) for singleton-only systems. It can improve the per-candidate factor scan charge on sparse or decomposed inputs. It does not imply the earlier explicit 512 L^3 constant. No mechanically certified all-input macro/admission theorem.

## Independent verification
D6F audit executed the same 510 normalized fixtures in both modes. Exact counts: 1020 executions, 896 SAT, 124 UNSAT; 860 crossing SAT and 116 crossing UNSAT; 26 fully connected; 5904 component discoveries and graph checks, 4858 singleton bypasses, 2372 candidate visits, 1338 conflict records. Independent decoded-relation reconstruction of local directory and canonical run-coded mask stream matched at every candidate entry (2372 comparisons of each), with 217520 cumulative local stream bits across candidate observations (not actual copied bytes) and maximum observed local stream 370 bits. Full candidate/conflict traces and original witnesses matched the existing independent exhaustive oracle and D6E. No discrepancy.

D6E vs D6F logical primitives across all 1020 paired executions: 32608902 vs 30178144; 468 improved, 434 regressed, 118 tied. This is aggregate 7.45% fewer primitives, not an aggregate physical speedup.

Selected pinned SAT exact source-accounted worker clocks:
| fixture | D6C | D6D | D6E | D6F |
|---|---:|---:|---:|---:|
| empty m2 |183311146|419632682|341343496|341343496|
| crossing pair m2 |194910862|outside|433535020|432306168|
| connected one-root m2 |609609700|outside|872189768|626941590|
| connected two-root m2 |988636830|outside|1340325688|821489416|
| equality triples m2 |1149574156|921521072|1227210254|864087950|
| connected one-root m3 |1270611344|outside|1669845836|1074675654|
| connected two-root m3 |3948529766|outside|4806193824|2785436958|
| equality triples m3 |4598984028|1629504332|2046556678|1120389220|

D6F m3 independent triples are 4.10x faster than D6C and 1.83x faster than D6E in worker accounting; some easy cases regress and copying increases physical high-water span. Not a uniform acceleration.

## Connected separator theorem and host-only implementation
Use the primal graph with a clique for each active scope (the star edge representation sufficient for ordinary connectivity must not be used as the separator graph without retaining each residual hyperedge). For a component c of size s, choose a separator H of h vertices, whose deletion leaves residual components B_j of sizes b_j. Once H is assigned, every factor either lies wholly in H or touches exactly one residual block; otherwise the residual graph would contain an edge between those blocks. Exhaustively enumerate at most m^h separator assignments, test separator-only constraints, and solve each block independently conditional on the assignment. Therefore at most m^h(1+sum_j m^b_j) combined separator-assignment and local complete-tuple visits suffice; fallback to m^s if cheaper. For an original lexicographically first witness, retain each residual block's lexicographic minimum for a fixed separator assignment, then compare the combined witnesses over all satisfying separator assignments in original coordinate order. Returning the first feasible separator assignment is not generally sound for that stronger witness requirement.

With a checked separator plan and a future physical implementation whose per-visit work is bounded by O(L^2), the resulting conditional envelope for a component is O(L^(2+min(s,h+max_j b_j)/3)), including plan/propagation work under the same assumptions and nontrivial component size. This is not a bound on the current physical D6F controller, which does not condition on separators. A one-vertex separator leaving blocks of size <=2 or a two-vertex separator leaving singleton blocks would yield a conditional cubic envelope even for connected systems; dense primal graphs may admit neither. The reference tries separator subsets of size <=2 and chooses the smallest exact integer ceiling, with unconditioned fallback. It tests 513 fixtures (510 inherited plus lex-order trap and two two-center fixtures): 451 SAT, 62 UNSAT, 73 selected plans (49 one-vertex, 24 two-vertex), 280 separator assignments, 5661 local candidates, all exact witnesses/status and candidate ceilings matched. These are host visits, not physical clocks. The lex-order trap has center vertex 8: first feasible center value 0 gives leaves 1, but center value 1 gives leaves 0 and is the required global minimum.

Examples of full connected-component candidate ceilings:
| shape/domain | joint | separator bound | observed combined visits |
|---|---:|---:|---:|
| one-root m2 |512|34|22 SAT|
| one-root m3 |19683|84|48 SAT|
| two-root m3 |19683|360|259 SAT|
| two-center m3 |19683|198|135 SAT|
| late-center lex trap m2 |512|34|26 SAT|

## Physical original-format lowering and observed execution
20 logical tapes, 4-bit segmented lowering. The target 21-bit threshold is not met; materialization adds modest descriptor overhead over D6E.
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |10729|4001365|2873311|226991573|12004095|
| full |10728|3999085|2871588|226855456|11997255|

| fixture/mode | physical transitions | head | span | result | quotient/cutoff |
|---|---:|---:|---:|---|---|
| crossing SAT bounded |465148874|45776|46567|SAT|matched; cutoff 465148873|
| connected UNSAT full |653378786|38293|47690|UNSAT|matched; cutoff 653378785|
| equality triples SAT bounded |899678178|46658|47471|SAT|original observed only|

Both SAT witnesses match the original oracle, with exact worker clocks 432306168 and 864087950 respectively matching observed phase differences. Full connected UNSAT has blank halt with no witness. Both observed cutoffs use quotient and no witness; native CI independently replays one-short cutoffs from serialized descriptor. The new Proctor matrix registers audit (including host separator test and inherited governance), twelve physical jobs and two native descriptor jobs. D6F completion not yet established at this checkpoint.

## Next D6G
Physical separator conditioning with lexicographic witness selection; use residual hyperedges (not simply delete vertices from the star graph), prove canonical local mask restriction or streaming membership without host assistance, retain general complete fallback. Optimize descriptor/control sharing toward 21-bit states and add a cost-aware indexed vs direct schedule. Strengthen physical macro/admission proof, confirm exact-head D6F Proctor. Main and PR #248 untouched. No global route or Omega obligation closed.
