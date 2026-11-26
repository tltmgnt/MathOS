# F038 — Locally bounded context sketches for three-context recovery

PNP_RESOLUTION_STATUS = OPEN. Parent 0ad2767f5da3dc1ba3d286a58a0d24549a422914 (split tail unions). Conditional mathematical machine-existence/resource derivation using inherited original parsing, pair-sliced map generation, fixed-track sweeps, mobile carry shifts, stationary width-five workers and adjacent spatial frames. Executed host semantic audit, not a compiled original-U implementation, independent mathematical review or Lean formalization. Parent combined status and PR-triggered runs empty; push CI unconfirmed.

## 1. New result: retain a function of all three contexts

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), actual selected negative cross-clause support bits F_B for widths one through three and fixed one-hot/OR/pin/guard extension. Choose compressed group g and three conditioning groups K with ordered context c=(c1,c2,c3). For nonempty contextual representative sets C_c and maps p_c(a) into them, beta=sum_c |C_c|/m^4 and delta=delta_n+delta_w are the inherited full weighted average losses divided by m^6. For wide H={g,u,v}, with u,v outside K, Z_H(a,b;x,y)=(1-F_H(a,x,y))*F_H(b,x,y); ell(a,b)=sum_H |Z_H(a,b)|. At most ten wide supports.

A retained *sketch* need not be one of the actual coordinates. Set d=ceil(log2 m), M=2^d. Use the following fixed finite family of uniform binary sketches:

* any of the three coordinate projections, represented by assigning all d bit positions to one conditioning digit;
* partition either all d positions, or the lowest d-1 positions, into three consecutive blocks of sizes differing by at most one, with boundaries floor(i*w/3), i=0..3, where w=d or d-1. Assign the three blocks to the three conditioning digits in any of the six permutations. In the second case set the highest bit to one.

In both cases masks B_i are disjoint, covering all positions except possibly the reserved high bit. The output is

    S(c)=f OR (c1 AND B1) OR (c2 AND B2) OR (c3 AND B3),

with f=0 or M/2. It is a key in [0,M), NOT necessarily a real digit or an actual replacement. All c_i in the learning phase are real digits [0,m). Let q(s)=#{c:S(c)=s}. Fibers may be unbalanced for m not a power of two. On the full padded domain the preimage count of any attainable s is M^2 (no reserve) or 2M^2 (reserve), since each output bit fixes exactly one input bit except the reserved bit. Thus q(s)<=2M^2=O(m^2) always. Also sum_s q(s)=m^3.

For each generated map of the parent's finite policy family (full-average facility greedy and fixed six-block-splice-penalized greedy), choose selected representative self ties. Learn the head P_(a,s) from the k highest-frequency actual replacement labels in the sketch fiber, plus self. Let n_(a,s)(b) count these assignments over actual contexts with S(c)=s. Ties by increasing b. Use k=0 or dyadic 1<=k<=m^(1/32), and r=0, powers of two below 10m^2, and 10m^2. The low tail consists of positive-frequency labels outside the head with ell(a,b)<=r; high tail the other positive-frequency labels outside the head. Write n_low,n_high for their assignment counts and U_(H,a,s) for the exact union of directed differences over low-tail labels on H. Let v=sum_H |U_(H,a,s)|.

Choose union or envelope separately per key: use union iff

    q(s)*v <= m^2*n_low.

If union is not used set its rows to zero. Always route the high tail through the envelope. In units of 1/m^6 the cost is

    m^2*n_high + min(m^2*n_low,q(s)*v).

This corrects for unbalanced fibers; an unweighted union density would not be appropriate for a general sketch. The old one-context rule is exactly the special case q(s)=m^2. Let gamma=heavy count/m^4 and eta=(sum_(H,a,s) q(s)*|retained U_(H,a,s)|)/m^6; let lambda be the actual head wide loss normalized by m^6. Compute

    Q_S = beta + delta_n + gamma + eta + (k+1)^13 lambda.

