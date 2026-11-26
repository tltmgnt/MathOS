# F038 — Approximate directed classes with one-sided correction recovery

PNP_RESOLUTION_STATUS = OPEN. Parent 76cc1630f971dc1e9afcd01cc5c395267498fc43 (difference class covers). Conditional mathematical fixed-machine-existence/resource derivation using inherited original parsing, pair-sliced maps, fixed-track sweeps, mobile carry shifts, adjacent frames, and space-capped stationary width-six recovery (12a69b594fde7aced18f48ee42a6e82a5148bbac). Executed host semantic regression. Not a compiled original-U implementation, independent mathematical review or Lean formalization. Parent combined status and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Result and scope

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), actual selected negative support bits F_B on widths one through three, and actual one-hot/OR/pin/guard extension. Choose compressed group g and three conditioning groups K. For the generated contextual nonempty representative sets C_c and maps p_c(a) into them, use beta=sum_c |C_c|/m^4 and delta_n,delta_w as the inherited weighted average narrow and wide directed losses divided by m^6. Selected representatives map to themselves. Inherit the finite map-policy family (full-average facility greedy and fixed six-block-splice-penalized greedy). No map reoptimization after approximate class learning.

For each fixed real source a and wide H={g,u,v} with both u,v outside K, write

    Z(a,b;x,y)=(1-F_H(a,x,y))*F_H(b,x,y).

For a common integer Hamming radius r, choose approximate classes independently for each (H,a). First choose a itself as the zero center and assign all target strings at distance <=r from it. Then repeatedly choose the least still-unassigned actual target label j as the next center and assign every still-unassigned string at distance <=r from Z(a,j). This deterministic rule terminates and defines j_H(a,b) with

    T_H(a,b)=Z_H(a,j_H(a,b)),
    E_H^-(a,b)=Z_H(a,b) AND NOT T_H(a,b),
    E_H^+(a,b)=T_H(a,b) AND NOT Z_H(a,b).

The radius guarantee is |E^-|+|E^+|<=r. Exact identity Z=(T minus E^+) union E^-. Self has zero template and corrections. A center need not be a selected contextual representative, and is NEVER substituted into any original constraint or narrow loss. It is only a wide recovery template. Radius zero recovers the preceding exact directed classes, up to the immaterial identifier of the null class.

Pad to M least power of two >=m, B largest dyadic with B^3<=m^2. As in the parent, enumerate alpha in {1,5/4}, dyadic C<=m^(1/32), C>=1. Trim actual nonzero template identifiers top-down at all aligned context scales t<=B, for each source and wide support independently, keeping at most floor(C*t^alpha) most frequent identifiers. Break ties by increasing label. Assignments discarded on any support are permanently heavy. Null templates never cause deletion, even when the actual directed difference is nonzero. Let gamma be heavy fraction and lambda_T be total template cardinality summed over surviving actual source/context assignments and wide supports, divided by m^6. This is template mass, not actual directed loss. Include the parent's raw-label trimming mode as an alternative at r=0.

For each wide H, let kappa_H be the exact missing-bit mass on ALL actual assignments, including heavy ones, divided by m^6:

    kappa_H = sum_(a,c) |E_H^-(a,p_c(a))|/m^6.

Define an original-scale source-only union

    U_H(a,x,y)= OR_(real b) E_H^-(a,b;x,y),
    eta_H=|U_H|/m^3.

The union is deliberately over ALL real targets, not merely used labels. Therefore it can be generated without storing the contextual map and may overestimate the actual corrections. For each H choose either this width-three union or the exact width-six correction, according to which charge is smaller. Fix a sufficiently large integer D0 and put Lambda=(1+ceil(log2 m))^D0. Define

    Q=beta+delta_n+gamma+C^P lambda_T
                    + sum_H min(eta_H,Lambda*kappa_H),
    (alpha,P)=(1,13) or (5/4,25).

