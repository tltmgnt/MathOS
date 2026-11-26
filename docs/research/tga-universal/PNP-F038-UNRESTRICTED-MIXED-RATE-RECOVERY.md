# F038 — Mixed-rate three-context recovery with penalized exact light exceptions

PNP_RESOLUTION_STATUS = OPEN. Parent 12a69b594fde7aced18f48ee42a6e82a5148bbac (space-capped width six). Conditional mathematical machine-existence/resource derivation using inherited physical parsing, pair-sliced generation, stationary width-five trees and space-capped width-six workers. Standalone semantic/arithmetic regression executed. Not compiled original-U transitions, Lean formalization or independent review. Parent combined status and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Result and distinction from the preceding cutoff

Use the same nine-group normalized selector family, n=19m-7, L=Theta(m^3), with selected negative cross-clause bits F_H on supports of width 1..3 and the fixed one-hot/OR/pin/guard extension. Choose g and three conditioning groups K disjoint from it. For each full context c on K, choose a nonempty representative set C_c and map p_c(a) into it. Write

    d_H,c(a,b) = m^(2-|H minus ({g} union K)|)
                  * #{free contexts z: F_H(a,c,z)=0,F_H(b,c,z)=1},
    beta = sum_c |C_c|/m^4.

Use only actual conditioning digits in the support. For H containing g, call H wide if H union K has size six, i.e. H={g,u,v} with u,v outside K; otherwise call it narrow. There are ten wide and 27 narrow sections. Define delta_n and delta_w as the sums over (c,a) of the corresponding weighted losses, divided by m^6. Each section has weight m^2. A wide loss ell_H(a,b)=d_H,c(a,b) is independent of c and counts newly forbidden free pairs.

There is a fixed integer B>0 and ONE fixed deterministic original three-symbol single-tape witness machine, correct on the entire family, attaining T(L)=o(L^3) and visited span O(L polylog L) along ANY sequence admitting competitor maps with

    beta_* -> 0, delta_n,* -> 0,
    (1+ceil(log2 m))^B delta_w,* -> 0.

Only wide loss needs a logarithmic-rate restriction. Capacity and narrow average loss can tend to zero arbitrarily slowly. In particular a polynomial saving on wide loss alone suffices, with no polynomial saving required on the other two parameters. No supplied rates, threshold, coordinate choice or representatives. This does NOT establish the full arbitrary-slow three-context average-loss claim when the wide loss itself vanishes too slowly. B is an existential fixed implementation-dependent integer, not a measured numerical constant.

A separate improvement tightens the full-average greedy comparison in the parent. On the original polynomial promise beta_*,delta_*=O(m^(-epsilon)), 0<epsilon<=1, the PARENT full-average algorithm (with no threshold penalty) actually satisfies

    T(L)=O(L^(3-epsilon/15) polylog L),

with original-scale span. This replaces the previously reported conservative epsilon/30 saving by epsilon/15, without changing its executable policy. Both descriptions can coexist in the universal search.

## 2. Threshold and exact restriction recovery

Let r be a common integer threshold in R_m={0,m^2} union {2^j: j>=0, 2^j<m^2}. Define tau=r/m^2. A pair (a,b) is heavy if some wide ell_H(a,b)>r. Use the distance

    D_c(a,b)=sum_(H narrow) d_H,c(a,b) + m^2 * 1{heavy(a,b)}.

For a chosen map p define gamma as the fraction of source/context pairs with heavy(a,p_c(a)). Put s=beta+delta_n+gamma. For the minimizing maps selected below, D_c(a,a)=0 ensures that a selected representative never has a heavy assigned replacement, even if zero-distance ties map it to another digit.

Use a width-four allowed envelope A on P={g} union K consisting of representatives and heavy source/context pairs. Its density is exactly beta+gamma. For every narrow H use the usual exact exception E_H on H union K (old raw bit zero, substituted raw bit one). Their normalized densities sum to delta_n. For every wide H use the EXACT light exception on all six coordinates Q=H union K:

    E_H^light(z)=1 iff F_H(z_H)=0,
        F_H(z_H with g replaced by p_(z_K)(z_g))=1,
        AND NOT heavy(z_g,p_(z_K)(z_g)).

Unlike the threshold-union and frequency-union routes, do not project the light exceptions, or take any union over alternative representatives. Use the actual chosen map and retain all context digits. For each fixed source/context pair that is light, at most r free pairs are in this restriction, by definition of heavy. Thus every wide branch density rho_H is at most tau (and their sum at most ten tau); at r=0 all light wide restrictions are empty and may be skipped.

