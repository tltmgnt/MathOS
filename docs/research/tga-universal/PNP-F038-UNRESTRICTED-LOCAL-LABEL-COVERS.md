# F038 — Input-adaptive multiscale local label covers

PNP_RESOLUTION_STATUS = OPEN. Parent b85dd333cd0b23c97ea51d3d988e23524853af03 (context sketches). Conditional mathematical fixed-machine-existence/resource derivation using inherited original parsing, pair-sliced maps, fixed-track sweeps, mobile carry shifts, width-four/five stationary workers and adjacent spatial frames. Executed host semantic audit; not compiled original-U execution, independent proof review or Lean formalization. Parent combined statuses and PR-triggered runs empty; push CI unconfirmed.

## 1. Result and quantifiers

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), original selected negative support bits F_B of width one through three, and actual one-hot/OR/pin/guard extension. Choose compressed group g and three conditioning groups K, with context c. Contextual representative sets C_c are nonempty, p_c(a) lies in C_c, and selected representatives use self ties. Let beta=sum_c |C_c|/m^4 and delta=delta_n+delta_w be the inherited weighted directed average loss normalized by m^6. Wide H={g,u,v} has both other groups outside K, with exact directed difference

    Z_H(a,b;x,y)=(1-F_H(a,x,y))*F_H(b,x,y).

All earlier loss identities are retained. Inherit the finite map-generator family (full-average facility greedy and fixed six-block-splice-penalized greedy with each distinguished context). Do not reoptimize maps after learning.

No fixed context sketch or global map factorization is required. Pad to M, least power of two >=m, and let B be the largest dyadic with B^3<=m^2, B=Theta(m^(2/3)). A local cover is learned for each real source a and each aligned context cube within a coarse K block of side B. Enumerate two fixed exponents alpha in {1,5/4} and dyadic capacities C, 1<=C<=m^(1/32). Define the label cap K_alpha,C(t)=floor(C*t^alpha), or equivalently cap at m if larger. Only NONSELF assignments count toward the cap, since self substitutions have empty directed difference.

For each coarse K block, start with all nonself assignments (a,c,p_c(a)). At scales t=B,B/2,...,1, group the current surviving assignments by (a, aligned context cube of side t). Count replacement labels, retain the K_alpha,C(t) most frequent labels in each key (canonical increasing-digit ties), and mark every other assignment heavy permanently. Self assignments neither consume capacity nor become heavy. This top-down trimming guarantees every aligned descendant cube at side t contains at most K_alpha,C(t) distinct surviving replacement labels for each fixed source. No supplied labels, sketch, convergence rate, or advice. The same labels may occur in unrelated cubes; no global consistency is imposed.

Let gamma=number of heavy assignments/m^4 and lambda=total wide loss of surviving assignments/m^6. Select minimum exact score, separately or jointly over the two exponents,

    Q_alpha = beta + delta_n + gamma + C^P lambda,
    (alpha,P)=(1,13) or (5/4,25).

The algorithm enumerates all g,K and finite map-policy choices and C. One fixed deterministic original three-symbol single-tape witness program is correct on the entire family. For a fixed alpha option, sufficiently small computed Q_alpha gives

    T(m)=O(m^p polylog(m+2) + m^9 Q_alpha^epsilon(1+log(1/Q_alpha))^A),
    visited span O(m^3 polylog m),

where [alpha,p,epsilon]=[1,42/5,1/6] or [5/4,419/48,1/12]. Here A is fixed and implementation-dependent. For the joint minimum use p=419/48, epsilon=1/12; the two options remain available separately. All preparation exponents are strictly less than nine. If any selected score tends to zero, the bound gives eventual exact cubic-stage inclusion, without a prescribed convergence rate.

This is not a proof that beta,delta->0 alone suffices. It replaces the earlier finite sketch family by actual multiscale diversity of generated maps and an explicit computable trimming charge. It does not dominate every earlier union score: a dense collection of labels with a shared sparse union can still favor the older worker. The new mechanism can be added to a finite portfolio alongside the previous ones.

## 2. A sufficient condition and a certified trimming inequality

For a fixed generated map and alpha,C, for each scale t<=B let L_t(a,D) count the original nonself assignments with c in D, and let H_t(a,D) be the sum of the largest K_alpha,C(t) original label frequencies there. Define

    tau_alpha,C(m) = (1/m^4) sum_(t<=B dyadic) sum_(a,D) [L_t(a,D)-H_t(a,D)].

