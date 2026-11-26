# F038 — Guard-conditioned residual semijoins

PNP_RESOLUTION_STATUS = OPEN. Parent 0449d65cf4693ce6cf0cc119c5c7b19d6dddaeaf (dyadic residual cover). Conditional mathematical machine-existence derivation using inherited fixed-track parsing, mobile carry shifts, pair-sliced map generation and stationary restriction trees. Executed standalone semantic regression, not compiled original-U transitions or independent review. Parent combined statuses and PR-triggered runs empty; push CI unconfirmed.

## 1. Result

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), original selected negative cross-clause bits F_B on supports B of width one through three, and the fixed one-hot/OR/pin/guard extension. For a compressed group g and three conditioning groups K, define normalized representative capacity beta and full weighted directed average loss delta=delta_n+delta_w as in the parent (denominators m^4 and m^6). An active wide support H={g,u,v} has u,v outside K and nonidentical raw rows indexed by g. Let P=H union K. All supports and actual digits are distinguished from padded digits. Define the map-independent possible-exception mask on H by

    W_H(a,x,y) = (1-F_H(a,x,y)) * 1{exists b: F_H(b,x,y)=1}.

Define a six-coordinate feasible guard

    G_H(z) = W_H(z_H) AND all original F_B(z_B)=0 for B subset P,

false on padding. For I subset P with |I|<=2 (including empty I), put Q_H,I=projection_I(G_H). This is an existential projection of the exact feasible guard, not a projection of a chosen representative map. For each residual support B not contained in P, let I=B intersect P, so |I|<=2, and set

    F'_B(w) = F_B(w) * 1{w_I in Q_H,I}.

This definition is specific to the wide branch H. Keep both the original and filtered representation as candidate choices for each residual ternary. A support passes the new certificate if EITHER its original forbidden array OR its filtered forbidden array admits the parent's canonical dyadic forbidden-cube cap C(D)<=c0*t^p at every aligned cube D of side t, for fixed rational 2<=p<3 and fixed c0>=1. As in the parent, c0=2 is a concrete choice. Different residual supports may use different choices; do not insist on filtering if it fragments homogeneous cubes. Residual unary/binary lists may simply be filtered or left unchanged. Require the certificate for every active H with nonempty G_H. Empty G_H branches are omitted, since no actual exception guard can be nonempty there.

There is one fixed deterministic original three-symbol one-tape witness program, correct on the entire family, such that along any sequence admitting a choice g,K with the certificate and competitor beta_*->0, delta_*->0, arbitrarily slowly, it attains T(L)=o(L^3) and visited span O(L polylog L). Its computed score sigma=beta+delta yields for sufficiently small positive sigma

    O(m^((15+p)/2) polylog(m+2) +
      m^9 sigma^((3-p)/6) (1+log(1/sigma))^A)

physical transitions. Here A is fixed and implementation-dependent, p,c0 are fixed in the program, and no supplied rate, choice, representation or map is needed. For p=2,c0=2 the bound is O(m^(17/2) polylog m + m^9 sigma^(1/6)(1+log(1/sigma))^A). The new certificate accepts every configuration accepted by the parent's dyadic cover certificate and additional configurations with cubically many incompressible raw forbidden entries. The extra preprocessing is polynomially subcritical independently of sigma. This does NOT prove the arbitrary-slow cutoff for every input, nor remove the need for a structural certificate.

## 2. Why the semijoin is exact and independent of maps

For ANY contextual map p_c(a) into any nonempty representative sets, its actual wide exception on P is

    E_H(z) = (1-F_H(z_H)) * F_H(z_H with g replaced by p_(z_K)(z_g)).

The actual strengthened guard is A_H(z)=E_H(z) AND all original P-contained support bits zero, with padding excluded. A_H is a subset of G_H: any actual replacing digit is one of the possible b counted by W_H. No assumption on minimizing ties, loss, representatives, or satisfiability is needed.

For a full tuple x with x_P in A_H, every intersection projection x_I lies in Q_H,I. Consequently F'_B(x_B)=F_B(x_B) for each residual support B. The same holds if x_P is merely in G_H. Thus, conditional on the guard, replacing any subset of residual arrays by their filtered arrays preserves the EXACT restricted original model set. We are not altering the actual external normalized selector or claiming unconditional equivalence of the filtered formula. All P-contained constraints remain enforced by A_H, not merely W_H. Private padding exclusions are separately retained. Every active H can have different masks and filtered arrays; never reuse a branch-specific simplification as a global change to the original formula.

