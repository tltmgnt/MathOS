# F038 — Direct sparse width-six recovery with factorized local generation

PNP_RESOLUTION_STATUS = OPEN. Parent f28a042a8ada7628622d927e003c5d6f98302630 (two retained unions). Conditional mathematical machine-existence derivation using the inherited original-tape parsing, fixed-track encoding, mobile carry-shift, pair-sliced map generator and stationary-frame bounds. Standalone semantic/abstract-layout audit executed. Not a compiled original-U machine, Lean proof or independent review. Parent combined status and PR-triggered runs empty; push CI unconfirmed.

## 1. New sufficient condition and tradeoff

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), actual raw forbidden bits F_H on supports of width 1..3, and the fixed one-hot/OR/pin/guard extension. Choose a group g and three conditioning groups K disjoint from it. For each full context c and source digit a choose representatives C_c nonempty and a map p_c(a) in C_c. Let

    beta = sum_c |C_c|/m^4,
    d_H,c(a,b) = m^(2-|H minus ({g} union K)|)
                 * #{free contexts z: F_H(a,c,z)=0,F_H(b,c,z)=1},
    delta = sum_(c,a,H containing g) d_H,c(a,p_c(a))/m^6.

Use only context digits present in the support in the raw lookup. Each section has weight m^2. Partition delta as delta_n+delta_w, for narrow H (|H union K|<=5) and wide H (|H union K|=6). There are 37 sections, of which ten are wide.

For ANY fixed 0<epsilon<=1, suppose an input sequence admits some choice g,K and maps with beta=O(m^(-epsilon)), delta=O(m^(-epsilon)). There is ONE fixed deterministic original three-symbol single-tape witness machine, correct on the entire family, taking

    O(m^(9-epsilon/10) polylog(m+2))
      = O(L^(3-epsilon/30) polylog L)

physical transitions on that promise, hence eventually fitting exact stage 3 ceil(log2 L). Neither the sets, maps, coordinate choice, nor epsilon are supplied. In particular no sparse projected union, zero-loss condition, or rare-frequency constraint is imposed, including on genuine width-six exceptions.

The more precise bound for its computed full-average score sigma=beta+delta is

    O((m^(17/2) + m^9 sigma^(1/5)) polylog(m+2))

for sufficiently small sigma. The wide contribution alone is O(m^9 sqrt(delta_w) polylog(m+2)) plus preparation. Unlike the preceding arbitrary-slow projected criteria, this bound DOES retain a global logarithm. Arbitrarily slow vanishing average loss is not established here. The worker deliberately uses expanded visited span O(m^(15/4) polylog m)=O(L^(5/4) polylog L), not the previous O(L polylog L) span. The original input, external clause width, actual pins and U clock remain unchanged. Tape span is not separately limited by U, but every physical movement is charged in the bound. The procedure remains exact outside the promise; the wide traversal bound alone may be O(m^9 polylog m) there. No unconditional exact cubic coverage or new general SAT result.

## 2. Adaptive full-average map selection

Use the actual sum D_c(a,b)=sum_H d_H,c(a,b) of all 37 sections, without thresholding or frequency penalties. This is in [0,37m^2] with D_c(a,a)=0. Inherit the deterministic greedy facility selection: start with residuals 37m^2, add the unused representative minimizing the sum of updated residuals, update minimizing labels, and select the smallest positive round k minimizing k*m^2+F_k with canonical tie rules (assign labels in round one). For any competitor set of size h and loss F_* in a context the sum of its marginal gains is at least F-F_*; hence F_k<=F_*+37m^3 exp(-k/h). Taking k=ceil(sqrt(h*m)) and averaging over m^3 contexts gives

    sigma <= 38 sqrt(beta_*) + 1/m + delta_*.

