# F038 — Thresholded row-union recovery for genuine width-six exceptions

PNP_RESOLUTION_STATUS = OPEN. Parent 37c3b986c50d65d7ac3d395b21150e5ed65879f3 (hybrid exception cover). Mathematical machine-existence derivation conditional on inherited physical parsing, mobile local matrix extraction, stationary restriction-tree and local-log bounds. Standalone semantic audit executed; not compiled original-U transitions, Lean proof or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push CI unconfirmed.

## 1. Result

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), raw selected forbidden bits F_H on supports H of width 1..3, and the fixed one-hot/OR/pin/guard extension. Fix one compressed group g and three conditioning groups K disjoint from g. A contextual map p_c(a) sends source digit a to a member of a nonempty representative set C_c, where c ranges over [0,m)^K. Write beta=sum_c |C_c|/m^4.

As in the parent, a support H containing g is wide if H union K has size six, equivalently H={g,i,j} with i,j outside K. There are ten such supports. Others are narrow. For a narrow support use the parent's weighted directed substitution loss

    d_H,c(a,b)=m^(2-|H minus ({g} union K)|)
                * #{z on H minus ({g} union K):
                     F_H(a,c,z)=0, F_H(b,c,z)=1},

omitting unused context digits. Put delta_n=sum_(c,a,H narrow) d_H,c(a,p_c(a))/m^6.

A wide support is independent of the conditioning digits. In the coordinate order (g,i,j), define

    Z_H(a,b)={(u,v): F_H(a,u,v)=0,F_H(b,u,v)=1},
    ell_H(a,b)=|Z_H(a,b)|,
    U_H(r)={(a,u,v): there exists b with ell_H(a,b)<=r
                                  and (u,v) in Z_H(a,b)}.

The internal tuple order (g,i,j) is converted to canonical support order when generating actual selectors. Let R_m={0,m^2} union {2^j: j>=0, 2^j<m^2}. The common threshold r is chosen from R_m. Define

    lambda(r)=sum_(H wide) |U_H(r)|/m^3,
    gamma_r=#{(a,c): some wide ell_H(a,p_c(a))>r}/m^4.

The new sufficient condition is existence of g,K,r and contextual sets/maps with

    beta -> 0, delta_n -> 0, gamma_r -> 0, lambda(r) -> 0.

All quantities may converge arbitrarily slowly; g,K,r and the representations may vary between inputs. There is ONE fixed deterministic original three-symbol single-tape witness machine correct on the entire family, which automatically detects this promise and takes o(m^9)=o(L^3) on every such sequence of SAT inputs. It computes its own normalized score sigma=beta+delta_n+gamma_r+lambda(r) and for sufficiently small positive sigma takes

    O(m^(42/5) polylog(m+2) +
      m^9 sigma^(1/5) (1+log(1/sigma))^a)

physical transitions and O(m^3 polylog m) visited span, with a fixed integer a. The unconditional O(m^9) bound (additive stage slack only) remains. In contrast to the parent hybrid theorem, wide substitution loss can be positive on EVERY nonrepresentative source/context pair, and individual wide losses may grow faster than m.

This is a structured width-six recovery theorem, NOT an arbitrary width-six relation solver and not a theorem for all vanishing average wide losses. It includes the parent's promise by choosing r=0, since U_H(0) is empty and gamma_0 is exactly the old wide-positive-loss fraction.

## 2. Exact witness recovery by dropping all three context coordinates on light wide pairs

Fix g,K,r and the computed minimizing maps. Define P={g} union K and the allowed envelope

    A={(a,c): a in C_c or some wide ell_H(a,p_c(a))>r}.

For every narrow H retain the exact exception relation E_H on Q=H union K as in the parent:

    E_H={z on Q: F_H(z_H)=0,
                   F_H(z_H with g replaced by p_(z_K)(z_g))=1}.

The normalized sum of narrow exception densities is delta_n by counting missing contexts and free digits. The envelope density is beta+gamma_r: representatives themselves have zero minimum hybrid distance, so no representative incurs a heavy flag. For arbitrary competing maps the union density is at most this sum.

