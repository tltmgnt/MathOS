# F038 — Two-context refinement of adaptive tail unions

PNP_RESOLUTION_STATUS = OPEN. Parent 4523ee0369201c4af38eb4ba6c162df3829afab2 (tail union recovery). This note combines the parent's learned head and per-key heavy/union decision with the earlier two-retained stationary width-five worker (f28a042a8ada7628622d927e003c5d6f98302630). Conditional mathematical fixed-machine-existence derivation using inherited physical routines. Executed host semantic regression, not compiled original-U execution or independent proof review. Parent combined statuses and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Result and quantifiers

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), original selected negative cross-clause support bits F_B of width one through three and actual fixed one-hot/OR/pin/guard extension. Choose compressed group g and three conditioning groups K, written (h,j,l); their context digits are (d,e,t). Keep a distinguished h for learning the head. For contextual sets C_c and maps p_c(a) into them, define beta=sum_c |C_c|/m^4 and delta_n,delta_w as the inherited weighted directed losses normalized by m^6. Use the same finite map-policy family as the parent (full-average facility greedy and fixed six-block-splice-penalized greedy), with representative self ties. No supplied map or choice. For each wide H={g,u,v} with u,v outside K, define Z_H(a,b;x,y)=(1-F_H(a,x,y))*F_H(b,x,y) and ell(a,b)=sum_H |Z_H(a,b)|.

Learn a head P_(a,d) from the k most frequent replacement digits among the m^2 contexts with retained digit d, plus a itself. Tie by increasing digit. Use the same enumerated k=0 or dyadic 1<=k<=m^(1/32), and thresholds r=0, powers of two below 10m^2, and 10m^2. Unlike the head, the tail is now split by a SECOND retained context digit. For each key (a,d,e), let f_e(b)=#{t:p_(d,e,t)(a)=b}, so sum_b f_e(b)=m. Low tail L_e consists of positive-frequency b outside the head with ell(a,b)<=r, high tail all other positive-frequency labels outside the head. Put n_e^low=sum_(b in L_e) f_e(b), n_e^high analogously, and

    V_(H,a,d,e)(x,y) = OR_(b in L_e) Z_H(a,b;x,y),
    v_e = sum_H |V_(H,a,d,e)|.

Route all low-tail assignments at this key through the union if v_e<=m*n_e^low, else through the heavy envelope. High tail always heavy. Set every rejected union row to zero. The cost per key, in units of 1/m^5, is

    m*n_e^high + min(m*n_e^low,v_e).

Let gamma be normalized heavy assignment fraction (denominator m^4), eta=sum_H |V_H(retained)|/m^5, and lambda normalized total wide loss of actual head assignments (denominator m^6). The adaptive score is

    Q2 = beta + delta_n + gamma + eta + (k+1)^13 lambda.

There is ONE fixed deterministic original three-symbol one-tape witness machine correct throughout the family, which enumerates all g,K,h,j choices (504*3*2), the parent's fixed policy family, and k,r, selecting minimum exact score. On sufficiently small positive computed Q2, the charged bound is

    T(m) = O(m^(44/5) polylog(m+2)
             + m^9 Q2^(1/6) (1+log(1/Q2))^A),
    visited span = O(m^3 polylog m),

for fixed implementation-dependent A. Hence Q2->0 implies T(L)=o(L^3), eventual exact cubic-stage witness coverage. No global logarithmic rate condition on Q2. The new score is pointwise no larger than the parent's score for the SAME generated map, h,k,r, and either choice of second context j. This is a dominance statement about computed scores, not a runtime improvement on every input: the preparation bound increases from 42/5 to 44/5. The prior program remains available separately.

## 2. Proof of refinement monotonicity

Fix (a,d) and the SAME head and threshold as in the parent. Its low/high frequency counts n_low,n_high are sums of their split counts over e. Every V_(H,a,d,e) is a subset of the parent's low-tail union U_(H,a,d), hence v_e<=v where v=sum_H |U_(H,a,d)|. Therefore

    sum_e min(m*n_e^low,v_e)
      <= min(sum_e m*n_e^low, sum_e v_e)
      <= m*min(n_low,v).

Adding the high charges gives sum_e [m*n_e^high+min(m*n_e^low,v_e)] <= m*[n_high+min(n_low,v)]. Divide by m^5 and sum over (a,d). Head wide loss, narrow loss, representative capacity are unchanged. The parent union's denominator is m^4, the refined union's m^5; the factor m is required for this comparison. No assumption of disjoint support sets, no claim that every split key individually has smaller unnormalized charge. At a fixed k,r the minimum refined score cannot increase, and the enumerated map-policy family includes every parent policy with that head context.