At a given trimming step the current label multiset is a submultiset of its original multiset. Retaining the original top labels would lose at most the original tail count, and the current frequency-optimal set loses no more than that. Therefore the number of assignments removed at this scale is <= the original tail count at the scale. Summing gives gamma<=min(1,tau_alpha,C(m)). Once a scale has been processed, later deletions can never increase its distinct surviving count. This is an exact feasible cover construction and an additive tail bound, not an optimal solution of the simultaneous hierarchical covering problem. In particular a competitor with small deletion mass does NOT immediately imply a comparable bound on tau without a factor for the number of levels.

If a sequence of generated maps has beta,delta_n,delta_w->0 and

    lim_(C->infinity dyadic) limsup_(m->infinity) tau_alpha,C(m)=0,

then the minimum Q_alpha->0. For any epsilon0 choose a FIXED dyadic C making the limsup tail bound small. It eventually passes the production cap, and at that fixed C the wide score term <=C^P delta_w tends to zero. Take the minimum before the limit. No uniform rate or supplied C. In particular any generated map family whose nonself local images have at most C0*t^alpha labels at every scale and source, for a fixed C0, has zero trimming at a fixed dyadic C>=C0. Even arbitrary input-dependent labels and nonuniform behavior across cubes are permitted. The actual computed gamma can be smaller than the sum of original tails.

At alpha=1 the condition includes exact local-label dependence through any function with image <=C0*t on every aligned context cube (even one with no efficient global sketch description). At alpha=5/4 it admits genuinely superlinear local images. Self exclusion is important: the representative envelope contains self assignments even if they were not among a local top list.

## 3. Exact witness recovery

Let S be the width-four restriction on {g} union K consisting of all selected representatives and all heavy source/context assignments. These sets are disjoint because selected representatives use self ties and self is never heavy. Its density is beta+gamma. Keep each ordinary exact narrow exception on B_support union K (here B_support is an original support, not coarse side B). For each wide H use

    E_H(a,c,x,y)=1{assignment survives and p_c(a)!=a}*Z_H(a,p_c(a);x,y).

All original constraints and padding exclusions are enforced in every branch. On substituting g in an original model, if the image satisfies it belongs to S; if it fails and the assignment is heavy the original belongs to S; otherwise a newly forbidden support containing g puts the original into its narrow or exact wide exception. A self substitution cannot fail. Every branch witness is original. This preserves satisfiability and witness existence, not the entire original model set under substitution. At most 38 branches. The sum of normalized wide exception cardinalities is lambda, not an overapproximation. No external higher-width clause or changed verifier.

## 4. Learning and deterministic regeneration in original-scale span

Use the inherited pair-sliced generator (O(m^5 polylog m) physical per retained pair for all unretained context values, O(m^7 polylog m) overall). It supplies actual map and representative records, and attaches narrow and wide loss counts via the existing directed tables. Choose any consistent retained pair, with the splice penalty computed on the local candidate records when needed. Enumerate K coarse blocks of side B. For each block regenerate every retained pair in its two intervals and keep assignments with the remaining context digit in the block's third interval. One pair occurs in O(M/B) such blocks, so total physical generator cost O(m^8/B polylog m); copying at most m*B selected entries per pair by original-scale per-bit shuttles fits the m^5 bound. A block holds m*B^3<=m^3 map records, including all real source digits and the original labels, loss counts, flags and context keys. No global m^4 map.

For each dyadic scale within the block, compute aligned cube identifiers by binary shifts. Sort current live nonself records by (source,cube,target), count frequencies, sort groups by decreasing frequency then increasing label, mark retained labels up to cap, merge back into the full block spool. Keep discarded records with a heavy flag for envelope construction. Each pass is O(m^3 polylog m) sequential bit work/span and O(m^6 polylog m) physical by fixed-track original-scale sweeps. At alpha=1 the cap comparison is integer; at 5/4 test k^4<=C^4*t^5 with exact O(log m)-bit integers. No floating point. The number of scales is logarithmic. Across (M/B)^3 blocks this costs O(m^9/B^3 polylog m)=O(m^7 polylog m). Accumulate exact integer score

    m^6 Q_alpha=m^2*(representative count + heavy count)
                + summed narrow weighted loss + C^P*summed surviving wide loss.

All integers have O(log m) bits (P fixed). Repeat for logarithmically many capacities and constant-many coordinate/policy/alpha choices. Total selection O(m^8/B polylog m + m^7 polylog m), subcritical. Only winning identifiers and scalar score retained. Regenerate marked block spools deterministically as needed; this is the same top-down process with the same global coarse block boundary B.