For every wide H add a separate branch restricting the original tuple's H projection to U_H(r), a WIDTH-THREE allowed relation. The union is over all possible representative digits, not just those actually used by a computed map, so no global contextual map need be stored to construct it. The exact width-six exception, for light pairs, is contained in the inverse projection of this width-three relation.

Every branch retains every original constraint. Let x be an original satisfying tuple and replace its g digit a by p_c(a). If the resulting y satisfies the original, y is a model in the representative envelope. If any wide loss exceeds r then x is already in the heavy envelope, irrespective of which support actually failed. Otherwise if a wide H is violated by y, the original projected digits (a,u,v) belong to U_H(r), by the definition of Z_H and the actual chosen b. If the replacement fails with no violated wide support, a narrow support witnesses x in its exact E_H. All cases are covered. Every returned model is original because we only restrict original models. This preserves SAT/existence and valid witness production, not necessarily the entire original model set. It is exact also for unique SAT. At most 38 branches suffice (one envelope and one per support containing g). No new external width-six clause is introduced.

## 3. Adaptive threshold and map selection

For fixed g,K,r define the bounded directed distance

    D_c(a,b)=sum_(H narrow) d_H,c(a,b)
               +m^2 * 1{some wide ell_H(a,b)>r}.

It is in [0,37m^2], with D_c(a,a)=0. In each context run the inherited greedy facility selection: initialize residuals 37m^2; add the unused representative minimizing the sum of the resulting residuals, tie by smallest digit; update minimizing labels with earliest-center ties, assigning labels in round one. Select the smallest positive k minimizing k*m^2+F_k, with F_k the residual sum. For competitor size h and loss F_* the gain averaging proof gives F_k<=F_*+37m^3 exp(-k/h); already selected candidates have zero gain. Taking k=ceil(sqrt(h*m)) and averaging over contexts gives

    beta+delta_n+gamma_r <= 38 sqrt(beta_*) + 1/m
                            +delta_n,*+gamma_r,*.

The loss of a minimum-distance map is no larger than that of any competing map into the same sets. The projected union term lambda(r) is independent of the sets/maps. Enumerate every one of the 504 choices g,K and every threshold in R_m, and minimize the integer score m^6 sigma, adding m^3 sum_H |U_H(r)| to the aggregate context scores. Fix canonical ties. Keep only the best choice, threshold and score, not the full map. Thus for ANY competitor choice and threshold,

    sigma <= 38 sqrt(beta_*)+1/m+delta_n,*+gamma_r,*+lambda(r_*).

This detects the stated promise without supplied parameters. If h is bounded at every context and the competing loss is zero, using k=ceil(h log m) in the comparison instead gives the computed context part O(log m/m). The number of candidate thresholds is O(log m); this factor is charged only to preprocessing, not the local-log density term.

## 4. Compute exact row-union tables without a fourth-order tape

The naive list of all (a,b,u,v) may have m^4 entries, and even at r=m^2 must not be materialized. For each wide support, extract its actual raw table and sort explicit zero/one bits by g digit and other digit pair. Its rows have m^2 bits. Compute all ell_H(a,b) by aligned sequential scans of a saved row and each other row, using O(m^4 polylog m) sequential bit time and O(m^3 polylog m) span. Store the m^2 count table.

For a given threshold, process source a one at a time. Keep a copy of its row and an initially zero accumulator indexed in the SAME sequential (u,v) order, both of size O(m^2 polylog m). Scan every candidate row b, obtain its count by a sequential scan of the saved count records (or a count-aligned stream), and if ell<=r OR the old-zero/new-one differences into the accumulator by aligned scans. Even scanning the entire m^2-entry count array per pair costs O(m^4 polylog m) bit operations across all pairs. At completion append the accumulator for a as the exact union row. This uses O(m^4 polylog m) bit time and O(m^3 polylog m) span, including the full output of m^3 bits. The OR accumulator is reset for the next source. A constant number of supports and O(log m) thresholds can be processed sequentially, discarding prior threshold tables after scoring. This is an explicit deterministic procedure with no free random-access queries. For r=0 the OR is all zero; for r=m^2 it is the union of every difference. The union is computed exactly, not estimated by the crude bound

    |U_H(r)| <= min(m^3,m^2*r).