At r=10m^2 all tail labels are low. Define tau2_k as the sum over (a,d,e) of min(m*outside-head assignment count, union bit count), divided by m^5. If along a sequence of the generated maps beta,delta_n,delta_w->0 and lim_(k->infinity) limsup_(m->infinity) tau2_k=0, then Q2->0: for any epsilon choose a fixed sufficiently large dyadic k with limsup tau2_k<=epsilon, which eventually satisfies the production cap. The head term at that FIXED k is at most (k+1)^13 delta_w->0. The selected minimum has limsup<=epsilon, hence tends to zero. By the preceding inequality tau2_k<=tau_k of the parent, so this covers all earlier tight-frequency and union-tail promises. More generally an input-dependent enumerated threshold can be used directly if its exact score vanishes. No assertion that arbitrary small beta,delta implies this new condition.

## 3. Exact witness/existence reduction

Use the representative envelope on {g} union K, including all selected representatives and all heavy assignments. These parts are disjoint since selected representatives use self, always in the head. Its density is beta+gamma. Keep every exact narrow exception on B union K. For each wide H search the exact head guard on H union K (old zero, substituted one, head membership), and the retained split union guard V_H on {g,h,j,u,v}. The latter has width five, independent of the third conditioning digit. All branches retain ALL original constraints and padding exclusions. A union guard may include a tuple whose actual map does not produce that exception; this is safe for existence because every returned tuple must satisfy the original clauses.

Given an original model, replace g by p_c(a). If successful the image lies in the envelope. If the map is heavy, the original lies in the envelope. Otherwise a newly violated narrow support gives the original in its exact exception, or a newly violated wide support gives the original in the exact head guard or its retained split union. Every branch witness is original. At most 48 branches, since 37 supports contain g, of which ten are wide. This is witness/existence equivalence, not equality of the original and substituted model sets. The exact union branch model set is the original model set intersected with its union restriction, not the set of actual low-tail failures.

## 4. Bounded-space learning and score computation

Use the inherited pair-sliced generator detailed in f28a042's Section 4: O(m^5 polylog m) physical moves for each retained (d,e) pair, all t, with O(m^3 polylog m) span. Raw directed distance caches, fixed-track parsing, actual pins and both map-policy generators are inherited from the parent. The fixed splice penalty depends on a,b and one context digit; align that digit with the retained pair for the generation of the map, or use a small mobile computation on its local distance records. It needs only polylog m bit work per candidate record, so it does not change the inherited pair bound. All policies use deterministic self ties on selected representatives.

First learn the head for each d by generating all m retained pairs with that d, accumulating an m^3-record spool of assignments and loss/representative metadata as in the parent. Sort/count on (a,b), select top k plus self. Keep the global head table of at most m^2(k+1) entries, O(m^3 polylog m) span. The score's beta,delta_n,lambda can be counted during a second pass over pair outputs by joining the maps with this head table and the original wide loss counts. For a fixed (d,e), regenerate its m^2 map records, sort by (a,b) to compute the actual frequencies f_e, join with head flags and ell. This can be done with sequential O(m^2 polylog m) bit steps within the pair's local data, or a global sweep O(m^5 polylog m). Extract the d-specific head slice by mobile scan at O(m^4(k+1) polylog m)<=O(m^5 polylog m). No global m^4 pair-frequency table.

For a fixed (a,d,e) and H, the earlier two-retained union row generator applies exactly: use mobile scratch of O(m^2 polylog m) blocks containing the old full raw row, its zeroed union accumulator, and the m target flags (positive frequency, not in head, ell<=r). Scan the stationary original raw stream of O(m^3 polylog m) blocks in (b,x,y) order, carrying scratch with the scan and ORing old-zero/new-one at matching flagged targets. Even a full scratch scan/one-block shift per stationary record costs O(m^5 polylog m) physical moves per key; extracting/copying the old row and flags, rewinding, counting and clearing fit the same charge. This improves on a generic global sweep per key, which would cost m^6. Exact counts of every wide union row suffice for v_e. Across m^3 keys and fixed H, O(m^8 polylog m) physical work. At completion of each key choose the per-key route using v_e<=m*n_e^low. Accumulate gamma and eta; the union row itself can be discarded. Only one pair's frequencies at once. The exact integer score is

    m^6 Q2 = m^2*(representative count + heavy count)
               + m*retained union bit count
               + summed narrow weighted loss
               + (k+1)^13*summed head wide loss.

