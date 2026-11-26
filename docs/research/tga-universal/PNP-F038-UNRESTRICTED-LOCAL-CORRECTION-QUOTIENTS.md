# F038 — Free-square local correction quotients and certified overflow recovery

PNP_RESOLUTION_STATUS = OPEN. Parent 54e7a185c2ab2682e8ea720558ddd3a85019d84b (approximate difference covers). Conditional mathematical fixed-machine-existence/resource derivation using inherited original parsing, pair-sliced maps, fixed-track sequential sweeps, mobile carry shifts, adjacent spatial frames, width-four/five stationary restriction workers, and the unpruned original-record spatial stack (8a9bdda24d709b976b7cc939af47c7b188ed1451, without optional projection tests). Executed host semantic audit. Not compiled original-U transitions, independent review or Lean formalization. Parent combined statuses and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Main theorem and new score

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), actual selected negative cross-clause bits F_H of width one through three, and actual one-hot/OR/pin/guard extension. Choose compressed group g and three conditioning groups K. For generated contextual nonempty representative sets C_c and maps p_c(a) into them, beta=sum_c |C_c|/m^4 and delta_n,delta_w are the inherited weighted narrow and wide directed losses divided by m^6. Selected representatives map to themselves. Keep the previous finite map-policy family (full-average facility greedy and six-block-splice-penalized greedy with each distinguished context).

For a wide H={g,u,v}, with u,v outside K, write Z_H(a,b;x,y)=(1-F_H(a,x,y))*F_H(b,x,y). Use the parent's approximate center j_H(a,b) learned by deterministic Hamming-radius clustering (self first, then least unassigned target). The missing-bit guard on six actual projected coordinates is

    E(a,c,x,y)=(1-F_H(a,x,y))*F_H(p_c(a),x,y)*
                               (1-F_H(j_H(a,p_c(a)),x,y)).

For direct recovery set j_H(a,b)=a, so E=Z_H(a,p_c(a);x,y). This is also the parent's radius m^2 option: every directed string has length m^2, hence all are assigned to the zero center, with no nonzero templates or trimming. Let R=|E|, rho=R/m^6; padded digits make E false. Correction mass counts ALL map assignments, independent of template trimming, as in the parent.

Pad to M least power of two >=m; B largest dyadic with B^3<=m^2, so B=Theta(m^(2/3)). Enumerate dyadic capacities C with 1<=C<=m^(1/32). The new certificate is LOCAL to both context cube and free square. For each aligned projected six-coordinate cube D of side t<=B and each real source digit a in its source interval, count distinct NONZERO strings

    E(a,c; . , .) restricted to D's free square,
                  over real c in D's three context intervals.

If this count exceeds C*t for any a, call the projected cube overflowing. The count is of actual restricted missing-bit rows, NOT global classes, actual target labels, or joint signatures across supports. Stop at the FIRST overflowing cube on each dyadic path below a projected B-root. Empty cubes have no descendants to process. These first-overflow cubes are disjoint, and define the exact computable charge

    omega_C(E) = (1/m^6) sum_(first overflowing D) side(D)^6.

This uses padded cube volume with real-domain denominator, so omega<=64; padding does not itself create a nonzero row. The charge is not the fraction of actual missing bits lost to overflow, and not the sum of all overlapping failing cubes. No approximation error is discarded. At a first overflow abandon ONLY the recovery guard on that cube and search its full original constraints exactly. Thus every reported witness is still original, even when admitted by this deliberate enlargement.

The new correction route charge is

    J(E)= min_(dyadic C<=m^(1/32)) [C^13*rho + omega_C(E)].

It can be computed exactly during a PROJECTED-ONLY census before running the full nine-coordinate search, in O(m^8 polylog m) physical time and O(m^3 polylog m) span (proof below). Unlike the parent exact correction route, it needs no fixed power of log m multiplying rho. Add this route to the preceding portfolio. With the parent's template capacity C_T, alpha in {1,5/4}, P=13 or25, gamma heavy-assignment density, lambda_T surviving template density, and eta_H source-only union density, define

    Q_new = beta+delta_n+gamma+C_T^P*lambda_T
                 + sum_H min(eta_H, Lambda*kappa_H, J(E_H)).

