# F038 — Local exception pruning with arbitrary slow contextual compression

PNP_RESOLUTION_STATUS = OPEN. Parent 90ce14087f04ba661a24247d1b6450dcd07418db (contextual representatives). Mathematical machine-existence construction conditional on the inherited parsing, fixed-track simulation and spatial-frame resource bounds. Executed standalone semantic reference, not a compiled original-U transition table, Lean proof or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push-triggered CI unconfirmed.

## 1. Result

Use the same nine-group normalized selector family, n=19m-7, L=Theta(m^3), selected negative cross clauses of width one through three and the fixed one-hot/OR/pin/guard extension. Retain the parent's adaptive context-conditioned representative algorithm. For an ordered pair (g,h) let C_c be a nonempty representative set for g at context digit c of h, with map p_c(a). Define beta=sum_c |C_c|/m^2 and delta as the sum of normalized newly forbidden-context densities over the 37 supports containing g (on H union {h}). The parent's directed greedy selection over all contexts and ordered pairs computes sigma=beta+delta satisfying

    sigma <= 38 sqrt(beta_*) + 1/m + delta_*

for any competitor pair and nonempty contextual sets with minimum-loss maps. No such competitor is supplied to the machine.

There is a single fixed deterministic original three-symbol single-tape witness machine correct throughout the family with visited span O(m^3 polylog m). For sufficiently small positive computed sigma its time is bounded by

    O(m^(33/4) polylog(m+2)
      + m^9 sigma^(1/4) (1+log(1/sigma))^a),

for a fixed implementation-dependent integer a. In particular ANY sequence of SAT selectors admitting beta_* -> 0 and delta_* -> 0 eventually has exact cubic-stage coverage, without a rate of convergence assumption. This removes the previous polynomial-slack requirement, including for genuine width-four exception relations. The machine does not choose a scale based on sigma or its convergence rate. Outside the promise it remains exact; the derived local traversal also gives O(m^9) on arbitrary selectors of the family, with the inherited additive stage constant interpretation, not unconditional exact-stage coverage.

The new estimate is designed for slow convergence; for polynomial decay the parent's separate fixed-description streamed-fusion bound may be stronger. Both descriptions are available in the original universal enumeration.

## 2. Exact existence reduction unchanged

For the selected pair and maps let S={(a,c):a in C_c} on {g,h}. For each original support H containing g, put P=H union {h}, and E_H={z on P: F_H(z_H)=0 and F_H(z_H with g replaced by p_(z_h)(z_g))=1}, where F_H is the actual raw forbidden bit. Then the normalized densities of S and the 37 E_H sum to sigma. The original formula is satisfiable iff at least one branch obtained by restricting its models to S or one E_H is satisfiable. Indeed a satisfying tuple either remains satisfying after replacement (and enters S), or a newly violated support contains g and witnesses membership in E_H before replacement. Every branch model satisfies all original constraints. Successful replacement can change a model, so this is an existence reduction, not a full model-set union assertion. The result also applies to unique SAT. Each branch support P has size k in {2,3,4}.

The new branch solver does not encode a width-four relation as original clauses or use a globally materialized table. It uses an internal record interface and outputs an actual original witness, leaving the external normalized syntax and U unchanged.

## 3. Coarse local materialization lemma

Let A be a restriction on k=2,3 or 4 fixed groups P, of size R and density rho=R/m^k. Assume its membership on any list of at most O(m^3) candidate tuples can be evaluated by a fixed sequential bit machine in O(m^3 polylog m) time and span, using stationary O(m^3 polylog m) original-scale data. This is an explicit interface with a resource hypothesis, not an arbitrary oracle. For S it holds by sorting queries against the chosen context/representative records; for E_H it holds by sorted merging against the map and two raw-bit queries per candidate (detailed below). Then the original problem restricted to A has a fixed original physical solver of time

    O(m^(33/4) polylog m
      + m^9 rho^(1/k) (1+log(1/rho))^a),

for 0<rho<=1, with the density term zero when R=0. Span O(m^3 polylog m). The proof deliberately avoids the previous per-chunk global log multiplier on R*m^(9-k).

Pad each digit domain to M, the least power of two >=m, using negative unary exclusions for invalid digits. Choose b as the largest power of two satisfying b^4<=m^3, so b=Theta(m^(3/4)) and b divides M. This choice uses only m and fixed binary arithmetic. Enumerate all (M/b)^9 coarse tiles of side b, with original-coordinate offsets maintained in the outer dispatcher. Process them one at a time. For a tile, scan the original selected cross records, filter those whose specified digits all lie in its intervals, subtract offsets, and add translated padding exclusions; the resulting list C has O(b^3) records. Enumerate the b^k possible projected digit tuples on P for this tile (at most b^4<=m^3). Reject candidates containing padding. Evaluate membership in A and retain the accepted tuples, translated to local coordinates, as a DISTINCT allowed list A_tile. It has at most b^k entries. Neither the full A nor its global complement is produced.

