# F038 — Canonical slab/run-coded local correction recovery

PNP_RESOLUTION_STATUS = OPEN. Parent 888067500d2880c0864c18bd76d90dfdb4582b69 (local correction quotients). Mathematical resource-accounted derivation conditional on inherited original parsing, pair-sliced maps, fixed-track sweeps, mobile carry shifts, adjacent spatial stacks and original-record fallback. Executed host semantic regression. Not a compiled original-U machine, independently reviewed proof or Lean formalization. Parent combined status and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Result

Retain the nine-group normalized selector family n=19m-7, L=Theta(m^3), actual width<=3 negative cross bits and original fixed one-hot/OR/pin/guard extension. Choose compressed group g, three conditioning groups K, generated representative sets C_c and actual maps p_c(a) with representative self ties. Use inherited beta, delta_n and delta_w. For a wide support H={g,u,v}, u,v outside K, use either the direct guard E(a,c,x,y)=(1-F_H(a,x,y))*F_H(p_c(a),x,y), or the parent's exact missing-bit guard with the additional factor (1-F_H(j_H(a,p_c(a)),x,y)), where j is the learned approximate center. All padding makes E false. Write R=|E| and rho=R/m^6.

Pad to M least power of two >=m; B largest dyadic satisfying B^3<=m^2. For each aligned six-coordinate projected cube of side t<=B, consider the exact nonzero restricted free-square strings for every fixed actual source a and actual context tuple in the cube. Intern equal strings per source, omit zero strings and retain the actual four-coordinate map entries referencing them. Instead of bounding the number of row strings, bound the total length of a CANONICAL compressed representation of those strings:

* For each row string, view the x coordinate as a sequence of Boolean y traces.
* Partition into maximal consecutive equal-trace x intervals; omit all-zero intervals.
* Encode each nonzero interval by its two x endpoints and the list of maximal nonempty consecutive y runs (two endpoints each, half-open).
* Define the weight of a nonzero string to be 1+sum_over_slabs(1+number_of_runs). The 1 counts its row header; every counted unit takes O(log(t+2)) bits.
* Let W(D) be the sum of these weights over DISTINCT nonzero restricted strings per source, summed across sources in the cube. Map references are separately bounded by t^4 records.

For dyadic C>=1, C<=m^(1/32), declare overflow iff W(D)>C*t^4. Stop at first overflow on each dyadic path below the projected B roots. Define omega_run(C)=(sum_D t_D^6)/m^6 over the disjoint first-overflow cubes. Exactly as in the parent, abandon only the auxiliary guard at those cubes, not any original constraint. The new route charge is

    J_run(E)=min_C [ C^13*rho + omega_run(C) ].

Include the previous dense-row quotient route J_dense in the portfolio. Both can be independently computed in O(m^8 polylog m) physical preprocessing and O(m^3 polylog m) visited span. For a direct program minimize

    Q_direct=beta+delta_n+sum_H min(J_dense(Z_H),J_run(Z_H)).

Then the derived bound, for sufficiently small positive Q_direct, is

    T(m)=O(m^(42/5) polylog(m+2)
           + m^9 Q_direct^(1/6)(1+log(1/Q_direct))^A),
    span=O(m^3 polylog m).

The approximate-template portfolio can add J_run as a fourth correction option alongside eta_H, Lambda*kappa_H and J_dense(E_H); its previous complete bound with preparation exponent 35/4 and density exponent 1/12 is unchanged. Include all inherited map policies, coordinate choices and (for approximate mode) radius/template options, with deterministic tie rules. Capacities and branch choices are learned, not supplied. All score comparisons exact integers. Score dominance over the preceding portfolio is by retaining its options, not by asserting that the weighted run certificate always dominates the row-count certificate at the same C. The new direct route does not need approximate centers. These are conditional fixed-machine-existence bounds on the selected score, not an unconditional cubic-stage result.

## 2. Canonical encoding and exact child clipping