Here kappa_H=rho_H is the actual missing-bit density, Lambda is the previous fixed log-power penalty, and each H chooses its correction route and local capacity independently. Keep all prior radius/policy/coordinate/template trimming options. Exact integer score m^6 Q_new; choose minimum and regenerate its data. In particular the score is pointwise no larger than the parent's score for identical maps/radius/template parameters. No claim of pointwise runtime dominance.

There is one fixed deterministic original three-symbol one-tape witness program correct throughout the family, whose charged bound for sufficiently small positive computed Q_new is

    T(m)=O(m^(35/4) polylog(m+2)
             + m^9 Q_new^(1/12)(1+log(1/Q_new))^A),
    visited span O(m^3 polylog m),

with fixed implementation-dependent A. If using just the direct route and no approximate template/old correction workers, minimize

    Q_direct = beta+delta_n+sum_H J(Z_H(a,p_c(a);x,y)).

For this separate fixed program,

    T(m)=O(m^(42/5) polylog(m+2)
             + m^9 Q_direct^(1/6)(1+log(1/Q_direct))^A),
    visited span O(m^3 polylog m).

Both implications Q->0 give T(L)=o(L^3), eventual exact cubic-stage witness inclusion, with no convergence rate on the new local quotient route. The result does not establish that arbitrary vanishing beta,delta implies vanishing first-overflow charge. All maps, classes, radii, capacities and choices are computed by the finite policy family; no supplied map or advice.

## 2. Root construction without global width-six materialization

Inherit the parent's pair-sliced generator O(m^5 polylog m) physical for one retained conditioning pair and all m values of the third digit. Enumerate K coarse blocks of side B first, regenerating pairs in the retained intervals and filtering the remaining digit to its interval. A pair occurs in O(M/B) blocks; total O(m^8/B polylog m). Hold a block spool with <=m*B^3<=m^3 actual map records, actual targets, representative flags, and (for correction) learned center labels and loss metadata. Join the O(m^2) stationary source/target center table using sequential sort/merge, O(m^6 polylog m) physical per K block. The full class/union census for approximate centers is inherited O(m^8 polylog m) per radius, original-scale span. The direct program does not need that census. No global m^4 map. Count R for each H by summing the exact pair directed or missing-bit weights over all actual assignments in the spools.

For one projected B-root on (a,c1,c2,c3,x,y), extract its <=B^4 valid source/context map entries and the restricted B-by-B raw bits for ALL m real row digits, including actual targets and center labels outside the source interval. Emit explicit zero/one records, zero on padded free columns. Sorting/merging with the original raw input and scanning the marked K block spool takes O(m^3 polylog m) sequential bit work/span. Sort the root map records by source and target, and process sources one at a time in increasing order. Use the following exact sequential routine for one source a:

* Copy its restricted old row and extract its used target labels with their actual center fields. From the restricted raw cache, obtain both target and center rows by exact sorted query/merge. There are at most m distinct actual targets for this source; the number of row requests including repeated centers is at most 2m. Sorting and copying whole fixed-length B^2-bit strings, including duplicating a center row for its requests, takes O(m B^2 polylog m) sequential bit steps and span. No indexed row lookup. The source's map references have at most B^3 entries, which is <=m B^2. Read the source's part of the ordered map spool sequentially, not the whole spool once per source.
* Compute each requested E row bitwise (or direct Z by center=a), sort its exact B^2-bit strings lexicographically, group equal strings, omit all-zero strings. Count actual nonzero classes. If their count exceeds C*B, return an overflow header, discard temporary output. Otherwise emit one row per class and translate the actual map entries to dense local source-specific row slots. The center/target labels no longer needed in local frames. There is no equality inference across sources. The row dictionary consists of actual restricted strings, not labels used as substitutes for actual representatives.

All temporary row strings for one source occupy O(m B^2 polylog m) bits. Process at most B sources, so the per-source work sums to O(m B^3 polylog m)=O(m^3 polylog m). Partial emitted root dictionaries before testing the next source are bounded by O(C B^4 polylog m); one can finish the source's count before appending any new dictionary. This also fits since C<=m^(1/32). Map spool, raw cache, one-source temporary buffers, and bounded partial output together have O(m^3 polylog m) span. In particular an overflowing root never requires allocating its entire six-coordinate relation or full uncapped dictionary. Global identifiers are used only in these root preparation routines.

