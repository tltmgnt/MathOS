# F038-REX-024D6H — Adaptive two-prefix separator and residual reuse

Parent D6G a2550e98ee62a738ade2001fc7c7b4670a77d224. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6G final-head Proctor 46041104910](https://github.com/tltmgnt/MathOS/actions/runs/46041104910): all 15 jobs now completed successfully, including both hard-3-sat, both conditioned SAT and both native jobs. D6F also remains verified (46038163256).

## Adaptive physical admission and conditioned execution
Preserve the D6G controller and immutable canonical stream. After sound GAC, probe original graph connectivity. Disconnected systems follow complete D6F-style component search. For connected systems, probe deletion of prefix {0}; if the residual graph splits, use one-prefix conditioning. Otherwise probe deletion of {0,1}; if that residual graph splits, use two-prefix conditioning. If neither splits, rebuild the original graph and perform complete direct search. This is a first-useful-prefix structural policy, not a measured cost-aware selector or global minimum-ceiling planner. It does not try the two-prefix option when the one-prefix option already splits.

Each active scope contributes star edges on its surviving coordinates. In particular (0,1,j) has no residual edge when both prefix coordinates are fixed; (1,j,k) or (0,j,k), j,k>=2, must contribute (j,k). The residual graph is built physically from actual scope IDs, not a host certificate. Its connectivity is exactly that of the residual primal clique graph, because a nonempty star has the same connectivity as its clique. Probe seeds and solved membership exclude both fixed prefix coordinates.

The two-prefix rank odometer enumerates surviving ranks of 0 then 1 in lexicographic order. The inner rank wraps to its first surviving value before advancing the outer rank. Fixed prefix ranks remain unchanged in residual candidate search; conflict at a prefix-only pair (0,1) rejects the branch instead of changing a fixed coordinate. That pair is copied into the first residual block only and is validated in its original prefix order; no later block needs to repeat it. Unary constraints have already been applied. All other factors are assigned to the residual block containing their nonprefix coordinates. Original arities and run-coded masks are retained; membership uses fixed prefix ranks, not projected masks.

After failure in the first residual block, cache the same immutable compact stream and scope directory, together with block membership. Advance the prefix odometer, reset nonprefix ranks, and restart the same block without closure or stream materialization. A19 tracks first block, later/direct, or reuse pending. After success in that block, invalidate the reuse flag. Failure in a later block forces all residual ranks and memberships to reset and reconstructs the first block. The optimization is safe precisely because the local stream has not been conditioned by destructive slicing; its factors are invariant across prefix values. It does not cache all blocks or all prefix branches. Twenty logical tapes retained.

## Source-level correctness
Under genuine normalized input, canonical stream, sound GAC and correct lowering: every active factor is either wholly prefix-contained or touches exactly one residual block by residual connectivity. Fixed prefix ranks make the residual conjunction factorize. Prefix-only constraints are checked before any later block can succeed, and their conflicts rule out the entire branch. In each block the inherited conflict-directed last-coordinate extension is sound and complete, because the last coordinate of any factor touching the block is a residual variable; the separator-only conflict is handled separately. Reset/carry cannot modify the prefix. Cache reuse changes no tested factor, rank enumeration or conflict order. The ordered prefix assignments plus lexicographically first solution of each residual block reconstruct the original lexicographic minimum at the first feasible prefix. Exhaustion of all prefix assignments is UNSAT. Nonadmitted graphs use complete direct fallback, not outside-class refusal. This does not establish all-input status semantics for malformed normalization.

## Conditional physical resource theorem
For admitted prefix length h in {1,2}, residual component sizes b_j summing to 9-h, and b=max b_j, at most m^h prefix assignments and C <= m^h sum_j m^b_j complete local visits occur. Thus combined visit ceiling V <= m^h(1+sum_j m^b_j). Prefix-only checks are included in the first block's visits; they do not add a new candidate product. The ceiling counts theoretical visits, not physical speedup. First feasible prefix early exit and cache reuse only reduce work.

Let S be original stream length, S_j local stream lengths (including prefix-only pair in first block), p propagation passes, and C_aj local visits for prefix a/block j. Sum S_j<=S. For fixed nine coordinates, at most four graph construction scans, bounded graph closure per discovery, and at most m^h rounds of residual materialization give the conditional primitive bound
T=O((p+1+m^h)(S+m+1)+sum_{a,j} C_aj(S_j+m+1)).
Reuse eliminates the first-block rebuild for applicable failed branches; this does not change the worst-case envelope. High-water segmented span N=O(S+m+1) includes all reused tapes. Under inherited lowering and producer/projector macro bounds, S=O(L), L>=4096m^3, and p<=4 bounded or p<=9(m-1)+1 full, we obtain t=O(L^2(p+1+m^h+V)) and the admitted bound O(L^(2+(h+b)/3)). Consequently h=1,b<=2 or h=2,b=1 gives conditional cubic-or-better complexity; h=2,b=2 gives O(L^(10/3)). General connected fallback retains the conditional O(L^5) ceiling. No explicit constant, universal cubic admission, unrestricted SAT reduction, or mechanically verified end-to-end macro proof. Fixed-nine normalized search is already polynomial in this encoding; these are restricted-family exponent improvements, not a P versus NP resolution.

## Independent audit
673 fixtures in two modes (1346 executions): 1110 SAT, 236 UNSAT. Conditioned 230 modes (40 one-prefix,190 two-prefix); two-prefix 180 SAT and 10 UNSAT. Total conditioned 216 SAT,14 UNSAT; fallback 898, early unary/propagation UNSAT 218. Independent decoded primal clique oracle matched all 370 prefix assignments, 7064 component discoveries and graph comparisons, 3534 candidate and local stream/directory comparisons,1486 conflicts; 42 prefix-only conflicts and112 first-block cache reuses. Exact original witnesses/status and D6G parity matched. No observed discrepancies. New fixtures include modular two-center stars through m4, prefix-only pair conflicts, unary restrictions, residual pairs, connected residual chains and 80 seeded two-prefix systems. Finite tests only.

Paired D6G vs final D6H logical primitives: 50065447 vs 55131083 over1346 executions;22 improved,1106 regressed,218 tied. The uncached initial D6H variant (ecdc83e509caf5cf066675a300c81eea5c8e943d) took 55892711 primitives on the same corpus; final reuse saves 761628, but does not erase general overhead. These are logical counts, not aggregate physical clocks. Example m3 two-root family source-accounted SAT worker: 3225446772 (D6G),4035871692 (uncached D6H),2426780928 (final D6H). Candidate visits D6G88 vs D6H52. One-root m3 SAT worker1938436986 vs1717866284.

## Hard two-prefix connected family
All seven residual coordinates connect to both prefix variables by ternary factors. Three equality pairs (2,3),(4,5),(7,8) and singleton6 remain after removing both prefix variables; deleting only0 leaves a connected graph. Final pair has independent ternary diagonal prohibitions involving each prefix rank; equality and these constraints retain local support, but their conjunction admits a solution only when both prefix ranks reach their last values (SAT variant), or never (UNSAT variant). Exact reference, graph shape, nonempty GAC and both physical IR modes verified for m2,m3 (8 additional executions).
| domain/result | D6G visits | D6H visits | D6G logical primitives | D6H logical primitives |
|---|---:|---:|---:|---:|
| m2 SAT |85|24|261512|227890|
| m2 UNSAT |122|27|353475|230222|
| m3 SAT |1489|82|5625515|545918|
| m3 UNSAT |1693|88|6465495|555694|

m2 SAT worker clocks2980386710 vs3796624646 (regression); m3 SAT53785925578 vs9450537036 (5.69x gain). Source-accounted, not measured end-to-end m3 physical halts. At m3 combined ceiling is 9(1+3*9+3)=279 vs19683 joint, observed82 local visits+9 prefix assignments. This family has h=2,b=2, so its conditional physical exponent is 10/3, not cubic. No m4 hard-family claim.

## Physical lowering and replay
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |13483|5149077|3516288|277786756|15447231|
| full |13482|5146797|3514565|277650639|15440391|

Four-bit segmented encoding, 20 tapes, 22-bit quotient state numbers. Bounded descriptor grows about9.5% over D6G; 21-bit target remains unmet.

| fixture/mode | raw physical transitions | head | span | classification |
|---|---:|---:|---:|---|
| two-prefix SAT bounded |1589157228|47056|47886|SAT|
| two-prefix UNSAT full |995312538|38331|47731|UNSAT|

Original, quotient and exact one-transition-short cutoff matched for both rows (1589157227 and995312537), verified in separate calls after an initial combined bounded UNSAT replay exceeded interactive limit. SAT witness0101010110101010101111111110000 and exact measured worker1552135504 match source reference/accounting. D6H Proctor registers16 physical mode/fixture jobs, two native jobs and one audit job (19 total); completion unconfirmed at checkpoint. Larger-domain hard replay is registered, not claimed complete.

## Next D6I
Introduce a measured cost-aware schedule (e.g. bounded direct probe followed by conditioned fallback) while preserving worst-case restricted bounds and exact lexicographic witnesses. Investigate physically sliced conditioned masks and persistent multi-block local caching; broader arbitrary separators require lex-preserving witness comparison or prefix scheduling. Reduce duplicated control and descriptor size, strengthen macro verification, confirm D6H exact-head Proctor. No main or PR #248 changes, no promotion.
