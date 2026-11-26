# F038 — Learned frequency palettes and rate-free tail selection

PNP_RESOLUTION_STATUS = OPEN. Parent aa8b88f40149196d3df9f4bcdad46a9f6bc94255 (context palettes). Conditional mathematical machine-existence/resource derivation using inherited parsing, fixed-track sweeps, pair-sliced map generation, mobile carry shifts, narrow stationary trees and adjacent spatial frames. Executed host semantic regression. Not compiled original-U transitions, independent mathematical review or Lean proof. Parent combined status and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. New theorem and its exact quantifiers

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), original selected negative cross-clause bits F_B on supports of width one through three, and the fixed actual one-hot/OR/pin/guard extension. Choose g and three conditioning groups K, with distinguished h in K. For the contextual sets C_c and maps p_c(a) into them define beta=sum_c |C_c|/m^4 and delta=delta_n+delta_w=sum_(c,a,B containing g) d_B,c(a,p_c(a))/m^6, with the parent's weights m^(2-number of free coordinates). Wide supports have g and two coordinates outside K. All other supports containing g are narrow.

We now LEARN palettes from computed maps, with no digit-splice rule required of those maps. Consider a fixed finite family of map generation policies: the inherited full-average greedy with no penalty, and the parent's greedy penalized by the fixed six-block source-context palette (one choice for each distinguished h). Use canonical ties and assign every selected representative to itself, which has zero distance and zero penalty. Evaluate every g,K,h choice. For one resulting map and a fixed (a,c_h), let f_(a,c_h)(b) be the fraction of the m^2 other conditioning contexts assigned replacement b. Define

    gamma_k = average_(a,c_h) mass outside the k most frequent labels AND self.

Include self separately even if not frequent. The top k labels are ordered by decreasing count, increasing digit to break ties. These palettes depend on the actual input. They may have k+1 entries, and k can grow with m. Define lambda_k to be the normalized summed wide loss on pairs retained by these learned palettes (so lambda_k<=delta_w). The weighted score is

    Q_k = beta + delta_n + gamma_k + (k+1)^13 lambda_k.

Select the minimum Q over the finite policy family, choices g,K,h, and dyadic k with 1<=k<=m^(1/32). This cap is part of the fixed algorithm, not an assumed convergence rate. Integer score m^6 Q_k is used. The selected policy and k determine the maps and learned palettes by deterministic regeneration.

There is ONE fixed deterministic original three-symbol one-tape witness program, correct throughout the family, with the following charged bound when computed Q is sufficiently near zero:

    T(m) = O(m^(42/5) polylog(m+2)
             + m^9 Q^(1/6) (1+log(1/Q))^A),
    visited span = O(m^3 polylog m).

A is fixed and implementation-dependent. In particular, suppose along a sequence there is a policy/coordinate choice in the finite family (allowed to vary with input) for which beta,delta_n,delta_w all tend to zero and its conditional replacement distributions are uniformly tight:

    lim_(k->infinity) limsup_(m->infinity) gamma_k = 0.

Then Q->0 and T=o(L^3) at original-scale span, eventually fitting the exact cubic stage. No fixed bounded palette need contain nearly all replacements. No rate on the wide loss, the palette tails, capacity or narrow loss is required. Bounded average conditional Shannon entropy of the generated maps is one sufficient tightness condition. The theorem also covers the entire preceding fixed-palette competitor promise by including that prior map policy.

This is a statement about the maps produced by an explicitly enumerated finite family, not an existential theorem over arbitrary maps. It does not show that beta_*,delta_*->0 alone ensures tight tails for one of these generators. The new selection and growing palette argument are conditional on tightness, not a resolution of the unrestricted arbitrary-slow problem.

## 2. Learn, score, and regenerate in original-scale space

Inherit the previous weighted facility algorithm: for each context add the best unused representative by summed residual reduction, choose the positive round minimizing k_facility*m^2+F, with deterministic ties. Its loss comparison against arbitrary competing sets follows from marginal averaging, and is unchanged for both policies. (The facility round count is unrelated to the learned palette parameter k.) Keep the original distance components. The full-average policy has distances in [0,37m^2], and the fixed-palette policy adds m^2 per incompatible source and candidate pair. Self distances vanish. For the selected round replace any selected representative's assignment by itself; this is still a minimizing assignment and preserves its score.

