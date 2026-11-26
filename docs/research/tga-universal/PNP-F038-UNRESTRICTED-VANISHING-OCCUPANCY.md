# F038 — Vanishing multiscale occupancy, exact-clock slack, and a dense proper-join unique control

PNP_RESOLUTION_STATUS = OPEN. Parent 8a9bdda24d709b976b7cc939af47c7b188ed1451 (dyadic join pruning). This is a refinement of the inherited resource-accounted machine-existence construction, not a compiled original-U machine, Lean proof, or independent mathematical review. Parent combined statuses and PR-triggered workflow runs were empty; push-triggered CI is unconfirmed.

## 1. Two stronger exact-cubic sufficient conditions

Use the inherited nine-group normalized family, n=19m-7, L=Theta(m^3), arbitrary negative cross clauses of width 1..3 and the fixed one-hot/OR/pin/guard extension. Let M be the least power of two >=m. Pad the domain with negative unary exclusions for digits m..M-1, on every group. For a dyadic width t dividing M, a tile consists of nine length-t digit intervals.

Fix k in {5,6,7,8} and use the parent's fixed spatial-frame dyadic solver, testing all k-group induced relations at each nonleaf. Let R_k be the smallest allowed join size on a k-group support at the original scale m, rho_k=R_k/m^k, and e=max(6,k)+1/2. Refine the parent's time estimate by retaining the LOCAL logarithm at every scale. For R_k>=1 the time is

    O(m^9 rho_k^((9-e)/k) (1+log(1/rho_k))^a + m^6 polylog(m+2)),

for some fixed integer a>=0 (depending on the fixed implementation, not m or rho_k). The visited span remains O(m^3 polylog m). If R_k=0, the root rejects in O(m^e polylog m) physical moves. Therefore ANY sequence of SAT inputs with rho_k tending to zero is eventually covered at the exact cubic stage. A polynomial density saving is NO LONGER necessary. The result extends to k=2,3,4 by taking a five-group superset. The program is fixed and does not need to know the density or the rate of its convergence.

The second sufficient condition is independent of individual proper-join density. Let N_k(t) count all scale-t tiles (not just those actually reached before a successful halt) in which every k-group induced relation has a satisfying tuple. These different projection witnesses need not agree with one another. Define

    nu_k(t) = N_k(t) / (M/t)^9.

Then the same fixed solver satisfies, for every dyadic 2<=t<=M,

    T(m) <= O(m^9 [nu_k(t) + t^(e-9)(1+log(t+2))^a]
                 + m^6 polylog(m+2)).

In particular if some dyadic scale t=t(m) tends to infinity and nu_k(t(m)) tends to zero on a sequence of SAT inputs, those inputs eventually meet the EXACT cubic clock. The solver need not select, calculate, or know that scale: this is an analysis of its single traversal. This second condition also holds for a fixed pair-only pruning solver, k=2, with e=6, described below.

These are o(L^3) results on the specified promises, including arbitrarily slow convergence. They do not prove o(L^3) on the unrestricted nine-group family. The prior unconditional O(L^3) with an additive stage constant remains the family-wide guarantee.

## 2. Local-log crossover proof

The parent's frame construction has fixed alphabet and control, a spatial stack of geometrically decreasing frame capacities, and local counters of O(log(t+2)) bits at scale t. It bounds the physical work per visited node by C t^e (1+log(t+2))^a. The constant C and exponent a are uniform. In particular there is no factor log m charged to every leaf or small frame. Retain the parent's once-only parsing O(m^6 polylog m) and witness reconstruction O(m^4 polylog m), rather than including them in each node cost. This accounting is essential; a global polylog m multiplier would not imply the slow-vanishing result.

For R=R_k>=1 the parent's upper bound on visited nodes at scale t is a constant times

    min((M/t)^9, R*(M/t)^(9-k)).