For envelope and narrow restrictions use b' largest dyadic with b'^5<=m^3 and b'<=B, so b'=Theta(m^(3/5)) and divides B. Enumerate K blocks of side B first and hold their complete marked spool across all projected subblocks of side b' whose K intervals are inside it. All these projected restrictions contain the whole K. Thus no repeated global m^4 flag table or recomputation of the trimming for each individual small query. Per projected block of width w<=5 enumerate at most b'^w candidate tuples; join exact candidate source/context keys to the marked spool by sorting/merging. Envelope flags come from representative and heavy indicators; narrow exception bits are two old/new raw bit queries with returned target labels and free local digits, merged against original explicit raw bit data. O(m^3 polylog m) sequential work/span, O(m^6 polylog m) physical per block. Build the inherited stationary w<=5 dyadic positivity tree, using immutable projected flags and O(t^3 local-log) writable residual frames. Tree extent O(t^max(3,w) local-log). Across (M/b')^w projected blocks this is at most O(m^8 polylog m); full original-list extraction O(m^12/b'^6 polylog m)=O(m^(42/5) polylog m). Local cost at most O(t^8 local-log) as in the stationary width-five worker. This explicit scheduling is necessary because the trimming decisions depend on the entire parent K coarse block. Reapplying trimming independently on b' cubes would change the score and guards.

## 5. Local row construction without a global sketch

For one wide support and one projected coarse block on (a,c1,c2,c3,x,y) of side B, take the surviving assignments from the winning marked K block spool whose source digits lie in the source interval. For every distinct actual (a,b) pair used in these assignments, create a row consisting of the exact difference on the local free B-by-B square. There are at most B*min(m,C*B^alpha,B^3) such pairs. Query actual original old and target raw bits by explicit sorted records; target may be outside the source interval. Source/context padding entries absent, padded free bits zero. Each of at most B^4 surviving map records is keyed by its four local coordinates and a slot identifying its row within the source. Sort/merge to assign dense local labels, discard global target digits. The root payload is O(C*B^(3+alpha) polylog B); sequential raw queries, sorting, joins and scan of full spool/raw input cost O((m^3+C*B^(3+alpha)) polylog m)=O(m^3 polylog m) because alpha<=5/4 and C<=m^(1/32). All query buffers fit original-scale span. Applying the full-span sweep gives O(m^6 polylog m) physical per projected block, O(m^12/B^6 polylog m)=O(m^8 polylog m) total.

Install the root representation once immediately adjacent to the active worker, charging original-scale per-bit shuttles O(m^3*C*B^(3+alpha) polylog m) per projected block. Across (M/B)^6 blocks this is O(C*m^9/B^(3-alpha) polylog m), subcritical (at alpha=5/4 exponent <=9-7/6+1/32). Reuse this cache for all private coarse tiles of the remaining three coordinates. Extract every original width<=3 record and padding unit for each full tile using mobile O(B^3 polylog m) scratch over stationary original-scale span, O(m^3 B^3 polylog m) physical per full tile. Copy the cached root by LOCAL per-bit shuttles across adjacent intervals, O(C^2*B^(6+2alpha) polylog m). Mandatory root positivity, cleanup and local initialization fit that bound. There is no original-scale shuttle per row bit on each private tile.

## 6. Child recoding and exact local physical bound

At side t a frame has at most t*min(floor(C*t^alpha),t^3) exact row strings of t^2 bits, and at most t^4 map records. It also holds O(t^3) original singleton records, counters and scratch. All persistent keys are local: a source coordinate uses log t bits and a row identifier at most log(t^3) bits, even if the global capacity C grows. The map retains its actual row reference, not a recomputed replacement label. The frame extent including temporary data is O(min(C*t^alpha,t^3)*t^3 polylog(t+2)), since alpha>=1. Reserve by actual payload or a local bound derived by halving the current side and retaining a suitably clipped cap; one can simply create a child frame sized by emitted records, allowing temporary parent-size scratch in the parent/child interval. No global C field needs to accompany a child.