The maximal y-run list of each trace is uniquely determined by its bits. The maximal nonempty equal-trace slabs, including their actual endpoints and gaps, are likewise unique. Thus exact string equality is equivalent to equality of these canonical records. A nonzero row takes at most 1+t+t*ceil(t/2)<=3t^2 counted units. A root may be generated from dense strings by scanning consecutive x traces, computing their runs and comparing each with the preceding trace, O(t^2 polylog(t+2)) sequential work per row, no random access.

For a free child quadrant with offsets ox,oy and side u=t/2, intersect each slab with [ox,ox+u), subtract ox. Intersect each run with [oy,oy+u), subtract oy, omit empties. Drop slabs with no remaining runs. Merge adjacent slabs iff their translated trace lists are identical and their x endpoints touch. Restriction never splits a run or slab into multiple intervals and cannot increase the counted weight before interning. Adjacent run lists remain separated by their original gaps; clipping cannot create a new gap or close an interior gap. The resulting canonical encoding is exactly that of the restricted Boolean string. This is important: after y clipping formerly distinct adjacent traces may become equal. Failing to merge such slabs would give an incorrect equality/weight certificate.

Restrict the actual map records in the four projected source/context coordinates, retain referenced rows only, restrict and translate the free quadrants, intern again by source and canonical string, drop zero rows and references, assign dense local IDs and translate map references. Equal parent rows stay equal after restriction, and unequal rows may coalesce. No actual global target or center labels in a descendant. The resulting weight is exactly W(child), not a conservative upper bound based on parent IDs. The same operation gives the correct overflow decision independent of private coordinates and original constraints.

Variable-length canonical strings can be lexicographically sorted by sequential merge sort on fixed multitapes with work linear in total bit payload times logarithmic factors. Compare from record starts using length/end markers; the common prefix and rewinds cost at most the shorter record length plus a constant, charge to the record consumed in that merge step (which is at least as long as the shorter one). Copy consumed records sequentially; no repeated full long-record scan just to compare a short prefix. Within each merge pass every record is consumed once. Count groups, join actual map references and omit zero strings. This is an exact bit procedure, no hash or collision probability assumption.

## 3. Original-scale root construction and census

Use the parent's pair-sliced generator O(m^5 polylog m) per retained conditioning pair and all values of its remaining coordinate. Enumerate K blocks of side B first, regenerate pair maps and filter to the third interval, hold <=m B^3<=m^3 actual records. Total O(m^8/B polylog m); include center metadata from inherited approximate census if needed. For each projected B root extract its <=B^4 map entries and the m B^2 restricted raw bits for all actual source, target and center labels by explicit sequential sort/merge. No global m^4 map.

Process one source at a time. There are at most m used target labels, each with at most one center label determined by the fixed source/target pair. Obtain requested old/new/center restricted raw strings by sequential sort/merge as in the parent. Duplicate repeated raw requests only as needed, at most O(m B^2 polylog m) total bit payload per source. Compute actual E rows, convert to canonical slab/run encoding, sort/intern exact strings, omit zero and count dictionary weight. Source-specific map entries <=B^3<=m B^2. If cumulative dictionary weight including this source would exceed C B^4, return an overflow header without allocating the full dictionary. The one-source temporary buffer O(m B^2 polylog m) and bounded partial dictionary O(C B^4 polylog m) fit original-scale span; even an overflowing source can be counted exactly within the temporary buffer. If an early source already exceeds the cap, remaining sources cannot reverse that decision. Otherwise emit the source dictionary and translated actual map references. R computed separately by exact directed/missing-bit weight sums over the map spools, not inferred from compressed size.

