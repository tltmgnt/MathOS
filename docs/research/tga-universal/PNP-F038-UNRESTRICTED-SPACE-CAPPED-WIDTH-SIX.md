# F038 — Space-capped direct width-six recovery by adaptive coarse refinement

PNP_RESOLUTION_STATUS = OPEN. Parent 6782138981e1dc2c544582f180b4e64f45150aca (sparse width six). This is a mathematical machine-existence/resource derivation conditional on the inherited fixed-track parsing, mobile carry-shift, pair-sliced generation and compact stationary tree bounds. Executed standalone semantic and abstract-layout regression, not compiled original-U transitions, Lean proof or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push CI remains unconfirmed.

## 1. Result and exact scope

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), actual selected negative cross-clause bits F_H on supports of width 1..3, and the fixed one-hot/OR/pin/guard extension. Choose one compressed group g and three conditioning groups K, with contextual sets C_c nonempty and maps p_c(a) into C_c. Use the parent's full average weighted directed loss d_H,c(a,b), weighting each free-context loss by m^(2-|H minus ({g} union K)|). Define beta=sum_c |C_c|/m^4 and delta=sum_(c,a,H containing g) d_H,c(a,p_c(a))/m^6. The full loss splits into delta_n and delta_w, according to whether |H union K|<=5 or equals six.

For every fixed 0<epsilon<=1, if some g,K and contextual sets/maps admit beta_*=O(m^(-epsilon)) and delta_*=O(m^(-epsilon)), ONE fixed deterministic original three-symbol one-tape witness machine, correct throughout the family, attains

    T(L)=O(L^(3-epsilon/30) polylog L),
    visited span = O(L polylog L).

Thus it eventually fits the exact cubic stage on the promise. No supplied sets, maps, coordinates, score or decay exponent. In contrast to the parent, the construction needs no expanded O(L^(5/4) polylog L) span. It recovers the original-scale O(m^3 polylog m) bound while retaining the same polynomial cutoff for full average loss, including genuine width-six exceptions with dense lower-dimensional projections.

More precisely, with computed sigma=beta+delta, for 0<sigma<=1 the charged total time is

    O((m^(42/5) + m^9 sigma^(1/5)) polylog(m+2)).

For the wide branch preparation alone a sharper estimate is

    O((m^(33/4) + m^9 sigma^(1/4)) polylog(m+2)),

plus O(m^9 sqrt(rho) polylog(m+2)) wide traversal for its actual exception density rho. These are upper bounds, not observed transition counts. The global logarithmic factor is still present. Arbitrarily slowly vanishing full average loss alone is NOT yet proved sufficient. The previous projected local-log theorems remain separate descriptions in U. Outside the promise this new worker remains exact with O(m^9 polylog m) time and the original-scale span, not necessarily exact cubic or even an additive constant stage bound from this worker alone.

## 2. Retain adaptive selection and exact recovery

Run the parent's full-average greedy policy on each of 504 choices g,K. In each context, greedily add the unused representative minimizing the summed residual weighted loss, then choose the positive round minimizing k*m^2+F_k, with deterministic ties. The inherited marginal-gain comparison with a competitor of size h gives F_k<=F_*+37m^3 exp(-k/h). Taking k=ceil(sqrt(h*m)), averaging over all contexts and minimizing across choices gives

    sigma <= 38 sqrt(beta_*) + 1/m + delta_*.

The selected score is the integer Q=m^6 sigma divided by m^6. Every context has at least one representative, so sigma>=1/m. Keep only the winning choice/score in the first pass and use the inherited pair-sliced generator to regenerate maps in O(m^5 polylog m) physical steps for all m contexts of one retained pair. Full selection, raw parsing, actual pin extraction and distance caches take O(m^7 polylog m) original moves and O(m^3 polylog m) span, as in the parent. Nothing in this selection depends on epsilon.