Every branch retains every original constraint. Given a satisfying tuple, substitute the g digit by its actual representative. If substitution succeeds the image belongs to the representative envelope. If it fails and its source/context pair is heavy, the original is in A. Otherwise any wide support newly violated by the replacement places the original in its exact light exception; a failure only on narrow supports belongs to an exact narrow E_H. All possibilities are covered, and every branch witness is original. This is exact satisfiability/witness equivalence, not necessarily preservation of all original models. It applies to unique SAT as well. At most 38 branches. No higher-width external clause or modified U interpreter.

## 3. Sharper greedy comparison

For a single context, use the inherited greedy facility procedure, with residuals initially 37m^2, adding the unused candidate minimizing the sum of updated residuals, and minimizing k*m^2+F_k over positive rounds k. Ties canonical; assign labels in round one even if the loss equals the initial bound. The distance above lies in [0,37m^2]; it need not be metric. Let a competitor set have size h>=1 and minimum total loss F_*. The sum of its individual marginal gains at residual total F is at least F-F_*. Already selected candidates have zero gain. Thus the best unused candidate decreases positive excess by at least a 1/h fraction, and monotonicity covers negative excess. This gives

    F_k <= F_*+37m^3 exp(-k/h).

Instead of the earlier square-root comparison, use in the analysis only k=ceil(h*(1+ln(m/h))). Since x*(1+ln(1/x))<=1 on 0<x<=1, this integer is at most m and at least one. Write x=h/m. Then the minimum normalized context score is at most

    x*(1+ln(1/x)) + 1/m + F_*/m^3 + 37*x/e.

Average over the m^3 contexts, using concavity of x ln(1/x), and write beta_* for the average x. With C=38 (a conservative constant) the computed score for the given g,K,r satisfies

    s <= C beta_*(1+ln(1/beta_*)) + 1/m + delta_n,* + gamma_*.

The loss of the minimum-distance map into the competing sets is at most that of any competing map, so the latter may be used on the right. This comparison requires no supplied h and does not change the selected greedy rounds. For the unthresholded full-distance algorithm, exactly the same proof gives sigma_full <= C beta_*(1+ln(1/beta_*))+1/m+delta_*. Thus under beta_*,delta_*=O(m^-epsilon), sigma_full=O(m^-epsilon log(m+2)). Applying the parent's O((m^(42/5)+m^9 sigma_full^(1/5)) polylog m) physical bound yields O(m^(9-epsilon/5) polylog m)=O(L^(3-epsilon/15) polylog L) because epsilon<=1. This is a refinement of the upper-bound analysis, not a new physical implementation or measured speedup.

## 4. Penalize light-relation size at selection time

Let ell_m=1+ceil(log2 m). All inherited resource estimates use fixed powers of logarithms. Fix A>=1 large enough to bound the global polylogarithmic exponents in the parent space-capped wide preparation and wide traversal; enlarge it if needed for the narrow local-log exponents and other overheads. Choose a fixed integer B>=4A (for example 4A+4). It depends only on the implementation, not on the input or competitor. Define Lambda=ell_m^B.

For each of the 504 choices g,K and every threshold in R_m, run the above greedy policy separately in each context and compute

    q=s+Lambda*tau.

Minimize q, using canonical tie rules. The exact integer score is m^6 q: the penalty contribution is Lambda*r*m^4. Binary lengths remain O(log m) for fixed B. Keep only the selected choice, r and score; regenerate its maps later. The machine does not compute square roots or the natural logarithms in the comparison proof.

For any competitor map, when tau>0 its heavy fraction is <=delta_w,*/tau, since the average over source/context pairs of the sum of normalized wide losses is delta_w,* and every heavy pair contributes >tau. At delta_w,*=0 choose r=0, so heavy fraction zero. Otherwise choose for comparison the smallest permitted positive r with tau>=sqrt(delta_w,*/Lambda), rounding up to at least 1/m^2. This comparison value exists for sufficiently large m because delta_w,*<=10 and Lambda grows. It has tau<=2 max(1/m^2,sqrt(delta_w,*/Lambda)). If the target is below 1/m^2 then delta_w,*/tau<=sqrt(delta_w,* Lambda) and Lambda*tau=Lambda/m^2. Otherwise the heavy and penalty sum is at most 3 sqrt(delta_w,* Lambda). Combining gives the chosen minimum

    q <= C beta_*(1+ln(1/beta_*)) + 1/m + delta_n,*
         + 3 sqrt(Lambda delta_w,*) + Lambda/m^2.

This inequality is intended for sufficiently large m; no promise of small q for every finite input. Since Lambda/m^2 tends to zero for fixed B, the mixed-rate promise implies q->0, and hence both s->0 and Lambda*tau->0. No arbitrary optimization of a coupled map objective is needed: the threshold is an outer fixed finite enumeration and the per-context distance is separable.