Total sequential root work O((m^3+m B^3+C B^4) polylog m)=O(m^3 polylog m); apply inherited original-scale sweep O(m^6 polylog m) per projected block, O(m^12/B^6 polylog m)=O(m^8 polylog m) total. Install successful cached root once adjacent to active worker, even charging original-scale per-bit shuttles O(m^3 C B^4 polylog m) per block, O(C m^9/B^2 polylog m) total. Overflow roots just a flag. All buffers and original-scale data O(m^3 polylog m), since C B^4<=m^(1/32+8/3)<m^3. No global six-dimensional guard materialization.

A nonoverflow side-t frame contains O(C t^4 polylog(t+2)) bits including row dictionary, actual map references, local counters, scratch and (during full search) O(t^3) original singleton records. The effective cap can be clipped to min(C,4t^2) since at most t^4 distinct rows each weigh <=3t^2, so this clipping does not change the overflow test. At child side u clip again to min(C_local,4u^2), exactly min(C,4u^2). All persistent fields are O(log(t+2)) bits (IDs at most t^3 per source). Temporary clipped rows and references no larger than parent payload up to fixed overhead, use parent-local scratch before appending compact child. The sequential clipping, sorting and recoding work is O(C t^4 polylog(t+2)), and inherited local sweeps and per-bit shuttles over same extent give O(C^2 t^8 (1+log(t+2))^A) physical work, including all fixed children. Adjacent stack capacities sum geometrically. Parent stationary, process one child then clear and pop, no global scan during recursive steps. Fixed product components encoded by constant-width blocks over actual symbols 0,1,2, not additional physical heads or input-dependent alphabet.

Census traverses only six projected coordinates, stopping at overflow or empty guard. At overflow charge t^6 once and stop its path. The canonical dictionary is nonempty iff some real guarded projected tuple exists (all referenced rows nonzero, source/context entries actual, free padding zero). Empty ancestors cannot hide later overflow. Even ignoring pruning the census local work is

    O(C^2 * sum_(t<=B dyadic) (M/t)^6 t^8 (1+log(t+2))^A)
       = O(C^2*m^6*B^2 polylog m) <= O(m^(355/48) polylog m).

Root preparation dominates. Sum local volume subtotals <=t^6 while unwinding, combine at global scale. No global list of overflowing cubes needed. First-overflow cubes disjoint; omega nonincreasing in C because a path passing the smaller cap also passes the larger cap. Weighted score need not be monotone. Enumerate logarithmically many capacities and fixed many coordinate/policy/support choices, logarithmically many radii and template options if applicable. Overall O(m^8 polylog m) selection; exact integer charge C^13 R+sum_D t_D^6. Regenerate winning data deterministically.

## 4. Full search, rate-free volume and density estimates

Every branch retains ALL actual original clauses and padding. The direct worker searches representative envelope (width four), ordinary narrow exceptions (width<=5) and each wide guard E with the chosen compressed/overflow representation. For an original satisfying tuple, a successful substitution yields an original model in the representative envelope. Otherwise a newly violated support gives the original tuple in its narrow or wide exception. For approximate mode use the parent's heavy envelope, surviving template and one-sided correction recovery proof. A local run-coded guard is exact before overflow; first overflow enlarges it to the entire projected cube. Thus any original E model survives, and every accepted tuple is original, even if outside E. No external higher-width clauses or approximate verifier. At singleton check guard and original forbidden records. Overflow searches the original tile with the inherited unpruned adjacent original-record stack, discarding only the auxiliary guard. On success reconstruct actual digits, pins and fixed auxiliary bits, emit contiguous n raw bits and halt at first output bit; on failure halt on blank.

For each full B tile extract original width<=3 records by mobile O(B^3 polylog m) scratch over original-scale stationary input, O(m^3 B^3 polylog m) physical per tile. Copy adjacent cached root locally at O(C^2 B^8 polylog m) including mandatory tests and cleanup. Across (M/B)^9 full tiles total

    O((m^12/B^6+C^2*m^9/B) polylog m) <= O(m^(403/48) polylog m).