For each winning map define S={(a,c):a in C_c} on {g} union K and E_H on H union K by old raw bit zero and replaced raw bit one. All branches retain every original clause and impose membership of the relevant projection in S or E_H. A satisfying tuple either remains satisfying after substitution, and its image is in S, or a newly violated support contains g and places the original tuple in E_H. Conversely every branch witness satisfies all original constraints. There are at most 38 branches. This preserves satisfiability and valid witness existence, not necessarily the full model set. The sum of normalized exception densities is delta by the weighted counting identity. Use the inherited shared-context stationary width-four/five worker for S and narrow E_H: O(m^(42/5) polylog m) preparation, O(m^3 polylog m) span, and O(m^9 sigma^(1/5)(1+log(1/sigma))^A) density cost for sufficiently small sigma. The new work concerns each wide E_H separately. The external normalized clause width and U clock do not change.

## 3. Adaptive coarse width and a certified cap

Pad all latent digit domains to M, the least power of two >=m, with unary negative exclusions for padding. The allowed exception predicate is false when a projected digit is padding. Set b0 to the largest dyadic integer with b0^2<=m. For 0<sigma<=1 choose b to be the largest dyadic integer satisfying

    b^16 Q <= m^14.

Equivalently b^16 sigma<=m^8. Because 1/m<=sigma<=1, b0<=b<=m^(9/16), b divides M, and

    b=Theta(sqrt(m)*sigma^(-1/16)),
    b0=Theta(sqrt(m)).

The machine computes b by repeated doubling and fixed integer arithmetic, using only polynomially bounded integers of O(log m) bits. If sigma>1 choose b=b0 instead; no density claim needed in that case.

For a wide support H={g,u,v}, its exact allowed relation E_H has six coordinates (a,d,e,t,x,y) with (d,e,t) on K and (x,y) on u,v. Let R=|E_H| and rho=R/m^6<=sigma. For each aligned projected coarse block B of side b, compute its EXACT allowed count R_B by the factorized predicate, before allocating any restriction tree. Call the block heavy if

    b^6 R_B > m^6.

A light block is processed at side b; for a heavy block, discard its coarse caches after counting and enumerate its dyadic subblocks of side b0, processing each separately. No tree is allocated for the heavy coarse block itself. Because b0^12<=m^6, every fallback block B' satisfies b0^6 R_B'<=b0^12<=m^6 even if completely allowed. If b=b0 the heavy case cannot occur. This is an exact deterministic certificate, not a probabilistic occupancy estimate or a resource guard that discards models.

The inherited compact tree bound at side w with r>0 entries is O(w^3 sqrt(r) polylog(w+2)); a zero block needs only a constant-size header. Therefore every tree actually built occupies O(m^3 polylog m) blocks, by the cap w^6 r<=m^6. This applies to its complete stationary subtree including reserved original-record frames and compact zero child headers, not just its list of allowed entries. The local builder caches and all original-scale data also fit O(m^3 polylog m). A constant factor times this span suffices for the simultaneous fixed reusable components. We do not assert a numerical tape-length cap m^3 without logarithms or constants.

## 4. Heavy block census and why the scale is chosen

Let h be the fraction of projected b-blocks that are heavy, counting padded blocks in the denominator. Disjoint projected blocks partition the padded six-coordinate domain, so their allowed counts sum to R. A heavy block has R_B>m^6/b^6, hence

    #heavy <= R*b^6/m^6,
    h <= R*b^12/(m^6*M^6)
       <= rho*b^12/m^6
       <= sigma^(1/4).

The last step uses rho<=sigma and b<=sqrt(m)*sigma^(-1/16). Empty projected blocks are light. The number of fallback projected blocks is exactly #heavy*(b/b0)^6, which equals h*(M/b0)^6. These identities charge only the heavy portion, not a full repeat of the smaller-scale search. They require no assumption on spatial distribution of E_H.