The empty intersection projection is either {empty tuple} or empty. A nonempty G_H therefore does not change private-only supports. An empty G_H proves every actual A_H is empty, so the branch may be skipped without even certifying its residuals. This avoids a spurious condition on an impossible exception branch.

The certificate cannot in general require the filtered cover in place of the raw cover. A full forbidden cube has one raw record, but restricting it to a checkerboard of projected digits may produce Theta(m^3) singleton records, even though its selected-bit count decreased. The per-support OR of the two certificates preserves the parent's sufficient condition and guarantees that every representation chosen for transfer actually has the required cap. It is not valid to infer a monotonicity theorem for dyadic cover complexity from a monotonicity theorem for raw tuple counts.

## 3. Compute map-independent projection masks in subcritical time

The main new preprocessing step is a deterministic bounded-span census of G_H, without storing a global width-six array.

Pad to M, the least power of two >=m. Compute W_H on real digits by a sequential sort/merge of explicit original zero/one records, ordered by (x,y,a). For each fixed (x,y), OR the bits over all a, then join the OR back to the old-zero records of that row fiber. Emit W_H bits or selected records in canonical support order. A constant number of sequential scans/sorts of O(m^3 polylog m) bits, with fixed tapes, suffices. Physical sweep cost O(m^6 polylog m). No fourth-order enumeration over pairs of replacement labels.

Let b be the largest dyadic integer with b^2<=m, so b=Theta(sqrt m), b divides M, and b^6<=m^3. Enumerate aligned projected coarse blocks on P. For each block extract the original selected P-contained records whose fixed digits fit its intervals, and the relevant W_H records, translating to local coordinates. There are O(b^3) records (fixed support count). With a mobile O(b^3 polylog m)-block scratch component scanning the original-scale stationary data, the inherited physical movement bound is O(m^3 b^3 polylog m) per projected block, including explicit padding checks and copying to a reusable local region. Across (M/b)^6 blocks this is O(m^9/b^3 polylog m)=O(m^(15/2) polylog m).

Enumerate b^6 local candidates. For each, reject padding, test W_H and every P-contained constraint using sequential scans of the O(b^3 polylog m) cache and a smaller mobile query/counter component, costing O(b^3 polylog m) physical transitions per candidate. This is a direct charged lookup, not a unit-cost indexed oracle. Keep local Boolean masks for each I subset P of size zero through two (22 possibilities), of total size O(b^2 polylog m). On a passing candidate OR the bit at the corresponding local projection; even linear scans of these local masks per candidate are dominated by the b^3 bound. This uses no representative-map information. Across all blocks the candidate enumeration and local mask maintenance cost O(m^6 b^3 polylog m)=O(m^(15/2) polylog m).

Maintain the accumulated global projection masks on stationary components, total O(m^2 polylog m) bits for fixed H. At completion of a block translate its local true flags to the global keys and OR them into those masks. Even per-bit shuttles and linear key scans across the original-scale O(m^3 polylog m) region cost O(m^3 b^2 polylog m) per block; across all blocks O(m^9/b^4 polylog m)=O(m^7 polylog m). Only the local mask flags leave the local region, not every passing full projected candidate. Reset the local cache and flags for the next block. The global masks are exactly the projections of the union of these disjoint coarse projected blocks. No global m^6 storage, unbounded tracks or random access. Thus the entire per-H projection computation costs O(m^(15/2) polylog m) with O(m^3 polylog m) visited span.

For each residual support B, compute F'_B by sorting its selected records on their I fields, merging against the accumulated explicit projection masks, retaining a selected bit iff the mask says true, then restoring canonical support order. Missing mask entries mean false. For |I|=0 with G_H nonempty keep the raw array. The sort/merge spans O(m^3 polylog m) and costs O(m^6 polylog m) original transitions by the inherited sweep. Use the parent's prefix-count canonical maximal-full-cube construction and certificate on BOTH arrays if necessary. All certificate/canonical-cover work is O(m^6 polylog m) physical time per branch. The raw arrays are preserved for later guard and directed distance calculations. The chosen filtered covers are internal residual data only.

## 4. Adaptive selection and original-scale resource composition