The map minimum is no worse than any competing map into its sets. Evaluate all 504 choices g,K, with a canonical retained pair J inside K solely for organizing the computation. Use the parent pair-sliced generator with full weighted distances, aligned stationary streams and nested mobile residual arrays. It produces all m context maps for one retained pair in O(m^5 polylog m) physical moves, with original-scale O(m^3 polylog m) span. A full census of m^2 pairs costs O(m^7 polylog m); keep the best score/choice only and regenerate maps as needed. Cache construction and canonical input parsing/pins cost O(m^7 polylog m), included. A looser O(m^8 polylog m) bound would also suffice. No global m^4 map is stored. All loops and tie rules fixed, and selection does not use epsilon.

## 3. Exact witness recovery without projection

For the winning policy define the representative relation S={(a,c):a in C_c}, of width four, and for every H containing g define the exact exception on Q=H union K:

    E_H={z on Q: F_H(z_H)=0,
                  F_H(z_H with g replaced by p_(z_K)(z_g))=1}.

Every branch retains all original constraints and restricts the tuple's projection to S or one E_H. If a satisfying tuple survives replacement, its image is in S; otherwise some changed support is violated and the original is in its E_H. Every branch witness is an original witness. Thus the OR of branch satisfiabilities is exactly original satisfiability, not necessarily equality of whole model sets; the construction also works for unique SAT. At most 38 branches. The sum of exception densities is delta by the weights above. No higher-width restriction is inserted as an external clause.

Use the inherited width-four/five stationary restriction solvers for S and narrow E_H, with context block maps regenerated by the parent pair generator. Rare flags are unnecessary. The previous b0=Theta(m^(3/5)) schedule gives O(m^(42/5) polylog m) preparation, original-scale span and local-log density cost O(m^9 sigma^(1/5)(1+log(1/sigma))^A) for sufficiently small sigma. Empty restrictions have no descendants. The remainder proves a different worker for exact wide E_H, without any projection or approximation.

## 4. Factorized generation of one width-six coarse block

Fix H={g,u,v} with u,v outside K. In internal order (a,d,e,t,x,y), where (d,e,t) is the full context, the membership predicate is exactly

    E(a,d,e,t,x,y) = (1-F_H(a,x,y))*F_H(p_(d,e,t)(a),x,y).

This is not an arbitrary width-six oracle. Pad latent domains to M, the least power of two >=m, excluding padding by unary units; membership E is false if any projected digit is padded. Choose b the largest dyadic integer with b^8<=m^5, so b=Theta(m^(5/8)), b divides M. Enumerate all coarse blocks of the six projected coordinates. For one block, retain only:

* maps for the valid (a,d,e,t) in its four intervals, at most b^4 entries;
* explicit raw bits F_H(z,x,y) for EVERY real z but only x,y in their two intervals, at most m*b^2 entries.

Both caches fit O(b^4 polylog m) bits, since m*b^2=O(b^4) at this scale. In particular b^4=O(m^(5/2)) is below original scale m^3. The raw cache includes all possible representative digits, even those outside the source interval. Querying a representative only inside the source interval would be incorrect.

For each valid retained pair in the block, regenerate all m context maps with the inherited O(m^5 polylog m) pair generator, operating in the original-scale workspace. Copy the at most b^2 relevant (a,t) entries into the block map cache and discard the pair spool. Per-bit shuttles of this output within the original-scale area cost O(m^3 b^2 polylog m), at most O(m^5 polylog m). The block cache stays stationary while pairs are generated. Each real retained pair is regenerated for (M/b)^4 combinations of the other projected intervals, so total pair cost over the branch is

    O(m^11/b^4 polylog m).

Generate the raw cache by scanning the original-scale stationary records with a mobile O(m*b^2 polylog m) workspace, selecting entries in the two intervals, including explicit zero bits. The inherited shift and append accounting gives O(m^4 b^2 polylog m) per projected block, hence O(m^10/b^4 polylog m) total. No global m^6 table and no simultaneous storage of all projected blocks. These operations occur on fixed components within an O(m^3 polylog m) region on one side of an anchor; the larger worker region extends on the other side. Do not charge the worker's entire extent as a sweep span for the pair generator or original-scale cache operations.

## 5. Build a compact positive-node stationary tree