## 5. Physical preprocessing and exact local interfaces

Inherit the parent's fixed sequential bit-tape parsing of canonical raw bits and actual pins, factorized count tables for supports meeting zero or one conditioning groups, raw vectors for supports meeting two, and full m-by-m wide count matrices. These fit O(m^3 polylog m) span. For a threshold, form the Boolean heavy matrix as OR of comparisons ell_H(a,b)>r over the ten wide supports. Form the narrow distance contributions and add m^2 times the heavy flag in the local pair-sliced generator. Cache extraction, aligned unretained-coordinate streams, nested mobile residual arrays, greedy passes and output shuttles have the same bounds as the parent: O(m^5 polylog m) original physical moves for all m contexts of one retained pair, O(m^7 polylog m) for all pairs. Threshold enumeration adds only O(log m), charged to preprocessing. All choices count is fixed. No global m^4 map. The required heavy flag for each actual chosen source/representative pair is attached before its pair spool is discarded, by matching against the saved wide counts; the output increases by one bit per source. This does not change the inherited pair generator exponent.

For A and narrow E_H use the parent's shared context-block map regeneration and stationary width-four/five worker. The envelope membership is the representative flag OR heavy flag, narrow membership is the two raw queries using the chosen map. The coarse width is the largest dyadic b0 satisfying b0^5<=m^3. The stationary tree is reused over private coarse blocks. This yields O(m^(42/5) polylog m) preparation and O(m^9 s^(1/5)(1+log(1/s))^A) density cost near s=0; all densities <=s, and no global log multiplies this density term. Empty restrictions skip descendants. Visited span O(m^3 polylog m). This is the same worker used in the previous hybrid theorem, not an assumed new solver.

For each nonzero-threshold wide branch use the space-capped width-six worker from the parent but replace its scale parameter sigma by

    eta=max(1/m,tau).

This is allowed because its proof uses the parameter solely as an upper bound for the branch density and as a scale selector with 1/m<=eta<=1. It does not require that it equal a facility score. Choose initial b as largest dyadic with b^16 eta<=m^8, fallback width largest dyadic w with w^2<=m. The exact count certificate on a projected block of side v is v^6 R_block<=m^6. Count before allocation; heavy blocks refine to w. Here a heavy BLOCK in this tree allocation sense is distinct from a heavy SUBSTITUTION pair in Section 2. The light exception membership oracle is the parent's local factorized formula with an additional test of the stored heavy flag:

    (1-F_H(a,x,y))*F_H(p_(d,e,t)(a),x,y)*(1-heavy(a,p_(d,e,t)(a))).

The local map cache contains the flag as well as the representative for each relevant (a,d,e,t). Include original raw rows for EVERY representative digit, not just source interval digits. The count and builder scans are still O(v^10 polylog m) physical work per block, because cache sizes remain O(v^4+m*v^2)=O(v^4) records for v>=w. No global m^6 table. The parent's cap, initial and fallback preparation census, and local Cauchy-Schwarz traversal apply to this actual allowed relation without modification; each has rho_H<=tau<=eta. Thus wide preparation costs O((m^(33/4)+m^9 eta^(1/4)) ell_m^A) and traversal O(m^9 sqrt(tau) ell_m^A), with O(m^3 polylog m) visited span. Count/build for a zero threshold can be omitted because all light restrictions are empty. The fixed product-alphabet, constant-width encoding over actual 0,1,2, reusable stationary components and physically charged mobile shuttles are inherited, not free RAM access. The local tree need not read original-scale data at each node.

## 6. Charge logarithms only to the quantity constrained by the threshold

For the computed q sufficiently small, s<=q and tau<=q/ell_m^B. Then

    eta^(1/4) ell_m^A
      <= m^(-1/4) ell_m^A + q^(1/4) ell_m^(A-B/4)
      <= m^(-1/4) ell_m^A + q^(1/4),

    sqrt(tau) ell_m^A
      <= sqrt(q) ell_m^(A-B/2) <= sqrt(q).

This is the reason to penalize tau rather than the whole facility score by a growing logarithm. With a constant number of branches, the complete time is

    O(m^(35/4) polylog(m+2)
      + m^9 q^(1/5) (1+log(1/q))^A).

The m^(35/4) term includes the eta floor m^9*m^(-1/4), earlier preparation, selection and once-only reconstruction of original one-hot/OR/guard and actual pins, with contiguous n-bit output and physical halt head at the first bit. Use halt on blank on exhaustion. Near zero, the narrow density expression is monotone up to constants, and q^(1/4),sqrt(q)<=q^(1/5), giving the displayed bound. Outside small q the procedure remains exact, with the inherited O(m^9 polylog m) upper bound; no claim of unconditional exact cubic or unconditional additive-stage slack from this worker. All phases sequentially reuse original-scale components.