To explain the exponent, write b approximately sqrt(m)*u. The leading initial pair-generation cost is m^9/u^4. The heavy fraction is at most sigma*u^12; the leading fallback cost is proportional to this fraction times m^9. Balancing these upper bounds gives u=sigma^(-1/16). The dyadic choice changes only constants. This balances two resource upper bounds; it is not a lower bound on other possible adaptive scales or an assertion of globally optimal runtime.

## 5. Count and build using bounded physical caches

Inherit the parent's factorized predicate

    E(a,d,e,t,x,y)=(1-F_H(a,x,y))*F_H(p_(d,e,t)(a),x,y),

with rejection of padded digits. For a projected block of side w (either b or b0), collect only its valid map entries (a,d,e,t), at most w^4, and all raw row bits F_H(z,x,y) for real z and its two free intervals, at most m*w^2. Representatives outside the source interval MUST be included. Since w>=b0>sqrt(m)/2, both caches occupy O(w^4 polylog m) blocks; w<=m^(9/16) implies w^4<=m^(9/4), below m^3. The pair generator and stationary original data remain in their original-scale region while assembling this cache. Regenerate each real retained pair inside the block once, copying its relevant O(w^2) entries with original-scale shuttles before discarding the pair spool. O(m^5 polylog m) physical moves per such pair occurrence, since m^3*w^2<=O(m^5). Extract the restricted raw row cache by mobile carry-shift over the original-scale stationary span in O(m^4*w^2 polylog m) moves per block, including explicit zero bits.

Before writing a projected root tree, enumerate the w^6 candidates and evaluate membership from the two caches. As in the parent, a mobile query counter and aligned sequential scans bound each lookup by O(w^4 polylog m) physical moves. Thus exact count takes O(w^10 polylog m). Test the integer cap. For a light block, repeat membership as needed to build its compact preorder tree with positive node frames and compact zero headers; the inherited builder's worst-case time is also O(w^10 polylog m). This accounts for O(w^6 log(w+2)) candidate evaluations across dyadic levels and shifting the mobile O(w^4 polylog m) cache along the serialized tree output. Crucially the tree is emitted ONLY after the exact count certificate guarantees bounded extent. The cap also guarantees that the builder's cache, output, stack and temporary marker margins fit original-scale span at all times. Do not first build a large tree and then reject it. For a heavy block erase its caches and restart the same routines on each b0 subblock. Both counting and generation use exact raw bits with no free random access. Empty roots can be skipped after counting. A fixed number of tracks, with constant-width binary block encoding over actual 0,1,2, suffices.

## 6. Charged mixed-scale preparation

For the initial b-block census (including construction for light blocks), pair occurrences are at most m^2*(M/b)^4, each costing O(m^5 polylog m). Raw cache extraction costs O((M/b)^6*m^4*b^2 polylog m). Counting plus possible tree writing costs O((M/b)^6*b^10 polylog m). For each accepted light projected block reuse its tree across the (M/b)^3 private-coordinate blocks, extracting only original width-three records using the inherited O(b^3 polylog m) mobile workspace on the original-scale stationary span. Over all full b-tiles this costs O(m^12/b^6 polylog m). Any optional root/tree cleanup and private offset enumeration cost at most O((M/b)^9*b^6 polylog m)=O(m^9/b^3 polylog m). These are upper bounds charging even empty/light tiles that may in fact be skipped.

The total initial-scale cost is therefore bounded by

    O((m^11/b^4 + m^10/b^4 + m^6*b^4
       + m^12/b^6 + m^9/b^3) polylog m).

For b as selected, the terms are bounded by constant multiples of

    m^9 sigma^(1/4),
    m^8 sigma^(1/4),
    m^(33/4),
    m^9 sigma^(3/8),
    m^(15/2),

respectively (the last uses b>=b0). Hence the initial cost is O((m^(33/4)+m^9 sigma^(1/4)) polylog m). All original-scale fixed-track sweeps can stay within O(m^3 polylog m) span because no oversized tree is allocated.