Full-span fixed-track sweep simulation charges O(m^6 polylog m) physical moves per projected block. Across (M/B)^6 projected roots this is O(m^12/B^6 polylog m)=O(m^8 polylog m). Map regeneration, joins, and extracting raw bits are within the same bound. Install each successful root cache once adjacent to the reusable active interval, with even original-scale per-bit shuttles O(m^3 C B^4 polylog m) per projected block, O(C m^9/B^2 polylog m) total. Overflow roots need only the overflow header. Reuse the cache for all private coarse choices or for a projected-only census. These operations do not store global E bits, global local-quotient tables for all roots, or an unbounded stack of query buffers.

## 3. Exact restriction, child recoding, and cap checks

A nonoverflow side-t frame contains at most t*min(C*t,t^3) nonzero rows of t^2 bits, at most t^4 actual source/context map entries referring to them, and (in full search) O(t^3) original width<=3 singleton records including padding. Include local counters, delimiters and scratch. Root sets C_local=min(C,t^2); at a child u=t/2 set C_local'=min(C_local,u^2). This is exactly min(C,u^2) and the effective cap C_local'*u is min(C*u,u^3). Since at most u^3 contexts exist per source, it is equivalent to testing the actual C*u cap. Thus no global log C or log m fields at small scales. All persistent local fields are O(log(t+2)) bits, including row IDs (at most t^3 per source).

Test positivity by a nonempty map list with a nonzero referenced row; zero/unreferenced rows were omitted. Every such row gives a real guarded projected tuple, because source/context entries and free one bits have no padding. For each child vector restrict four map coordinates, keep only referenced rows, clip source key and the free quadrant, then INTERN AGAIN by exact content per source. Drop locally zero rows and their references, densely relabel slots, and update all surviving map records. Previously equal parent rows stay equal when restricted, so parent equality never loses information needed for the child. Previously different rows may coalesce, or become zero. This computes exactly the nonzero row classes of the actual restricted E in the child, even though the actual targets are no longer available. No global label lookup, hash collision, or assumption that local class counts equal global class counts. A row zero in a parent free square stays zero in every child; removing its map references is safe. If a child exceeds its cap return its overflow flag without descending further. The overflow decision depends only on the projected six coordinates and E, not on private original records.

The child candidate buffers are no larger than the parent payload: restriction cannot increase bit count or number of references before interning. Use temporary parent-size scratch within the parent-local interval, then append only a bounded child frame (or overflow header). No assumption of an actual-size lower bound for the child. Sequential clipping, content sorting, map joining and recoding take O(C*t^4 polylog(t+2)) bit work and span for a fixed child. Use inherited local sweeps and adjacent per-bit shuttles over that extent. The physical charge per nonoverflow node is

    O(C^2*t^8*(1+log(t+2))^A),

including all fixed children (64 for census or 512 for full search), testing child overflow, clipping the original lists, setup/cleanup and return. At each recursion only one child is appended next to its stationary parent, popped before the next. All active frame extents sum geometrically, O(C B^4 polylog B). Local child offsets stored in the parent, no global addresses or ever-growing track alphabet. Fixed finite product components use constant-width blocks over actual 0,1,2. No extra physical head or random access. At singleton a true guard and no forbidden original record give exactly a restricted original model.

## 4. Certified overflow census is subcritical

For each projected root build the exact dictionary or overflow header as above. Traverse only the six projected coordinates, omitting private coordinates and original constraints. At overflow add t^6 to an integer counter and stop that path. At zero flag stop without charge. At nonoverflow positive node visit the 64 projected children. The census visits each projected cube at most once for a fixed H,capacity and map choice. The reported omega is exact: the first-overflow projected cubes form a disjoint family partitioning their union, and their padded volume is exactly the sum of t^6. Empty ancestors cannot hide a later overflow (all child strings would be zero). Larger C can only shrink this union: every path that passes the smaller cap also passes the larger cap, and if a larger-cap first overflow occurs then that path either already overflowed earlier for the smaller cap or overflows there. Hence omega_C nonincreasing. There is no assumption that the whole weighted score is monotone, since C^13*rho increases.

Even ignoring positivity and overflow pruning, the census local physical work across scales is bounded by

    O(C^2 * sum_(t<=B dyadic) (M/t)^6*t^8*(1+log(t+2))^A)
       = O(C^2*m^6*B^2 polylog m).