The latter follows by counting at most m^2 pairs, each contributing at most r entries, and ignoring overlap. Actual overlap can be much more favorable.

For the narrow loss sections retain the parent's factorization by J=H intersect K. For |J|<=1 cache candidate-major count arrays of size O(m^3) total over fixed supports, constructed in O(m^4 polylog m) sequential bit time. For |J|=2 keep raw tables and generate a context's matrix from its m-bit slice. Wide counts have J empty and their threshold flag can be formed from the cached ell arrays. Initial normalized parsing, explicit raw records, pins and all count caches use O(m^3 polylog m) span. The inherited fixed-track sweep bounds charge O(m^7 polylog m) physical moves for these operations and threshold-union generation (including all thresholds and choices in the logarithms).

Inherit the parent mobile O(m^2 polylog m)-block workspace for extracting relevant narrow slices and wide count arrays for a single context across the O(m^3 polylog m) stationary span. A carry-shift scan costs O(m^5 polylog m) physical moves. Local matrix formation and greedy candidate-major scans take O(m^3 polylog m) bit steps with a local O(m^2 polylog m) sweep overhead, also O(m^5 polylog m) physical moves. There are m^3 contexts per threshold/choice. Output the score only during the first pass; on the winning choice recompute set membership, map and heavy flags for one context at a time as in the parent. Copy its O(m polylog m) fields via shuttles within original span for O(m^4 polylog m) moves, dominated by the per-context bound. Thus complete adaptive threshold selection and blockwise map recomputation are O(m^8 polylog m) original moves, O(m^3 polylog m) span. O(log m) threshold enumeration is absorbed here only. The fixed number of product tracks, fixed finite alphabet encoding over 0,1,2, local physical simulations and actual stationary record layout are inherited assumptions/constructions.

## 5. Compose the existing physical branch solvers

For each nonempty U_H(r), regenerate an actual normalized branch by adding negative triples on H that forbid its complement, retaining every original clause and actual pin. This is legal external width-three syntax, with unchanged n,L. Sequential merges against canonical raw bits and the saved union tables take at most O(m^4 polylog m) multitape bit steps with O(m^3 polylog m) span; the charged sweep bound is O(m^7 polylog m) physical moves. Any five-group superset of H has allowed join density at most |U_H(r)|/m^3<=sigma. Invoke the inherited fixed five-join local-log solver on that actual branch, following its local physical head on a reusable component with constant block overhead, preserving saved outer data. Its density term is O(m^9 sigma^(1/2)(1+log(1/sigma))^a) for sufficiently small sigma; zero joins reject in the inherited O(m^(13/2) polylog m) bound, dominated by preprocessing. Empty U_H branches are skipped. The original witness is unchanged.

For A and E_H (widths four/five), use the parent's shared context-block construction unchanged, with heavy flags instead of the old wide-positive flags. Pad to M, the next power of two >=m, choose b as the largest dyadic width with b^5<=m^3, so b=Theta(m^(3/5)). For one coarse K block recompute the maps and save at most m*b^3 records. For each envelope or narrow-exception projected coarse block generate b^k<=m^3 candidate memberships by sequential sort/merge with saved maps and raw bits. Build a stationary restriction tree once per projected block, O(m^6 polylog m) physical moves each, O(m^8 polylog m) total. Reuse it over all private-coordinate tiles. Original width-three record extraction costs O(m^3 b^3 polylog m) per full tile by the inherited mobile carry-shift workspace; across all (M/b)^9 full tiles this is O(m^12/b^6 polylog m)=O(m^(42/5) polylog m). The shared context maps are not regenerated for every projected or private tile.