For the fallback portion, the exact count of projected b0-blocks is h*(M/b0)^6. Each contains at most b0^2 real retained pairs, so even with independent regeneration per block, pair cost is O(h*m^11/b0^4 polylog m). Raw cache cost O(h*m^10/b0^4 polylog m), count/build O(h*m^6*b0^4 polylog m). Each fallback projected block is combined with (M/b0)^3 private blocks, so original-record extraction and mandatory root/cleanup costs are O(h*m^12/b0^6 polylog m + h*m^9/b0^3 polylog m). Rounding and padding are absorbed by M<2m and b0>sqrt(m)/2. Substitution of b0=Theta(sqrt(m)) shows total fallback cost O(h*m^9 polylog m)<=O(m^9 sigma^(1/4) polylog m). Do not multiply all initial costs by a number of fallback blocks: each coarse block is counted once, and only heavy blocks are replaced. The fixed number of wide supports does not affect exponents.

All caches, original raw records, scores, output, pins, local reserved tree and workers are on reusable components. Original list extraction and copying to the root are bounded by the original-scale span and b^3 or b0^3 list size, not a global random address access. Thus the combined visited span is O(m^3 polylog m) throughout. Reconstruction of the original tuple and actual fixed extension at success, emitting contiguous n bits with physical halt head at their first bit, costs O(m^4 polylog m) once, dominated. On exhaustion halt on blank. Outside sigma<=1 simply use b0 everywhere, with the same space cap and O(m^9 polylog m) preparation.

## 7. Mixed-scale local traversal

For each actual projected coarse block (light or fallback) the compact stationary tree worker is unchanged from the parent. At a positive full node of side t with R_i allowed projected tuples, only the translated original width-three records move between reserved frames; navigation uses stationary delimiters. Its work including all child choices is O(t^6 sqrt(R_i) (1+log(t+2))^A). Zero child headers are checked without list copying and charged to their positive parent. At a singleton with true flag, acceptance is exactly emptiness of the retained forbidden list. This preserves every valid restricted model's path, not merely an approximate projection. Private alternatives reuse projected child frames sequentially; active ancestors are at distinct projected depths. All local counters and fields depend on t, not m; the outer offsets are restored at the root. The local physical head follows the worker component rather than performing a global sweep per transition.

The projected coarse blocks form a disjoint dyadic partition; for each one the private coarse blocks cover all private digits at the same side length. Thus across mixed coarse scales, any two full visited nodes at the SAME dyadic side t belong to disjoint full tiles. A projected block at t can occur with at most (M/t)^3 private choices. Consequently

    sum_i R_i <= R*(M/t)^3,
    N_t <= (M/t)^9,
    sum_i sqrt(R_i) <= M^6 sqrt(R)/t^6

by Cauchy-Schwarz. Unlike the parent's uniform coarse partition, equality in the mass sum need not hold at intermediate scales, because some of the full domain starts at a smaller coarse root. Only the inequality is needed. At t=1 every allowed projected leaf with every padded private combination is visited if the search is exhausted without early stopping. Multiplying by t^6 and local logs and summing across dyadic scales gives the inherited O(m^9 sqrt(rho) polylog m) wide traversal bound. Mandatory empty coarse roots are covered in preparation. No independence or uniform spatial distribution assumption.

For sufficiently small sigma, combining all wide branches with the narrower worker gives

    O((m^(42/5)+m^9 sigma^(1/5)) polylog m),

because m^(33/4)<=m^(42/5), sigma^(1/4)<=sigma^(1/5), and sqrt(rho)<=sqrt(sigma)<=sigma^(1/5). Nonzero narrow densities are at least m^-5, so their local logs are bounded by polylog m; alternatively retain the stronger local-log expression separately. Under beta_*,delta_*=O(m^-epsilon), sigma=O(m^-epsilon/2). This gives O(m^(9-epsilon/10) polylog m) because epsilon<=1, hence o(L^3) at original-scale span. Once eligible, the fixed machine of actual description length ell receives at least L^3/2^ell transitions at s=3 ceil(log2 L); the little-o bound eventually fits the exact clock. No explicit ell, numerical threshold, compiled program or actual U run supplied.