For one projected block, build a 64-ary dyadic preorder tree. A node of side t represents the corresponding projected six-dimensional subblock. Test whether it contains ANY allowed E tuple by enumerating its t^6 projected candidates and evaluating the formula above from the two local caches. At a node with no allowed tuple emit only a zero header and end delimiter, without a writable frame or descendants. At a positive node emit a one header and a reserved original-record frame of O(t^3 polylog(t+2)) blocks; if t>1 recursively emit all 64 projected child regions in fixed order (including compact zero headers). End delimiters define disjoint subtrees. Store a local side length and child markers in the header, not global absolute addresses, and use local coordinate widths in the worker frames. At t=1 all fields and reserved capacity are constant-sized. A builder may count all allowed entries for analysis, but the worker only needs the Boolean flag and topology.

Here is a physical construction bound, avoiding a global sweep for each output flag. Copy the two caches once to a mobile component of O(b^4 polylog m) blocks. Carry the builder's dyadic prefix stack and enumeration counters (O(polylog m) bits) with it. At a candidate, scan the map and raw cache to determine its representative and both raw bits by exact key comparisons. A smaller mobile counter/query component of polylogarithmic width within the cache interval suffices for aligned key comparisons; even a linear cache scan times a polynomial in log m is O(b^4 polylog m) physical moves per candidate. No indexed lookup. At a fixed dyadic scale the candidate subblocks tested are disjoint, so at most b^6 candidate evaluations per scale, O(b^6 log(b+2)) in all. Keep the preorder builder stack on the mobile component, not the eventual worker frames. Write the current header or reserved frame sequentially to a stationary output component next to the mobile workspace, advancing its output cursor and shifting the workspace with the inherited carry-shift routine. The emitted length is O(b^6 polylog(b+2)) by summing the worst-case frame capacities over scales; one pass advancing and returning the workspace over that distance costs O(b^10 polylog m). Frame capacities, path counters and end delimiters use fixed binary arithmetic and local field lengths. This bound includes reserving blank writable regions and erasing builder scratch. No per-candidate shuttle to an original-scale anchor after caches have been copied. The total tree-generation time per projected block is O(b^10 polylog m), hence O(m^6 b^4 polylog m) over all projected blocks. The resulting immutable topology/flags and writable frames occupy at most O(b^6 polylog b) span. This is the reason for the expanded space allowance. Tree building is deterministic, even when density is not small.

## 6. Sparse subtree extent and physical traversal

Let R_t>=1 be the number of allowed projected tuples in a positive node of side t. At descendant scale s the number of positive projected nodes is at most min((t/s)^6,R_t). Each needs O(s^3 polylog(s+2)) space. Compact zero child headers cost at most a constant times the number of positive parents, and are absorbed by their capacities. The whole compact subtree extent is bounded by

    S(t,R_t) <= C sum_(s<=t dyadic) min((t/s)^6,R_t)
                               * s^3 (1+log(s+2))^A
             = O(t^3 sqrt(R_t) (1+log(t+2))^A).

For the equality as an upper bound, split at s0=t/R_t^(1/6) in [1,t]. Below s0 the R_t*s^3 term decays geometrically toward smaller s; above s0 the t^6/s^3 term decays geometrically toward larger s. Bound the logarithms by the local t logarithm. The maximum polynomial term at crossover is t^3 sqrt(R_t). This bound is valid for arbitrary clustering of the allowed entries, not an average-case assumption.

For each fixed projected coarse block reuse its tree over all private three-coordinate coarse blocks. Extract the original selected width<=3 records with the inherited mobile b^3 workspace, filtering all nine coordinate intervals and translating padding units. The original-scale stationary span is O(m^3 polylog m); the root frame is adjacent to its anchor, not at the far end of the enlarged tree. Extraction, copying to root and returning cost O(m^3 b^3 polylog m) per full tile. Across all full tiles this is O(m^12/b^6 polylog m). Mandatory root visits and optional whole-tree cleanup at the end of a tile, even if charged O(b^6 polylog b) per full tile, add O(m^9/b^3 polylog m), dominated. Do not perform a global sweep across the enlarged tree per original record or per local transition.