For one h digit value, generate all maps for its m^2 remaining contexts, using retained conditioning pairs (h,i) and the inherited O(m^5 polylog m) physical generator per pair for all unretained j values. Attach the narrow weighted loss and wide unweighted sum for each selected pair. The wide count is from the existing O(m^2) per-support table; the narrow count is the total raw distance less the wide component (and less any fixed-palette penalty). These can be joined to the chosen pair labels by local sequential sorts. The m retained pairs generate a spool of at most m^3 records (a,c_i,c_j,b,loss components, representative flag), O(m^3 polylog m) bits. Copying each pair's m^2 output records to the spool with original-scale shuttles costs O(m^5 polylog m), within the pair bound. Sort the spool by (a,b), count occurrences and sum wide loss; sort by (a,-count,b) to extract the top k labels and aggregate retained counts and wide masses. Unobserved labels need not be stored, since adding a zero-count label changes neither tail nor retained mass. Include self if absent. Obtain gamma_k and lambda_k from exact integer counts, and beta and delta_n from the map spool. This takes O(m^3 polylog m) sequential bit time and span, hence O(m^6 polylog m) physical time by inherited fixed-track sweep per h. Across all m values of h and repeated k choices, total O(m^7 polylog m). No need to store the m^4 global maps. Fixed number of policies/coordinate choices, O(log m) scales k.

Choose minimum integer score

    m^6 Q_k = m^2*(number of representative occurrences
                        + number of outside-learned-palette assignments)
              + summed narrow weighted loss
              + (k+1)^13 * summed retained wide loss.

All integers have O(log m) bits since the exponent is fixed. Compare without real logarithms, entropy computation or supplied rates. After selection regenerate the winning maps and frequency palettes. The global palette table has at most m^2(k+1) entries, original-scale space. Keep its canonical keys and slot numbers. Subsequent map generation for either policy remains the inherited generator, followed by exact lookup of learned palette membership and slot. For a retained pair (h,i), extract the h-specific palette slice (O(m(k+1)) records) by mobile carry-shift across original-scale stationary data at cost O(m^4(k+1) polylog m)<=O(m^5 polylog m). Locally sort/merge the selected pair's m^2 map records against this slice; local sequential bit time and span O(m^2 polylog m), physical O(m^4 polylog m). Attach the learned flag and slot. This fits the original pair generator bound. The prior fixed-palette penalty, when used, is still computed by the inherited rule, not by the learned palette. No greedy reoptimization after learning is required.

## 3. Exact recovery

Form the width-four envelope on {g} union K containing every selected representative and every source/context pair whose assigned b is outside the learned palette. Self inclusion and representative self ties make the two sets disjoint. Its density is beta+gamma_k. For each narrow support use its unchanged exact directed exception on B union K (density sums delta_n). For each wide H={g,u,v}, use the actual light exception on P=H union K,

    E_H(a,c,x,y) = 1{p_c(a) in learned P(a,c_h)}
                      * (1-F_H(a,x,y))*F_H(p_c(a),x,y).

All original constraints are retained in each branch. A satisfying tuple either remains satisfying on substitution and its image is in the representative envelope, or fails on an outside-palette pair and the original tuple belongs to the envelope, or fails on a permitted pair and a newly violated support puts the original tuple in its exact exception. Every branch witness is original. At most 38 branches. This preserves witness existence, not the entire model set under replacement. The normalized wide light densities sum to lambda_k. Inactive wide supports can be skipped. All original syntax, actual pins and universal-machine encoding unchanged.

Envelope and narrow branches use the inherited width-four/five stationary worker with O(m^(42/5) polylog m) preparation and O(m^9 Q^(1/5)(1+log(1/Q))^A) density cost for small Q. For these branches the learned palette is used only in evaluating exact membership, via the pair-generated flags. No factor (k+1) multiplies their local traversal cost.

## 4. Growing local payload with genuinely local fields