Enumerate r=0, powers of two <=m^2, and m^2; all choices are computed, not supplied. Exact integer score m^6 Q is used. Store the winning policy, coordinates, radius, trimming mode, capacity, exponent and branch choices. One fixed deterministic original three-symbol one-tape witness machine correct throughout the family has the following charged bound for sufficiently small positive computed Q:

    T(m)=O(m^(35/4) polylog(m+2)
              + m^9 Q^(1/12)(1+log(1/Q))^A),
    visited span O(m^3 polylog m).

The log exponents and D0 are fixed implementation constants, not input advice. On Q->0 this gives T(L)=o(L^3), original-scale visited span and eventual exact cubic-stage witness inclusion. At r=0 the score is exactly the parent's (with null identifier convention immaterial), since both corrections vanish. Including both prior trimming modes yields pointwise score dominance for the same generated maps; no dominance claim for greedy approximate trimming alone. The preceding faster preparation bounds remain available as separate programs.

The additional exact-correction option is not rate-free in kappa alone; it requires Lambda*kappa->0 unless the union option is small. The rate-free statement is in the complete computed Q. This does not establish arbitrary-slow full-average recovery from beta,delta alone.

## 2. Why one-sided corrections suffice

For every actual pair the bit identity is Z=(T AND NOT E^+) OR E^-. For existence recovery we only require the containment Z subset T union E^-. Extra template bits are safe because ALL original constraints are enforced in every branch. We do not claim the template alone, or its union with missing bits, equals the actual exception. There is no changed verifier or approximate acceptance.

The width-four envelope on {g} union K contains selected representative digits and every heavy assignment. These sets are disjoint because selected representatives map to self, whose template is zero on every H. Its density is beta+gamma. Keep every ordinary exact narrow exception on B_support union K, using the ACTUAL target p_c(a). For each wide H use two guards:

    template: 1{not heavy} * T_H(a,p_c(a);x,y)
                    on (a,c,x,y),
    correction: either U_H(a,x,y) on H,
                 or E_H^-(a,p_c(a);x,y) on (a,c,x,y).

No heavy mask is needed in either correction guard. The exact correction covers every actual missing bit, including heavy assignments; the union is a further safe enlargement. This choice simplifies physical regeneration of the exact correction map. At most 48 branches.

For an original satisfying tuple, substitute g by the actual selected representative. If successful the image is an original model in the envelope. If unsuccessful and heavy, the original tuple is in the envelope. Otherwise some newly forbidden support containing g is violated. A narrow support places the original in its exact exception. A wide support gives a Z bit equal to one, so either the surviving template is one or E^- is one, in which case the selected correction guard is true. Conversely all returned witnesses satisfy all original constraints. This establishes exact satisfiability and witness existence, not preservation of the entire model set under substitution. A null template with nonzero actual difference is explicitly recovered by its correction. False positives need no negative correction branch. If exact evaluation of Z is desired it uses both E^+ and E^- in the bit identity, but the search does not store E^+.

## 3. Rate-free approximate-cover criterion

At fixed radius r, the multiscale frequency-tail bound of the parent applies with nonzero template identifiers. For each original nonzero template multiset on a source and aligned context cube, count the occurrences outside the top floor(C*t^alpha) identifiers. Sum these counts over supports, levels, sources and cubes, divide by m^4, obtaining tau. At each sequential step the current multiset is a submultiset of the original one. Keeping original top identifiers would delete at most its original tail count, and current frequency trimming is no worse. Thus gamma<=min(1,tau). Later deletions preserve earlier caps. This is not optimal simultaneous trimming.

The total template mass satisfies

    lambda_T <= delta_w + 10*r/m^2,

because there are at most ten wide supports, and for each surviving assignment |T|<=|Z|+r. Moreover

    kappa_H <= r/m^2,
    eta_H <= min(1,r/m),

since each source has at most m possible targets and the union has at most m*r bits per source. The eta bound is worst case; actual unions can be much smaller even at larger radii. These are upper bounds, not assumptions about disjoint corrections.