To test exact positivity scan each row for a one, then sort/merge nonzero flags with the actual map references. A referenced nonzero row iff some real projected tuple lies in E_H. This does not test compatibility with the remaining original constraints. For each of 512 child vectors restrict the four actual map coordinates to child intervals. Keep only rows referenced by surviving map entries. Clip their source key and free-coordinate quadrant, densely renumber surviving labels within each source and update references by sequential sorting/merging. No global target lookup. The all-scale trimming cap applies to the smaller context cube, so the child distinct row count obeys the same bound. Repeated labels across contexts share one row. Padded source/context entries never created; free padding zeros remain zero. Translate all original singleton records by child intervals. This is exact restriction of the learned wide relation, not re-learning at a descendant.

Use inherited adjacent spatial frames: one child appended immediately next to its stationary parent, processed completely and popped before next child, active capacities summing geometrically. Temporary parent-size work remains within the parent-local extent, and when reserving bounded-capacity frames the ratio of successive upper bounds is at most a fixed constant. If using actual-size frames, construct temporary data in parent scratch and transfer only the compact child persistent payload; no assumption that actual child payload has constant-factor lower bound. All local fields use O(log(t+2)) bits, even at singleton. Fixed sequential sorting/clipping and local sweeps, together with per-bit shuttles of at most O(C*t^(3+alpha) polylog(t+2)) payload across the same local distance, cost

    O(C^2*t^(6+2alpha)*(1+log(t+2))^A)

physical moves per node, including all fixed children, counters, clearing, return and success offsets. No global scan in a local transition. Inherited fixed finite product components are encoded by constant-width blocks over actual tape symbols 0,1,2. No extra head or input-dependent alphabet. At singleton a true wide flag and empty original forbidden list characterize exactly a restricted original model. Every such model survives its unique path.

## 7. Preparation and rate-free density sum

Across (M/B)^9 full tiles, original-list extraction and adjacent root initialization/test cost

    O((m^12/B^6 + C^2*m^9/B^(3-2alpha)) polylog m).

At alpha=1 the second exponent is 25/3+1/16=403/48, below narrow preparation 42/5. At alpha=5/4 it is 9-1/3+1/16=419/48, above 42/5 but below nine. Other root generation, installation, map learning and regeneration charges are below these. Span O(m^3 polylog m) since C*B^(3+alpha)<=O(m^3), including the adjacent cache, active stack and all original-scale data. Original witness reconstruction once on success restores actual coarse offsets and actual pins, reconstructs the fixed one-hot/OR/guard bits, emits contiguous n bits with physical halt head at first bit; exhaustion halts on blank. O(m^4 polylog m) once.

Write R=|E_H| and rho=R/m^6. Positive full nodes at side t number at most min((M/t)^9,R*(M/t)^3); visited descendants obey the same up to fixed factors by positive parents. Mandatory roots separately charged. With e=6+2alpha<9, sum

    C^2 sum_t min(M^9*t^(e-9),R*M^3*t^(e-3))*(1+log(t+2))^A.

For R>=1 crossover t0=M/R^(1/6), both tails decay geometrically with exponents 9-e and e-3; local logarithmic growth is absorbed. Bound O(C^2*m^9*rho^epsilon*(1+log(1/rho))^A), epsilon=(9-e)/6. Empty guards have no positive descendants. For X=C^P*rho with P=13 or25, C^2*rho^epsilon=C^(-epsilon)*X^epsilon. Also log(1/rho)=log(1/X)+P log C. For X near zero, the negative power C^(-epsilon) absorbs all fixed log C powers uniformly. Thus the local term is O(m^9*X^epsilon*(1+log(1/X))^A), no global logarithmic multiplier on Q_alpha. X<=Q_alpha; narrow/envelope density exponent >=1/5 is stronger. Combine fixed many branches and preparation for the stated bound. For large scores the exact branches remain correct; no strict saving promised there.

For Q_alpha->0 time o(m^9)=o(L^3), span O(L polylog L). A fixed actual machine description length ell receives >=L^3/2^ell moves at exact stage 3 ceil(log2 L) once eligible. Little-o eventually fits this allocation. No explicit compiled program, description length, numerical inclusion threshold or actual U-stage execution supplied.

## 8. New separation from literal and fixed-mask sketches

Let m=2^d, identify the binary labels with GF(m) in a fixed basis. Let A,B_mask partition the lowest d-1 bits into two consecutive blocks of sizes floor((d-1)/2) and ceil((d-1)/2). Define the nonzero target

    f(c)=m/2 OR ((c1 XOR c2) AND A) OR ((c2 XOR c3) AND B_mask).