## 8. Remaining logarithmic issue

The adaptive space cap removes the expanded workspace, not the critical dyadic time factor. At a scale t, the Cauchy bound charges up to O(m^9 sqrt(rho) polylog(t+2)). Unlike width-five stationary trees, the polynomial factor has no decaying geometric tail for t above the density crossover. Even ignoring logs, summing this bound can introduce log m. Reducing b with the space cap does not eliminate that sum when b grows polynomially with m. The preparation estimate itself also contains a global polylog m on the small-score term. Both must be addressed before claiming arbitrary-slow full-average recovery. This is a limitation of the current upper-bound analysis, not a time lower bound. No sequence of actual exact cubic misses is constructed.

## 9. Executed finite verification

Standalone JS audit based on the parent's reference executed in the tool runtime; identical function committed with a Node entry point. Twelve fixtures at m=2,3 across six constraint modes use a supplied modular-sum contextual map and a single wide support. Force initial width B=2 for these small semantic cases (rather than the production adaptive scale), compute exact root mass, apply the cap and split heavy roots to the fallback scale. Verify the mixed-scale partition is disjoint and complete, the heavy census inequality, exact fallback block count, allocated tree cap, abstract layout extent, local factorized membership, exact restricted model set, and mixed-scale mass/Cauchy bounds. Of 390 initial projected roots, 5 were heavy and 385 light; the 5 heavy roots became 320 fallback blocks, for 705 actual projected roots, including 540 empty ones. One fixture exercised both light and heavy roots. There were 9,210 full coarse tiles, 705 cap checks and 24,960 root-count predicate checks. Aggregate model census: 334 allowed width-six tuples across fixtures, 48,259 original model occurrences, 121,170 direct full tuple checks and 3,984 recovered restricted models (equal to the direct reference). Tree/worker counts: 32,960 factorized membership evaluations, 8,705 projected headers, 8,246 zero headers, 459 positive projected frames, 182,125 aggregate abstract slots, maximum one-tree extent 2,535 abstract slots, 20,808 positive full-node visits, 19,808 singleton leaf checks, 512,000 child choices, and 18,816 positive child shuttle assertions. The audit builds constant-size empty headers even where the mathematical worker can skip empty trees. The total of allocated slots over all trees is not simultaneous space.

Separately check the production dyadic scale with BigInt inequalities for every m=2..4096 at four rational scores sigma=p/m (p=1,floor(sqrt m),floor(m/2),m, truncated to at least one). There are 16,380 arithmetic cases, verifying the adaptive scale bounds, fallback cap and numerical heavy-fraction/pair-cost factor inequalities. The forced semantic fixtures do not assert that B=2 is the production b. The inherited fixed-map controls m=3,5,9,17 recheck dense lower-dimensional projection and sparse exact mass; they do not separate the whole preceding algorithm class. All assertions passed.

The host reference uses indexed arrays/maps, host recursion, direct enumeration for the root mass census, and abstract slots, not actual tape movement or the physical builder. It uses supplied maps, not all 504 adaptive choices, and does not integrate the normalized encoder/verifier, actual sequential membership caches, compiled transitions, or the exact U stage. The arithmetic checks validate formulas at sampled finite inputs, not asymptotic physical performance. Independent mathematical review, Lean formalization and exact-head CI remain unconfirmed.

## 10. Disposition

Original-scale visited span is restored for direct three-context polynomial average-loss recovery, via adaptive dyadic coarse refinement and an exact count certificate before allocating each compact stationary tree. Full arbitrary-slow average-loss recovery remains OPEN; in particular a local-log or different transfer method must eliminate the critical width-six traversal logarithm AND the global logs on the density-dependent preparation cost. General unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not freshly recounted. Promotion NONE.