This follows by counting disjoint projected blocks containing one of the R allowed tuples on a minimizing support; every visited nonroot node has a passing parent. The root and leaves are also covered by the bound with a fixed constant. Let t0=M/R^(1/k), lying in [1,M]. Here e<9 and e>9-k for the stated k. The weighted dyadic sum is bounded by a constant times

    sum_t min(M^9*t^(e-9), R*M^(9-k)*t^(e-(9-k)))
                   *(1+log(t+2))^a.

For t<=t0 the second polynomial term decreases geometrically as t decreases, and its logarithm is bounded by that at t0. For t>=t0 the first term decreases geometrically as t increases. On the j-th dyadic scale above the crossover the logarithmic factor is at most a constant times (1+log(t0+2))^a (1+j)^a. Summing the exponentially decaying tail times this fixed polynomial is finite and independent of m and R. Rounding the crossover to either adjacent dyadic scale changes only constants. Thus the total is

    O(M^e R^((9-e)/k) (1+log(t0+2))^a).

Since M/m is between one and two, t0=Theta(rho_k^(-1/k)), so this is precisely the first claimed bound after adding preprocessing. For any c>0 and fixed a, x^c(1+log(1/x))^a tends to zero as x tends to zero through positive values. The conclusion is o(m^9)=o(L^3), not merely O(m^9). If a proper support P of size j in {2,3,4} has R_j allowed tuples, any five-group superset has at most R_j*m^(5-j) allowed tuples: all its allowed tuples must project to an allowed P tuple. Therefore rho_5<=rho_j, proving the extension to smaller supports with the SAME k=5 solver.

## 3. Joint projection occupancy and a scale split

For any scale t>=2, count ALL passing tiles according to the k-support tests, without requiring that a full original solution exists in the tile. A passing tile has a passing ancestor at every larger scale, because its satisfying projection for each support maps into that ancestor's induced relation. The parent tests are exact, so this is a combinatorial property of the tiles, not of the order of search. A visited node strictly below t must descend from one of the passing tiles at t. Thus at scale u<t, the visited count is at most N_k(t)*(t/u)^9. This includes rejected nodes and leaves. The actual algorithm may stop much earlier upon finding a witness.

For scales u>=t, bound the visited count by (M/u)^9. The weighted geometric tail is

    O(M^9*t^(e-9)*(1+log(t+2))^a).

For u<t, use the descendant bound. The sum of local costs is

    O(N_k(t)*t^9 * sum_(u<t, dyadic) u^(e-9)*(1+log(u+2))^a)
    = O(N_k(t)*t^9) = O(M^9*nu_k(t)).

The residual series over u=1,2,4,... converges because e<9. Adding one-time root parsing and reconstruction proves the scale-split estimate. The theorem is not a claim that an external oracle computes the occupancy cheaply, nor a new uncharged pruning operation. It bounds the existing traversal using an analytic parameter that can depend on the whole selector and on m.

For the pair-only version, use the same fixed spatial frames, test all 36 closed two-group relations at each nonleaf, and at each leaf test the full original local list INCLUDING ternary clauses. Pair tests are necessary but not sufficient for global SAT; rejecting an empty pair projection is safe. To implement a pair test, enumerate t^2 local pairs, emit default records and forbidden completions of selected unary/binary clauses on the pair, sort by digit pair and OR-merge flags; check whether any pair survives. O(t^2 polylog(t+2)) multitape bit work suffices for one pair after scanning the node's O(t^3) records. Including repeated scans, the fixed number of tests takes O(t^3 polylog(t+2)) bit steps and visited span. The inherited constant-width encoded product-track sweep simulation within the frame costs O(t^6 polylog(t+2)) physical moves. Node translation, push/pop, copying, and cleanup also have that bound by the parent frame construction. Leaf cost remains constant with local counters; no per-leaf root access occurs. This defines a fixed original machine with e=6 in the scale-split estimate, correct on arbitrary unary, binary and ternary cross constraints. The pair-only solver does not require the entire family to have binary constraints. Span and one-time preprocessing remain as before.

## 4. Consequences for the exact stage, rather than an unspecified cubic coefficient