There is ONE fixed deterministic original three-symbol one-tape witness program correct on the entire family, selecting the minimum exact score over g,K, the finite sketch/policy choices and k,r. Its charged bound for sufficiently small positive computed Q_S is

    T(m)=O(m^(26/3) polylog(m+2)
             + m^9 Q_S^(1/6)(1+log(1/Q_S))^A),
    visited span O(m^3 polylog m).

A is fixed and implementation-dependent. In particular Q_S->0 implies T(L)=o(L^3), visited span O(L polylog L), and eventual exact cubic-stage witness inclusion. There is no supplied sketch, factorization, map, rate or threshold. The prior split-union solver can additionally be included in the same fixed program: compare its score Q2 against the sketch minimum, run the winning worker, and replace 26/3 by max(26/3,44/5)=44/5 in preparation. This combined variant weakly dominates both prior score minima, not their pointwise running times. The sketch worker alone includes the one-context parent but need not dominate every two-context score.

The crucial property is not merely that S has O(m) possible outputs globally. On every aligned dyadic context cube of side t the sketch has at most t possible outputs and its local representation can be clipped without carrying global labels. That property enables recovery even for maps which depend on all three context digits. This is a new structural sufficient condition, not a deduction from arbitrary beta,delta->0.

## 2. Witness recovery and score meaning

Retain every original constraint in each branch. Use the width-four envelope on {g} union K containing all selected representatives and heavy assignments (disjoint because representative self ties are in the head). Keep each exact narrow exception on B union K. For each wide H include

    E_H^head(a,c,x,y) = 1{p_c(a) in P_(a,S(c))}*Z_H(a,p_c(a);x,y),
    E_H^union(a,c,x,y) = retained U_(H,a,S(c))(x,y).

Both wide predicates are considered on six actual projected coordinates. The latter can enlarge the actual tail exception set; all original constraints are still enforced. It is not inserted as a clause into the external selector. Its exact expanded cardinality is sum_(a,s) q(s)*|retained U_(H,a,s)|, since all q(s) actual contexts have the same union row. Head cardinality equals its actual directed loss count. Both normalizations use m^6; the envelope uses m^4. This proves the weighted comparison in Section 1, including q(s)=0, which has no assignments and can be omitted.

Given an original satisfying tuple, replace its g digit by the selected representative. A successful substitution yields a model in the envelope. If it fails on a heavy assignment the original is in the envelope. Otherwise a newly violated narrow support places it in the exact narrow branch, or a newly violated wide support places it in the head guard or its retained union. Every recovered tuple is original. At most 48 branches. This preserves witness existence, not equality of all original/substituted model sets. The union branch model set is exactly the intersection of the original model set with the expanded sketch-union guard.

A rate-free sufficient condition is the analogous tightness of the *weighted union charge*: for a generated map and sketch, let tau_k=(1/m^6) sum_(a,s) min(m^2*n_tail,q(s)*v_tail) at r=10m^2. If beta,delta_n,delta_w->0 and lim_(k->infinity) limsup_(m->infinity) tau_k=0, then Q_S->0. Indeed fix a dyadic k with limsup tau_k arbitrarily small; it eventually passes the production cap, and at this FIXED k the head term tends to zero. Take the minimum before taking limits. No uniform convergence rate is used. Uniformly tight replacement frequencies conditioned on (a,S(c)) are sufficient, but not necessary. The finite policy family and sketches are fixed; no optimization over arbitrary maps or sketches is asserted.

## 3. Exact learning within original-scale span

Inherit the O(m^5 polylog m) pair-sliced generator for all m values of the unretained context for a retained pair, and full map generation O(m^7 polylog m) with O(m^3 polylog m) span. Raw directed-count tables and original actual pin parsing are inherited. Both parent policies are retained, including the splice penalty computed on the corresponding local distance records. When the penalty depends on the varying context coordinate, evaluate it within each local context matrix using fixed polylog bit work per candidate/source record. This does not change the pair bound. The maps are not reoptimized after learning.

