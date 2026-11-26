# F038 — Bounded source-context palettes and certificate-free local differences

PNP_RESOLUTION_STATUS = OPEN. Parent 5ef064f74e6b0a64eca8f12366c11f82e6664990 (directed-difference factors). Conditional mathematical fixed-machine-existence/resource derivation using inherited original parsing, pair-sliced maps, fixed-track sequential sorting/sweeps, mobile carry shifts and adjacent spatial frames. Standalone host semantic audit executed. Not a compiled original-U transition implementation, independent proof review or Lean proof. Parent combined status and PR-triggered runs empty; push CI unconfirmed.

## 1. Main result and the changed hypothesis

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), original selected negative cross-clause bits F_B on supports B of width one through three, and the fixed actual one-hot/OR/pin/guard extension. Choose g and three conditioning groups K disjoint from g, and a distinguished h in K. For every context c on K, nonempty representative sets C_c and maps p_c(a) into them, define

    beta = sum_c |C_c|/m^4,
    delta = sum_(c,a,B containing g) d_B,c(a,p_c(a))/m^6,

where d_B,c is the number of old-zero/new-one free contexts weighted by m^(2-number of free coordinates), as in the parent. A wide support H={g,u,v} has u,v outside K. Its genuine exception has six coordinates P=H union K.

The new filter is a bounded palette depending on the source digit a and ONE conditioning digit c_h, not on every raw row difference at once. Explicitly, let d=ceil(log2 m), pad to M=2^d, and partition the d binary digit positions into six consecutive blocks with boundaries floor(i*d/6), i=0..6 (empty blocks allowed). Independently in each block choose its bits from a, from c_h, or from the all-zero vector. Keep all resulting real digits b<m, with canonical least ternary-choice index j in 0..728 for duplicates. Call this list P(a,c_h). There are at most 3^6=729 choices, including a itself. The 64 block-deletion masks (using a or zero only) form a subpalette. The palette rule is uniform, fixed, computable by sequential binary scans and fixed arithmetic in polylog(m+2) bit steps per entry. It is not a restriction on the external clauses. Define

    gamma = fraction of (a,c) for which p_c(a) is not in P(a,c_h).

There is ONE fixed deterministic original three-symbol single-tape witness machine correct on the entire family, with the following implication: along ANY sequence admitting g,K,h and competitor maps with beta_*,delta_*,gamma_* ->0 arbitrarily slowly, it attains T(L)=o(L^3), visited span O(L polylog L), and hence eventual exact cubic-stage witness inclusion. In particular no rank, distinct-row, dyadic cube, sparse projection or residual support certificate is required. For the computed score s=beta+delta+gamma sufficiently near zero, the charged bound is

    T(m)=O(m^(42/5) polylog(m+2)
          + m^9 s^(1/6)(1+log(1/s))^A),
    visited span=O(m^3 polylog m).

A is fixed and implementation-dependent. The wide-branch preparation alone costs O(m^(25/3) polylog m); inherited narrow-branch preparation dominates it. The additional promise gamma_*->0 is essential to the theorem as proved. It is a compatibility condition on near-lossless representative maps, not a deduction from beta_*,delta_*->0 alone. No unconditional exact cubic coverage or general SAT algorithm is asserted. In this note 'certificate-free' refers only to removing the raw/difference representation certificates from the wide worker. The previous algorithms remain available.

The mechanism works for any fixed bounded list rule depending on a and one retained context digit with self inclusion and the stated per-entry polylog bit computation. A fixed finite family of such rules can be enumerated at constant-factor overhead. The theorem and strict separation below use the explicit six-block splice palette, not an assumed arbitrary or oracle-computed palette.

## 2. Why the palette avoids global factorization

The parent required the restricted differences of ALL permitted global pairs (a,b) to satisfy a rank or dictionary cap for every aligned free square. This can be much stronger than the local payload actually needed.