For either fixed solver let ell be its actual finite description length in the original interpreter. The exact stage s=3 ceil(log2 L) assigns that description at least L^3/2^ell original transitions once eligible. All sufficient conditions in Sections 2-3 give T/L^3 tending to zero. Therefore each eventually fits even this fixed positive coefficient. There is no need to compute ell, optimize the finite control, or assume it is small. This is precisely where o(L^3) differs from the preceding unconditional O(L^3) bound.

More quantitatively (existential constants, not computed): for every fixed k in {5,6,7,8}, the refined density bound implies that there exist c_k>0 and m_k such that every SAT input missed by the actual exact cubic stage with m>=m_k has rho_k>=c_k. Indeed choose c_k sufficiently small that the first normalized time term is below half the fixed clock coefficient uniformly for rho<=c_k, and make the one-time preprocessing term smaller than the other half. For k=2,3,4 use rho_5<=rho_k. Thus all proper-subset joins must have a density bounded away from zero by constants on an eventual miss sequence, not merely density m^(-o(1)).

For each of the fixed projection solvers k=2,5,6,7,8, the scale-split estimate likewise gives constants T_k>=2, eta_k>0 and m'_k such that every sufficiently large exact cubic SAT miss has nu_k(t)>=eta_k at EVERY dyadic scale T_k<=t<=M. Choose T_k so that the local-log tail is uniformly small for all t>=T_k, then eta_k small enough for the occupancy term and finally m'_k for preprocessing. These constants depend on the particular machines and hidden resource constants; no practical threshold or explicit numerical values are supplied. The statement is necessary for actual misses because the original stage includes those fixed machines. It does not assert any such misses exist or that the necessary conditions are sufficient.

## 5. A dense proper-join unique control with vanishing occupancy

Let m=2h+1 with h a positive multiple of eight, h>=8. The digit 0 is special. The other digits are in two contiguous type classes, each with h labels: digit 1+tau*h+x has type tau in {0,1} and label x in [0,h). The nine groups are the vertices of a cycle of length nine.

Use only binary negative cross clauses. For each pair i<j impose the following allowed relation, selecting exactly its complement in the actual pair selector positions:

* On cycle edges (j=i+1 or (i,j)=(0,8)), allow (0,0), or two nonzero digits of OPPOSITE types whose label difference (y-x) mod h is outside [h/4,h/2). No mixed zero/nonzero pair is allowed.
* On noncycle pairs allow every pair involving zero. For two nonzero digits, of any types, require their label difference outside the same interval.

Each pair excludes some entries, so the primal graph is K9. The cycle constraints make zero/nonzero status equal around the connected cycle. A fully nonzero solution would give a two-coloring of an odd cycle, impossible. Thus the unique global tuple is all zero, which satisfies every pair. The inherited pins and auxiliaries give exactly one full model for any actual pin pattern.

Every proper subset Q of groups induces a disjoint union of paths and isolated vertices on the cycle. Choose any two-coloring of those components and choose all labels independently from I=[0,h/8). All pair differences lie outside the forbidden interval, including wraparound, so these are |I|^|Q| allowed Q tuples. Consequently for all 2<=k<=8, rho_k >= (h/(8m))^k, bounded below by a positive constant. No individual proper-subset density tends to zero. Each specified local digit can also be extended on every support of size <=3: use all zero if the specified digit is zero, otherwise choose a type coloring respecting that digit and assign its same label to all groups of the support. Thus every digit has local support.

For each group, already in the binary context of a cycle neighbor, the zero row is {0} and all nonzero rows exclude zero. The latter have cardinality 3h/4 and are distinct: opposite type rows have disjoint nonzero supports, and within a type the forbidden label arc has a unique cyclic starting boundary. The same is true in either endpoint order. Hence raw and contextual signatures are pairwise incomparable; both static and contextual pruning retain full domain width. Each directional maximum fanout on any closed support of width <=3 is at least h/8, by fixing a compatible proper-support coloring, fixing parent labels in I, and varying the appended label throughout I. Therefore the global fanout product W is Theta(m^9). On a cycle pair the empty-context row family has m distinct nonempty rows; on every noncycle pair it has at least h distinct nonempty rows (fix one nonzero type and vary the label). All such row sets form a clique of size at least h in the context-conflict graph, in either endpoint order. The earlier minimum greedy color count K is therefore Theta(m). Every ordered pair has a row forbidding at least h/4 partner digits, so the earlier sparse-forbidden parameter D is Theta(m) as well. These assertions use actual binary contexts; there are no ternaries in this construction.