Consequently, consider a sequence of generated maps with beta,delta_n,delta_w->0 and an enumerated radius sequence r=r(m) such that r/m^2->0 and the nonzero template frequency tails are tight in the parent's multiscale sense:

    lim_(C->infinity dyadic) limsup_(m->infinity) tau_alpha,C(m)=0.

If either sum_H eta_H->0, or sum_H Lambda*kappa_H->0, or their per-support minima sum to zero in the limit, the selected Q->0. For each epsilon choose a FIXED dyadic C giving small limsup tau, which eventually passes the cap; at this fixed C, C^P lambda_T->0. Take the selected minimum before the limit. No rate restriction on delta_w or gamma. In particular r=o(m) automatically makes union corrections small; r=O(m^(2-epsilon)) for any fixed epsilon>0 automatically makes the exact correction charge small even when all the source-only unions are dense. The latter condition concerns template approximation error, NOT the full wide loss. There is no requirement that the true average wide loss vanish polynomially or at a logarithmic rate. More generally the actual score suffices without these convenient radius estimates.

## 4. Deterministic census and exact selection in bounded space

For one H,a construct the m complete directed strings of m^2 bits each by aligned raw scans as in the parent. They occupy O(m^3 polylog m) blocks. Maintain target labels, assigned flags and the current center row. For each chosen center, scan all unassigned target rows in order, compare bit-by-bit with the center, compute distance and both one-sided counts, assign those within radius. Use sequential bit tapes; rewind the center per target, and retrieve the next least unassigned center by scanning the stored rows. At most m rounds, O(m^4 polylog m) sequential bit work per source with O(m^3 polylog m) span. Self is selected first, before increasing-label order for other centers. At radius zero the nonzero centers are exactly the least labels of their exact classes. No probabilistic hashing, indexed lookup or storing all m^4 difference bits.

When assigning b to its center, emit the small record (H,a,b,j,|Z|,|T|,|E^-|); null is recorded if |T|=0. In the same aligned comparison OR E^- into a source-specific accumulator of m^2 bits. One may make a second scan with the known distance decision before updating the accumulator, so rejected candidates do not pollute the union. Store the resulting explicit U_H(a) row for this source and discard the source's difference buffers. The global table of all source/target metadata uses O(m^2 polylog m) bits per support, and global U_H uses O(m^3 polylog m), both original-scale span. Full-span fixed-track sweep costs O(m^7 polylog m) physical moves per source, including original-scale output shuttles for metadata and union rows; across m sources O(m^8 polylog m). All supports and coordinate choices are fixed finite, logarithmically many radii. The census is independent of the map policy and capacities.

For each K coarse block of side B, inherit the O(m^5 polylog m) physical pair-sliced generator for all m values of the unretained context for each retained pair. Regenerate its maps, preserve actual labels and loss metadata, filter to the block and spool <=m B^3<=m^3 assignments. Each pair occurs in O(M/B) K blocks, so total generation O(m^8/B polylog m). Sequential sort/merge with the stationary metadata table attaches the template keys, weights and missing-bit counts. Apply exactly the parent's frequency trimming, either on raw labels (r=0 alternative) or nonzero template identifiers per support and dyadic scale. Integer caps and tie rules unchanged. Each pass O(m^3 polylog m) sequential work/span, O(m^6 polylog m) physical. Across (M/B)^3 blocks, O(m^7 polylog m), including logarithmic scales. At fixed radius and capacity accumulate beta,delta_n, gamma,lambda_T and kappa_H exactly; kappa counts ALL maps before any trimming. Obtain eta_H from the union census. Integer score is

    m^6 Q = m^2*(representative count+heavy count)
            + narrow weighted loss sum
            + C^P*surviving template weight sum
            + sum_H min(m^3*|U_H|,Lambda*missing-bit sum_H).

All fields have O(log(m+2)) bits since exponents fixed. Evaluate the logarithmically many capacities/radii and constant-many policies/coordinates; total selection O(m^8 polylog m), original-scale span. Keep only winning identifiers and score, regenerate the same class census and marked spools for the worker. No global m^4 map or width-six exception array.

## 5. Template, envelope and union workers