Fix a full projected tile of side t on (a,c_h,c_i,c_j,x,y). The two intervals on a,c_h contain at most t^2 pairs of digits. Each pair has at most 729 candidate slots. For each valid (a,c_h,j) store the entire directed difference string on the local t-by-t free square:

    Z_(a,c_h,j)(x,y) =
      (1-F_H(a,x,y))*F_H(P_j(a,c_h),x,y).

Here P_j means the canonical candidate at slot j, not the jth element of a dense list that changes on restriction. There are O(t^2) such rows, each t^2 bits, total O(t^4) bits even without compression, irrespective of the original wide matrix's rank or distinct-row count. This bound concerns source and one context interval as well as the free square, not merely the free square.

For each of at most t^4 light source/context map entries, store its four local digits and the canonical slot j of its selected candidate. Reference the row by the LOCAL key (source digit, distinguished context digit, slot). Heavy entries (not in the palette) are absent. No global representative digit is stored in a descendant. Different global source/context keys may have identical row strings, but no interning or rank reduction is necessary. Padded source/context digits have no map entries. Padded free coordinates have both raw bits zero and hence difference zero. At a child, the first two intervals and both free intervals shrink together; this keeps the row volume O(t^4). This is a restriction of actual local rows, not a claim that all global palette pairs have low rank.

## 3. Adaptive map selection and exact recovery

For a chosen g,K,h run the inherited greedy facility policy on

    D_c(a,b)=sum_(B containing g) d_B,c(a,b)
                  + m^2 * 1{b not in P(a,c_h)}.

The range is [0,38m^2] and self distance zero. Initialize residuals 38m^2, assign labels on the first round even in a tie, greedily add the unused representative minimizing summed updated residuals, and choose the positive round minimizing k*m^2+F_k, with fixed tie rules. For a competing set of size h0 and its minimum total loss F_*, marginal averaging gives F_k<=F_*+38m^3 exp(-k/h0). At k=ceil(h0*(1+ln(m/h0)))<=m the per-context score divided by m^3 is at most

    (h0/m)*(1+ln(m/h0)) + 1/m + F_*/m^3 + 38*h0/(e*m).

Average and use concavity of x ln(1/x). The chosen minimum over the 504 choices g,K and the three distinguished h (a fixed 1512 possibilities) satisfies

    s <= 40 beta_*(1+ln(1/beta_*)) + 1/m + delta_* + gamma_*.

The minimizing map into a competing set is no worse than any supplied competitor; no competitor is actually supplied. The computed s tends to zero under the promise. No representation-certificate test or threshold selection is used. All configurations have the self-pair property and can be compared. The actual machine remains correct when s is large.

The exact recovery envelope S on {g} union K contains representative digits and source/context pairs whose selected replacement is outside the palette. Its density is beta+gamma because a selected representative has self distance zero, so its minimizing replacement has zero penalty. For every narrow support use the ordinary exact old-zero/new-one exception on B union K. For every wide support H use the exact light exception

    E_H(a,c,x,y) =
      1{p_c(a) in P(a,c_h)}
        * (1-F_H(a,x,y))*F_H(p_c(a),x,y).

Every branch enforces every original constraint. For an original satisfying tuple substitute only g by its chosen representative. If successful its image belongs to S. If unsuccessful on an unpermitted replacement, the original tuple belongs to S. Otherwise some newly violated support contains g, and the original tuple belongs to its exact narrow or light-wide exception. Every branch witness is an original witness. At most 38 branches. This establishes exact satisfiability/witness equivalence, not equality of the entire original model set under substitution. Branch densities are individually <=s, and the sum of the normalized light-wide densities is at most delta_w. Inactive wide supports need no branch.

For the envelope and narrow branches use the inherited width-four/five stationary restriction tree, O(m^(42/5) polylog m) preparation and O(m^9 s^(1/5)(1+log(1/s))^A) local-log density work near s=0. No higher-width restriction is inserted into the external selector.

## 4. Physical map generation and coarse root preparation