All fields O(log m) bits, constant exponents. Learning over fixed policies/coordinates and logarithmically many k,r options costs O(m^8 polylog m). Save winning identifiers, regenerate its head and route decisions. One bit per (a,d,e) suffices for the low-tail route, O(m^3 polylog m) span. Do not retain every tail label for every key, nor any global m^5 union. During regeneration use actual map frequencies and the saved head and threshold to reconstruct the low-tail flags. For envelope/narrow/head map generation attach the needed flags by joining the pair maps against its head slice, route decision slice and ell. Even charging global sweep or mobile extraction for these O(m^2 polylog m) local data costs O(m^5 polylog m) per retained pair. The maps are not reoptimized after learning.

## 5. Width-five union preparation and local physical traversal

Use b the largest dyadic with b^5<=m^3 (b=Theta(m^(3/5))), pad to M least power of two >=m. For a projected five-coordinate coarse block on (a,d,e,x,y), enumerate real retained pairs within it. Regenerate each pair's maps/frequencies once at O(m^5 polylog m). For each source a in its interval regenerate the whole union row by Section 4; if its saved route rejects the low tail use zero. Extract the b-by-b requested free square and append its flags with local translated keys. A full row's O(m^5 polylog m) cost dominates per-bit output shuttles O(m^3 b^2 polylog m). For padding the union bit is zero. Each actual row (a,d,e) is regenerated for each of (M/b)^2 free interval choices. Each retained pair occurs in (M/b)^3 combinations of source and free intervals. Thus pair regeneration O(m^10/b^3 polylog m), row regeneration O(m^10/b^2 polylog m).

At most b^5<=m^3 flags in a projected coarse block. Use the inherited stationary width-five builder (f28a042 Section 6; earlier stationary-restriction-tree note): sequentially sort/OR dyadic prefix flags and serialize preorder subtree with compact zero headers and O(t^3 polylog(t+2)) writable residual frames at positive nodes of side t. Tree extent O(t^5 polylog(t+2)) by summing over 32-ary levels. The builder costs O(m^6 polylog m) per projected block via inherited sorting/sweep. Across (M/b)^5 blocks this gives O(m^8 polylog m). Reuse the tree over every private coarse block on the four coordinates outside its support. Extract ALL original width<=3 records including padding with a mobile O(b^3 polylog m) scratch over original-scale span, translating to local keys and transferring to the root. O(m^3 b^3 polylog m) per full tile, hence O(m^12/b^6 polylog m)=O(m^(42/5) polylog m). Clear writable frames between private choices; immutable flags remain. No full width-five guard is stored globally.

At a positive full node of side t, enumerate the 512 full children. The five projected bits choose its stationary child header; private alternatives reuse that child frame sequentially. Active ancestors have distinct depths. Restrict/translate the original lists to the child, using per-bit shuttles within the parent subtree of extent O(t^5 polylog(t+2)). Original payload O(t^3 polylog(t+2)) blocks; local work O(t^8(1+log(t+2))^A) physical moves including navigation, filtering, copying, child choices, clearing and return. Global sizes, coordinates and pins are not carried into local frames. At singleton a positive flag and no forbidden record are exactly an original model in the union branch. All such models survive their unique path. The local positivity flag already encodes the exact union, not a reevaluation of a translated candidate digit. No global reads within the recursive worker. Fixed finite product components encoded by constant-width blocks of original 0,1,2, not additional physical heads.

Preparation for these branches is dominated by O(m^10/b^2 polylog m)=O(m^(44/5) polylog m). The other exponents are 41/5 pair regeneration, 8 builder, 42/5 original extraction. All visited span O(m^3 polylog m), including raw data, route decisions, pair spool, scratch and stationary tree. Reconstruct original latent digits, actual pins, one-hot/OR/guard extension once, emit contiguous n raw bits with physical halt head at first bit, or halt on blank on exhaustion, O(m^4 polylog m) once. This is the inherited physical construction, not a measurement of compiled transitions.

## 6. Combined local-log bound and original clock

Envelope/narrow branches retain the inherited width-four/five worker with preparation exponent 42/5. Exact head-wide branches retain the parent growing one-context palette representation and adjacent root/child frames with coarse width Theta(m^(2/3)); the second context is not included in head keys, so its payload bound is unchanged. Preparation O(m^(403/48) polylog m) with k<=m^(1/32). Map generation from the new saved decisions uses Section 4; no new factor k from split unions. For the head branches, local work O((k+1)^2 t^8 (1+log(t+2))^A). The parent density exponent 1/6 with X=(k+1)^13 rho absorbs the multiplier and log(k+1) uniformly because (k+1)^2 rho^(1/6)=(k+1)^(-1/6) X^(1/6). Empty guards have no positive descendants.