Under the mixed-rate promise q->0, the displayed runtime divided by m^9 tends to zero. Since L=Theta(m^3), the fixed program's actual description length ell receives >=L^3/2^ell transitions at stage 3 ceil(log2 L) once eligible. The little-o bound eventually fits the exact allocation. Neither B, ell nor the numerical inclusion threshold is supplied as an explicit compiled-machine constant. The derivation establishes an existence cutoff conditional on the inherited physical routines, not measured original-clock performance. It also implies an implementation-dependent positive threshold on computed q for sufficiently large actual exact cubic SAT misses, if any exist; no such misses are constructed.

The mixed-rate promise includes, for example, capacity and narrow loss bounded by 1/log log m with wide loss bounded by 1/m. Such parameter rates are not in the prior all-polynomial promise. These are illustrative admissible parameter bounds, NOT a construction proving that some family necessarily has these best achievable rates or that previous algorithms fail on it. The theorem also includes arbitrary slow narrow loss when wide loss is zero, a case already covered by prior hybrid routes. The genuinely new range allows positive wide losses with dense projections, provided the wide average obeys the stated logarithmic rate. When wide average loss vanishes arbitrarily slowly without a logarithmic margin, the penalty bound need not tend to zero; the remaining critical width-six traversal and density-dependent preparation global logs are not removed in that generality.

## 7. Executed finite checks

Standalone JS audit executed in the tool runtime; identical function committed with Node entry point. Initially the fixtures did not exercise simultaneous heavy/light failure recovery in a single pass, so an extra asymmetric ternary fixture was added and the audit rerun with a required positive count of such passes. Eighteen fixtures at m=2,3 across nine modes, with supplied g=0,K={1,2,3}, enumerate 90 threshold choices. Use a test penalty exponent one for score mechanics (not the production exponent B). Check exact greedy residuals, marginal inequalities against all competing subsets, sharper entropy-style comparison, integer score identities, exact narrow mass, full wide mass partition into discarded-heavy and exact-light entries, each light density bound, zero-threshold emptiness, representative envelope size, and witness recovery by exhaustive original tuple enumeration.

Selected maps: 501 representative occurrences, 62 heavy flags, zero light-wide entries, 116 discarded-heavy wide entries, 71,498 original satisfying tuple occurrences, 36,659 original model occurrences already in some branch, 68,518 successful substitutions, 2,980 heavy-envelope failures recovered, and 181,755 full tuple checks. Forced singleton maps at every threshold: 1,746 representative occurrences, 352 heavy flags, 5,040 light-wide entries, 2,424 discarded-heavy entries, 425,528 original model occurrences, 204,717 original model occurrences already in a branch, 387,876 successful substitutions, 9,665 heavy-envelope failures, 17,298 exact-light wide failures, 10,689 narrow-only failures, and 1,081,314 full tuple checks. Two forced passes exercise both heavy and light failure routes simultaneously. Classifications follow priority, not necessarily disjoint branch sets. There were 11,070 sharper greedy comparison checks and 32,346 marginal-gain inequalities.

An independent arithmetic loop for every m=2..512 at eight loss masses (including zero) checks the dyadic comparison threshold, rounding and penalty bound, with test exponent eight and exact integer comparisons for the scale. 4,088 cases. Floating point is used only for numerical verification of inequalities with tolerances; the actual algorithm uses integer score selection. An illustrative rate table tests the arithmetic example beta=delta_n=1/log2(k), delta_w=2^-k, m=2^k, for k=8,16,32,64,128. This is not a generated instance family. All corrected assertions passed.

The host audit uses arrays/maps, indexed lookup and direct enumeration; it does not execute the full 504 coordinate selection, the pair-sliced physical generator, the physical space-capped or stationary-tree worker, compiled transitions, normalized verifier integration or exact U stage. The production log exponent B is not determined numerically. No independent review, Lean formalization or exact-head CI confirmation.

## 8. Disposition

Decoupled wide-loss threshold selection establishes arbitrary-slow capacity and narrow-loss recovery with sufficiently fast logarithmic wide-loss decay, at original-scale span. Sharper greedy comparison also improves the prior all-polynomial exponent guarantee. Arbitrarily slow wide average loss itself remains OPEN. Next target: remove the remaining dependence on a global logarithmic rate for width-six loss, by improving the underlying wide traversal/preparation rather than shifting the penalty onto another parameter. General unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