Inherit canonical raw-bit parsing, actual pin extraction, directed support distance tables, and the pair-sliced map generator: O(m^5 polylog m) physical moves per retained conditioning pair for all m values of the unretained context, O(m^7 polylog m) across m^2 pairs with O(m^3 polylog m) span. Include h in the retained pair. The palette penalty depends only on (a,b,c_h), constant on that pair's unretained-coordinate stream. It can be computed directly on the aligned distance records using the six masks, or from a stationary table of at most m^2*729 candidate-slot records (a,c_h,b,j) sorted by the appropriate keys. The latter can be generated in O(m^2 polylog m) sequential bit work and joined to the pair's distance stream within the inherited generator bounds. Fixed-size enumeration of 729 slots and polylog bit comparisons only change fixed constants/log powers; they do not change matrix dimensions or polynomial exponents. Attach the canonical slot to light selected maps by the same exact matching. Full selection, parsing and regeneration setup cost O(m^7 polylog m) as before. Keep only winning identifiers/score, not all global maps.

Choose b the largest dyadic integer satisfying b^3<=m^2, so b=Theta(m^(2/3)), b divides M, b^4<=m^(8/3). Enumerate K coarse blocks first and regenerate maps for all their real contexts and all real sources. Save at most m*b^3<=m^3 entries. Each real retained pair is generated for at most (M/b) intervals of its remaining context digit; the total pair generation cost O(m^8/b polylog m) includes original-scale output shuttles of at most O(m^4*b polylog m) per occurrence, dominated by m^5 polylog m. Keep the K block spool across all its other projected coarse blocks.

For one six-coordinate projected block, generate all palette slots for real (a,c_h) in its two intervals. For every slot and every column in the two free intervals emit two explicit bit queries, one for the old raw row, the other for the actual global candidate digit, with a common local row/column key. There are O(b^4) query records including the fixed constant 729. The new candidate digit can lie outside the source interval and MUST still be queried. Sort/merge against explicit original raw zero/one bit records keyed by (global row,x,y), using zero for padded free columns. Restore local row/column order, join the two answer streams and emit the AND of old-zero and new-one. This exact sequential routine uses O((m^3+b^4) polylog m)=O(m^3 polylog m) bit work and span, including reading the raw stationary data and producing the map records with local keys and slots. Applying the inherited fixed-track sweep costs O(m^6 polylog m) original physical moves per projected block. Across (M/b)^6 blocks this is O(m^12/b^6 polylog m)=O(m^8 polylog m). No global width-six array or global pair-difference table is built, and no indexed lookup is assumed.

Store the resulting local root representation in a stationary cache of O(b^4 polylog b) blocks immediately adjacent to a reusable active root interval, on the worker side of an anchor. The original-scale raw records, context spools and global offset counters occupy components on the other side. Even charging per-bit shuttles across the original-scale interval to install this cache once per projected block costs O(m^3*b^4 polylog m) per projected block, O(m^9/b^2 polylog m) total, dominated by m^8. Do not charge that original-scale installation once per PRIVATE tile.

For each of the (M/b)^3 private coarse tiles with this projected block fixed, extract ALL original width<=3 records (including all padding exclusions) into a local list with O(b^3) entries. Use the inherited mobile O(b^3 polylog m) scratch over the original-scale stationary span, filter keys by the nine intervals, translate matching records and copy to the root. Cost O(m^3*b^3 polylog m) per full tile. Crossing the cached root region on the way to the active root still fits the original-scale bound since b^4<=m^3. The root difference payload and map need only be copied from the adjacent stationary cache to the active root's reserved slots by local per-bit shuttles, O(b^8 polylog m) per full tile. The root cache stays fixed during this entire private-tile loop. Reset the active root and its descendants between tiles; no scan of the entire original raw input per local transition. This adjacent root-copy schedule is a deliberate change from the parent's coarse whole-span copy estimate.

## 5. Adjacent spatial frames instead of a stationary projected tree