Root generation and cache installation below 42/5. Narrow/envelope stationary worker uses b'=Theta(m^(3/5)) dividing B, with B-sized K spools held across nested projected blocks; preparation O(m^(42/5) polylog m), local density exponent >=1/5. Span O(m^3 polylog m) throughout.

At an overflow of side t, the unpruned original-record stack visits at most (t/s)^9 nodes at scale s, O(s^6 (1+log(s+2))^A0) physical work per node. The geometric local-log sum gives O(t^9), not O(t^9 polylog m). There are at most (M/t)^3 private tile choices for that projected overflow. Thus total fallback O(M^3 sum_D t_D^6)=O(m^9 omega_run). Disjoint first-overflow volumes counted once. No accumulated level multiplier.

At nonoverflow positive nodes use the parent's count min((M/t)^9,R*(M/t)^3), charge child tests to positive parents and mandatory roots separately. With local cost C^2 t^8 local-log, crossover t0=M/R^(1/6) gives

    O(C^2*m^9*rho^(1/6)*(1+log(1/rho))^A).

R=0 has no positive descendants. Set X=C^13 rho; C^2 rho^(1/6)=C^(-1/6) X^(1/6), and log(1/rho)=log(1/X)+13 log C. The negative capacity power absorbs all fixed log C factors uniformly near zero. Add overflow volume charge to obtain O(m^9 J_run^(1/6)(1+log(1/J_run))^A) for small charge. Consequently the new direct bound and inherited approximate portfolio bound hold with no global logarithmic multiplier on the new route's score-dependent term.

In particular if rho->0 and lim_(C->infinity dyadic) limsup_(m->infinity) omega_run(C)=0, choose a FIXED sufficiently large C first, eventually under production cap, then C^13 rho->0. This gives vanishing selected route score without any convergence rate. Does not prove that small rho alone implies vanishing overflow. On Q->0 time o(m^9)=o(L^3), visited span O(L polylog L); a fixed actual machine description length ell is allocated >=L^3/2^ell transitions at exact stage 3 ceil(log2 L) once eligible. Little-o eventually fits; no actual compiled ell, threshold or U run supplied.

## 5. Strict separation of local overflow conditions on generated maps

Use m=2^d, r=floor(9d/10), q=2^r, T=[m/2,m/2+q), B=2^floor(2d/3). Let N be the least power of two >=2*r*log2(d) for large d, S=B/N. Then S is dyadic, S^3>=m eventually, N=O(d log d). Define f(c) as m/2 plus the r-bit string interleaving successive low bits of c1 and c2 (even output positions from c1, odd from c2). In every aligned context B cube its image is the full T and uniform, since all required input bit positions are below log2 B. Use g=0,K={1,2,3}. One unary support excludes g digits outside T; two binary supports check the corresponding output bits against the context digits. Together these narrow supports force f(c), and all narrow bits vanish at f(c). Optional unary zero exclusions on other groups.

For sole wide H={0,4,5} define h_a(x,y)=binary dot(a,x) XOR lowbit(y). For each aligned x block of side B divide into N consecutive slabs of side S and label them i=0..N-1, repeating the arrangement in every x block. Put:

* For a outside T, F_H(a,x,y)=1 on m/4<=y<m/2, equals h_a on m/2<=y<m, zero elsewhere.
* For b in T, F_H(b,x,y)=1 on y<m/4 precisely in slab i<2r where i mod 2 equals bit floor(i/2) of b-m/2. On m/4<=y<m/2 it equals h_b; zero on y>=m/2. Each target selects exactly one slab of each of r adjacent pairs.

No other cross supports. Easy SAT family: choose nonzero contexts, a=f(c), nonzero x,y>=m/2 and all other digits nonzero. No hardness claim.