Enumerate the fixed 504 choices of g,K. Determine active H using actual raw directed-loss tables. Compute the above masks and certificate for each active H, then retain only the eligibility decision for the coordinate choice. Number of configurations and wide supports is independent of m. Do not accumulate all large temporary trees or branch spools. For eligible choices run the inherited full-average directed facility greedy, choosing the positive round minimizing k*m^2+F_k per context and the smallest total score sigma=beta+delta across eligible choices. The mixed-rate note's comparison, from the exponential residual bound at k=ceil(h(1+ln(m/h))), gives

    sigma <= 38 beta_* (1+ln(1/beta_*)) + 1/m + delta_*.

Map-independent eligibility is important: the arbitrary competing maps in this comparison do not have to pass a certificate defined by their own possibly different chosen replacements. All choices passing the parent certificate are eligible here by retaining their original covers, and every A_H for every map is contained in the precomputed G_H. Recompute the winning branch masks and chosen covers as needed. One pass or recomputation over a fixed number of configurations changes only constants. Parsing, actual pins, distance caches and full greedy selection take O(m^7 polylog m) as in the pair-sliced parent; the new mask phase O(m^(15/2) polylog m) dominates that but is below the existing preparation bound. If no eligible choice exists, use an exhaustive inherited original solver; correctness is unconditional but the promised saving is not claimed for such inputs.

For each winning map the original witness recovery uses the representative relation S={(a,c):a in C_c} and exact E_H on H union K. A successful substitution yields a model in S; any failed substitution identifies an original newly violated support, so the original tuple lies in E_H. Each branch enforces every original constraint, including the branch-specific equivalence proved in Section 2. At most 38 branches. The sum of normalized exception densities is delta by weighted counting. S and narrow E_H continue to use the inherited width-four/five stationary solver, O(m^(42/5) polylog m) preparation and O(m^9 sigma^(1/5)(1+log(1/sigma))^A) local-log density term.

For wide branches use the parent's guard A_H (NOT the larger G_H) in the stationary six-coordinate tree. Only the residual records are replaced by the selected certified covers. Retain original P-contained raw bits and all original distance data. Use b=Theta(sqrt m), shared K-block map regeneration, local actual map cache of O(b^4) entries, wide raw row cache of O(m*b^2) entries for all possible representative digits (including representatives outside source intervals), and O(b^3) P-contained raw records. Their construction and exact A_H tree generation cost O(m^8 polylog m), as in the parent. The complete projected tree fits original-scale span since b^6<=m^3. At positive side-t nodes reserve O(t^p polylog(t+2)) blocks for certified residual records. All data fields and child offsets inside the worker have local bit widths. Private padding units add at most O(t) records per group.

The parent's canonical-cover clipping lemma applies unchanged to each selected residual array: the intersection of an aligned dyadic record with the tile projection is empty or a single aligned cube. Transfer only that intersection, translated into local coordinates. Repeated clipping equals direct clipping, so the certified cap applies at every descendant. Semijoin masks need not be queried during the physical worker. Some residual records may be spurious away from G_H; they are irrelevant because the actual guard is enforced exactly at the leaf. Do not reject a whole nonempty guard cube solely because its projected feasibility mask has one bit; the worker still performs exact leaf checks. A full original restricted model survives every ancestor guard flag and never encounters a violated retained record at its leaf; a passing leaf satisfies A_H and all original residuals by Section 2.

The residual coarse extraction cost across all nine-coordinate tiles is O(m^12/b^(9-p) polylog m)=O(m^((15+p)/2) polylog m). Stationary subtree extent at side t is O(t^6 polylog(t+2)), since each level's frame capacities sum as in the parent. Local work transferring at most O(t^p) records across it is O(t^(6+p)(1+log(t+2))^A). Each active ancestor has a different projected depth; private alternatives reuse a child's reserved frame sequentially. No global sweep per local transition, no mask table consulted at leaves. Fixed number of finite product components encoded over original 0,1,2; span O(m^3 polylog m). Success reconstructs original latent digits, fixed auxiliaries and actual pins and outputs contiguous n-bit witness at the physical halt head; exhaustion halts on blank. Once-only reconstruction O(m^4 polylog m) is dominated.

## 5. Local-log bound and original clock