The wide worker uses the inherited adjacent spatial DFS frames, not a stationary private or projected tree. All original constraints are retained as moving singleton lists. At local side t reserve O(t^4 polylog(t+2)) blocks for the row strings, map entries, original list, local offsets/counters and temporary bit-tape scratch. The original list has O(t^3) entries because there are a fixed number of original supports of width at most three. Use the fixed finite product alphabet encoding on the actual three-symbol tape. Append a single child frame adjacent to its parent on the worker side; the parent remains stationary until that child returns. Process the fixed 512 child vectors sequentially, reusing the same child region. The sum of active frame capacities over decreasing dyadic sides is O(b^4 polylog b). Parent and child intervals are bounded by O(t^4 polylog(t+2)); locating either by delimiters and local counters stays within those intervals. No copying across all previously visited nodes. Parent scratch, child scratch and temporary data of parent size fit a constant multiple of these bounds, since parent/child sides differ by a factor of two. Only outer coarse root knows global offsets and actual pins; descendants carry local fields whose widths are functions of t.

Exact local positivity is obtained by scanning each stored row string for a one, then checking whether any light map references a nonzero row by sorting/merging on the local (a,c_h,j) key. The rows and maps are O(t^4 polylog(t+2)) bits, and fixed sequential scans/sorts over this payload have O(t^4 polylog(t+2)) bit work and span. A local sweep simulation charges O(t^8 polylog(t+2)) physical moves. This decides nonemptiness of E_H on the current projected tile, because each map entry references a row on its independently varying free square. It does NOT decide original full satisfiability. A zero flag safely prunes. It is not necessary to absorb projected-only constraints or construct private existence flags.

At a positive internal full node, for a chosen full child vector restrict the difference rows to those whose (a,c_h) keys lie in the selected two intervals, translate those keys, and take the selected free-coordinate quadrant of each remaining string in canonical order. The candidate slot j is unchanged. It originally referred to a global candidate determined by the original a,c_h; after translation it is only a LOCAL row reference, not a newly evaluated palette of the translated digits. This distinction is necessary for exactness. Restrict/translate the four-coordinate map keys without changing j. Translate the original singleton records by their child projection intervals. Child row strings are exactly the original directed difference restrictions for their retained source/context keys, and map references continue to identify the same differences. Padding is still enforced. The row count remains <=729*(t/2)^2 even if unused rows are retained. No rank or dictionary cardinality test at any scale.

The sequential bit work for each restriction, recoding, child payload creation and/or sort/merge fits O(t^4 polylog(t+2)); the payload copied by per-bit shuttles and shuttle distance each have the same bound. Local fixed-track sweeps and copying therefore charge O(t^8 polylog(t+2)) original moves, including local counters, all fixed child choices, initialization/clearing, parent return and success propagation. Each child is processed to completion and popped before proceeding to another. The exact local positivity test is repeated on entry, with all original constraints still present. At singleton, a nonzero referenced row means the exact exception bit is one; the empty original forbidden list then characterizes precisely a restricted original model. Every valid model survives its unique path. On success restore its local digits while unwinding, then the coarse offsets and actual original pins; reconstruct one-hot/OR/guard bits and emit contiguous n raw bits at the physical halt head. Once-only reconstruction O(m^4 polylog m). On exhaustion halt on blank. No input-dependent alphabet, extra physical head or global-address lookup.

## 6. Preparation, local-log bound and exact clock

For one wide branch, sum the coarse costs across full tiles:

    original-list extraction: O((M/b)^9*m^3*b^3 polylog m)
                              = O(m^12/b^6 polylog m),
    adjacent cached-root copy: O((M/b)^9*b^8 polylog m)
                              = O(m^9/b polylog m).