For the contextual S branch, issue a query for (c,a) in the representative-set membership stream, sort and merge; missing records mean exclusion. For E_H, emit a query (c,a,ID) for each valid candidate, sort and merge against the saved p_c(a) map, then emit the old and translated queries on the actual support H with that candidate ID and an old/new flag. Sort by raw support and digit tuple; merge with actual raw bits (or sorted selected records with missing entries interpreted as zero). Restore candidate order by ID, and retain exactly old zero/new one. Duplicated queries are answered separately; each candidate is enumerated once. The map and raw streams each have O(m^3) records or fewer. External merge sorting on fixed sequential bit tapes, with O(log m)-bit fields and a fixed number of passes of these sorting routines, takes O(m^3 polylog m) bit time and span per coarse tile. The restriction S and raw supports H are chosen by a fixed dispatcher; no arbitrary growing-support routine is required.

The fixed encoded-track sweep simulation with span O(m^3 polylog m) charges O(m^6 polylog m) physical moves for each such preparation, including scans, rewinds, counters and extraction of C. Initialize the local worker frame and copy the two translated lists by per-bit shuttles over the global span, at most O(m^3 * b^4 polylog m)<=O(m^6 polylog m) moves. The local fields are then encoded using b, not global m. Outer records and offsets stay on stationary components. Keep the worker on reusable separate encoded product components and follow its local physical head with constant overhead per physical local step. Mark and clear the used extent, return to the dispatcher and advance the coarse tile counters. The O(m^6 polylog m) per-tile bound covers this initialization, copying, cleanup and all accesses to global-scale data; no such access occurs within each small local node. If needed the fixed worker starts in an interval with margins accommodating its stated span. One fixed finite alphabet encoded by constant-width blocks over physical 0,1,2 suffices; no additional physical head or input-dependent tracks.

The preparation cost over all coarse tiles is

    O((M/b)^9 m^6 polylog m)
      = O(m^(33/4) polylog m).

This cost is independent of rho and subcubic in L. The bound includes the mandatory visit to each coarse root even if its restriction is empty.

## 4. Internal higher-width local spatial stack

A local node of dyadic side t<=b stores two lists: (i) precisely the original selected cross records translated to this node (including padding units) and (ii) the distinct allowed tuples of A on P within the node, translated to local digits. If list (ii) is empty, reject the entire node. At t=1, if list (ii) is nonempty, the sole local tuple belongs to A. It is a valid model iff list (i) is empty: every retained forbidden record would be violated by the all-zero local tuple. The fixed one-hot extension and pins are reconstructed only on success, not used as additional latent constraints. At t>=2 with nonempty (ii), enumerate all 512 children in fixed order. For each list retain exactly records whose specified digits fit the chosen child intervals and subtract child offsets. This operation is injective, including for the allowed list. A valid original model is never pruned, and each successful leaf reconstructs a distinct valid original tuple restricted to A. The actual machine may stop at its first witness.

The spatial-frame implementation is the inherited adjacent-frame stack, with the following larger LOCAL capacity. At side t, the two lists have O(t^4) records total with O(log(t+2))-bit fields. Reserve O(t^4 polylog(t+2)) contiguous blocks for local data, markers, counters and scratch. A fixed iterative dispatcher uses delimiter markers to push a child immediately adjacent to the parent and pop on return. Child fields use local coordinate widths; do not store original offsets or global m in small frames. All counters for capacities and relative positions have O(log(t+2)) bits. Each child list can be filtered, translated, initialized and copied by sequential scans and per-record shuttles within the two adjacent intervals. A quadratic bound in the parent frame capacity times a fixed polynomial in local field lengths is sufficient, so total cost per visited node, including its fixed number of children, is O(t^8 (1+log(t+2))^a) for some fixed a. Leaf cost is constant. On pop clear the completed child region; propagate successful local digits by adding the saved child-choice vector times the half-width. There is no traversal to the original-scale data during push/pop, and the same fixed product-track components are reused in disjoint physical frame intervals. The sum of capacities along a halving path is O(b^4 polylog b)<=O(m^3 polylog m). No actual width-four selector encoding, extra variable group or full original-scale m^4 workspace is needed.

At success, add the coarse offsets, recover the original full one-hot/OR/guard/pin assignment using actual saved pins and emit the original contiguous raw n-bit witness with the head at its first bit. The inherited per-bit shuttles over O(m^3 polylog m) span cost O(m^4 polylog m) once. On exhaustion halt on blank.

## 5. Local-log amortization for a sparse restriction

Across all coarse tiles, passing nodes at side t are at most

    min((M/t)^9, R*(M/t)^(9-k)).

Indeed their projected P interval must contain an allowed tuple of A, and disjoint P blocks partition the padded P domain. The other 9-k block indices have (M/t)^(9-k) possibilities. Every visited node at t<b has a passing parent at 2t and at most 512 children per parent, so its count is bounded by a fixed constant times the same expression. At the coarse-root level t=b all nodes are visited; charge them separately by O((M/b)^9 b^8 polylog b)=O(m^(33/4) polylog m). This also covers R=0 (no smaller nodes then exist). Counting all visited nodes including rejected children is essential. No density-aware ordering or stage clock is used by this internal search.