This is O(m^(22/3+1/16) polylog m) at the production cap, below m^8. This is the key distinction from a full nine-coordinate search: a potentially expensive local class test is performed ONCE per projected cube, not once for every private cube. Root preparation dominates the census at O(m^8 polylog m). No global storage of the first-overflow cubes is needed: sum their volumes in a counter at root level. On popping the projected stack propagate an integer local volume subtotal <=t^6 in O(log(t+2)) bits; combine root subtotals at original scale. For an overflowing root add its volume directly. Root preparation reuses data, then discards its cache and local stack. The entire census span O(m^3 polylog m).

At fixed radius, actual E independent of template trimming, so the correction census can be reused across template parameters, or recomputed for them with only logarithmically many repeats. Enumerate logarithmically many dyadic C, fixed many supports, all fixed coordinate/policy choices, and logarithmically many radii and template capacities. All original-scale preparations still O(m^8 polylog m), except the inherited branch-specific search preparation below. Compare exact integers

    m^6 * (C^13*rho + omega_C) = C^13*R + sum_(first overflow D) t_D^6.

The normalization by real m^6 is chosen to avoid any additional rational arithmetic. All integers have O(log(m+2)) bits, with fixed exponent 13. Add options to the parent's score and select deterministically; save only winning IDs, branch modes, capacities and scores, regenerate identical data for search. This is actual computable selection, not a minimum over unobserved overflow masses.

## 5. Full witness search and overflow enlargement

For each selected local quotient branch regenerate its root dictionaries under the winning parameters. Combine each projected root with every private coarse choice on the other three coordinates. For each full coarse tile extract ALL original selected width<=3 singleton records and padding units via inherited mobile O(B^3 polylog m) scratch scanning original-scale stationary data. Cost O(m^3 B^3 polylog m) per full tile. For a nonoverflow root install the active root representation via LOCAL shuttles from its adjacent cache, O(C^2 B^8 polylog m) per full tile. All root checks, clearing and counters fit. Across (M/B)^9 tiles, these terms are

    O((m^12/B^6 + C^2*m^9/B) polylog m),

at most O(m^(403/48) polylog m), below 42/5. Root generation O(m^8), installation and K-block regeneration are also below 42/5. Overflow root extraction is charged in the same sum. No global scan during a local recursive transition.

For the ordinary nonoverflow worker enumerate full child vectors; original records are clipped and translated, preserving the exact original predicate on each full tile. The first time a projected overflow header is reached, instead of further evaluating the recovery guard, run the inherited unpruned ORIGINAL-record adjacent stack in that full tile. Retain all original constraints, including all g-containing ones and padding. There is no claim that every satisfying tuple in such a tile is an actual E tuple; this is an intentional safe enlargement. A successful original tuple outside E may be returned. If an E tuple satisfies the original constraints then it survives either the exact guarded path or the unpruned overflow search, so no witness lost. Every original satisfying tuple in the enlarged branch is accepted if exhaustive search is used. The branch predicate is original satisfiability AND (E OR membership in the union of first-overflow projected cubes). Empty projected tiles can be discarded because they contain neither E nor a later overflow. Early stopping can only reduce cost.

This integrates into the parent's substitution existence proof unchanged: a successful replacement has an original witness in the representative envelope; a failed heavy replacement in that envelope has its original tuple there; a newly violated narrow support gives its exact narrow exception, and a newly violated wide support gives the surviving template guard or a missing-bit correction. The selected correction route covers all actual missing bits (regardless of heavy flags). With direct recovery no template/heavy branch is needed beyond the representative envelope, and every wide exception is directly guarded by Z or its overflow enlargement. Original constraints are never replaced by template rows or correction centers. All actual pin, auxiliary and output reconstruction unchanged. On success restore local offsets while unwinding, reconstruct original digits and actual pin/one-hot/OR/guard bits, emit contiguous n raw bits with physical halt head at first bit; exhaustion halts on blank. Once-only O(m^4 polylog m). No new external higher-width clause or changed verifier.

## 6. Rate-free physical charge for overflow and nonoverflow work

At a side-t overflow full tile the original-record stack uses O(t^3 polylog t) adjacent frame span. Without optional projection tests, its local node work at side s is O(s^6(1+log(s+2))^A0): restrict and translate the original O(s^3) records and shuttle them across adjacent intervals of the same order. There are at most (t/s)^9 nodes per scale. Therefore

    sum_(s<=t dyadic) (t/s)^9*s^6*(1+log(s+2))^A0
       = O(t^9),