Template search is exactly the preceding local directed-class worker with j as the canonical template key, and nonzero template assignments surviving the trim as references. For each projected six-coordinate coarse B-block, query the actual old and center raw rows on its free B-by-B square by explicit sort/merge. The center can lie outside the source interval and the actual representative set. Each source contributes at most C B^alpha nonzero rows; O(B^4) actual map entries. Root payload O(C B^(3+alpha) polylog B)<=O(m^3 polylog m); the global query/sweep cost O(m^8 polylog m) across all projected blocks. Install the cached root once adjacent to active root; copy locally for each private coarse choice. Original constraints are extracted using mobile scratch across original-scale stationary data. In local frames discard unreferenced rows, clip row quadrants and source/map coordinates, compact slots by sorting and merging. All persistent fields have local O(log(t+2)) width. No global key needed in descendants. A referenced nonzero row is exact positivity of the TEMPLATE guard on the tile, not a check of original satisfiability.

Inherit parent local work O(C^2 t^(6+2alpha)(1+log(t+2))^A) and the geometric active stack space. The same local density sum for R template tuples, rho=R/m^6, yields O(C^2 m^9 rho^epsilon(1+log(1/rho))^A) with epsilon=(3-2alpha)/6. Substitution X=C^P rho absorbs the capacity multiplier and local logs since C^2 rho^epsilon=C^(-epsilon)X^epsilon, and the negative power absorbs all fixed log C factors. Preparation remains O(m^(42/5) polylog m) at alpha=1 or O(m^(419/48) polylog m) at alpha=5/4, including the new m^8 census. The inherited full-scale costs and fixed product-alphabet simulation apply, with original-scale visited span.

Envelope/narrow branches are unchanged from the parent: keep marked B-sized K spools across nested b'=Theta(m^(3/5)) projected blocks, use the stationary width<=5 restriction tree, preparation O(m^(42/5) polylog m), local density exponent at least 1/5. All narrow evaluations use actual targets, never the approximate centers.