Compute q(s) by enumerating the m^3 actual contexts, evaluating the fixed sketch by binary scans, sorting by key and counting. Sequential O(m^3 polylog m) bit steps, physical O(m^6 polylog m) using inherited full-span sweep. For each s with q(s)>0, regenerate the full map stream (O(m^7 polylog m)), keeping only assignments whose context has that sketch. Filter pair outputs before appending to the fiber spool. The spool holds m*q(s)<=2m*M^2=O(m^3) records, including representative flags and narrow/wide loss metadata. Even per-record output shuttles across original-scale span cost O(m^6 polylog m) per fiber. Join chosen labels with the raw pair loss counts, sort by (a,b), count frequencies, sort by (a,-count,b) and extract head and tail labels. These operations on O(m^3 polylog m) bits cost O(m^6 polylog m) physically. At most M=O(m) fibers; the deliberately conservative regeneration costs O(m^8 polylog m) in total. No global m^4 map table.

For each (a,s) form each wide union row by scanning all target raw rows with the current low-tail flags, computing the aligned old-zero/new-one OR into an m^2-bit accumulator; use a sequential bit routine of O(m^3 polylog m) work and original-scale span, followed by the inherited sweep charge O(m^6 polylog m). At most m*M=O(m^2) keys, constant supports, so O(m^8 polylog m) total. Count each union row, apply the weighted key comparison, sum head actual losses, narrow losses and capacities. Keep no global union array. Repeat for logarithmically many k,r and constant-many coordinate/policy/sketch choices. All integer scores use O(log m) bits with fixed exponent 13. The total O(m^8 polylog m) score preparation is strictly subcritical.