The stationary local tree work is O(t^8 (1+log(t+2))^a) per node of scale t, because only O(t^3) original records are shuttled within its O(t^5 polylog t) subtree; all immutable allowed flags remain in place. The local-log counting proof in the parent bounds passing nodes by min((M/t)^9,R*(M/t)^(9-k)) for a relation with R entries on k groups. Visited descendants are within a constant multiple of this, and coarse roots are charged separately. The dyadic crossover at t0=M/R^(1/k) yields O(m^9 rho^(1/k)(1+log(1/rho))^a) with rho=R/m^k, plus the coarse preparation. Here k=4,5 and every density is <=sigma. Therefore the envelope, narrow exceptions and width-three row-union branches together have the claimed O(m^(42/5) polylog m + m^9 sigma^(1/5)(1+log(1/sigma))^a) bound. Constantly many branches; no global log m on the density term. Unpruned geometric sums give O(m^9) outside the small-score promise. All components are reused sequentially; combined span O(m^3 polylog m). Once-only reconstruction of the original latent digits, one-hot/OR/guard extension and actual pin bits, with raw contiguous n-bit output and physical halt head at its first bit, costs O(m^4 polylog m) moves as inherited. On exhaustion halt on blank.

When the competitor promise holds, the adaptive score tends to zero and this time is o(L^3). The fixed description length ell does not depend on input or threshold: at s=3 ceil(log2 L) its original allocation is at least L^3/2^ell once eligible, so eventual exact cubic inclusion follows. No explicit description length, numerical threshold or actual stage run is supplied. The uniform small-score bound implies a positive implementation-dependent lower bound on the computed score of sufficiently large actual exact-cubic SAT misses, if any exist; it is not a lower bound on computational time.

## 6. Average-loss corollary with no fixed polynomial margin beyond 1/m

Define the full normalized wide average loss

    delta_w = sum_(c,a,H wide) ell_H(a,p_c(a))/m^6.

Suppose competitor maps have beta->0, delta_n->0 and m*delta_w->0. Put x=m*delta_w. If x=0 take r=0, so both gamma_r and lambda(r) are zero. Otherwise let r be the least threshold in R_m >= max(1,m sqrt(x)), capped at m^2 (eventually the cap is unnecessary). It is at most twice max(1,m sqrt(x)). For positive x, a heavy source/context pair has total wide loss >r; hence

    gamma_r <= m^2 delta_w/r = m*x/r <= sqrt(x).
    lambda(r) <= 10*r/m <=20*(1/m+sqrt(x)).

Thus the adaptive algorithm covers ANY sequence with delta_w=o(1/m), even delta_w=1/(m log log m), and arbitrarily slowly vanishing beta and narrow loss. This is strictly weaker than requiring the fraction of positive wide losses to vanish: one lost pair per source/context gives delta_w=Theta(1/m^2) even when every distinct substitution has a positive loss. The algorithm does not need to know x or the competitor maps. This corollary is not the full delta_w=o(1) claim. The main exact-union criterion can go substantially beyond this crude threshold estimate, as follows.

## 7. Strict separation with superlinear individual wide loss

Let q=2^d, m=q-1, digits identified with distinct nonzero binary vectors. Use the previous three-context algebraic control: forbid <x0,xi+xj>=1 for triples {0,i,j}, 1<=i<j<=3; forbid <x0,x1> != <x1,xj> for j=4..8; forbid inner product one on all binary pairs among groups 1..8. ADD one genuinely wide ternary on {0,4,5}:

    F_{0,4,5}(a,u,v)=1 iff u in S and <a,v>=1,

where S is the first s=floor(sqrt(q)) nonzero vectors in natural binary order. No other cross constraints. Every pair belongs to a constrained support, so the graph is complete. All coordinates equal the weight-two vector 3 is a satisfying tuple: its self inner product vanishes. This is an easy SAT representation control, not asserted unique or computationally hard.

For g=0,K={1,2,3}, choose at most eight representatives per context, one per nonempty triple of inner-product bits (<a,x1>,<a,x2>,<a,x3>). All narrow loss is zero. For EVERY distinct nonzero a,b, the wide section loses exactly s*q/4 pairs, because the two binary linear forms are independent and <a,v>=0,<b,v>=1 has q/4 solutions, all nonzero. Therefore this loss grows as Theta(m^(3/2)); it is not in the o(m) average per-source regime. The old projected positive-loss flag is one for every distinct replacement. For any sublinear representative capacity, old gamma_w tends to one. Also delta_w>= (1-beta)*s*q/(4m^2)=Theta(m^(-1/2)) when beta tends to zero (upper bound follows from the same count). In particular m*delta_w diverges, so the crude corollary in Section 6 does not suffice on this intended configuration.

