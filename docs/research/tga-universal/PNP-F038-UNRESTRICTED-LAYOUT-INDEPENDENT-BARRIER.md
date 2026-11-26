# F038 — Any fixed permutation of the explicit supergroup tensor has a cubic barrier

PNP_RESOLUTION_STATUS = OPEN. Extends the parent 2f128372a35f125ebc1e75f4b318b2d88f540554 from one lexicographic order to every input-independent permutation of tensor entries. Parent exact-head CI not confirmed. No external algebraic theorem needed.

## Statement and quantifiers

Let r=9, n=19m-7, L=n+1+2n^2+8 binom(n,3), M=m^3, Q=M^2. Fix ANY sequence of permutations of the Q entries of the owner tensor on supergroups (0,1,2) from the previous algebraic reduction. The permutation may depend arbitrarily on m, and need not be efficiently computable, but is fixed independently of the selector bits. Along the parent's unbounded near-dyadic subsequence of m, for each sufficiently large m there is a subfamily of 2^(2M-O(log M)) SAT selectors on which the fraction admitting explicit raw contiguous materialization of that tensor in the prescribed order, at any position and intermediate time of any exact-cubic eligible original tape program, is at most 2^(-M/25). In particular no fixed entry permutation can remove the worst-case obstruction. The subfamily can depend on the permutation; we do NOT assert a common hard input for all permutations.

The same SAT instances have a uniform fixed original solver in O(L^2 polylog L), independent of permutation. The obstruction is to an output representation, not to SAT.

## Two complementary supports

Pair original groups (0,1),(2,3),(4,5),(6,7). The sole variable clauses are arbitrary negative ternaries on groups (0,2,4) and on (1,3,5), two disjoint sets of M actual canonical positions. All other cross clauses are absent; retain the parent's fixed one-hot, OR, zero-pin and guard clauses. Let S(x),T(y) in {0,1}, x,y in [0,m)^3, denote allowed bits (complements of selected clause bits). The owner tensor A on the first three supergroups is

    A(x,y)=S(x) T(y).

Its Q entries are exactly the pairs of an M-by-M complete bipartite graph, in a bijective correspondence with the supergroup digit triples. The other owner tensors are constant one. Any fixed permutation is an ordering of these graph edges.

## Dense end blocks force recoverable information

Set P=floor(Q/6). For either the first or last P positions in the permutation, let E be its set of edges. On each side call a vertex high if its E-degree is >=M/500. Removing edges incident to low vertices removes at most 2M^2/500 edges. Thus the high vertex sets H_X,H_Y satisfy

    |H_X| |H_Y| >= P-2M^2/500 >= (4M/10)^2

for all sufficiently large M, and hence |H_X|+|H_Y|>=4M/5 by AM-GM. This holds separately for both end blocks, without any geometric assumption on their ordering.

Choose anchor sets X0,Y0 such that every high vertex of either end graph has an opposite-side anchor neighbor IN THAT GRAPH. Such sets of O(log M) vertices exist: independently sample k=1000 ceil(log2(8M)) vertices with replacement on each side, then keep distinct samples. Each high vertex misses its neighbors with probability <=(1-1/500)^k <= exp(-k/500) <1/(4M). There are at most 4M high-vertex/end requirements, so by a strict union bound a joint choice succeeds. Fix one such choice for this m and permutation. Both sets are nonempty for large M (or add one arbitrary vertex on each side). They are free public constants in this counting argument, not data supplied to the tape machine.

Fix S=1 on X0 and T=1 on Y0; vary all remaining bits independently. All selectors are SAT: choose any anchor on each side and arbitrary other digits. Their cardinality is exactly 2^F where F=2M-|X0|-|Y0|. Reading either end block recovers S on its high X vertices by reading an incident edge to a Y anchor, and similarly T on its high Y vertices. Therefore for EACH end separately the block determines at least R=4M/5-O(log M) free bits, at fixed known positions. Values of the other free bits are unconstrained by this argument. No efficiency of recovery or of choosing anchors is needed. The decoding depends on the prescribed permutation and anchors, which are fixed across the family, never on the unknown mask bits.

## Crossing certificate and counting

As in the parent, a contiguous table [h,h+Q) has either right extension h+Q-L or left extension -h at least (Q-L)/2. Set J=floor(Q/3)-L. For sufficiently large m, J>=3Q/10 and P+J<=(Q-L)/2. Thus the far P-bit end is entirely in the initially blank exterior half for all J cuts on the chosen side (right c=L+i or left c=-i, 1<=i<=J). This includes overlap with input and arbitrary input-dependent placement.

Use the parent's deterministic local replay certificate for a run prefix: description, side, cut, h, crossing states (running states encoded in b=ceil(log2 q) bits, terminal halt flag), crossing count and total transitions departing the exterior. This reconstructs the entire exterior at the prefix endpoint. Averaging across J cuts yields k<=t/J crossings. For q=1 the state payload is empty; for q>=2 the exact original syntax gives b/2^ell<=2^-42. Along the parent's near-dyadic subsequence, 2^j<=21 L/20, L<=9146 M, t=2^(3j-ell). Consequently b*k<3M/4 by the parent's exact integer inequality 40*21^3*9146^3<9*20^3*2^42. All other certificate data have O(log m) bits, including description length O(log m). There are at most 2^(3M/4+O(log M)) certificates. The certificate determines the chosen end block and thus at least R free bits. At most 2^(F-R) selectors can be associated with each certificate. Summing over certificates bounds the fraction by

    2^(3M/4-R+O(log M)) <= 2^(-M/20+O(log M)) <= 2^(-M/25)

eventually. The parent replay proof covers timeouts, arbitrary prefixes and terminal crossings; builtins are abstract proposals, not tape materializers. No algorithm-dependent entry order is included in this theorem. In particular choosing a different fixed permutation for each m is covered, but selecting a permutation after seeing the mask is not. The bound also does not apply to compression, sparse or implicit tensors, multiple noncontiguous regions, or general witness generation.

## Direct implicit solver

Scan the actual normalized selector and identify a zero bit in each distinguished ternary support. Store the two triples, interleave their digits into the six original groups, choose zero for groups 6,7,8 and reconstruct the fixed auxiliary/zero-pin/guard bits. If either scan finds no allowed triple, halt on blank. Both supports are independent; this is correct on the full two-mask family even without anchors. Fixed sequential multitape time O(L polylog L) and the parent's charged three-symbol one-tape simulation give O(L^2 polylog L), constant description length. This eventually fits the exact cubic clock. No expanded table or entry permutation is required. The new obstruction therefore survives arbitrary fixed layout choices yet remains entirely representation-specific.

## Finite regression and limitations

Executed separate JavaScript checks on M=8,27,64,216, with four edge orders (row-major, column-major, seeded shuffle, cyclic-diagonal), both end graphs, deterministic first-neighbor anchors and 16 mask trials per order. Checks: 32 end graphs, 68,712 edge occurrences, 63,776 recovery reads, 512 end/mask trials, zero discrepancies. These reduced checks use greedy first-neighbor anchors, not the probabilistic size argument; they test graph density and decoding, not asymptotic fraction or exact cubic materialization. Python regression repeats them and checks the inherited exact arithmetic slack. Python execution and exact-head CI unconfirmed; no compiled solver, Lean proof or independent review.

Next target: implicit algorithms on overlapping constraints (these two complementary supports are intentionally independent), or rejection-preserving barriers not requiring explicit outputs. No nine-group general cubic cutoff or unbounded SAT failures established. Finite cubic interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