Regenerate the winning policy/keys and retain the head labels and low-tail membership flags, with at most O(m*M*m)=O(m^3) records, including the union decision. Missing flags false. Store q(s) and outer identifiers. For later map generation attach head slot/route flags by a sequential sort/merge of one retained pair's m^2 map records keyed (a,S(c),b) with this stationary O(m^3) flag table. Even charging a full original-scale sweep for this O(m^3 polylog m) sequential merge gives O(m^6 polylog m) per pair occurrence. This is deliberately weaker than the prior pair-local flag join, and must be charged at coarse initialization. For each K coarse block of side b, regenerate each retained pair inside it and keep only assignments for its remaining context interval. The block spool is at most m*b^3<=m^3 records at the head coarse scale b=Theta(m^(2/3)), and also at the narrower scale b'=Theta(m^(3/5)). Each pair occurs at most O(M/b) times across the K blocks; total O(m^9/b polylog m) (or O(m^9/b' polylog m)=O(m^(42/5) polylog m) for narrow/envelope). Hold each block spool across all its other projected coarse intervals; no regeneration for every private tile. For narrow and envelope guards the other inherited query, stationary tree and extraction charges are unchanged, O(m^(42/5) polylog m).

## 4. Local sketch identity, including padding

For aligned context intervals with lower offsets o_i multiples of side t=2^j, write c_i=o_i+z_i, 0<=z_i<t. These additions have no carry from low to high bits. Define B_i(t)=B_i AND (t-1) and

    s0 = S(o1,o2,o3),
    s_local(z) = OR_i (z_i AND B_i(t)).
    S(c) = s0 OR s_local(z).

The bit fields of s0 and s_local are disjoint: the reserved bit is not in any mask, and every varying mask bit is below j. There are at most t possible local keys, even though S can depend on all three actual digits. In the full padded local cube, a local key has at most 2t^2 preimages (at most one unassigned reserved bit); actual prefixes can only reduce this count. For each context coordinate keep the number L_i of real digits in its local interval, 0<=L_i<=t. Real local context digits are precisely 0<=z_i<L_i. To prevent false positive pruning counts, compute the exact set of attainable local sketch keys over those real prefixes. One may enumerate at most t^3 contexts and mark their keys in a length-t Boolean list; even linear scanning the flag list to mark a bit costs O(t^4 polylog(t+2)) sequential work, O(t polylog t) auxiliary span besides the local frame. If any L_i=0 the attainable set is empty. Do not infer all low keys are attainable at non-power-of-two m.

At a dyadic child of side u=t/2, its three context offsets are eps_i*u with eps_i in {0,1}. Put q=OR_i ((eps_i*u) AND B_i(t)); q is either 0 or u. Parent local keys for this child have high bit q, and the child key is their low part AND (u-1). Child masks are B_i(u); real lengths L'_i=max(0,min(u,L_i-eps_i*u)). Recompute exact attainable keys for these lengths. Every actual child sketch is exactly parent key q OR child key. The reserved fixed bit never varies. Source/free intervals and padding are also clipped as usual. Neither global s0 nor global mask widths need be carried into descendants: truncate masks and use local keys and lengths. The outer root alone knows global offsets and original m. This is an exact restriction identity, not a hash collision or approximate coordinate transform of the original formula.

## 5. Compact wide root frames and charged preparation

Use b largest dyadic with b^3<=m^2, b=Theta(m^(2/3)), divides M. In each projected six-coordinate coarse block on (a,c1,c2,c3,x,y), there are at most b^2 real (source,local sketch) keys. For a union branch extract the actual low-tail flags for these global (a,S(c)) keys and the m*b^2 raw bits on the chosen free intervals for ALL real row digits, including representatives outside the source interval. Prepare by exact sequential sort/merge and original-scale scans; O(m^3 polylog m) bit work/span. For each of the at most b^2 keys, copy the old restricted row and its m flags, then scan all restricted target rows in order and OR their directed differences into a b^2-bit accumulator. Even retrieving each key's data by scanning the full restricted cache fits O(m*b^2 polylog m) sequential work per key. Only attainable keys retained; source and free padding zero. The result is O(b^4) union bits. Total sequential work per projected block O((m^3+m*b^4) polylog m), span O(m^3 polylog m). Apply the original-scale sweep bound: O((m^6+m^4*b^4) polylog m) physical time per block. Across (M/b)^6 projected blocks this costs

    O((m^12/b^6 + m^10/b^2) polylog m)
      = O(m^(26/3) polylog m).

This is the new cost of preparing skewed union guards without storing a global six-coordinate array. Regenerating a full m^2 union row per local key would be unnecessarily expensive. The restricted cache scan is essential.

For head branches use the winning K block spool from Section 3. At most b^2 keys times k+1 head slots, each with b^2 free bits. Generate exact directed rows by explicit old/new raw bit queries, sort/merge against the original raw array (including zero bits), and join the map records for this projected block by their local (a,sketch,slot) reference. The global keys/labels used only during root preparation. O((m^3+(k+1)b^4) polylog m)=O(m^3 polylog m) sequential work/span, since k<=m^(1/32). Physical O(m^6 polylog m) per projected block, O(m^8 polylog m) total. Root compacting discards unused rows and renumbers used slots per key. There are at most 2b^2 relevant actual context tuples for one local sketch, so local slot labels have O(log(b+2)) bits. Do not recompute the original replacement digit from a translated sketch.

Install each cached root payload immediately adjacent to the active worker once per projected coarse block, with cost O(m^3*(k+1)*b^4 polylog m) (union uses k+1=1). Across all projected blocks this is O((k+1)m^9/b^2 polylog m), below m^8. Reuse cache for all (M/b)^3 private coarse choices. For each full coarse tile extract ALL actual original width<=3 selected records and padding units by the inherited mobile O(b^3 polylog m) scratch scan over original-scale stationary data, O(m^3 b^3 polylog m) moves. Copy cached root by LOCAL per-bit shuttles across adjacent interval, O((k+1)^2 b^8 polylog m). Mandatory root tests, clearing and counter work fit same bound. Across (M/b)^9 tiles these terms are O((m^12/b^6+(k+1)^2 m^9/b) polylog m), at most O(m^(403/48) polylog m) for head and O(m^(25/3) polylog m) for union. The map/flag regeneration O(m^9/b polylog m), head query cost and narrow/envelope preparation are also below 26/3. No global scan per local recursive transition. All raw, learning, cache and active worker components fit O(m^3 polylog m) span, including b^4(k+1) local payload and local scratch. Only one branch/tile at a time.

## 6. Local exact traversal and local-log bound

Use the parent's adjacent spatial frame architecture. For a union branch store the O(t^2) attainable (source,local sketch) rows of t^2 bits, original list O(t^3) records, masks, real lengths, local offsets and scratch. Positivity is exactly whether any such row has a one, because every retained sketch is attainable by some real context tuple and source and free intervals are independent. This ignores original constraint compatibility for pruning, not for acceptance. Each child restricts source interval, the sketch high bit and child attainability, and both free intervals; translates local source and sketch fields; clips and translates original singleton records. The exact child union guard follows from Section 4. The local work and span of sequential restriction, key computation, sorting and attaining flags are O(t^4 polylog(t+2)); inherited local sweep/copy charge O(t^8(1+log(t+2))^A) physical moves. Includes fixed 512 child choices, parent/child navigation, clearing and success offsets. One child appended adjacent to its stationary parent, popped before the next. The active frame capacities sum geometrically, no retained explored subtrees.

For a head branch also store at most t^4 actual light map entries on four actual coordinates, each referencing one of O(min(k+1,2t^2)*t^2) local rows. Restrict map keys and sketch/free rows together; discard unused rows, densely renumber references by exact sequential sort/merge. Recompute local sketch fields from translated coordinates or clip their low bits; both are equal by the identity. All persistent fields are O(log(t+2)) bits, including local slot labels. No global log m or k copied to small descendants. Positivity is a referenced nonzero row via exact merge of flags and references, not a check of all original constraints. Local payload O((k+1)t^4 polylog(t+2)), charged physical work O((k+1)^2*t^8*(1+log(t+2))^A). Temporary parent-size data fit a fixed multiple of child capacity using min(k+1,2t^2) bound; constant-width encoding of a fixed finite product alphabet over actual 0,1,2. No input-dependent alphabet or extra physical head. At singleton the true guard and empty original list characterize exactly an original restricted model. Recover digits while unwinding, restore actual coarse offsets and pins, reconstruct actual original auxiliaries, emit n contiguous bits at physical halt head; exhaustion halts on blank. Once-only output O(m^4 polylog m).

For either wide guard write R for its *expanded real* six-coordinate cardinality and rho=R/m^6. The attainable-key restriction ensures that a positive projected cube contains a real guarded projected tuple. Thus positive full nodes at side t number <=min((M/t)^9,R*(M/t)^3); visited descendants bounded up to fixed factors by positive parents. Roots already charged separately. Multiply by t^8 local-log work, split the dyadic sum at t0=M/R^(1/6) for R>=1. Geometric exponents 1 and 5 absorb local log growth, yielding O(m^9 rho^(1/6)(1+log(1/rho))^A). Empty guards no positive descendants. The union cannot use the literal width-four exponent 1/4 because its guard is on six actual coordinates; use 1/6. For head, multiply by (k+1)^2 and set X=(k+1)^13 rho, absorbing log(k+1) powers with (k+1)^(-1/6) as in the parent. Each union density <=eta, each head X<=(k+1)^13 lambda. Narrow/envelope exponent 1/5 stronger near zero. Constant-many branches give the main bound; no global log m multiplying the small-Q term. Outside promise the branches or inherited exhaustive solver still correct.

For Q_S->0 all preparation exponents are strictly below nine, so T=o(m^9)=o(L^3). For fixed actual original program description length ell, stage 3 ceil(log2 L) allocates at least L^3/2^ell moves once eligible. The little-o bound eventually fits this allocation. No explicit ell, numerical threshold, compiled transition table or actual U-stage run supplied.

## 7. Strict score separation: maps depending on all three context coordinates

Take m=2^d, binary vector labels identified with GF(m), d large. Use the reserve-high-bit sketch with w=d-1, blocks B1,B2,B3 as in Section 1, f=m/2. Let target b0=S(c), necessarily nonzero, and let J be a linear subspace of codimension l, with l positive and tending arbitrarily slowly to infinity (e.g. floor(log2(log2(d+2))) eventually). Put zeta=|J|/m=2^-l. For g=0,K={1,2,3}, put unary forbidden digits on g exactly those with high bit zero (includes zero); unary zero exclusions on other groups. On each support {0,i}, i in K, forbid a whenever (a AND B_i)!=(c_i AND B_i). These are genuine binary supports, and their intersection together with the unary support forces the unique g digit b0. Add a single wide H={0,4,5}:

    F_H(a,x,y)=1{a*x+y in J}.

Other cross supports empty. All bits on full domains are defined, including zero. The family is SAT for large m: choose nonzero conditioning digits, a=b0, nonzero x, choose nonzero y outside the forbidden coset (there are m-|J| possibilities), all others nonzero. Easy SAT control, not a hardness or complete-primal-graph instance.

For every a!=b the field map (x,y)->(a*x+y,b*x+y) is bijective, hence directed loss is D=|J|*(m-|J|)=m^2 zeta(1-zeta), including pairs involving zero. For every context target b0 has zero narrow directed loss from every source, because it satisfies every narrow bit. Every other target has strictly positive total narrow loss (at least one source, namely b0, would acquire a forbidden bit). Summed wide loss is (m-1)D for EVERY target. Thus b0 is the unique first full-average greedy representative. Afterward any extra candidate improves only its own source, by at most D<m^2, since all other wide losses remain D and narrow losses cannot be negative. Further marginal gains nonincreasing. The actual selected positive round is singleton b0, p_c(a)=S(c) for all a. Beta=1/m, delta_n=0, delta_w=(1-1/m)zeta(1-zeta). For ANY contextual maps on this configuration, self assignments account for at most beta of all assignments, so delta_w >= (1-beta)*zeta(1-zeta). The loss can genuinely vanish arbitrarily slowly under vanishing capacity; no fixed polynomial loss rate is required.

For any choice of two actual retained context digits, the omitted digit varies over its block W of dimension j>=floor((d-1)/3) in the target. With retained digits fixed, the target set B is an affine translate of W, |B|=2^j, and every label occurs m/|B| times in the final fiber. The preceding two-retained solver's head includes at most k+1 labels per first-context key, hence captures at most (k+1)/|B| of this fiber, tending uniformly to zero for k<=m^(1/32). Self is always in head, so all tail substitutions are distinct and have loss D. For threshold r<D the heavy fraction is 1-o(1).

For r>=D all tail labels are low. Let pi:GF(m)->GF(2)^l be the quotient map with kernel J. For a fixed nonzero functional phi on the quotient, x such that phi(pi(xw))=0 for every w in W form a subspace of size m/|W|. Indeed the pairing (x,w)->phi(pi(xw)) is nondegenerate on the full field: for each nonzero w multiplication by w is bijective and the composed linear functional is nonzero. Restricting the pairing to W gives a surjective map from the field to W*, so the annihilator has dimension d-j. If pi(xW) is not the full quotient, some nonzero quotient functional annihilates it. Union bound: at most (2^l-1)*m/|W| values x fail surjectivity. For all other x and every y, exactly |W|/2^l targets b in B satisfy bx+y in J. For the slow chosen l this count exceeds k+1 uniformly in the production cap. Deleting the head labels cannot delete all of them. Thus for each good x every old-zero y (exactly m-|J| of them for every source a) lies in the low-tail union. Its cardinality is at least

    m^2 (1-(2^l-1)/|W|)*(1-zeta).

This tends uniformly to m^2 in relative size. Also m*n_low>=m^2*(1-(k+1)/|W|). The previous per-key minimum min(m*n_low,v) divided by m^2 tends to one for every key, every retained pair and every r>=D. Consequently the immediate parent's Q2 is bounded away from zero for all its k,r and retained choices on the designated generated maps. The obstruction is not based on merely high entropy or artificial inefficient representative sets.

For the new sketch choose precisely S and k=0 (head self), r=10m^2. For each (a,s) the only actual replacement is s. If a=s no tail, otherwise union exactly Z_H(a,s) with size D, and n_low=q(s). Since D<m^2 the weighted comparison selects union everywhere. No heavy or head-wide mass. Therefore

    Q_S = 1/m + (1-1/m)*zeta*(1-zeta) -> 0.

This is strict separation of the computed sufficient conditions on these actual greedy maps with all choices of two retained actual context coordinates. It is NOT separation from the prior full adaptive solver across other compressed groups or map policies (the example is easy and sparse), or from all earlier algorithms. No computational lower bound. It shows precisely why a locally bounded function of all three context digits can retain information that two literal digits lose.

## 8. Executed host semantic regression

Standalone JS audit executed in the tool runtime, identical function committed with Node entry point. Sixteen fixtures m=2,3 across eight modes, 48 passes (full greedy and two forced singleton policies to exercise distinct routes), designated g=0,K={1,2,3}, balanced bit-splice sketch with and without reserved high bit. Prescribed b=2, k in {0,1,2}, r in {0,1,10m^2}, not production cap. Compute actual unbalanced q(s), head/low-tail flags, weighted score and expanded recount, original-model recovery, compact head and union rows and exact local clipping, slot relabeling, positivity and original-record clipping. For H={0,4,5}, compare complete recovered head/union branch model sets with direct enumeration. Other wide supports included in exact score and recovery checks but not traversed separately in this regression. Counts:

    2,784 weighted key score and fiber checks each
    215,760 exact union bit checks
    776 greedy residual checks
    484,680 full tuple checks
    170,527 successful substitutions
    5,263 heavy-envelope failures
    1,004 head-wide failures
    6,736 union-tail failures
    1,039 narrow failures
    1,006 recovered head-branch model occurrences
    7,125 recovered union-branch model occurrences
    1,560 projected root constructions
    1,304,600 local positivity checks
    2,080,256 projected membership comparisons (both predicates)
    1,292,288 full child choices
    199,520 slot relabels.

All revised assertions passed. Independent padding/clip control uses m=3,5,9,17, both reserve modes, every aligned dyadic context tile and its children: 85,568 child checks, exact sketch identity for every real local context, at most t attainable keys and exact child subset translation. No global padded context used to assert positivity. Independent finite-field controls at m=64,512 verify every nonzero multiplication map is a permutation, count bad x by quotient image, verify uniform fibers when surjective and direct old-zero union coverage for source zero and one affine target block per omitted coordinate, then test the unique first greedy choice and all possible second marginal gains for one full context. Output [m,|J|,D,x tests,[[block size,bad x,union hits] for each omitted block],target]:

    [64,32,1024,192,[[2,32,1536],[4,16,1792],[4,16,1792]],45]
    [512,256,65536,1536,[[4,128,114688],[8,64,122880],[8,64,122880]],363]

The finite control uses l=1 and k=0, not the slow asymptotic sequence or all contexts. During review removed an extra zero-target penalty from the separate control to match the single unary forbidden-high-bit support in the proof, added the unbalanced-fiber bound assertion and reran the audit; counts unchanged. The mathematical field loss identity and bad-x asymptotics are analytic, not inferred from the small tests.

The host uses direct enumeration, arrays/maps, indexed queries, recursive objects and finite-field bit operations; it does not implement all-choice policy/score selection, physical sorting, actual carry shifts, serialized adjacent frames, original normalized encoder/verifier, compiled U transitions or exact universal clock. No measured single-tape transitions, independent review, Lean formalization or exact-head CI confirmation.

## 9. Disposition

Locally bounded context sketches replace literal retention by a uniform function of three context coordinates, preserving O(t^4) local union payload and original-scale visited span. A weighted charge accounts for actual sketch fiber sizes, and exact attainable-key pruning handles padding. The new control defeats the two-retained tail unions for all retained-coordinate choices on the designated actual greedy maps, even with genuinely slow loss. The result still depends on the finite sketch family and generated-map score. Arbitrary maps can depend on context combinations without any of these sketches having a small union/tail score. Next investigate input-adaptive locally bounded sketches, or a rigorous obstruction to deriving such a sketch from small average loss alone. Unrestricted arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
