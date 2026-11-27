# F038-REX-024D6G — Physical prefix separator conditioning

Parent D6F 5c313095b67aac8b318f0a144b949f28c91cd95a. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6F exact-head Proctor 46038163256](https://github.com/tltmgnt/MathOS/actions/runs/46038163256): all fifteen jobs completed successfully, including native and physical quotient/cutoff verification.

## Physical admission and conditional membership
Retain D6F GAC, local materialization and direct extension. Probe original active scope connectivity using the genuine stream and scope directory. If disconnected, use the D6F path. If connected, rebuild the graph after deleting coordinate 0: for a pair (0,j) omit the edge; for a triple (0,j,k) append edge (j,k); for scopes not containing 0 preserve the star edges. This constructs a graph inducing exactly the residual primal connected components; deleting the center of the original star graph without rebuilding the residual edge is incorrect. Probe closure from coordinate 1. If all eight residual vertices are reached, rebuild the original graph and use the complete direct path. Otherwise admit the prefix separator. This is a structural split guard, not a measured cost selector or discovery of arbitrary separator coordinates.

Tape A positions 16,17 encode mode/probe flags. In admitted mode, enumerate surviving ranks of coordinate 0 in increasing order, marking it solved/fixed for each branch. Discover each residual component, including singletons, and materialize its local factors. For a scope starting at coordinate 0, select the factor by its second coordinate, otherwise by its first. Preserve original factor arity, directory order and run-coded mask tokens. The fixed separator rank participates in original tuple-row membership, but never changes during local search; no physical mask slice/projection is claimed. Nonseparator coordinates reset on branch failure; advance the separator and restart the residual search. Exhaustion of the separator is UNSAT. If all residual blocks succeed, emit the original witness immediately. No host plan or rank is used. Twenty tapes retained.

## Source-level completeness and lexicographic theorem
Assume genuine normalized input, canonical stream, sound GAC and correct lowering. Residual graph closure places the nonseparator coordinates of every active factor in exactly one block (unaries already constrain the domains). For each fixed surviving separator value, the formula factors into independent residual subproblems; retaining the original rows and treating coordinate 0 as constant is equivalent to conditioning. Every conditioned factor has at least one nonseparator coordinate and its last coordinate is nonseparator, so inherited direct last-coordinate extension, reset and carry are local and sound. Singleton blocks cannot bypass membership in conditioned mode. Local enumeration is lexicographic and complete. Failure of any block rules out the entire separator value. Since 0 is the first original coordinate, the first feasible surviving separator value, together with each block's lexicographic minimum, gives the global lexicographic minimum. Arbitrary or late separators would require comparing reconstructed witnesses or a different lex-preserving schedule. GAC cannot delete a rank used by a satisfying tuple. All other genuine inputs use the D6F complete fallback. Malformed or out-of-family normalization remains outside this theorem.

## Conditional physical resource envelope
If admitted residual blocks have sizes b_j summing to eight and b=max_j b_j, the count of complete local candidate visits is C <= m sum_j m^b_j. Including separator assignments yields V <= m(1+sum_j m^b_j) = O(m^(1+b)). First feasible root early exit only lowers this ceiling. For b<=2 the bound is cubic in m; for b=1 quadratic in m. On fallback use the D6F component ceiling (in particular m^9 for a connected graph). For fixed nine coordinates, graph construction/probes take O(S+m+1) primitives, residual graph stays immutable across branches, membership discovery and rebuilding local tapes costs O(S+m+1) per root branch, and local trial cost is O(S_j+m+1) under inherited cursor/extension macro assumptions. GAC passes p<=4 bounded or p<=9(m-1)+1 full; high-water segmented span N=O(S+m+1). Thus conditional T=O((p+1+m)(S+m+1)+sum_{a,j} C_aj(S_j+m+1)), t=O(L^2(p+1+m+V)) under inherited physical macro/producer/projector bounds. Since L>=4096 m^3 and S=O(L), admitted complexity is O(L^(2+(1+b)/3)). In particular b=1 gives O(L^(8/3)); b=2 gives O(L^3) on genuinely connected instances. General fallback remains conditional O(L^5). No explicit 512 L^3 constant, actual cubic admission, unrestricted SAT reduction or mechanical macro proof.

## Independent audit
580 fixtures, both modes (1160 executions): 932 SAT, 228 UNSAT. Conditioned 40 modes (36 SAT, 4 UNSAT), fallback 904, early propagation/unary refusal 216. 54 separator assignments, 6116 component and edge-list comparisons, 2530 candidate and local directory/mask comparisons, 1298 conflicts. Independent decoded primal-clique graph and relation-level conditional traces agree, as do original exact oracle and D6F results. Includes prefix stars, ternary residual pairs, residual-connected adversary, late-center lex trap (fallback) and 60 seeded prefix-cut fixtures. No observed discrepancy; finite tests only.

D6F vs D6G logical primitives: 32362851 vs 35963963 on 1160 paired executions: 6 improved, 938 regressed, 216 tied. Guard and repeated materialization dominate ordinary inputs. Keep D6F/D6C as baseline; do not infer uniform speedup.

## Hard connected prefix-cut family
Four residual equality pairs, all attached to root 0 by ternary factors. Last pair has a separate ternary diagonal prohibition for all roots (UNSAT) or all but the final root (SAT). For m>=2 the pair equality and ternary prohibition each retain local support; GAC does not resolve their incompatible conjunction at a forbidden root. Earlier equality pairs permit free ranks, causing repeated direct search. D6G solves them independently per root. Exact reference and both modes verified for m2 and m3 (8 additional executions). m4 paired audit exceeded the inherited 10-million-primitive interpreter limit; no m4 result asserted.

| domain/result | D6F visits | D6G visits | D6F logical primitives | D6G logical primitives |
|---|---:|---:|---:|---:|
| m2 SAT |47|11|104207|110353|
| m2 UNSAT |92|14|181012|111191|
| m3 SAT |483|24|1198432|168515|
| m3 UNSAT |723|30|1868899|172140|

SAT worker clocks m2 1146902402 vs 1758944128 (regression), m3 11501726628 vs 2791995002 (4.12x gain); source-accounted, not m3 end-to-end physical measurements. Ordinary one-root m3 SAT regresses from 1074675654 to 1938436986. Hard family m3 SAT candidate ceiling m(1+4m^2)=111 vs joint 19683; actual 24 local visits plus 3 root assignments. This compares ceilings, not actual runtime.

## Physical lowering and replay
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |12466|4696170|3211170|253682434|14088510|
| full |12465|4693890|3209447|253546317|14081670|

Four-bit segmented encoding, 20 tapes, 22-bit state numbers. Descriptor grows versus D6F; 21-bit threshold remains unmet.

| fixture/mode | raw physical transitions | head | span | classification |
|---|---:|---:|---:|---|
| conditioned UNSAT bounded |755096272|38293|47242|UNSAT|
| crossing SAT fallback full |506422476|45784|46575|SAT|
| conditioned SAT bounded |1555051146|46582|47397|SAT|

Original/quotient and one-short cutoff matched for first two rows (755096271 and 506422475). Conditioned SAT original replay matched exact witness 0101010101010101011111111110000 and exact worker clock 1519327558. Its combined quotient/cutoff replay exceeded interactive limit; CI registers both modes and native checks. Crossing witness 1001101010101010101111111110000. D6G CI completion unconfirmed at this checkpoint.

## Next D6H
Optimize physical admission, local stream reuse between root assignments and conditioned row slicing; add two-prefix-coordinate separators and eventually arbitrary separator plans with lex preservation. Add measured cost-aware direct/conditioned dispatch. Reduce descriptor/control duplication toward 21-bit threshold, mechanically strengthen macro proof, and confirm exact-head Proctor. No main or PR #248 changes, no promotion.