At r=m^2, however, U_H(r) consists exactly of triples with u in S, v nonzero and <a,v>=0. Indeed any such v admits a nonzero b with <b,v>=1; conversely the original bit must be zero and the replacement bit one. Its row size is s*(q/2-1), giving lambda(r)=s*(q/2-1)/m^2=Theta(m^(-1/2)). All other wide sections are empty, and gamma_r=0. The sharper constant-h greedy comparison gives computed sigma=O(log m/m+m^(-1/2))=O(m^(-1/2)). The main runtime is O(m^(89/10) polylog m)=O(L^(89/30) polylog L). Thus genuine wide errors can be both pervasive and individually superlinear while their union over potential representatives is sparse.

For completeness, the prior hybrid sufficient condition fails on this entire family for EVERY g,K choice, not just the designated one. If g=0 but K differs from {1,2,3}, some main triple has at least one unconditioned other group. For any distinct a,b, the earlier two-form argument gives at least q/4-1 lost free digits if one of its other groups is fixed, with weight m, or q(q-2)/4 lost ordered nonzero pairs if both are free. If narrow, the weighted loss is Omega(m^2); if wide the old flag costs m^2. If g>=1 choose a free binary neighbor in 1..8 distinct from g (three conditioned groups leave such a neighbor); its loss for distinct nonzero a,b is mq/4. In each of these alternative configurations, a sublinear capacity forces a nonvanishing hybrid normalized loss. In the designated configuration every distinct replacement incurs the wide flag just proved. This separates the new and prior structural promises, not all algorithms or all hardness criteria.

## 8. Executed finite validation

Standalone JavaScript audit executed in the tool runtime; identical function committed with a Node printing entry point. Sixteen fixtures at m=2,3 across eight modes include full/empty originals, all-different pairs, genuine wide and narrow exception supports, patterned ternaries and a unique unary fixture. It computes all common dyadic thresholds, exact row unions and greedy contextual maps, chooses the minimum score for the supplied g,K, and checks exact narrow mass and full original tuple replacement/recovery semantics. Adaptive totals: 466 representative occurrences, zero heavy flags and narrow loss, 8 union entries, 56,470 original satisfying tuples, 23,153 original models already in a restricted branch, 54,948 successful replacements and 1,522 failed replacements recovered via the wide union with zero heavy flags. Thus the new recovery route is exercised by the chosen adaptive maps, not solely by forced examples. There were 161,560 full-tuple checks. Forced singleton maps at both extreme thresholds (32 passes) exercise 1,857 heavy-envelope failures, 1,522 wide-union failures and 3,383 narrow failures, with 323,120 tuple checks. The routes are disjoint as classified by the audit's priority rule, not necessarily disjoint branch model sets. Additional counts: 15,520 exact row-union membership checks, 28,752 greedy marginal inequalities and 80 threshold-range checks. All assertions passed.

Algebraic controls q=8,16,32,64 verify exact individual wide loss and exact union row size by explicit pair enumeration: m,s,min=max loss,union entries are [7,2,4,4,42], [15,4,16,16,420], [31,5,40,40,2325], [63,8,128,128,15624]. They check the component wide relation, not the full nine-group family. The host audit uses indexed arrays/sets and direct enumeration rather than sequential physical tapes. It exercises common threshold selection for a supplied coordinate choice, not all 504 choices, the full physical branch solvers, actual normalized encoder/verifier, compiled transitions or exact U stage. No independent mathematical review or Lean formalization. Exact-head CI unconfirmed.

## 9. Disposition

Thresholded context-free row unions remove genuine width-six exceptions whenever their projected union remains sparse, while retaining heavy pairs in the parent width-four envelope. Arbitrarily slowly vanishing narrow loss, heavy fraction, union density and capacity suffice; the new criterion strictly extends the preceding hybrid condition. It does not establish full three-context arbitrary vanishing average loss: sparse row differences may have a dense union at every threshold that leaves few heavy pairs. Next investigate partial context projection (retaining one or two conditioning coordinates) or frequency-aware unions to avoid that residual overapproximation. Unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