For the pair-only dyadic solver, a passing tile cannot contain a coordinate interval wholly outside [0,m). Call a nonempty interval exceptional if it contains digit zero or contains nonzero digits of both types. There are at most TWO exceptional intervals at each scale: the interval containing zero and the interval straddling the boundary of the two contiguous types (possibly the same interval). Padding does not add another type; it is forbidden. If all nine tile intervals are nonexceptional and nonempty, each fixes a nonzero type, so some cycle edge has equal types. That pair projection is empty and the tile fails. Every passing tile therefore has at least one exceptional coordinate. By a union bound,

    N_2(t) <= 18*(M/t)^8,
    nu_2(t) <= min(1,18*t/M).

Choose dyadic t=Theta(m^(1/4)), which tends to infinity. In the scale-split estimate with e=6, both t/M and t^(-3) are O(m^(-3/4)), up to fixed constants; the local-log factor is polylog m. Thus the pair-only machine runs on this family in

    O(m^(33/4) polylog m) = O(L^(11/4) polylog L).

Strict polynomial cubic slack is recovered even though all proper-subset join densities are bounded below, the graph is complete, contextual width is full, K and D grow linearly and W has full exponent nine. This separates the occupancy promise from all the listed preceding necessary conditions. Its all-zero witness is easy to find, so this is NOT a hardness example. No claim is made about all complete graphs or all unique instances.

## 6. Executed finite semantic verification

A standalone JavaScript audit executed in the tool runtime; the same audit function was committed with a Node printing entry point. It compared pair-pruned dyadic full model sets with direct enumeration on 18 fixtures at m=2,3,4 (including a ternary-only control so the leaf checker is essential), with 512265 satisfying tuples, 1827840 leaf checks and 65 per-scale occupancy/descendant inequalities. It verified every pair-pruning passing box count by a separate compatible-block enumeration, and all asserted model sets agreed. For the dense proper-join cycle family, at m=17,33,65,129 it verified constructive type colorings on 2004 proper supports, 81252 local digit-support extensions, 288 directional row-family checks and 12 coarse occupancy bounds. At each of those four sizes, with M/t equal to 2,4,8 respectively, exact passing tile counts were 76, 8480, 148322 out of 512,262144,134217728 tiles; these are semantic counts, not timing data. Additional exact pair-model checks at m=3,5,9 gave one solution each; the unbounded proof uses h a multiple of eight and does not rely on these small controls. Numerical sanity checks of the weighted crossover sum tested 480 parameter combinations with a fixed illustrative log exponent three, not a proof of the asymptotic inequality. All assertions passed. The audit uses indexed host structures, cached compatibility tables and recursive host calls; these are not the physical spatial-frame implementation. Actual normalized encoder/verifier integration, compiled transitions, actual stage execution, independent review and Lean formalization were not performed. Exact-head CI is unconfirmed.

## 7. Disposition

The proper-join density condition has strengthened from polynomial saving to arbitrary vanishing density. More importantly, multiscale joint projection occupancy gives exact-clock slack even on a complete-graph unique family with all proper joins dense. Any actual unbounded exact-cubic miss sequence must have uniformly positive proper-join density and occupancy at all sufficiently large dyadic scales for the fixed solvers. These are necessary conditions, not a lower bound. Next investigate whether dense multiscale occupancy itself can force efficient witness search or support a different pruning strategy (including coordinate relabeling or stronger simultaneous projection consistency). The unrestricted family still has only the unconditional O(L^3) / constant additive stage guarantee; eliminating that penalty for all inputs, unbounded B_3 and P versus NP resolution remain OPEN. Finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