For a split union of R entries on five coordinates, rho=R/m^5. Positive full-node count at side t <=min((M/t)^9,R*(M/t)^4), and visited descendants satisfy this bound up to a fixed factor by the positive-parent condition. Charge mandatory coarse roots separately (O(m^9/b polylog m) <= preparation). The dyadic sum for R>=1 is bounded by

    sum_t min(M^9/t,R*M^4*t^4)*(1+log(t+2))^A
      = O(m^9 rho^(1/5)(1+log(1/rho))^A).

Split at t0=M/R^(1/5): both tails decay geometrically (exponents 1 and 4), dominating local logarithmic growth. R=0 has no positive descendants. Unpruned sum O(m^9). No global log m multiplier on the small-density term. Since each branch density (weighted for head) <=Q2, the fixed branch count and 1/5>=1/6 give the claimed complete bound. For Q2 not small the exact branches still give correctness, or use the inherited exhaustive solver; no strict time claim outside the promise.

For Q2->0 this is o(m^9)=o(L^3) with O(L polylog L) visited span. A fixed actual program of description length ell receives >=L^3/2^ell transitions at stage 3 ceil(log2 L) once eligible, so little-o eventually fits the exact clock. No explicit ell, numerical threshold, compiled machine or actual U stage supplied.

## 7. Dense-union obstruction on genuinely diffuse generated maps

This control strengthens the earlier two-retained note's fixed-policy polynomial-loss example: the new control has genuinely slow optimal wide loss for the designated configuration, uses the actual unpenalized full-average greedy maps, and obstructs all the immediate parent's k,r choices for those maps and every distinguished h in K. It does NOT separate the entire earlier adaptive solver across other policies and coordinate choices.

Take m=2^d, identify the real domain with GF(m) in a fixed binary basis. Let J be the additive subspace whose first ell_d bits are zero, with ell_d positive and slowly tending to infinity, ell_d<d. Put zeta=|J|/m=2^-ell_d; e.g. ell_d=max(1,floor(log2(log2(d+2)))) eventually. Use unary zero exclusions on all groups. Put one narrow ternary on {0,1,2} forbidding a!=f(c1,c2) where f=1+((c1+c2) mod (m-1)) using ordinary integer digit labels. Put a wide ternary on H={0,4,5},

    F_H(a,x,y)=1{a*x+y in J},

with addition and multiplication in the field. No other cross supports. Choose g=0,K={1,2,3}. This simple family is SAT for large m: take nonzero c1,c2, a=f, arbitrary nonzero x, then choose nonzero y with a*x+y outside J, and all other digits nonzero. No hardness or complete primal graph claim.

For any a!=b the map (x,y)->(a*x+y,b*x+y) is bijective: the difference of the coordinates determines x by division by a-b, and then y. Therefore EVERY ordered distinct pair (including zero) has the exact same directed loss

    D = |J|*(m-|J|) = m^2 zeta(1-zeta).

Self loss zero. For a fixed context the narrow constraint contributes m^2 exactly at source a=f and target b!=f. The unary exclusion contributes m^2 for nonzero-to-zero. The total summed wide loss to any candidate is (m-1)D. Thus target f (nonzero) uniquely minimizes first facility loss. After selecting f, any other nonzero candidate improves only its own source by D<m^2, and adding zero improves only source zero by D (nonzero sources lose the unary penalty). All future marginal gains are nonincreasing. Consequently the selected positive round is exactly one representative f, p_c(a)=f for every source. This is a proof for the actual greedy map; no choice of artificial high-loss maps is needed. It gives beta=1/m, delta_n=0, delta_w=(1-1/m)zeta(1-zeta). In fact for ANY maps on this configuration delta_w >=(1-beta)zeta(1-zeta), since a self assignment implies a is in C_c. Wide loss vanishes arbitrarily slowly for the indicated ell_d and cannot vanish at a fixed polynomial rate under vanishing capacity.