For every outside source a and every target b in T, directed difference consists exactly of the r selected slabs times the low y region (old one on middle region, new zero on high region). Its weight D0=m^2*r/(4N), independent of both labels. Let zeta=r/(4N), tending to zero at rate Theta(1/log d), slower than any fixed negative power of log m. Every distinct outside/outside directed loss is D_s=m^2/8 by independence of distinct h forms with the shared independent low y bit. For distinct targets b,b', directed loss is m^2/16 plus Hamming distance of their r-bit strings times m^2/(4N); the middle contribution is again probability 1/4 of old-zero/new-one. Summed target-to-target loss over all sources in T is independent of the candidate in T, since each bit is balanced. Target-to-outside losses nonnegative and acquire unary narrow penalty m^2.

For every context the actual unpenalized full-average greedy first facility is f(c): each target has equal summed wide loss, f(c) has zero narrow loss from all sources, each other target incurs positive narrow loss from source f(c); an outside candidate has wide loss from other outside sources alone >=(m-q-1) D_s, eventually larger than the full loss to f(c) because q/m,zeta->0. After the first selection, a candidate in T cannot strictly improve any outside source (wide loss D0 unchanged and narrow nonnegative); an outside candidate can improve only its own source by at most D0<m^2 (other outside sources incur D_s>=D0, inside sources incur unary penalty m^2, whereas current loss <=m^2). The inherited greedy assignment rule retains the earliest selected target on equal residual loss, except selected facilities map to themselves. Therefore as long as only T facilities are selected, all outside assignments remain f(c). Every outside marginal is below facility penalty; by nonincreasing marginal gains the best positive greedy round never contains an outside facility: if one is chosen later, its round and all subsequent rounds have strictly increasing objective. Extra T facilities are permitted. Thus actual C_c subset T and p_c(a)=f(c) for EVERY outside a. Unlike a singleton claim, this argument allows large marginal improvements on inside sources.

It follows beta<=q/m, delta_n=O(q/m), delta_w<=zeta+q/m, all tending to zero. Moreover for any maps on this configuration, outside nonself loss >=D0 eventually, self fraction<=beta, so delta_w >=max(0,1-q/m-beta)*zeta. In particular the actual wide loss genuinely decays slowly. This is about loss, not SAT complexity.

For the parent dense-row quotient at any projected B-root with an outside source and free y interval wholly in [0,m/4), the exact nonzero restricted directed rows over actual contexts include q distinct patterns: the r slab-pair choices encode every target uniquely on the complete x block. Its capacity <=m^(1/32)*B=o(q), uniformly over the parent's permitted C. Consequently all such roots overflow. Their padded volume fraction (m=M) is at least (1-q/m-2B/m)/4, bounded away from zero. The parent direct dense quotient charge cannot vanish for these generated maps. For the null-template source-only union over all real targets, the high y region gives density at least (1-q/m)(1-1/m)/4: for x!=0 the nonzero dot functional takes both values on the outside set (size >m/2), so every old-zero high-region column for outside a has some outside target forbidding it. The log-weighted correction also fails for any fixed positive log power by the slow zeta bound. These are statements about the same null-template candidate, not all earlier radii or alternative policies.

For the new run-coded quotient, any root whose source interval lies wholly outside T contains only actual E rows of the simple slab-pair form. At scales t<=S, aligned x interval lies inside one slab; each source has at most one nonzero restricted string, with weight 3 (one header, one slab, one run). At t>=S, each row has at most t/S nonzero slabs and at most one y run per slab; weight <=1+2t/S<=3t/S. Even bounding the number of distinct rows per source by m, total W(D)<=3m*t^2/S<=3t^4 because t>=S and S^3>=m. This covers all aligned descendant squares, not just roots. At fixed C=4 no overflow on outside-only source roots or descendants. Roots with source interval meeting T may overflow anywhere, but all their first-overflow descendants are disjoint subsets of those roots, so omega_run(4)<=q/m+2B/m. The direct score satisfies

    Q_direct <= beta+delta_n+4^13*delta_w+q/m+2B/m ->0.