Let b be the largest dyadic side satisfying b^3<=m^2, so b=Theta(m^(2/3)); pad to M power of two. In one projected tile of side t, there are at most t^2 source/distinguished-context keys and at most k+1 possible replacements per key. Store the exact directed difference rows on the local t-by-t free square and the at most t^4 light map records. A row reference consists of the two local digits and a local slot. At the coarse root generate the rows by exact sort/merge of explicit old and new raw bit queries as in the context-palette parent, including representatives outside source intervals and padded free columns as zero. Root queries O((k+1)b^4 polylog m) bits fit original-scale space. Root slot keys can initially use O(log m) fields.

Crucial for the density sum: do NOT carry a log m or log k field down into every node. After generating a root, discard unused rows and renumber the referenced slots densely per (a,c_h). There are at most min(k+1,t^2) referenced rows per local key because only t^2 remaining context pairs exist in that tile. This makes all persistent fields O(log(t+2)) bits. At every child restrict four map coordinates and translate their keys; restrict rows by the two key intervals and free quadrant; discard any rows no longer referenced by a surviving map. Renumber the remaining slots densely per key and update all references by exact sorting and merging. The child slot is a pointer to a restricted directed difference, NOT a reevaluation of the learned palette on translated digits. These operations preserve every exact exception bit. They also handle a row used by many context pairs, duplicate raw strings with different keys, and a zero row. No rank or dictionary complexity certificate.

At side t the moving persistent payload, original width<=3 lists (including all padding exclusions), counters and scratch have size O((k+1)t^4 polylog(t+2)). The row bound is actually O(min(k+1,t^2)t^4). Reserve adjacent frames using this latter bound, so no global k field needs to be copied down: for the child a capacity parameter can be obtained from the parent's local row cap and the smaller context count, or simply from the actual emitted row counts. Temporary parent-size data fit a constant multiple of the child cap because min(k+1,t^2)<=4 min(k+1,(t/2)^2). Parent remains stationary; one child is appended and popped before the next. All active frame extents form a geometric sum.

Exact positivity is a scan of rows for nonzero bits and a sort/merge of their flags with the map references. A passing row referenced by a map entry is precisely a nonempty light exception on that projected tile. This is not a full satisfiability test. Per child, fixed sequential restriction, recoding and sorting have O((k+1)t^4 polylog(t+2)) bit work and span. Copy via per-bit shuttles across the adjacent parent/child interval and simulate only the local interval, using the inherited constant-width physical encoding over 0,1,2. Positivity, all 512 child choices, copying, clearing, delimiters and success propagation charge

    O((k+1)^2 t^8 (1+log(t+2))^A)

physical moves per node. At singleton the true exception and empty original forbidden list exactly characterize a restricted model. Every such original model survives its path. No global table queries at local nodes.

## 5. Charge coarse work separately

As in the parent, enumerate K coarse blocks first and regenerate all source maps for their valid contexts, retaining <=m*b^3<=m^3 entries. Total pair generation O(m^8/b polylog m), including shuttles and learned flag joins as above. For each six-coordinate projected coarse block produce all needed root directed rows by emitting O((k+1)b^4) pairs of explicit raw bit queries, sorting and merging with original zero/one data, producing local map records, compacting used slots. Since k<=m^(1/32), this is O(m^3 polylog m) sequential bit work/span, hence O(m^6 polylog m) physical per projected block and O(m^12/b^6 polylog m)=O(m^8 polylog m) total. Install this cached root representation ONCE adjacent to the active worker, O(m^3*(k+1)b^4 polylog m) per projected block and O((k+1)m^9/b^2 polylog m) total. Root cache and active stack occupy O((k+1)b^4 polylog m) blocks, original-scale span.

For each private coarse tile, extract all original records into mobile O(b^3 polylog m) scratch, scanning the original-scale stationary span and copying to active root at cost O(m^3 b^3 polylog m). Crossing the root cache still fits the original-scale span. Copy the cached root into active slots by LOCAL shuttles, O((k+1)^2 b^8 polylog m); root test and cleanup fit same bound. Across all (M/b)^9 full tiles these two costs are

    O(m^12/b^6 polylog m + (k+1)^2 m^9/b polylog m).