For R=|A_H|, rho=R/m^6<=sigma, positive full nodes at side t are bounded by min((M/t)^9,R*(M/t)^3). Rejected children are charged to their positive parents, coarse root visits separately to preparation. If R=0 there is no positive traversal. Multiplying the local work by the positive count and summing gives

    sum_t min(M^9*t^(p-3), R*M^3*t^(p+3))*(1+log(t+2))^A.

The crossover t0=M/R^(1/6) yields geometric tails with exponents p+3 and 3-p, both positive since p<3. Local log growth is a fixed polynomial in dyadic distance from the crossover, so the sum is O(m^9 rho^((3-p)/6)(1+log(1/rho))^A). No global log m multiplies the density term. The same unpruned sum is O(m^9) on eligible inputs. The added m^(15/2) preprocessing term and earlier m^8, m^(42/5) terms are below (15+p)/2 for p>=2. This proves the displayed bound conditional on inherited physical constructions.

Under the stated promise, sigma->0, time o(m^9)=o(L^3), span O(L polylog L). For a fixed actual original machine description of length ell, the stage 3 ceil(log2 L) allocates at least L^3/2^ell transitions once eligible; the little-o bound eventually fits this clock. Neither ell nor numerical threshold nor an actual compiled U program is produced. Ineligible choices are not excluded from the universal search, only from this worker's adaptive structural comparison.

## 6. Strict certificate separation: an incompressible redundant ternary

Modify the parent's finite-field slow-loss control. Let m=q=2^d, full digit domain GF(2)^d, also identified with GF(q), negative unary zero exclusions in all groups. Set g=0,K={1,2,3},P={0,1,2,3,4,5}. Retain the main triples {0,i,j} for 1<=i<j<=3 forbidding <x0,xi+xj>=1, the binary inner-product-one forbiddances among groups 1..8, and the equality forbiddances on pairs involving 0. Retain the wide field-hash support {0,4,5}, F(a,u,v)=1 iff the first l bits of a*u+v in GF(q) are zero. Here zeta=2^-l tends arbitrarily slowly to zero. Use the sparse Latin forbidden relation x+y=z on all triples among groups 1..8 EXCEPT B={1,2,6}, where replace it by

    F_B(x,y,z)=1 iff <x,y>=1 AND the least significant bit of z is one.

This is a genuinely three-coordinate raw support with dense forbidden and allowed sets. Every aligned cube of side >=2 contains a z with least significant bit zero, hence no such cube is entirely forbidden. All canonical cover members are singletons. There are (q-1)*q/2 pairs (x,y) with <x,y>=1, and q/2 digits z with low bit one. Thus raw forbidden and canonical cover count are both q^2(q-1)/4=Theta(q^3). The previous dyadic certificate fails on the entire support at t=q for any fixed p<3 and c0. In fact even arbitrary raw full forbidden cubes of equal side cannot compress this pattern. This is a statement about this representation, not an incompressibility claim for every possible encoding.

However G_H requires <x1,x2>=0 by the P-contained original binary constraint. The projection Q_H,{1,2} contains no forbidden pair of that binary constraint. Therefore every selected F_B record is removed by the semijoin, and F'_B is identically zero. All other residual ternaries are Latin and have at most t^2 forbidden singletons in any t-cube (fix first two digits). This configuration passes the new p=2,c0=2 certificate. The example uses a semantically redundant raw ternary to demonstrate the exact structural relaxation. A general redundancy detector or other algorithm may also eliminate it; no computational hardness assertion.

The representative construction and loss from the parent are unchanged, since B does not contain g. Isolate zero and the three conditioned digits, then one representative per nonempty fiber of the three inner products with conditioning digits on remaining nonzero digits. At most 12 representatives; beta<=12/m, delta_n<=5/m by the five unconditioned binary inequalities. For distinct a,b the map (u,v)->(a*u+v,b*u+v) is bijective, so the exact wide loss is q^2*zeta*(1-zeta), independent of the pair. Thus delta_w<=zeta*(1-zeta), and any sublinear-capacity map has delta_w>=(1-beta)*zeta*(1-zeta) in the designated configuration. The context-free row union is dense, with density (1-1/q)*(1-zeta). Choose l growing slowly, for example max(1,floor(log2(log2(d+2)))) eventually, so zeta->0 but zeta*(log m)^C diverges for any fixed C>0. The new arbitrary-slow cutoff applies. The original family is SAT for large q: all groups 1..8 equal vector 3 (nonzero, self dot zero, x+y=0 not 3 for Latin supports, and the modified support false). Choose nonzero a !=3 with hash of a*3+3 not all zero in its first l bits; multiplication by 3 is bijective so this exists for large q. The primal graph is complete by binary pairs. The possible guard G_H is nonempty on the projection of this tuple because there is also some replacing b giving the forbidden hash for u=3!=0. This is an easy SAT control.