Mandatory root positivity, even at every empty projected root and each private coarse tile, costs at most O(m^9/b polylog m); root cleanup and counter overhead are dominated. For b=Theta(m^(2/3)) these exponents are 8 and 25/3, respectively. The other wide preparation terms in Section 4 are at most 8 (map regeneration 22/3, query/sweep 8, once-per-projection cache installation 23/3). All use original-scale O(m^3 polylog m) visited span; the cached representation plus active spatial stack occupies O(b^4 polylog m), a smaller polynomial scale. Sum over constant-many branches. The inherited narrow/envelope preparation 42/5 dominates 25/3, giving the stated complete preparation. The adjacent root placement is important; with an original-scale shuttle per cached root bit per full tile, the weaker 26/3 preparation exponent from the private-stationary note would result. Either exponent is subcritical.

For R=|E_H|, rho=R/m^6, every positive full node at side t has at least one allowed projected tuple in its projected cube. Disjoint full tiles at a given dyadic scale and at most (M/t)^3 private choices for a projected cube imply

    N_t <= min((M/t)^9, R*(M/t)^3).

Visited nonroot nodes have positive parents, so their counts satisfy the same bound up to a fixed factor. Roots charged separately. Multiply by O(t^8(1+log(t+2))^A) local work and extend the sum to M:

    sum_t min(M^9/t,R*M^3*t^5)*(1+log(t+2))^A.

For R>=1 split at t0=M/R^(1/6). The polynomial terms have geometrically decreasing tails below and above the crossover (exponents 5 and 1), and local logarithms are bounded by a fixed polynomial in the dyadic distance from crossover times the crossover logarithm. Thus traversal is O(m^9 rho^(1/6)(1+log(1/rho))^A). Empty E_H has no positive descendants. Unpruned local work sum is O(m^9). There is no global log m factor multiplying the density term. With rho<=s and the narrower exponent 1/5, combine constant-many branches to prove the main bound. For large s use the unpruned bound, maintaining exactness; no strict universal-stage inclusion from a constant upper bound alone.

Under the competitor promise s->0, runtime o(m^9)=o(L^3). The actual fixed machine description of length ell receives >=L^3/2^ell transitions at stage 3 ceil(log2 L) once eligible. The little-o bound eventually fits the exact clock. This is a conditional mathematical machine-existence derivation based on inherited physical subroutines, not an explicit ell, numerical threshold, compiled transition table or U execution.

## 7. Strict separation from the immediate parent, including alternative coordinate choices

Take m=2^d, digits full binary vectors. For large d choose ell(d) positive, tending slowly to infinity, e.g. max(1,floor(log2(log2(d+2)))) eventually, and let J=[0,m/2^ell), containing 0,1,2,3 for all sufficiently large d. For each v in J choose a permutation pi_v of all binary vectors. For v=0,1,2,3 prescribe

    pi_v(u)=e_(4v+u), for u=0,1,2,3,

where the e_i are sixteen distinct coordinate unit vectors (d>=16). These four injective partial prescriptions extend to permutations, for example by completing unused values in increasing digit order. For other v take the identity. Define the wide support

    F_H(a,u,v)=1{v in J} * <a,pi_v(u)>_2.

All raw bits are defined on the full domain, including zero. For every distinct nonzero a,b their binary linear forms are independent. Each pi_v ranges over all m vectors as u varies, so the exact directed loss is the SAME for every such pair:

    |Z_H(a,b)| = m*|J|/4.

For a=0,b!=0 it is m*|J|/2; for b=0 it is zero. This is actual directed loss, not symmetric distance.

Embed H={0,4,5} in the previous algebraic nine-group control, with g=0,K={1,2,3}, any h in K. Keep unary zero exclusions in all groups, main triples {0,i,j} for 1<=i<j<=3 forbidding <a,x_i XOR x_j>=1, binary inner-product-one forbiddances among groups1..8, equality forbiddances on pairs involving0, and Latin forbidden triples x XOR y=z among groups1..8 except V={6,7,8}, where use low-bit parity forbiddance. No other active wide support for the designated choice. Primal graph complete. The family is SAT for large d: take groups1..8 all equal vector6, a=1. Nonzero, dot(6,6)=0, dot(1,6)=0, all main XOR differences vanish, equality exclusions involving0 pass, Latin and private parity pass. For v=6, pi_v is the identity, so the wide bit is zero, whether 6 is in J or not. This is an easy SAT control, not unique or hard.