For g=0,K={1,2,3}, forbid high-bit-zero digits on g by one unary support, and on the narrow ternaries {0,1,2}, {0,2,3} forbid a precisely when its corresponding low-bit block differs from that of f(c). These are valid width-three support bits, not a width-four predicate; together with the unary bit they force the unique target f(c). Other groups have unary zero exclusions. Add one wide H={0,4,5},

    F_H(a,x,y)=1{a*x+y in J},

where J is an additive subspace of codimension l(d), positive and tending arbitrarily slowly to infinity (e.g. floor(log2(log2(d+2))) eventually). Set zeta=|J|/m. All other cross supports empty. The family is SAT for large m by selecting nonzero contexts, a=f(c), nonzero x, and nonzero y outside the forbidden coset. Easy SAT control, not hardness.

Every distinct a,b has the same wide loss D=m^2*zeta*(1-zeta), because (x,y)->(a*x+y,b*x+y) is bijective. This includes zero labels. For every context, f(c) has zero narrow directed loss from every source, and any other target incurs positive narrow loss at source f(c). All targets have equal summed wide loss (m-1)D. Hence the actual unpenalized full-average facility greedy chooses f(c) first uniquely. After this first choice an extra candidate improves only its own source by at most D<m^2; other sources have unchanged wide loss and nonnegative narrow loss. Further marginal gains cannot increase. The optimal positive round is exactly one representative, p_c(a)=f(c) for all a. Beta=1/m, delta_n=0, delta_w=(1-1/m)zeta(1-zeta). Any maps on this configuration satisfy delta_w >=(1-beta)zeta(1-zeta) since self assignments require membership in C_c. Thus the loss can genuinely vanish arbitrarily slowly under vanishing capacity.

On every aligned context cube of side t, high bits of each context are fixed, and every output bit of f at position >=log2 t is fixed. Hence |image f|<=t; arbitrary subsets caused by padding could only reduce the image. C=1, alpha=1 retains every nonself assignment with zero gamma, so Q_1=1/m+delta_w->0. No fixed sketch needs to be found. The local row references are learned from actual maps.

In contrast, each of the immediate parent's fixed-mask sketches reveals at most one input bit per bit position (or a fixed bit). Conditional on its output, uniform real contexts at power-of-two m leave the XOR of the two input bits at EACH low output position uniformly random. Distinct positions are independent. Therefore f(c) is uniformly distributed over the full affine high-bit-one space B of size m/2 in every sketch fiber. This includes literal one-coordinate projections and every reserve/no-reserve permutation. At k<=m^(1/32) its head plus self captures at most 2(k+1)/m. Also for any two retained literal context coordinates, the omitted coordinate determines an affine target subspace of dimension at least floor((d-1)/2); its labels are equally frequent. The corresponding head captures at most (k+1)/|B|.

For either kind of fiber, let B=b0+W with dimension j>=floor((d-1)/2). The quotient map pi to GF(2)^l has kernel J. For each nonzero functional phi on the quotient, the pairing (x,w)->phi(pi(xw)) is nondegenerate on the full field (nonzero w multiplies bijectively). Its restriction to W gives an annihilator of size m/|W| in x. By union bound at most (2^l-1)*m/|W| multipliers x fail pi(xW)=GF(2)^l. For every other x and every y, exactly |W|/2^l labels b in B have bx+y in J. For the stated slow l this exceeds k+1 uniformly over the production cap, hence deleting head labels cannot delete all such targets. At every old-zero y for these x the union bit is one. The union size is >=m^2*(1-(2^l-1)/|W|)*(1-zeta), asymptotically full. If r<D every nonself tail label is high, so heavy fraction tends to one. If r>=D the normalized low-tail count and union count both tend to one on every such key. Weighted fiber normalization in the immediate parent gives the same conclusion, since sum_s q(s)=m^3. Thus the immediate parent's sketch score and the preceding split literal score are bounded away from zero for all their k,r and sketches/retained choices on these generated maps. The present cover score vanishes. This is a strict separation on designated generated maps, not a separation from the entire adaptive solvers across other coordinates/policies. Easy sparse instances may be solved in older ways.

## 9. Why the superlinear option is real

A second family separates the two local label-cap options themselves, on the same generated maps. For power-of-two m=2^d, reserve high output bit one and fill the d-1 lower output positions from a fixed list of independent input features. In increasing input bit position i, take bit i of c1, and additionally bit i of c2 if i is divisible by four. Stop after d-1 features. This is a uniform linear bit-selection map f'(c), not necessarily position-preserving. Force the target by unary high-bit exclusion and two binary supports {g,1}, {g,2} checking their respective output positions against the corresponding input bits. Keep the same wide field relation and other unary exclusions. The preceding unique greedy-target and uniform-loss arguments apply unchanged.