The first exponent is 8. The second is at most 25/3+1/16=403/48<42/5 by the chosen k cap. Earlier installation, factor generation and pair selection are below this. Hence even with the growing palette, the complete preparation remains O(m^(42/5) polylog m) including the narrow branches. If k is fixed, wide preparation alone is O(m^(25/3) polylog m) as before. All global data and local reusable components occupy O(m^3 polylog m) visited span. Once-only reconstruction of original digits, actual pins, fixed auxiliaries and contiguous n bits at physical halt head costs O(m^4 polylog m). Exhaustion halts on blank. This accounting is conditional on inherited physical routines, not measured single-tape execution.

## 6. Rate-free amortization of palette growth

For one light wide relation R=|E_H|, rho=R/m^6, positive full-node count at side t is at most min((M/t)^9,R*(M/t)^3). Visited descendants have positive parents, hence same estimate up to constants; charge coarse roots separately. By the inherited geometric crossover at t0=M/R^(1/6), the O(t^8 local-log) cost sum is O(m^9 rho^(1/6)(1+log(1/rho))^A). With growing palettes the extra multiplier is (k+1)^2. Put X=(k+1)^13 rho. Then

    (k+1)^2 rho^(1/6) = (k+1)^(-1/6) X^(1/6).

Also log(1/rho)=log(1/X)+13 log(k+1). For 0<X<=1 the factor (k+1)^(-1/6) absorbs every fixed power of 1+log(k+1), uniformly in k. Therefore the charged density cost is O(m^9 X^(1/6)(1+log(1/X))^A). Empty relations have no positive descendants. X<=Q by definition. Near zero the latter function is increasing, up to a constant if necessary, and constant-many branches give the main theorem. This is why the exponent 13 is used instead of the critical exponent 12: one extra power absorbs local logarithms in the conversion from rho to X. No claim of optimal exponent. There is no global log m multiplying the small-Q density term. For arbitrary inputs a fallback or the exact branch traversal still gives correctness; no unconditional subcubic time claim.

If beta,delta_n,delta_w vanish and the tails are uniformly tight, fix any desired epsilon>0. Choose a fixed dyadic k large enough that limsup gamma_k<=epsilon. It eventually satisfies the production cap. At this FIXED k, (k+1)^13 lambda_k<= (k+1)^13 delta_w ->0 regardless of the speed of convergence. Since the selected minimum is no larger than this candidate, limsup Q<=epsilon. Epsilon arbitrary, hence Q->0. This argument requires neither an input-supplied k nor a uniform convergence rate. It does not exchange an unbounded k with the limit without justification.

For the entropy corollary let f_i be probabilities in nonincreasing order for a key. For every i>k, f_i<=1/(k+1), since the first i masses sum at most one. The mass outside the top k therefore satisfies tail*log2(k+1)<=sum_i f_i log2(1/f_i). Adding self can only reduce the tail. Averaging over keys gives gamma_k<=average conditional entropy/log2(k+1). A uniform entropy bound implies tightness, even if the number of distinct possible replacements per key is unbounded. Entropy is a proof criterion only, not computed by the machine.

The preceding fixed 729-slot palette promise is contained: its greedy policy in the enumeration has beta+delta+gamma_old->0 by its prior competitor comparison. The actual fixed palette for each key has at most 729 entries, so the top k learned set captures at least as much frequency mass as that palette for any k>=729. Thus gamma_k<=gamma_old and all score terms vanish at a fixed dyadic k>=729. This includes prior cases without requiring bounded entropy (rare outside-palette substitutions may have large entropy).

On Q->0 the time is o(m^9)=o(L^3). For fixed actual machine description length ell the stage 3 ceil(log2 L) allocates >=L^3/2^ell transitions once eligible. Little-o eventually fits the exact clock. No explicit compiled machine, numerical inclusion threshold, or U-stage execution supplied.

## 7. Strict separation from the immediately preceding fixed splice promise

Let m=2^(2d), q=2^d, partition the m real source labels into q balanced classes of q digits each. Denote class(a) by C(a). Use a balanced partition chosen as follows. For the parent's fixed 729-slot palette P(a,h), the probability under a uniformly random balanced partition that a given b!=a belongs to a's class is (q-1)/(m-1). For each key (a,h), union bound over at most 728 other candidates. Averaging over keys and partitions proves existence of a partition for which the fraction of keys with ANY nonself same-class candidate is at most

    728*(q-1)/(m-1) = O(1/sqrt(m)).