Construct competitor maps using ONLY block-deletion slots, not even the splicing freedom. Partition a into its six disjoint block vectors a_1,...,a_6. Let U be the set of all vectors with at least one zero block. Its size is at most 6*2^(d-floor(d/6)). For a context c, take C_c=U union its three conditioned digits. If a is in C_c choose a itself. Otherwise all six a_i are nonzero and independent (disjoint supports). The linear map from six subset coefficients to the three inner-product bits with the conditioned digits has rank <=3. The fiber matching the original source's three bits has at least 2^3=8 elements among the 64 distinct block-deletion candidates. Exclude the original a, zero and the three conditioned digits: at most five exclusions. Thus at least three remaining choices, all proper deletions in U, nonzero and distinct from the conditioned digits. Pick one deterministically. This preserves all main triples, unary zero exclusions and conditioned equalities; the five free binary equality constraints incur weighted average loss <=5/m. All replacements are permitted (gamma=0). Hence

    beta_* <= 6*2^(-floor(d/6)) + 3/m,
    delta_n,* <= 5/m,
    delta_w,* <= |J|/(4m),
    gamma_* = 0.

They vanish even when J shrinks relatively at an arbitrarily slow prescribed rate. Moreover the designated configuration has a genuine lower bound on optimal wide loss when beta and narrow loss vanish: at most beta fraction of source/context pairs are self replacements (self implies membership in C_c), at most 1/m have zero source, and nonzero-to-zero replacements have unary loss m^2 so their fraction <=delta_n. Therefore delta_w >= (1-beta-1/m-delta_n)*|J|/(4m). For the specified slow ell(d), this excludes the immediate earlier mixed-rate logarithmic-loss promise for any fixed positive log exponent as well. The palette condition is not merely a low upper bound obtained by artificially using bad maps.

Now consider the immediate parent's directed-difference pair filters on this same configuration: same dyadic source block of width w, and a common maximum wide loss threshold r. If w stays bounded along a subsequence, a context's permitted replacements cover at most w*|C_c| source digits, giving 1-gamma<=w*beta after averaging. Thus beta,gamma->0 requires w->infinity. If r<m*|J|/4, every nonzero distinct permitted replacement must be zero (or is impossible). The fraction of such replacements is <=delta_n by the unary exclusion, so 1<=beta+gamma+1/m+delta_n. Therefore along any vanishing-score sequence eventually r>=m*|J|/4. All distinct nonzero pairs in the same dyadic block are then permitted. For w>=2^17 take the two digits a=2^16 and b=2^16+p for every 16-bit integer p (including the self pair). They lie in the same source block, are nonzero, and all are permitted. On the fixed aligned free square [0,4)^2, the old row is zero and the new row realizes all sixteen bits of p via the prescribed permutations. Thus the directed difference strings include ALL 2^16 Boolean strings of length sixteen. Rank is sixteen, distinct count 65536. At t=4 neither rank<=4*4^alpha for any fixed alpha<1/2 nor distinct count<=2*4^2 can hold. This square is below b0 for large m. Hence no immediate-parent filter can simultaneously pass its certificate and admit vanishing beta,delta,gamma in the designated configuration. The present palette worker handles the same example without factorization.