For any alternative g,K, the earlier full-average lower-bound arguments are unchanged. If g=0 but K differs from {1,2,3}, a main triple has a free other coordinate; distinct nonzero replacement forms are independent, giving q^2/4 weighted loss whether one other group is fixed or neither is fixed. Nonzero-to-zero incurs m^2 unary loss. If g>=1, choose a free binary neighbor among groups 1..8 distinct from g; distinct nonzero replacements lose q/4 partner digits with weight m, and nonzero-to-zero has the same unary obstruction. Thus for every alternative coordinate choice, all distinct replacements of nonzero sources have at least a fixed fraction of m^2 directed loss on some support. With sublinear capacity the normalized full loss cannot vanish. Therefore the new sufficient condition strictly includes a family failing the immediately preceding dyadic certificate plus vanishing full-average promise for all coordinate choices. This is not a separation from all earlier solvers or a lower bound.

## 7. Executed finite audit

Standalone JS function executed in the tool runtime, then committed with a Node entry point. Sixteen fixtures at m=2,3 across eight modes use g=0, K={1,2,3}, H={0,4,5}. Compute possible-exception W and G independently by testing all replacing digits, enumerate coarse local projection masks and compare their merged global result against the direct exact projections. Filter every residual support by the appropriate projection, build canonical covers and verify exact memberships and clipping during recursive traversal. Test two forced maps (contextual modular sum and constant), comparing every guarded residual evaluation and the complete restricted model set with direct original tuple enumeration. Counts:

    280 possible-exception raw entries tested
    6,344 real projected candidate checks against direct replacement-existence test
    33,280 padded coarse projected candidates
    4,237 emitted local projection flags
    1,816 global mask membership checks
    1,299 residual singleton records tested, 979 removed
    230 removed records passed P-only feasibility, so the W refinement mattered
    320 selected cover records, 40,368 selected representation membership checks
    41,984 local cover certificate checks
    323,120 full tuple checks across both maps
    16,184 actual-guard semijoin equivalence checks
    39,134 positive full-node visits, 37,792 singleton checks
    687,104 child choices
    15,977 recovered restricted model occurrences, exactly matching direct reference.

Eight fixtures have empty G. The small fixture b=2 is prescribed, not the asymptotic scale. All small fixtures passed the filtered certificate; the original-cover fallback was not needed there. Independent dense redundant ternary controls [m,raw count,raw cover count,filtered cover count] for m=4,8,16,32,64 are [4,12,12,0], [8,112,112,0], [16,960,960,0], [32,7936,7936,0], [64,64512,64512,0]. A separate fragmentation control filters a full raw cube by the parity of one projected digit: [m,raw cover,filtered cover,filtered root fails cap] = [4,1,32,false], [8,1,256,true], [16,1,2048,true], [32,1,16384,true]. This explicitly tests why the original-cover option must remain available, rather than claiming monotonic cover complexity. All revised assertions passed.

The audit uses host maps/sets, indexed queries, direct enumeration and recursive clipping. It tests semantics, coarse mask composition and certificate counts, not the proposed physical scan costs, stationary tree serialization, all 504 choices, greedy maps, normalized encoder/verifier, compiled original transitions or actual U stage. The dense control tests only its component residual relation, not the full finite-field sequence. No independent mathematical review, Lean formalization or exact-head CI confirmation.

## 8. Disposition

Map-independent possible-exception feasibility masks now relax the residual cover requirement by exact branch-specific semijoins. A dense, raw dyadically incompressible residual can disappear when its forbidden projected keys cannot meet the guard. The original-cover option is essential to preserve earlier certificates when filtering fragments homogeneous cubes. The remaining obstruction includes residuals dense on actually feasible keys, especially private-only triples for nonempty G. Next investigate local guard-fiber masks (rather than global existential projection) or stationary treatment of private-only constraints, with fully charged extraction and transfer. General arbitrary-slow full-average recovery without a structural certificate, unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