since the local sum over s=2^j of 2^(-3j)*(1+j)^A0 converges. This bound has NO global log m multiplier and no log t multiplier on t^9. Initialization of an overflow child's original list and discarding its temporary guard data are charged to the nonoverflow parent or mandatory root initialization. The active original-record fallback is adjacent to its stationary ancestors and fits the same original-scale span. Return without retaining explored subtrees.

For a first-overflow projected cube of side t, there are at most (M/t)^3 private-coordinate cubes at that scale across all full root/private choices. Thus ALL unpruned fallback work is at most

    sum_(first overflow D) (M/t_D)^3*O(t_D^9)
        = O(M^3*sum_D t_D^6)
        = O(m^9*omega_C).

This counts first-overflow cubes once, not all failing scales. No multiplication by the number of levels. The disjoint projected partition is crucial. Private original pruning, if any, can only reduce this bound. Root overflow is included. The charge measures actual enlarged projected volume, not missing-bit density alone.

For nonoverflow work write R=|E| and rho=R/m^6. Exact positivity on every nonoverflow cube implies positive full-node count at side t <=min((M/t)^9,R*(M/t)^3). Nonroot tests, including child overflow tests, charged at positive parents. Mandatory roots separately charged. With local work O(C^2 t^8 (1+log(t+2))^A) the dyadic sum is bounded by

    O(C^2*m^9*rho^(1/6)*(1+log(1/rho))^A).

For R>=1 split at t0=M/R^(1/6); the two geometric tails have exponents 1 and 5 and absorb all local log growth. Empty E has no positive descendants and no overflow. Set X=C^13*rho. Then C^2 rho^(1/6)=C^(-1/6)*X^(1/6), and log(1/rho)=log(1/X)+13 log C. The negative power absorbs every fixed log C power for X sufficiently small, uniformly in C. Consequently the new route's total physical time for small positive charge J_C=X+omega_C is

    O(m^(42/5) polylog m
       + m^9 [ X^(1/6)*(1+log(1/X))^A + omega_C ]).

Zero X handled separately. Since omega_C<=J_C and X<=J_C, this gives the desired rate-free density term with exponent 1/6. No global logarithm multiplies omega or X. The direct program also searches the representative envelope and exact narrow exceptions using the inherited width-four/five stationary worker with preparation O(m^(42/5) polylog m), density exponent >=1/5. Its scheduling uses the same B-sized K spools across nested b'=Theta(m^(3/5)) narrow projected blocks. The full portfolio also retains the parent's template and original union/exact correction workers, with preparation exponent at most 35/4 and smallest density exponent 1/12. All branch counts fixed, all components reused within O(m^3 polylog m) visited span. This proves the bounds of Section 1 conditional on inherited physical routines.

For Q->0 the time is o(m^9)=o(L^3). The fixed actual machine of description length ell receives >=L^3/2^ell transitions at exact stage 3 ceil(log2 L) once eligible; the little-o bound eventually fits. No explicit compiled description length, numerical threshold or actual U-stage execution supplied.

## 7. New arbitrary-slow criterion and null-template separation

For any sequence of generated maps and correction predicates with rho_H->0, suppose for each H

    lim_(C->infinity dyadic) limsup_(m->infinity) omega_C(E_H)=0.

Fix a finite dyadic C with limsup overflow arbitrarily small; eventually it satisfies the cap, and at this FIXED C the term C^13*rho_H tends to zero. Take the computed minimum before taking limits. Thus J(E_H)->0 without any prescribed rate. In particular if all local nonzero class counts are at most a fixed C0*t at every t<=B, choose a fixed dyadic C>=C0 and overflow vanishes identically. For the direct program combine this with beta,delta_n,delta_w->0 on generated maps to obtain Q_direct->0. The full portfolio contains this null-template candidate. There is no assertion that arbitrary small average loss forces the displayed tightness of overflow volumes. The certificate allows high global class diversity and even local cap failures if their first-overflow union volume is small.

Here is a family showing the new correction condition can hold when BOTH prior correction charges fail for the SAME null-template candidate, and for actual greedy maps with arbitrarily slowly vanishing wide loss. It is not a separation from the parent's entire adaptive solver across other radii, choices or policies.