Thus the run-coded local overflow condition is strictly weaker on these actual generated maps, even at genuinely slow wide loss and a dense all-target union. Note that outside source digits are excluded by a unary original constraint in this deliberately easy example; older solvers could exploit that. No claim of separation of full algorithms, actual SAT runtime lower bound, or universal guarantee. The derivation shows the representation certificate can be strictly improved, not that it is necessary for efficient witness search.

## 6. Executed regression

Standalone JS audit executed in tool runtime and committed with Node entry point. Twenty fixture passes at m=2,3 with five raw modes and prescribed maps; each uses either direct center=a or prescribed center=0 (not necessarily a learned radius center), finite B=2,C=1. Build canonical dictionary, compare exact local weight and overflow decisions with direct encoding, test clipping/interning, membership and positivity, count disjoint first-overflow volume, and compare complete original AND (E OR overflow membership) model set with recursive host traversal. Independent m=4 overflow controls use B=2,4 and C=1,4, and full original private constraints. All assertions passed. Counts including controls:

    780 root builds, 29376 projected child builds
    9100 referenced row inspections, 5871 zero omissions, 80 merges
    23584 child row clipping checks, 1509 dictionary checks
    93784 local membership checks, 28516 positivity checks
    1640 overflow events, 57984 projected volume checks
    3675136 full padded tuple checks
    83768 recovered original model occurrences, of which 46712 by overflow fallback.

The test counts include repeated model occurrences across different passes. At C=1 a nonzero singleton has weight 3>1, so overflow may be confined to leaves; this is expected and safely charged, not an assertion that the guard is compact at C=1. The m=4 independent controls give [B,C,R,overflow volume,first-overflow cubes] = [2,1,386,386,386],[2,4,386,0,0],[4,1,386,386,386],[4,4,386,0,0]. They exercise actual fallback but not a large-scale overflowing root in this cycle. Exhaustively checked all 65536 binary 4-by-4 strings and all four aligned quadrants: 262144 exact clipping/re-encoding comparisons, including merging after y restriction.

Finite slab-code controls at m=32,64,128 (small q,B,N chosen for finite execution, not asymptotic parameter relation) explicitly compute all directed pair losses, equal summed target loss, unique first greedy facility for each possible forced target, every outside second marginal, and absence of strict outside-source improvements by other target candidates. They also verify distinct coarse rows and one run per nonzero local slab over every aligned free square for source zero. Output [m,q,B,S,D0,distinct root rows,max single-source dictionary weight/t^3,outside marginal checks]:

    [32,8,16,2,96,8,3,192]
    [64,16,32,2,256,16,3,768]
    [128,32,32,2,1280,32,3,3072].

The finite S does not satisfy S^3>=m in these controls; the asymptotic bound uses a separate inequality. Arithmetic-only checks at d=64,128,256,512 verify q>B*m^(1/32) and S^3>=m for the chosen asymptotic parameters, not enumeration of those enormous domains.

The host uses indexed arrays, direct enumeration, JSON canonical strings and recursive objects; it does not implement all production map policies, center learning, exact adaptive score selection, physical sequential variable-string sorting, mobile carry shifts, serialized adjacent tape frames, original normalized encoder/verifier, compiled transitions or exact universal stage. The greedy control checks the first facility and outside marginal/tie property, not every actual full greedy map on the asymptotic family. No measured physical transition counts, independent review, Lean formalization or exact-head CI confirmation.

## 7. Disposition

Replace the number of distinct local exception rows with their exact canonical encoded length. This avoids overflow for many distinct geometrically simple traces, preserves a subcritical projected-only census, and keeps the rate-free density/overflow cost. The remaining obstacle is that arbitrary sparse difference strings may have many runs and many distinct row patterns; no general implication from small average loss to compact run dictionaries is established. Next investigate adaptive per-tile factorizations or multiscale sparse bit dictionaries that can compress irregular traces, or establish a rigorous limitation of representation-based overflow certificates. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census 1603 unchanged, not freshly recounted. Promotion NONE.