For R>=1, bound the remaining weighted sum by extending to ALL dyadic scales from 1 to M:

    sum_t min(M^9/t, R*M^(9-k)*t^(k-1))
           *(1+log(t+2))^a.

Let t0=M/R^(1/k) in [1,M]. For t<=t0 the second term falls geometrically as t decreases because k-1>0, and the logarithm is bounded by the one at t0. For t>=t0 the first term decreases geometrically; at the j-th scale above t0 the logarithmic factor is at most O((1+log(t0+2))^a (1+j)^a). Its product with the decaying geometric term is summable, uniformly in m and R. Rounding t0 to an adjacent dyadic scale changes only constants. Evaluation at the crossover gives

    O(M^9/t0 * (1+log(t0+2))^a)
      = O(m^9 rho^(1/k) (1+log(1/rho))^a).

This is the parent's local-log crossover argument applied to a different node predicate and per-node exponent e=8. In particular the logarithm is NOT log m multiplying rho^(1/k). This proves the coarse materialization lemma. Without sparsity, the full traversal below b is bounded by O(M^9 sum_t t^(-1)(1+log(t+2))^a)=O(m^9), since t runs over dyadic powers; coarse cost is o(m^9). Thus the solver is also exact and cubic-order without any density promise, not necessarily within the exact universal allocation.

## 6. Compose with adaptive contextual selection

The parent's full contextual facility selection costs O(m^8 polylog m) original transitions and O(m^3 polylog m) span. Retain that procedure unchanged, including deterministic tie breaking and all 72 ordered pairs. Each branch has rho<=sigma and support size k<=4. For sufficiently small sigma, the upper envelope of rho^(1/k)(1+log(1/rho))^a over 0<rho<=sigma is O(sigma^(1/4)(1+log(1/sigma))^a); this follows from 1/k>=1/4 and monotonicity sufficiently near zero. There are at most 38 branches, a fixed number; use one reusable worker. Adding preprocessing and all coarse costs gives the claimed main bound (m^8 is dominated by m^(33/4)). No branch requires constructing an external augmented instance or invoking the universal search as a subroutine.

The parent greedy score inequality implies sigma->0 whenever beta_* and delta_* both tend to zero, without any rate requirement. Then sigma^(1/4)(1+log(1/sigma))^a->0, so T=o(m^9)=o(L^3). For the actual fixed description length ell, stage 3 ceil(log2 L) allocates at least L^3/2^ell transitions once eligible. This dominates the little-o bound eventually. The description is independent of m, sigma, any competing map or pair, and convergence rate. No numerical threshold or compiled table is supplied. The uniform estimates also imply the existence of a positive constant c and threshold m0 such that actual exact cubic SAT misses for m>=m0 must have computed sigma>=c. This is stronger than merely resisting polynomial contextual savings; it is not a proof that any misses exist.

## 7. Executed finite checks

The standalone JavaScript audit executed in the tool runtime; the same audit function was committed with a Node printing entry point. It exercises 13 fixtures at m=2,3,4: full and empty binary restrictions, context-dependent exceptions of width three and four, patterned original constraints and a singleton four-coordinate restriction on a unique unary control. It verifies sorted raw-bit query merges against direct membership, list capacities, child translation, padding, exact branch model sets and the passing/visited node bounds. Totals: 47 allowed restriction entries (summed over fixtures), 26,222 original satisfying restricted tuples, 19,120 raw-bit query answers, 3,079 coarse roots, 677,895 visited nodes, 482,241 empty-restriction prunes, 195,654 passing nodes, 194,336 nonempty-restriction leaf checks, 3,526,208 translated original records, 194,368 translated allowed entries and 25 per-scale inequalities. The m=4 fixture uses a prescribed coarse width 4 to exercise three local levels; this and the other prescribed widths test semantics rather than the asymptotic scale choice. A separate arithmetic loop checks the coarse-width inequality for every m=2..4096 (4,095 cases) and 300 numerical weighted-series comparisons with illustrative log exponent three. All assertions passed.

The reference uses indexed host arrays, sets, direct map access, host sorting and a recursive host stack. It does not execute the full adaptive selection (tested in parent), sorted map query construction on bit tapes, physical frame encoding, actual normalized encoder/verifier, compiled transitions or the exact U stage. It tests actual contextual exception branches with supplied maps, not the full existence reduction anew. Finite numerical series checks are sanity checks, not the proof of the asymptotic inequality. Exact-head CI, independent mathematical review and Lean formalization remain unconfirmed.

## 8. Disposition

Arbitrarily slowly vanishing contextual capacity and directed loss now suffice, including width-four exceptions. The new approach uses a bounded local fourth-order list only within coarse tiles and retains local logarithms in their recursive traversal. The remaining extension to two conditioning coordinates can create width-five restrictions: simply replacing b^4 by b^5 in the present argument gives b<=m^(3/5), and the coarse preparation exponent exceeds nine; the naive quadratic frame bound would also give e=10. Neither resource barrier is a lower bound on all algorithms. Next investigate a structured width-five membership interface or an alternative multi-coordinate substitution mechanism. General nine-group unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