For every distinguished h in K and each retained d, all nonzero labels occur among the m^2 contexts, each at most 2m times: if h is 1 or 2 vary the other summand, if h is 3 fix one summand and vary the other. Thus the one-context head plus self captures at most 2(k+1)/m assignments, uniformly for k<=m^(1/32). The parent's one-context charge is bounded away from zero for EVERY r:
* If r<D, every distinct replacement outside the head is high, so heavy mass is 1-o(1).
* If r>=D, all tail labels are low. For any x!=0 and old-zero column (x,y), the map b->b*x+y is bijective, so |J| candidate b produce new bit one. At most one is zero and at most k+1 are in the head. For large m, |J|>k+2 uniformly in the production cap (for the indicated slow ell_d). Hence at least one actual positive-frequency tail label makes that column one. Each x!=0 has exactly m-|J| old-zero columns for each source a. The parent's low-tail union has at least (m-1)*(m-|J|) entries per key. Its low-tail assignment count is at least m^2-2m(k+1). Both normalized by m^2 tend to one, so the parent per-key minimum tends uniformly to one. Threshold selection and head weighting cannot remove this obstruction.

In the new worker choose h=1,j=2,k=0,r=10m^2. Head contains only self, which has zero wide loss. At every (a,c1,c2) the actual map is independent of c3: if a=f, no tail; otherwise all m assignments have the same tail label f. The union is exactly Z_H(a,f), of size D<m^2=m*n_low, so it is retained. There is no heavy charge and eta=(1-1/m)D/m^2, lambda=0. Consequently Q2=1/m+(1-1/m)zeta(1-zeta)->0 even at arbitrarily slow decay. This is a strict separation of the two score conditions on these generated maps, including every one-context choice for the designated g,K. Another earlier map policy or coordinate choice may solve the same easy family (e.g. it has a sparse primal graph). No separation from every earlier algorithm, lower bound on computation time, or P versus NP conclusion.

## 8. Executed host semantic regression

Standalone JS audit executed in the tool runtime and committed with identical Node entry point. Sixteen fixtures m=2,3 across eight constraint modes, 48 passes (unpenalized greedy and two forced choices to exercise routes), designated g=0,K={1,2,3},h=1,j=2. Finite prescribed b=2, k in {0,1,2}, r in {0,1,10m^2}. It explicitly computes both unsplit and split scores for each candidate, checks the per-key refinement inequality, exact union bits and score recount, original-model recovery and exact union-branch model sets. Immutable projected five-coordinate positivity trees reused over all private coarse tiles; verify child flags, exclusive active frames, residual clipping and exact singleton acceptance. Counts:

    464 candidate scores
    3,016 refinement inequalities
    11,136 per-key charge checks
    280,488 exact union bit checks
    484,680 full tuple checks
    180,477 successful substitutions
    7,975 heavy-envelope failures
    1,004 head-wide failures
    10,494 union-tail failures
    1,527 narrow failures
    12,017 recovered union-branch model occurrences
    1,034 original head-guard model occurrences by direct evaluation
    7,406 stationary projected tree flag evaluations
    1,167,872 full child choices
    40,014 coarse roots
    776 greedy residual checks.

All executed assertions passed. The exact head guards are checked by direct evaluation for recovery, not by executing the compact head worker. The count of recovered union models may exceed the number of actual tail failures because the union guard deliberately enlarges the exception relation.

Independent finite field controls explicitly enumerate all ordered distinct pairs and all free columns at m=8,16,32,64 with |J|=m/4 and test the uniform directed loss. At k=0 they compute the sum of the one-context per-key charge for a fixed first context digit across all source labels, and the refined per-key charge divided by m (so same units); test dense union cardinality and exact normalization. For every possible nonzero target f, test the first greedy choice and every possible second-facility marginal. Output [m,|J|,D,pair checks,unsplit charge,split charge rescaled,tail assignment count,greedy stop comparisons]:

    [8,2,12,56,336,84,448,49]
    [16,4,48,240,2880,720,3840,225]
    [32,8,192,992,23808,5952,31744,961]
    [64,16,768,4032,193536,48384,258048,3969]

These finite tests use fixed zeta=1/4; the vanishing-rate and all-k,r obstruction are analytical, not experimentally inferred. The host uses indexed arrays/maps, direct enumeration, recursive objects, and finite-field arithmetic for controls. It does not execute physical sorting/sweeps, actual mobile shifts, serialized stationary frames, all adaptive policies/coordinates, compact head traversal, normalized encoder/verifier, compiled original-U program or exact stage. No measured physical transition counts, independent review, Lean formalization or exact-head CI confirmation.

## 9. Disposition

The two-context refinement weakly dominates every immediate parent score for the same generated maps and exposes a new dense-union control with genuinely slow optimal wide loss on the designated configuration. The stationary width-five worker preserves a rate-free density term at original-scale span. The remaining gap is the case in which even the two-retained unions are dense, or the actual map depends diffusely on all three conditioning coordinates. Small average loss alone is not yet sufficient. Next investigate decomposing the last context fiber without constructing a critical-width stationary tree or multiplying density savings by global logarithms. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