Let m=2^d, B=2^floor(2d/3), N=m/B. Partition the free x-coordinate into N aligned intervals of side B. For each interval i choose a permutation pi_i of the m labels. Let j=m/2^l with l tending arbitrarily slowly to infinity, 1<=l<d, and zeta=j/m. On the sole wide H={0,4,5} put

    F_H(a,x,y)=1{ (y - pi_floor(x/B)(a)) mod m < j }.

For any distinct a,b their forbidden circular intervals have length j. In each block the directed loss in y is at most j, exactly j if the intervals are disjoint. There exist permutations such that EVERY distinct pair has disjoint intervals in at least N/2 blocks for all sufficiently large m: choose permutations independently uniformly for an existence proof. For fixed a!=b, overlap probability at most 2j/(m-1)<=3*zeta. The probability of overlap in more than N/2 blocks is at most 2^N*(3*zeta)^(N/2). Multiplying by m^2 still tends to zero as N>=m^(1/3) and zeta->0. Fix any such permutations for each input. The worker is deterministic; no randomized advice or permutations supplied beyond the original constraint bits. Therefore all distinct ordered pair losses satisfy

    (zeta/2)*m^2 <= |Z(a,b)| <= zeta*m^2.

The sum of wide losses to a fixed target is independent of that target, since every block contains a permutation of all interval starts. This additional identity is not needed for the greedy bound. The raw union over all targets covers every column.

For concreteness choose g=0,K={1,2,3}. One may force a designated nonzero target f(c) by the same unary high-bit exclusion and two binary interleaved-bit constraints as in the parent; take the entire high-bit-one target set, with low bits taken alternately from the low bits of c1 and c2. At f(c) all g-containing narrow bits vanish. Optional unary zero exclusions on other groups. No further cross supports. This is SAT for large m (take a=f(c), nonzero x, y outside its forbidden interval, other digits nonzero). Easy control, not a complete-primal-graph or hardness construction.

The competitor singleton C_c={f(c)}, p_c(a)=f(c) has beta_*=1/m, delta_n,*=0 and delta_w,*<=zeta. By inherited full-average greedy marginal comparison the ACTUAL unpenalized generated maps for this coordinate choice have beta+delta_n+delta_w<=38/sqrt(m)+1/m+zeta (the earlier sharper logarithmic capacity bound also works). No need to claim greedy selects exactly a singleton. Since self assignment implies membership in C_c, every map satisfies

    delta_w >= (1-beta)*zeta/2.

Take l=max(1,floor(log2(log2(d+2)))) eventually, so zeta*(log m)^D diverges for every fixed D>0. The actual generated maps thus have genuinely slow wide loss under vanishing capacity, not just an inefficient prescribed map.

At null-template radius m^2 (also radius m*j suffices), all actual pairs map to zero center, all template mass and trimming vanish, E=Z. The source-only union contains exactly all old-zero columns for each source, hence eta=1-zeta. The previous exact correction charge Lambda*kappa=Lambda*delta_w does not tend to zero for this sequence. Both previous correction options fail to yield a vanishing charge for this candidate.

But at every aligned free square of side t<=B the x interval lies within ONE x block. Rows are constant in x there. As the interval start in y runs around the circle, each of the t local y bits toggles at most twice, so at most 2t+1 distinct raw traces occur. Multiplying by the fixed old-zero mask for each a cannot increase the number of distinct strings. Thus for ANY map, any source and any context cube the nonzero restricted E classes number at most 2t+1<=3t. At fixed dyadic C=4 every first-overflow charge is identically zero. Consequently

    J(E) <= 4^13*delta_w -> 0,
    Q_direct <= beta+delta_n+4^13*delta_w ->0.

This proves a strict relaxation of the correction-route sufficient condition at the null-template candidate, even for actual generated low-capacity maps whose wide loss vanishes arbitrarily slowly and whose source-only union stays dense. Other radii or older workers may solve these easy instances; no full solver separation or lower bound on SAT time is claimed. The novel resource saving is local equality of free-square traces, not global equality or polynomially small error.

## 8. Executed host regression and limitations