At aligned scale t=2^j, at most j+ceil(j/4) features vary, so local image <=2*t^(5/4); each varying feature is an independent uniform bit over the full cube. At alpha=5/4,C=2 no trimming is needed and Q=1/m+2^25 delta_w->0. At coarse side B=2^floor(2d/3), for large d none of the features at positions below log2 B are cut off by the d-1 output limit. The image then has at least B^(5/4) labels, equally frequent. The alpha=1 cap C*B with C<=m^(1/32) retains at most C*B^(-1/4) fraction of any such original context cube, plus a self fraction at most 1/B^(5/4). This tends to zero uniformly over allowed C. Hence gamma->1 at the first trimming scale for every linear-cap option. The superlinear exponent genuinely enlarges the local-image sufficient condition and is not just a different score penalty. This second example has only two context dependencies and can also favor earlier two-retained unions. No hardness conclusion.

## 10. Executed host regression and limitations

Standalone JS function executed and committed with Node entry point; revised with additional independent controls and rerun. Two preliminary attempts failed before committing: a spread append exceeded the host call-stack limit at a large control, and a small-image assertion incorrectly inferred that a globally small image implies the local cap at every scale. Replaced spread append with an explicit loop, removed the invalid implication and tested actual all-scale caps. The final audit has twelve fixtures m=2,3 (six modes), 24 passes (actual full greedy and forced singleton maps), prescribed coarse side 2, capacities 1,2,4 and both alpha options (not production cap). Counts:

    144 candidate score comparisons
    314 level tail-bound checks (including independent controls)
    348525 all-scale cap checks (including independent controls)
    242340 direct full-tuple checks
    134750 successful substitutions
    26592 wide failures, 1522 narrow failures, zero heavy failures in main fixtures
    1464844 local positivity checks
    1852672 exact projected membership comparisons
    330752 row slot relabels
    1458688 child choices, 6156 coarse roots
    27110 recovered wide-branch models, exact equality with direct enumeration.

Every main pass selected or was forced to alpha=1,C=1. At m<=3 the nonself label set is at most two, so no nontrivial trim is expected at side two. Separate m=8 real-label map control: 512 nonself assignments, 168 retained, 344 trimmed, original multiscale tail bound 536 (not a probability), all 344 discarded assignments independently checked as heavy-envelope original witnesses in a directed-bit failure control. This is not integrated heavy-branch stationary traversal.

XOR controls exhaust every aligned context cube for m=8,16,32,64 and verify local image cap, zero trimming for source zero and a representative copied-bit sketch's diffuse fibers. [m,cubes,max image/side,sketch keys,omitted-coordinate image sizes,trimmed]:

    [8,585,1,8,[2,4,2],0]
    [16,4681,1,16,[2,8,4],0]
    [32,37449,1,32,[4,16,4],0]
    [64,299593,1,64,[4,32,8],0]

Superlinear feature controls [d,t,actual labels,linear-cap fraction for C=1]=[8,16,32,0.5],[12,64,256,0.25],[16,256,1024,0.25]. Field controls [m,|J|,D,ordered distinct pair checks]=[8,2,12,56],[16,4,48,240],[32,8,192,992]. Each pair loss checked by enumerating every free column. These tests support individual identities; the asymptotic separations, all-mask statements, all-context greedy argument and clock bound are mathematical derivations, not empirical conclusions. The host audit does not implement the production all-choice policy family, coarse block flag regeneration, physical sorting/carry shifts, serialized adjacent frames, stationary narrow/envelope workers, actual normalized encoder/verifier, compiled original-U transitions or exact stage. No measured physical transitions, independent review, Lean formalization or exact-head CI confirmation.

## 11. Disposition

The worker learns local replacement rows directly from the generated maps instead of seeking an explicit global sketch. Multiscale trimming gives exact recovery even when some local images exceed the bound, provided the adaptive deletion/loss score vanishes. A superlinear diversity option up to the fixed exponent 5/4 is charged with strict local exponent slack. Both earlier mask sketches and literal retained contexts can lose essential information on the designated XOR maps. The new result does not imply that arbitrary low average loss forces small multiscale label covers, or that a more economical cover can always be learned. Next investigate local coverage of actual difference strings instead of label diversity, or an approximation guarantee for trimming that avoids summing all dyadic-level tails. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