This is a nonconstructive existence of input arrays, not a randomized worker. Once chosen, the partition is encoded only through the actual constraints below; no partition advice is given to the worker. The bound applies to every distinguished context coordinate because the raw key ranges over all m^2 labels uniformly and the palette rule is the same.

Assign distinct nonzero binary vectors v_C orthogonal to vector 6 to the q classes; enough exist for large d. In the nine-group selector put unary zero exclusions in all groups. For each pair {0,j}, j=1..8, forbid exactly <v_(C(a)),x_j>_2=1. For every pair among 1..8 forbid <x_i,x_j>_2=1. Add only one ternary support H={0,4,5}, with F_H(a,u,v)=1{v in J}*<a,u>_2, J=[0,m/2^ell_d), where ell_d is a positive integer tending arbitrarily slowly to infinity with ell_d<2d. Put zeta=|J|/m. All arrays include the full raw domain including zero. Complete primal graph. SAT for sufficiently large d: take groups 1..8 all vector 6 and group0 vector 1; self dot of 6 zero, v_C orthogonal to 6, dot(1,6)=0, all unary exclusions pass. This is an easy SAT control, not a hardness instance.

For g=0 choose K={1,2,3}. At least five binary sections are free; between different classes the two nonzero distinct class codes are independent, so each free binary section contributes m^2/4 directed loss. Within one class all binary rows agree, including conditioned sections. Nonzero-to-zero has unary loss m^2; other unary directed losses zero. The sole wide support has directed loss zeta*m^2/4 for every distinct nonzero pair, zeta*m^2/2 from zero to nonzero, zero toward zero. Thus the full-average greedy map actually has tight tails, not just an existential low-loss competitor:

* Once a class has a selected nonzero representative, any further nonzero candidate in that class can improve only its own source, by <=zeta*m^2/4. All other source costs to the two nonzero candidates in the class agree. Its own current minimum is at most zeta*m^2/4.
* A class without a selected nonzero representative has at least q-1 nonzero sources. Their current losses are >=m^2: either a different class incurs >=5m^2/4, or target zero in the same class incurs the unary loss. Adding a nonzero candidate in that class improves at least (q-1)*(1-zeta/4)*m^2, greater than m^2 for large q. Thus while any such class is missing, the best round strictly decreases the facility score, and no duplicate nonzero representative from an already represented class is selected. Digit zero itself may be selected once.
* After all classes have a nonzero representative, every extra nonzero candidate improves by less than m^2. If zero not selected, adding it improves at most source zero, by <=zeta*m^2/2. All later marginal improvements are no larger by monotonicity. The optimal positive round therefore has one nonzero representative per class, and possibly zero.
* Before the first nonzero representative of a class is chosen, every nonzero candidate in it has the same marginal improvement: the current losses of its nonzero sources are identical and choosing a particular candidate changes only which one receives the zero self cost. Outside sources, including zero, see the same loss for any nonzero target in that class. Canonical increasing-digit ties therefore choose the smallest nonzero digit in the class, independent of context. Every nonzero source then assigns to that representative (self tie included); crossing classes or targeting zero cannot improve. Source zero may assign to self or the canonical class-zero representative, the only two possibilities, both captured by top-one plus self.

The first greedy round can be treated with all initial losses set to 37m^2; the same marginal comparisons hold, and before every missing-class round this initializer dominates the lower bounds. Hence the generated maps for the designated configuration have beta<=(q+1)/m, delta_n=0, delta_w<=zeta/4+zeta/(2m), gamma_1=0. The new theorem applies even when zeta vanishes arbitrarily slowly. The class partition need not be inferred explicitly by the solver; the distances and canonical greedy policy suffice.

The parent's fixed splice compatibility cannot hold on this family, even with arbitrary competing maps. For g=0 and ANY three-context choice, at least five binary neighbors are free, so crossing classes costs >=5m^2/4. The fraction of self assignments is <=beta. Any same-class distinct assignment within the fixed palette must occur at one of the rare (a,c_h) keys, fraction O(1/sqrt m). All other assignments either are outside the palette or cross classes. Hence

    1 <= beta + gamma_old + (4/5)delta_n + O(1/sqrt m).