For a chosen source-only union correction, U_H is already stored as an explicit width-three bit relation of O(m^3) bits. Use b' largest dyadic with b'^5<=m^3. For each projected H block of side b', extract its b'^3 flags by sequential sort/merge with U_H. Build the inherited stationary width<=5 positivity tree, this time with three projected coordinates and O(t^3 local-log) writable original-record frames. O(m^6 polylog m) build per projected block via full-span sweep, total O(m^9/b'^3 polylog m). Reuse tree over all six private coarse coordinates. Extract all original records and padding via mobile O(b'^3 polylog m) scratch, total O(m^12/b'^6 polylog m)=O(m^(42/5) polylog m). No expanded width-six union. Local subtree extent O(t^3 local-log), moving original payload O(t^3 local-log), physical node cost at most O(t^8 local-log) (a conservative inherited bound). Positive full-node count at side t <=min((M/t)^9,|U_H|*(M/t)^6). Charge roots separately; descendants have positive parents. The dyadic sum with t^8 gives O(m^9 eta_H^(1/3)(1+log(1/eta_H))^A) by crossover t0=M/|U_H|^(1/3) and geometric exponents 1 and 2. Empty U_H skipped. This correction route has no global logarithmic factor in its density term. All original bits are checked at singleton.

## 6. Exact correction worker and log-weighted selection

The exact missing-bit correction has six projected coordinates and factorized membership

    E_H^-(a,p_c(a);x,y) =
       (1-F_H(a,x,y))*F_H(p_c(a),x,y)*
                          (1-F_H(j_H(a,p_c(a)),x,y)).

False on padding. The previous space-capped width-six worker (12a69b594fde7aced18f48ee42a6e82a5148bbac, Sections 3--7) applies with two small modifications: attach the center j to every actual pair-generated map record, and evaluate the third raw bit in the existing cache. There is no heavy mask or dependency on the B-scale trimming. For a retained pair, extract the stationary O(m^2 polylog m) metadata table using mobile scratch over original-scale span O(m^5 polylog m), sort/merge its O(m^2) map records locally against the table. This fits the inherited O(m^5 polylog m) per-pair cost. A projected block of side w holds <=w^4 actual source/context map entries, now each with two target fields, and <=m*w^2 raw bits for all real row digits. Both actual and center labels may be outside the source interval. The old factorized membership lookup remains O(w^4 polylog m) physical per candidate with mobile counters; a fixed third bit query adds only a constant factor. No assumption of random access. All original constraints, not template constraints, are retained.

If R=0 skip this exact branch. Otherwise rho=kappa_H=R/m^6, and choose sigma=max(1/m,rho)<=1 (each support's normalized density <=1). Inherit adaptive b=largest dyadic satisfying b^16 sigma<=m^8, b0=largest dyadic with b0^2<=m, so b=Theta(sqrt(m)*sigma^(-1/16)). Before allocating a tree count exact projected mass R_B using the factorized cache. If b^6 R_B>m^6 subdivide into b0-blocks; otherwise build the compact stationary tree whose extent is O(b^3 sqrt(R_B) polylog b)<=O(m^3 polylog m). The heavy fraction is <=sigma^(1/4). Neither count nor cap discards a model. Local frames and private alternatives reuse the stationary projected subtree, moving only original width<=3 records. The inherited preparation O((m^(33/4)+m^9 sigma^(1/4)) polylog m) and wide traversal O(m^9 sqrt(rho) polylog m) are unchanged by the third raw bit. To see preparation remains unchanged, its terms are m^11/b^4 (pair generation), m^10/b^4 (raw extraction), m^6 b^4 (count/build), m^12/b^6 (original extraction), m^9/b^3 (cleanup), with the same fallback fraction. The same local Cauchy estimate for positive projected subtree mass applies to E^- because it uses only exact cardinality and disjoint tiles, not its algebraic form.

Consequently with a fixed A0 absorbing all inherited global log powers the exact correction cost is bounded by

    O((m^(35/4) + m^9 rho^(1/4))*(1+log(m+2))^A0).

Here sigma^(1/4)<=m^(-1/4)+rho^(1/4) and sqrt(rho)<=rho^(1/4). The global log issue is NOT solved for arbitrary rho->0. Instead choose fixed integer D0>4A0 (and large enough to absorb the constant difference between log bases). Whenever the exact route is selected, Lambda*rho is its contribution to Q. Then rho^(1/4)*(1+log(m+2))^A0=O((Lambda*rho)^(1/4)). This is an integer-computable, conservative selection penalty, not a measured or optimized log exponent. Its existence follows from fixed inherited subroutine log exponents; no explicit numerical D0 or transition table supplied. If the union route is selected, its eta_H is the score contribution and the preceding local-log bound applies instead. This gives genuine adaptive selection between a low-width overapproximation and a sparse exact higher-width correction.

## 7. Complete bound and original clock

All branch densities, with the capacity multiplier for templates and the log penalty for exact corrections, are bounded by Q. There are fixed many supports. The strongest preparation exponent needed is 35/4=8.75 from exact correction fallback, exceeding 419/48 only slightly, and strictly below nine. For small positive Q, template exponents >=1/12, envelope/narrow >=1/5, union 1/3, exact 1/4 are bounded by a constant times the stated Q^(1/12) local-log term. All phases reuse original-scale O(m^3 polylog m) components. No global log m multiplies the complete Q-dependent term. Outside a small-score promise the exact branches still preserve correctness, or inherited exhaustive fallback can be used. No strict cubic bound claimed there.

On success recover actual latent digits and actual original pins, reconstruct fixed one-hot/OR/guard bits and emit n contiguous raw bits with physical halt head at first bit; exhaustion halts on blank. Inherited once-only O(m^4 polylog m) reconstruction. On Q->0 the derived time is o(m^9)=o(L^3). A fixed actual machine description of length ell receives >=L^3/2^ell moves at exact stage 3 ceil(log2 L) once eligible. Little-o eventually fits this allocation. No explicit ell, numerical threshold, compiled original-U machine or actual U-stage execution supplied.

## 8. Strict score separation: distinct directed rows with one-bit corrections

Modify the preceding exact-class separation to make even its actual directed strings distinct. For m=2^d let r0=floor(9d/10), q=2^r0, T=[m/2,m/2+q) (for large d, q<=m/2). Force the unique target f(c)=m/2 plus the r0 low input bits interleaved from c1 and c2, by the unary exclusion outside T and two binary supports checking the respective output features. As in the parent, every aligned K context cube of side B=2^floor(2d/3) has all q targets equally often for large d. All narrow g bits vanish at f(c). Choose g=0,K={1,2,3}. Put one wide H={0,4,5} and optional unary zero exclusions on other groups; no other cross supports.

Choose ell(d)>=4 tending arbitrarily slowly to infinity with ell<d, j=m/2^ell, zeta=j/m. Let h_a(x,y)=binary dot(a,x) XOR low bit(y). For a outside T, raw row is one on m/4<=y<m/2, equal to h_a on m/2<=y<m, zero elsewhere. For b in T, raw row is one on y<j, equal to h_b on m/4<=y<m/2, and additionally one at its private marker column (x=b-m/2,y=j), zero elsewhere. All markers are distinct and outside the shared band and middle/high regions. Every raw row distinct. This family is SAT for large m: choose nonzero contexts, a=f(c), nonzero x,y with y>=m/2, and other digits nonzero. Easy control; no hardness or complete primal graph claim.

For every outside source a, every target b in T has directed difference equal to the common band y<j plus its marker. Thus every target has a different nonzero directed class, but all these strings have pairwise Hamming distance two. The wide loss is D0'=m*j+1. For distinct outside rows directed loss is D_s=m^2/8; for distinct inside rows it is D_t'=m^2/16+1. For the latter two identities, the two distinct linear forms h_a,h_b of uniform x and the independent low y bit are independent, giving probability 1/4 of old zero/new one in the corresponding half or quarter region. The extra private marker gives precisely one more new bit for inside pairs. Target-to-outside loss nonnegative plus unary narrow loss m^2.

The actual unpenalized full-average greedy facility selects singleton f(c). Every target in T has the same summed wide loss (m-q)*D0'+(q-1)*D_t'. Target f(c) has zero narrow loss from all sources, every other target incurs positive narrow loss from source f(c). Any outside target has summed wide loss from other outside sources alone >=(m-q-1)*D_s, eventually larger than the total to f(c) because q/m,zeta->0. Thus unique first selection. An additional target in T improves only its own source by at most D_t'<m^2. An additional outside target improves only its own source by at most D0'<m^2, since D_s>=D0' eventually and inside sources incur unary loss. Subsequent marginal gains cannot increase. The best positive facility round is therefore exactly one representative. Beta=1/m, delta_n=0,

    delta_w=((m-q)*D0'+(q-1)*D_t')/m^3 ->0.

For arbitrary maps on this configuration every nonself replacement of an outside source incurs wide loss at least D0' eventually, and self fraction<=beta, so delta_w>=max(0,1-q/m-beta)*D0'/m^2. Choosing ell(d) extremely slowly increasing makes this a genuinely slow optimal wide-loss control under vanishing capacity. It is not a SAT time lower bound.

At radius r=2, for every outside source the target strings are all assigned to one center. The zero row cannot capture them since D0'>2, and an outside candidate string is zero on the common band, so its distance to each target is >2. When the first target center is chosen all target strings lie within radius two. For outside sources the single nonzero template satisfies C=1,alpha=1 cap on every cube, with no trimming. Inside sources contribute at most q/m heavy fraction. All template weights bounded by actual weight plus two, so lambda_T<=delta_w+2/m^2 for the sole wide support. The general union bound eta_H<=2/m, and exact correction kappa_H<=2/m^2. Therefore

    Q <= 1/m + q/m + delta_w + 2/m^2
                      + min(2/m,2*Lambda/m^2) ->0.

In the preceding exact class cover (and raw-label cover), every outside source has q equally frequent distinct nonzero directed classes at coarse side B, whereas the maximum cap is C B^(5/4)<=m^(83/96)=o(q). Thus it discards 1-o(1) of assignments for every outside source, uniformly over permitted alpha,C; the score cannot vanish on these generated maps. Unlike the parent control, exact directed quotienting no longer helps; one-sided near-row correction does. This is a strict separation on the designated actual generated maps and the previous two capacity options, not across other compressed groups or map policies, and not from every older solver. In particular the outside sources are forbidden by a unary original constraint, and this easy family may be solved by earlier routes. No computational hardness or complexity-class conclusion.

## 9. Executed host semantic regression

Standalone JS audit executed in tool runtime and committed with identical Node entry point; revised and rerun to add independent exact-route and extra-template controls. Twelve fixtures m=2,3 across six modes, 24 passes (full-average greedy and forced singleton maps), two designated wide supports (second active in mode five), B=2, radii 0,1,2, capacities 1,2 and alpha=1. Test radius and bit identities, exact one-sided weights, class trimming/caps, exact integer score selection (finite log penalty 4 rather than production Lambda), full original-model substitution recovery, compact template row clipping, local positivity, correction inclusion in union and expanded cardinalities across child partitions. Results:

    144 candidate comparisons
    11,364 radius checks
    35,794,596 directed bit partition assertions (including controls)
    576 tail checks, 4,646 cap checks
    242,340 full tuple checks
    125,874 successful substitutions
    1,522 narrow failures, 23,260 template failures recovered
    3,204 correction recoveries through selected union routes
    zero heavy or exact-route failures in main fixtures
    26,726 template-guard original model occurrences
    3,300 exact missing-bit original model occurrences
    9,516 union-guard original model occurrences
    101,400 local positivity checks, 199,680 local membership comparisons
    99,840 projected child choices, 8,224 slot relabels
    582 greedy residual checks.

Main greedy passes selected radius zero,C=1; forced passes prescribed radius two,C=1. Model counts are direct enumeration, not full recursive nine-coordinate model-set recovery. The projected recursive tests exercise template clipping and exact missing/union cardinalities, not the physical compact stationary width-six tree. No integrated heavy traversal or superlinear option tested in this cycle.

Independent private-marker controls at m=16,32,64 use q=m/2 and j=m/16 (finite fixed fractions, not asymptotic q,zeta), and check every outside source's exact distinct target classes, one approximate class at radius two, exact pair weights, <=1 missing marker per pair, exact union row count, unique first greedy facility and every second marginal for every possible target. Output [m,q,marker checks,outside union bits,greedy marginal checks,total union bits]:

    [16,8,64,56,120,56]
    [32,16,256,240,496,240]
    [64,32,1024,992,2016,992].

Null-template correction control has one missing bit despite zero template. Separate exact-route control at m=8 has exactly one actual missing bit, versus union expanded mass 25,088; score prefers exact route at finite penalty 4, and the original witness bit is checked. Separate nonzero-template control has both a missing and an extra bit; it verifies the full difference identity and one-sided recovery, not equality of template and true difference. All final assertions passed. The host uses indexed arrays/maps, direct enumeration and recursive objects. It does not execute all production choices, raw-label fallback, physical sort/merge/carry shifts, serialized tape frames, normalized encoder/verifier, compiled original-U transitions or exact stage. Independent mathematical review, Lean formalization and exact-head CI remain unconfirmed.

## 10. Disposition

Approximate directed classes permit distinct near-identical exception rows with exact missing-bit recovery. The source-only union route has a local-log density bound; the alternative exact width-six route explicitly charges its inherited global logs in the score. This covers polynomially small approximation errors even with arbitrarily slowly vanishing original wide loss, and small shared union support without a rate requirement. It leaves open approximation error that vanishes too slowly for exact recovery and produces dense correction unions, as well as arbitrary small average loss without a suitable template cover. Next investigate free-square-local approximation, or a multiscale decomposition of correction support that avoids the global logarithmic penalty. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