Alternative coordinate choices cannot evade the separation. If g=0 and K differs from {1,2,3}, at least one main triple has a free other group. For distinct nonzero a,b the two linear forms are independent; exactly m/4 sums satisfy old form zero, new one. With one other group fixed this gives m/4 free digits weighted by m; with both free it gives m^2/4 free pairs. If g>=1 choose a free binary neighbor among groups1..8 distinct from g, always available because only three context groups. It gives m/4 lost partners weighted by m. In either case distinct nonzero replacements cost at least m^2/4 on some support; nonzero-to-zero costs m^2 on unary zero exclusion. Apart from selected representatives and zero sources, almost every source/context pair must incur this constant normalized loss when beta->0. Thus no alternative g,K can admit vanishing full loss. This is a strict separation from the immediate parent's enumerated-filter sufficient condition even allowing alternate coordinates, and from the earlier mixed-rate promise on the slow-loss example. It is NOT a separation from every preceding algorithm, a lower bound on SAT time or a complexity-class separation.

## 8. Executed finite validation

Standalone JS function executed in the tool runtime, then committed with identical Node entry point. Sixteen fixtures at m=2,3 across eight constraint modes, each with two passes (actual greedy choice and forced singleton contextual map), using the actual 729-slot six-block palette and prescribed coarse width 2. The host tests exact weighted losses and greedy comparisons against every competing subset, canonical palette/self inclusion, penalty identities, representative and heavy/light/narrow recovery, root row construction, two-key child clipping and slot preservation, local frame capacities, exact membership and positivity against direct projected enumeration, original-record translation, and complete light restricted model equality against direct full enumeration. Counts:

    323120 direct full tuple checks
    113765 successful substitutions
    3502 heavy-envelope failure occurrences
    5438 light-wide failure occurrences
    341 other exact exception failure occurrences
    4976 root difference rows
    1606528 emitted child row records
    1253904 frame-capacity and positivity checks each
    503296 exact local membership checks
    49585 positive nodes, 47152 singleton checks
    1245696 child choices, 8208 full coarse tiles
    5438 restricted models in each traversal
    4920 greedy marginal comparisons, 1552 penalty checks.

Aggregates [representative occurrences,unpermitted replacements,unnormalized weighted raw loss,restricted models] for greedy passes [466,0,294,2980], forced passes [280,208,10226,2458]. The forced passes are included to exercise heavy recovery, not claimed to optimize the score. Recovery counts classify original model occurrences by priority; multiple branches may cover a model.

Additional controls: 2048 six-block deletion/kernel checks at d=6,9,12,18 with 367 nontrivial all-nonzero-block sources requiring a proper deletion; 1497 palette checks across m=2,3,5,9,17,33 including non-power-of-two padding and invalid splice digits; exact permutation and uniform directed loss tests at m=16,32,64 using a finite two-by-two feature prescription and |J|=m/2, output [m,|J|,ordered distinct nonzero pairs checked]=[16,8,210],[32,16,930],[64,32,3906]. Finally all 65536 length-sixteen difference patterns were explicitly checked from the prescribed sixteen independent coordinate evaluations at dimension17, without enumerating the enormous full matrix. This verifies the local certificate obstruction, not the complete large-d SAT family or its asymptotic rates. All assertions passed.

The host reference uses arrays/maps, indexed queries and recursive objects; no actual bit-tape sorts, mobile shifts, root placement or serialized physical adjacent frames are executed. It checks one distinguished context and one wide support, not full all-choice adaptive selection. It does not integrate the actual normalized encoder/verifier, compile the original three-symbol machine, or execute the exact universal stage. The theoretical resource bound relies on inherited physical movement lemmas, with explicit new adjacent root-copy accounting. No independent mathematical review, Lean formalization, or exact-head CI confirmation.

## 9. Disposition

A bounded candidate palette depending on a source and one retained context digit makes local differences small by localization, not by raw matrix compressibility. The new condition permits arbitrary high-rank/high-cardinality raw and global difference matrices, arbitrary residual arrays, and genuinely slow optimal wide average loss on the separation control. It removes the previous factorization certificate, but replaces it with a map compatibility requirement. It remains unknown whether small beta and delta imply existence of comparably good maps in any efficiently discoverable bounded local palette, or whether another direct worker can recover arbitrary palette violations at arbitrarily slow average loss. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