For g>=1, at least one free binary neighbor among groups 1..8 remains; distinct nonzero replacements lose m^2/4 on that section and nonzero-to-zero loses m^2 on the unary exclusion. Apart from self and zero source, this precludes simultaneous vanishing beta and full loss. Thus no alternative coordinates satisfy the parent fixed-palette promise. The new learned-tail condition strictly extends that sufficient condition, including across alternative choices. It does not separate from every older solver; in particular global directed representative methods may also cover this easy family.

On the designated choice the exact lower bound delta_w >= (1-beta-1/m-delta_n)*zeta/4 holds for arbitrary maps because nonzero nonself nonzero-target assignments have that loss, self fraction <=beta, zero source fraction 1/m, and nonzero-to-zero fraction <=delta_n. Choosing ell_d=max(1,floor(log2(log2(2d+2)))) eventually makes zeta*(log m)^B diverge for every fixed B>0. This verifies that the example can have genuinely slow optimal wide loss under vanishing capacity and narrow loss. It is still not a SAT complexity lower bound.

## 8. Executed finite regression and limitations

Standalone JS audit executed in tool runtime and committed with identical Node entry point. An initial adaptation required a positive narrow-failure count within the small main fixtures; that assertion failed because those maps route all observed failures through heavy or wide branches. Rewrote the audit and added a separate narrow-only directed-bit control instead of claiming integrated narrow traversal was exercised. Sixteen fixtures at m=2,3 (eight modes), 32 passes (full greedy and forced contextual singleton maps), prescribed b=2, test all k=1..m rather than the tiny production cap. Exact frequency optimality against every subset of matching size, entropy bounds, integer score minimization, representative self ties, heavy/light recovery, full light restricted model equality, local slot compaction, original-record translation, positivity and capacity checks. Main results:

    323120 full tuple checks
    113767 successful substitutions
    5290 heavy-envelope failures
    3989 wide light failures; 3989 restricted models recovered exactly
    0 narrow-only failure occurrences in main traversal fixtures
    323328 local membership checks
    765456 positivity checks
    197664 local slot relabels
    757248 child choices, 8208 coarse roots
    776 greedy residual checks, 80 main score comparisons.

All 32 main passes used k=1 (forced passes prescribe it). Separate m=4 uniform-label synthetic map control with zero wide loss yields [k,excluded count,integer score] = [1,144,3328],[2,96,2560],[4,0,1024], so the optimizer chooses k=4. Including this control, 1376 top-k frequency checks and 608 entropy checks. Separate geometric frequency distributions at m=16,64,256,1024 have growing support, entropies below two bits, and verify the tail inequality. Separate class-distance controls at m=16,64,256 with cyclic balanced classes and five free binary sections plus unary and wide loss check every ordered distinct nonzero wide pair and run the actual one-context facility algorithm: [m,class count,pair checks,selected reps,nonself assignments] = [16,4,210,4,12],[64,8,3906,8,56],[256,16,64770,16,240]. These controls do not realize the random balanced partition separation, all 1512 coordinate choices, or all contexts of the full family. The probabilistic separation and rate-free limit are mathematical arguments, not inferred from the controls.

All revised assertions passed. The host uses arrays/maps, direct enumeration and recursive objects. It does not execute actual bit-tape sort/merge, carry shifts, physical adjacent frames, full adaptive map-policy selection, normalized encoder/verifier, compiled original-U machine or exact stage. Independent mathematical review, Lean formalization and exact-head CI remain unconfirmed.

## 9. Disposition

Frequency-tail learning removes the fixed digit-rule compatibility requirement and admits growing input-adaptive palettes under a uniform tightness condition for the computed map family. A polynomial penalty in learned palette size absorbs its physical traversal multiplier without imposing a global logarithmic convergence rate on wide loss. A random-balanced-class existence argument strictly separates the new promise from the preceding fixed splice promise. The remaining gap is proving tight tails (or an alternative resource bound) for arbitrary vanishing-capacity/vanishing-average-loss instances, not just the enumerated map policies. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