At a positive full node, the corresponding projected tree node's reserved frame holds its translated original forbidden records. Test each of the 512 full child vectors; the six projected bits determine the stationary child header. Locate it by scanning subtree delimiters with local depth counters, within the parent extent S(t,R_t). If it is zero, skip it WITHOUT copying an original list. Otherwise translate and copy at most O(t^3) original records into its reserved frame, using per-record/bit shuttles inside the parent subtree. Different private children reuse the same projected child frame sequentially, after earlier visits clear it. Active ancestors are at distinct projected depths. Pop/cleanup preserves immutable topology and flags. Only width-three original records move; no allowed-entry list is copied. Local field lengths and saved child bits depend on t, not m. Parent work including all child operations, zero-header navigation, cleanup and success propagation is

    O(t^3 S(t,R_t) polylog(t+2))
      = O(t^6 sqrt(R_t) (1+log(t+2))^A')

for a fixed integer A'. At a positive singleton leaf, the unique projected tuple is allowed, and the sole full tuple satisfies the original constraints iff its forbidden list is empty. Therefore the worker enumerates exactly the original satisfying tuples restricted to E (stopping at first success). Successful local digits are restored via child offsets during pop, and original coarse offsets at root. Reconstruct original one-hot/OR/guard/pin assignment and emit contiguous raw n bits with actual halt head at first bit; return blank on exhaustion. The once-only output cost across the expanded span is O(m^(19/4) polylog m), dominated. Fixed reusable components on a finite product alphabet encoded by constant-width blocks of actual 0,1,2; no extra physical head, input-dependent alphabet or unit-cost global address lookup.

## 7. Density amortization and charged preparation

Write R=|E|, rho=R/m^6. At scale t across all coarse tiles, the positive full nodes are a subset of the complete dyadic partition. For the full traversal every positive projected block occurs with exactly (M/t)^3 private choices. Consequently

    sum_(positive full nodes i) R_i <= R*(M/t)^3,
    N_t <= (M/t)^9,
    sum_i sqrt(R_i) <= sqrt(N_t * sum_i R_i)
                   <= M^6 sqrt(R)/t^6.

The first inequality allows early termination or additional safe pruning. For a complete traversal of this worker the first count is equality. Cauchy-Schwarz, not an independence assumption, gives the last bound. Multiply by t^6 and local logarithms to bound the work at any scale by O(M^6 sqrt(R) (1+log(t+2))^A'). Summing O(log m) scales yields

    O(m^9 sqrt(rho) polylog(m+2)).

For R=0 no positive node work occurs. All zero children are charged to their positive parent; empty coarse roots are charged to preparation. This proves a density saving even when every large projected block is nonempty. The dense-tree t^9 bound alone would not give that conclusion. The current Cauchy bound does NOT remove the global logarithmic loss: the per-scale estimate has no geometric decay on the large-scale side. Do not infer arbitrary-slow cutoff from it.

The wide branch preparation sum is

    O((m^11/b^4 + m^10/b^4 + m^6*b^4
       + m^12/b^6 + m^9/b^3) polylog m).

With b=Theta(m^(5/8)), the exponents are respectively 17/2, 15/2, 17/2, 33/4, 57/8. Thus the preparation bound is O(m^(17/2) polylog m), including cache setup and tree building. The global visited span O(m^3+b^6) times polylog is O(m^(15/4) polylog m). The left original-scale region and right enlarged worker region are sequentially reused by each branch; all original-scale sweep charges in Sections 2,4 and narrow branches refer only to the smaller region, not to the full visited extent. On completing a projected block erase its used tree extent; even charging one full scan per projected block costs O(m^6 polylog m), dominated.

There are ten wide and at most 27 narrow supports plus S. Sum the constant number of branch bounds. For small sigma, all rho<=sigma, sqrt(sigma)<=sigma^(1/5), and inherited narrow local-log terms are bounded by O(m^9 sigma^(1/5) polylog m) because nonzero densities are at least m^-5. Add selection and preparation, proving Section 1. Under the polynomial competitor promise sigma=O(m^(-epsilon/2)), and m^(17/2) is dominated by m^(9-epsilon/10) for epsilon<=1. Thus runtime is o(L^3); the fixed description ell receives at least L^3/2^ell transitions at exact cubic stage once eligible, so eventually a valid witness is included. No explicit ell, numerical threshold, compiled transition table, or actual U execution. The algorithm also covers other rates for which the displayed logarithm-weighted terms vanish, but no unspecified log exponent is dropped.

## 8. A fixed-policy obstruction to even two-retained projection

Let the wide support be F(a,x,y)=1 iff y=a and x!=a, all other cross bits zero. The all-equal tuple satisfies the formula. Use the fixed singleton policy p_(d,e,t)(a)=(d+e+t) mod m, independent of a. A distinct replacement loses m-1 pairs, with disjoint loss sets for different representative digits. The exact width-six relation contains R=m^3*(m-1)^2 entries; normalized wide loss is (m-1)^2/m^3=Theta(1/m), beta=1/m, narrow loss zero. At ANY choice of two retained conditioning digits, the omitted digit makes the representative uniform: every b has frequency one. At threshold f=1 the union has m^3*(m-1)^2 entries on five coordinates, density (m-1)^2/m^2 -> 1. At f>1 all positive-loss substitutions are rare, fraction (m-1)/m ->1. Thus neither one- nor two-retained projection with a frequency threshold is sparse for this FIXED policy, whereas the direct width-six predicate is sparse. The full-average greedy comparison can use this policy as competitor without enumerating its maps as a candidate policy. This is a representation control, not a separation from the entire previous algorithm class: other policies (including a constant representative) can solve this easy family and attain sparse projections. No hardness claim.

## 9. Executed finite validation

Standalone JS audit executed in the tool runtime; identical function committed with Node entry point. Twelve fixtures at m=2,3 across six modes (including empty, genuine wide, patterned and unique unary controls) use a supplied modular-sum map and one wide support. The builder explicitly tests the factorized membership using only its four-coordinate local map cache and raw rows restricted to two free intervals, verifies positive/zero subtree structure and abstract reserved-slot extents, and uses the same stationary sparse tree for all private coarse tiles. The worker checks exclusive active frames, child translation, exact restricted model set against direct enumeration, positive node mass conservation, Cauchy-Schwarz and abstract shuttle charges. Aggregate output: 334 allowed width-six entries, 48,259 original model occurrences, 121,170 direct full tuple checks, 3,984 recovered restricted models, 33,280 factorized membership evaluations, 8,710 projected tree nodes built (8,246 zero headers and 464 positive nodes), 187,330 abstract reserved slots including headers, 20,820 positive full-node visits, 19,808 singleton leaf checks, 518,144 child choices and 19,808 positive child shuttle checks. Separate m=3,5,9,17 controls verify exact width-six mass, dense width-five projection counts, rare count and uniform third-digit frequencies. All assertions passed.

The reference uses arrays/maps and host recursion; positions are abstract slots, not physical tape addresses or measured moves. It uses a prescribed coarse width two and forced maps, not the asymptotic width, full greedy selection, narrow branch pipeline or all supports. It does not implement mobile cache movement, physical sparse tree serialization, actual normalized encoder/verifier, compiled transitions, or exact stage. The resource result is conditional on inherited physical subroutines, and needs independent mathematical review. Exact-head CI and Lean formalization unconfirmed.

## 10. Disposition

Full three-context average-loss recovery is now derived for polynomially vanishing capacity and loss, with no projection promise, by permitting moderately enlarged tape span and charging compact positive-node trees by their local allowed counts. The arbitrary-slow vanishing average-loss target remains open; so does recovering original-scale span for this direct construction. The next target is a geometric large-scale saving or a more efficient frame-transfer method, eliminating the global logarithm and ideally the expanded span. General unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