Standalone JS audit executed in the tool runtime and committed with Node entry point. Twelve fixtures m=2,3, six constraint modes, 24 map passes (full-average greedy and forced singleton maps), each tested with direct center=a and prescribed correction center=0, yielding 48 full passes. B=2,C=1 (finite test settings, not production). Construct exact root rows, intern by source and content, clip/re-intern children, omit zero rows, compare exact local class sets/overflow decisions/positivity with direct enumeration, check first-overflow cubes disjoint and their expanded volume exactly, compare complete full-model set with original AND (E OR first-overflow membership). The prescribed center=0 is a semantic correction control, not necessarily an actual parent radius choice. Recovery checks include ordinary representative and narrow routes, plus one separate g-containing binary in mode five checked by its direct bit when the wide support does not fail. Full test counters:

    1,756 root quotient builds, 36,480 projected child builds
    4,108 exact nonzero map-reference checks, 8,696 zero rows omitted
    16 exact local row merges
    8 overflowing root builds, 16 overflowing child builds
    179,584 exact local membership comparisons, 38,212 positivity checks
    128,512 first-overflow disjointness/volume checks
    484,680 direct full-tuple checks
    251,748 successful substitutions
    3,044 counted narrow failures, 23,548 direct and 23,548 correction/template failure checks
    12,312 full coarse roots, 2,132,992 full child choices
    33,060 exact enlarged-branch model occurrences in main fixtures
    582 greedy residual checks.

The main fixtures do not overflow; separate m=4 controls exercise both first-overflow roots (B=2) and first-overflow children (B=4) with three distinct nonzero rows in side-two cubes, C=1. Both yield eight first-overflow cubes of total padded volume 512, with 363 projected tuples admitted only by abandonment and satisfying the original wide bit. Full integrated host overflow search includes extra original private constraints and recovers exactly 16,128 original model occurrences in each case, all by fallback (32,256 total). Direct model-set equality checked. The host fallback enumerates local full tuples, not a physical original-record DFS. Independent local-merge control with distinct global raw rows yields 16 local merges, R=106, no overflow. A separate capacity census at B=4 produces [C,R,overflow volume,m^6 route score]=[1,85,512,597],[2,85,0,696320],[4,85,0,5704253440], verifying monotonic overflow and nonmonotonic weighted score. Actual source-only union count is four, expanded charge 256; portfolio chooses 256 over the local or finite log-weighted route. Initially the finite union charge was assigned rather than counted; corrected to direct union recount, reran. Independent sparse-map control R=1,overflow=0, expanded union charge 256, finite log-weighted charge 100, selects local route charge 1.

Finite interval-permutation controls at [m,B,j]=[16,4,2],[32,8,2],[64,16,4] use deterministic seeded permutations, check every aligned free square through side B, raw trace count <=2t+1, exact pair loss upper bound and equal summed loss over targets, coverage of every column by some target. Results [m,B,j,trace checks,max trace/side,min distinct pair loss,summed target loss,column union checks]:

    [16,4,2,336,2,20,448,1024]
    [32,8,2,1360,2,48,1920,4096]
    [64,16,4,5456,2,128,15360,16384]

These finite controls do not assert the asymptotic all-pairs half-disjoint probability estimate (the first two minimum losses are smaller than the corresponding half-loss bound). The latter is a mathematical existence argument for sufficiently large m. No all-context greedy generation test on that asymptotic family, nor experimental inference of slow convergence. All final regression assertions passed.

The host uses direct indexed arrays/maps, explicit enumeration, recursive objects and full temporary root dictionaries in small fixtures. It does not execute the bounded one-source sequential physical root builder, serialized tape frames, actual carry shifts, all production policy/radius/capacity choices, the parent template worker or stationary narrow/envelope worker. No measured physical transitions, normalized encoder/verifier integration, compiled original-U description, exact stage, independent review, Lean formalization or exact-head CI confirmation.

## 9. Disposition

Free-square local quotienting replaces global exact class identity by exact restrictions on actual six-coordinate dyadic tiles. Certified first-overflow volume is computable via a projected-only traversal, and unpruned original recovery on those tiles has a rate-free physical volume charge. This adds a third correction route and, in the null-template case, a direct wide worker without global log-weighted loss. It handles arbitrarily slowly vanishing actual correction mass with dense global union when local overflow volumes vanish or are uniformly tight. Remaining obstruction: arbitrary low-loss generated maps may have high local row diversity at many scales, and the first-overflow volume need not vanish by any argument here. Next investigate local overflow splitting by free-column geometry or alternative exact compressed representations with a computable subcritical census. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
