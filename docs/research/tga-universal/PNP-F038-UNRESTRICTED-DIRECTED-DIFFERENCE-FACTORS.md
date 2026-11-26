# F038 — Directed-difference factors with certified pair filters

PNP_RESOLUTION_STATUS = OPEN. Parent 2dfe52c4a8015b2ec2d75392b56b06de1b297000 (hybrid row factors). Conditional mathematical resource and fixed-machine-existence derivation using inherited original parsing, fixed-track sweeps, mobile carry shifts, pair-sliced maps, stationary private trees and localized coefficient transfer. Executed host semantic regression, not a physical transition implementation or independent proof review. Parent combined statuses and PR-triggered runs were empty; push CI unconfirmed.

## 1. Main result

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), original negative cross-clause support bits F_B of widths one through three, and the actual one-hot/OR/pin/guard extension. Choose g and three conditioning groups K. Contextual maps p_c(a) take values in nonempty representative sets C_c. As previously beta=sum_c |C_c|/m^4 and delta=sum_(c,a,B containing g) d_B,c(a,p_c(a))/m^6, where each directed raw support loss is weighted by m^(2-number of free coordinates). A wide support H={g,u,v} has u,v outside K; active means its raw rows indexed by g are not all identical. Denote its exact directed difference string by

    Z_H(a,b;x,y) = (1-F_H(a,x,y))*F_H(b,x,y).

Pad digits to M, least power of two >=m, raw bits zero on padded free coordinates. Choose b0 largest dyadic with b0^3<=m^2, b0=Theta(m^(2/3)). The new certificate applies directly to Z, not the two raw rows individually.

Enumerate pair filters indexed by a dyadic block width w in {1,2,4,...,M} and threshold r in {0,1,2,4,... below m^2,m^2}. A real pair (a,b) is permitted iff

    floor(a/w)=floor(b/w)
    AND max_(active wide H) |Z_H(a,b)| <= r.

The empty maximum is zero. All self pairs are permitted. For every active H, require one of two options (fixed for H across scales): for EVERY aligned free-coordinate square of side t<=b0, the matrix of restricted strings Z_H(a,b) over ALL permitted pairs has GF(2) rank <=4*t^alpha, OR the number of distinct restricted strings is <=2*t^2. Here alpha is any fixed rational in [0,1/2), concretely 3/8. These are two separate options, not an OR independently chosen at each square. No condition on any other original support, or on raw row rank or cardinality, or on any unpermitted pair. Requiring certification only through the largest local scale b0 suffices, since no worker node is larger.

Let gamma be the fraction of actual source/context pairs whose chosen replacement is not permitted. There is one fixed deterministic original three-symbol single-tape witness program, correct throughout this family, with the following conditional guarantee: if a sequence admits choices g,K,w,r passing this certificate and competitor maps with beta_*,delta_*,gamma_* ->0 arbitrarily slowly, its computed score s=beta+delta+gamma tends to zero and its charged runtime near s=0 is

    O(m^((26+2alpha)/3) polylog(m+2)
      + m^9 s^((1-2alpha)/6) (1+log(1/s))^A),
    visited span O(m^3 polylog m).

A is fixed and implementation-dependent. At alpha=3/8 these are preparation exponent 107/12 and density exponent 1/24. At alpha=0 the bound is O(m^(26/3) polylog m + m^9 s^(1/6)(1+log(1/s))^A). These are fixed programs for fixed alpha, not a claim for alpha tending to 1/2 with m. On the promise T=o(L^3), hence eventual exact cubic-stage witness inclusion. Neither a factorization, filter, choice, map, rate nor score is supplied. This is a new structural sufficient condition, not a superset claim for every prior raw-row certificate. In particular raw-row dictionary size does not bound the number of distinct pair differences by the same size. Previous solvers remain separate descriptions.

## 2. Permit rare unrepresented substitutions without losing witnesses

For a chosen eligible filter, use distance

    D_c(a,b)=sum_(B containing g) d_B,c(a,b)
                  + m^2*1{pair (a,b) not permitted}.

It lies in [0,38m^2] and D_c(a,a)=0. Run the inherited greedy facility procedure for every context: add unused representative minimizing sum of updated residuals, select the positive round minimizing k*m^2+F_k, assign minimizing map labels with deterministic ties. Initialize residuals 38m^2 and assign labels on the first round even if unchanged. With a competing h-element set and minimum loss F_*, marginal averaging gives F_k<=F_*+38m^3 exp(-k/h). Comparing at k=ceil(h(1+ln(m/h)))<=m and averaging, using concavity of x ln(1/x), yields

    s <= 40 beta_*(1+ln(1/beta_*))+1/m+delta_*+gamma_*.

The conservative constant covers 1+38/e. Actual competing maps need not minimize distances into their sets; the minimum only improves the comparison. Enumerate all 504 g,K choices, all O(log^2 m) filters, and eligible factor options (a fixed number of active H). The certificate is independent of selected maps. Retain the minimum score and identifiers. Self pairs have zero loss and penalty, so each selected representative has a permitted chosen replacement (including zero-distance ties). Inactive wide supports cannot generate exceptions.

Use a width-four envelope S on {g} union K containing selected representatives and every source/context with an unpermitted replacement. Its density is beta+gamma (disjoint for minimizing maps). For every narrow support use the unchanged exact E_B on B union K. For each active wide H use the exact light exception on P=H union K:

    E_H^light(a,c,x,y)=1{(a,p_c(a)) permitted}*Z_H(a,p_c(a);x,y).

All branches retain every original constraint. Given any original satisfying tuple, substituting g by its representative either succeeds (the image is in S), fails on an unpermitted pair (original in S), or fails on a permitted pair. In the last case a newly violated narrow support gives the original tuple in its narrow E_B, or a newly violated wide support gives the original tuple in its E_H^light. Each branch witness satisfies all original constraints. This is exact existence/witness equivalence, not preservation of the full original model set under replacement. At most 38 branches. All branch densities are <=s by the weighted counting identity; the sum of light wide densities is at most delta_w. If no eligible choice exists use the inherited exhaustive spatial original-record solver, with no promised saving. There is no modification to external clause syntax or U.

## 3. Bounded-space pair factor certification

Use actual raw directed loss counts already constructed by the inherited pair-sliced map preprocessing. They are O(m^2) entries per support; the permitted-pair mask can be constructed by fixed integer comparisons of the maximum count and dyadic quotient. It fits O(m^2 polylog m). For each t<=b0 and wide H, sort explicit raw bit records (including zero bits) by free-square key, source digit and local column index. There are m*M^2=O(m^3) raw bits per scale before key overhead. Process squares sequentially. Within a square generate the directed difference rows in (a,b) order by copying the current source row to a work tape and scanning the target rows in order, reading the corresponding permitted flags. Use aligned sequential old-zero/new-one bit operations, rewinding source row as needed. All pair flags can be traversed once per square in pair order. No all-pair matrix is stored. Generating rows takes O(m^2*t^2 polylog m) sequential bit work per square and O(m^3 polylog m) span. This includes scanning the raw rows for each source, even for unpermitted targets.

For the linear option reduce each permitted difference row against an echelon basis of current rank, inserting nonzero remainders by pivot order. Reject as soon as the rank cap is exceeded, storing only cap plus one rows. Cost O(m^2*t^2*(1+t^alpha) polylog m) sequential bit work per square. Rank certification uses exact fixed integer comparisons (at alpha=3/8, r_rank^8<=4^8*t^3, where r_rank is rank, not the filter threshold). Store basis rows and a working row of t^2 bits. No need to store all coefficient vectors during certification.

For the dictionary option process difference strings in batches of at most O(m^3 polylog m) bits. Sort each batch by the full bit string, deduplicate and merge against the accumulated exact dictionary. Stop if the distinct count exceeds 2*t^2. Before exceeding the cap, the dictionary has O(t^4 polylog m) bits, at most O(m^(8/3) polylog m), because t<=b0. Store only the current batch and dictionary plus raw input and mask. Choose a batch capacity of floor(m^3/t^2) strings (up to fixed log factors for keys); each full batch has Theta(m^3) payload, so repeatedly merging the dictionary incurs at most a constant times full-batch payload. For a sole small batch the dictionary initially is empty; a final short batch after a full one incurs at most one additional full-batch bound. If there are no permitted strings, the empty dictionary works. Exact sequential merge sorting compares and copies whole strings, cost linear in total bit volume times fixed logs per pass. Thus bit work O(m^2*t^2 polylog m) per square, and original-scale span. A partial batch can have many distinct strings but remains within the batch space; abort before writing a too-large persistent dictionary. No probabilistic hashing or unbounded number of tape tracks.

Summing over (M/t)^2 squares and all dyadic scales through b0 gives O(m^4*b0^alpha polylog m) sequential bit work, with O(m^3 polylog m) span. Applying the inherited fixed-track original-scale sweep yields O(m^7*b0^alpha polylog m)=O(m^(7+2alpha/3) polylog m) physical time. Sorting, filters, active support tests and repeated choices add only fixed constants and log powers. Retain eligibility and successful option identifiers, not all square bases/dictionaries. Pair-sliced map selection with the added m^2 penalty has the same O(m^7 polylog m) cost as before: the stationary pair flag table adds one aligned distance contribution and no change to local matrix dimensions. Thus certification and selection are strictly subcritical independently of s.

## 4. Root factor generation without an m^4 pair-difference table

For each K coarse block of side b0, regenerate maps for all its valid contexts and real source digits using the inherited pair generator, retaining at most m*b0^3<=m^3 records. Attach one permitted flag per actual chosen pair via the stored mask. Total O(m^8/b0 polylog m) physical work across K blocks as in the hybrid parent. Keep the spool across its other projected coarse blocks.

For a projected six-coordinate block extract the m*b0^2 raw row bits on its two free intervals for ALL real row digits, and the at most b0^4 actual map entries for its four other intervals. Include representatives outside source intervals. For its chosen factor option, generate all permitted differences in the free square by the Section 3 sequential routine. In the linear case build the final echelon basis, then regenerate the difference rows and express each against the FINAL basis, giving one length-r_rank coefficient vector per permitted (a,b). In the dictionary case build the final dictionary, then regenerate batches of strings, sort and merge against it to assign exact identifiers. In both cases join the resulting keyed pair references to actual light map entries by sequential sorting/merging, translate their four coordinates and discard global pair identifiers. Do not carry heavy map entries down into the worker. The pair label table has at most O(m^2*(1+b0^alpha) polylog m) bits, below original scale; the root map payload at most O(b0^(4+alpha) polylog m), also below original scale. All scratch and streaming batches fit O(m^3 polylog m) span. The operation never materializes all m^2*b0^2 difference bits at once.

A conservative bound, even regenerating the pair factors independently for each projected coarse block, is O(m^2*b0^(2+alpha) polylog m) sequential bit work per block. The O(m^3) original-scale raw scans, map joins, sorting and padding are within this bound at b0=Theta(m^(2/3)). Physical sweep O(m^5*b0^(2+alpha) polylog m) per projected block. Summed over (M/b0)^6 blocks this is

    O(m^11/b0^(4-alpha) polylog m)
    = O(m^((25+2alpha)/3) polylog m).

This extra pair census is more costly than the raw-row root preparation in the parent, but still below the new overall preparation exponent. The generated local frame is held across all its private coarse choices. No need to retain pair representations for unrelated free squares.

## 5. One reference per map record and exact local positivity

Use the parent's private-stationary tree on V, the three coordinates outside P. Its immutable flags express existence of a private tuple satisfying all V-contained original supports and private padding exclusions. Keep all other original singleton lists (including P-contained supports) moving, O(t^3) records per full tile. No residual compression condition.

The moving exception frame at side t contains the basis or dictionary for the restricted differences of ALL permitted pairs, plus a map on the local (g,K) four-coordinate cube with at most t^4 entries. Each light entry contains its local key and only ONE reference: the coefficient vector or dictionary identifier of its directed difference. Heavy and padded entries are absent. Every free column of the referenced string equals the exact light exception bit at those four digits. Raw row bits and global pair labels are not needed inside the worker. Padding on free coordinates is zero. Frame capacity including local scratch is O(t^(4+alpha) polylog(t+2)), because a dictionary has O(t^4) raw payload and a linear map at most t^4 coefficient vectors of length O(t^alpha). Original lists are smaller. The private subtree's reserved extent is O(t^(4+alpha) polylog(t+2)) by summing (t/s)^3*s^(4+alpha) over dyadic descendant sides with their local logs.

The positivity test is now simpler than the raw-row hybrid test. In a linear basis, a referenced string is nonzero iff its coefficient vector is nonzero, by independence. In the dictionary case keep an exact nonzero flag for each string, obtained by scanning that string when building the dictionary. A local exception is nonempty iff some map entry references a nonzero string. This follows because the free pair ranges are independent of the four map coordinates inside the tile. Sequentially scan map coefficients or sort/merge dictionary references with the nonzero flags. Even a full local sweep for O(t^(4+alpha) polylog t) sequential bit steps costs at most O(t^(8+2alpha) polylog(t+2)) physical moves, though positivity by itself may be cheaper. No matrix of raw-row pairs or repeated enumeration of t^6 projected tuples is necessary. This tests E_H^light alone, not full satisfiability. Private flags and residual singleton checks remain necessary.

## 6. Exact child transformations and charged worker

For each of 512 full dyadic child choices, locate its stationary private child header by delimiter scans; skip zero private flags. Restrict the current basis or dictionary strings to the selected free quadrant. The child linear span equals the restriction of the span of all permitted pair differences, so it obeys the same certified cap. Recompute an echelon basis and transformation U from the restricted parent basis into child coordinates. Rebase each surviving map coefficient c to cU. For a dictionary, intern the restricted strings, build old-to-new identifiers and recompute nonzero flags; relabel map references by exact sort/merge. The fixed permitted-pair filter does not change with scale. Restrict and translate four-coordinate map keys and all moving original singleton records. Both cases preserve every child exception bit by linearity or exact dictionary equality. A coefficient vector can become zero after restriction; no assumption of persistent nonzero status. The frame may retain unused basis/dictionary data, within the cap.

Charge per-bit shuttles of at most O(t^(4+alpha) polylog t) payload across the same parent-local subtree extent. This costs O(t^(8+2alpha) polylog t) per child. Factoring restricted basis and producing U costs O(t^2*(1+t^alpha)^2 polylog t) sequential bit steps, dictionary sorting O(t^4 polylog t), and label/map merge O(t^(4+alpha) polylog t); a local sweep over the frame fits the same charge. For coefficient multiplication use the parent's localized transformation interval holding U, current vector and accumulators: extent and sequential work O(t^(2alpha) polylog(t+2)) per vector, physical O(t^(4alpha) polylog(t+2)) within that small interval. Shuttling one input/output record over the full local frame costs O(t^(4+2alpha) polylog(t+2)); over t^4 records this dominates the multiplication and fits O(t^(8+2alpha) polylog(t+2)). Do not sweep the full frame per bit of all vector transformations.

Temporary parent-size data fit a fixed multiple of the child capacity (ratio of sides two). Private alternatives reuse frames sequentially after clearing; active ancestors distinct. All local fields are functions of t, not m; original coarse offsets restored at root. Fixed finite product components encoded by constant-width blocks of original 0,1,2. No extra physical head, global random access, or input-dependent alphabet. At singleton, true private flag, nonempty exact light exception and empty moving original list are equivalent to the restricted original model condition. Every such model survives its unique path. Including positivity, all fixed child transfers, clearing, navigation, return and witness offsets, local work O(t^(8+2alpha)(1+log(t+2))^A). This is inherited charged physical reasoning, not a measured implementation.

## 7. Coarse root copy, density sum, and clock

Use b0=Theta(m^(2/3)) as above. For each full coarse tile construct the private stationary tree and extract residual original lists by the parent's mobile cache scans O(m^3*b0^3 polylog m). Serialize private tree flags and O(t^(4+alpha) polylog(t+2)) reserved frames using a b0^3-sized mobile private cache, O(b0^(7+alpha) polylog m) per tile including exact private candidate tests. Copy root map/factors and original lists into the root frame by original-scale shuttles O(m^3*b0^(4+alpha) polylog m) per full tile. Charge even rebuilding the private tree for each full tile. With (M/b0)^9 tiles, this costs O(m^12/b0^(5-alpha) polylog m)=O(m^((26+2alpha)/3) polylog m); private serialization O(m^9/b0^(2-alpha) polylog m) is dominated. Mandatory root tests O(m^9/b0^(1-2alpha) polylog m)=O(m^((25+4alpha)/3) polylog m) are also dominated for alpha<1/2. Pair root census, certificate, map selection and inherited width-four/five preparation O(m^(42/5) polylog m) are below the copy exponent. All stationary data, caches and worker components occupy O(m^3 polylog m) span since b0^(4+alpha)<m^3. Success restores latent digits and actual pins, reconstructs fixed auxiliaries and emits contiguous n bits with physical halt head at first bit (O(m^4 polylog m) once); exhaustion halts on blank.

For light wide density rho=R/m^6, positive full nodes at side t count at most min((M/t)^9,R*(M/t)^3). Private pruning only reduces this; visited descendants with positive parents obey the same estimate up to fixed factors. Charge coarse roots separately. Let e=8+2alpha<9. Dyadic traversal cost is bounded by

    sum_t min(M^9*t^(e-9), R*M^3*t^(e-3))
                     *(1+log(t+2))^A.

For R>=1 split at t0=M/R^(1/6). Geometric tails on both sides dominate local log growth and give O(m^9 rho^((1-2alpha)/6)(1+log(1/rho))^A). Empty guards have no positive descendants. Unpruned sum O(m^9). Since every branch density <=s, the fixed number of wide branches and inherited narrow/envelope local-log cost of exponent 1/5 give the main bound. There is no global log m multiplying the density term. All preparation is strictly subcritical independently of s. Greedy comparison makes s->0 on the promise, yielding o(m^9)=o(L^3). For fixed actual program description length ell, exact stage 3 ceil(log2 L) provides at least L^3/2^ell moves once eligible. Little-o eventually fits; no actual ell, numerical inclusion threshold, compiled transition table or exact U run supplied.

## 8. Strict representation separation: cancel cluster-dependent baselines

Let m=2^(2d), w=2^d, cluster index c=floor(a/w). On a single wide support define raw rows as follows (d sufficiently large):

    on (u,v) in [0,2)^2: bit_(2u+v)(c);
    on v=0,u=c+2: 1;
    on v in J=[m-m/2^l,m): least significant bit of a;
    elsewhere: 0.

The three regions are disjoint for large d, l positive with l<2d. The first two pieces are common to all rows of a cluster. J may shrink relatively at any rate with l->infinity. For all same-cluster pairs, the exact directed difference is either the all-zero string or the indicator of v in J, according as the old low bit is zero and the new low bit one. Thus on every aligned free square the permitted difference rank is at most one, distinct count at most two. Choose w as the source block width and r=m^2; all same-cluster pairs are permitted. This passes even alpha=0. It is a genuinely directed difference: the opposite substitution contributes zero, not the unsigned XOR of the two raw rows.

For the raw rows, either parity subset contains all w clusters. At side t=2, each parity subset realizes all sixteen patterns when w>=16, exceeding the parent's dictionary cap 2*t^2=8. At the full free square, the unique marker columns (c+2,0) form an identity submatrix on one row from every cluster, in either parity subset. Rank >=w=sqrt(m), violating the parent's 4*m^alpha for any fixed alpha<1/2 at sufficiently large m. Indeed the marker submatrix already fits the square [0,b0)^2 for large m. Thus all-linear and all-dictionary fail; both parity hybrid partitions fail as well. The difference-only certificate succeeds by cancelling the common, cluster-dependent baseline. This is a separation from the immediate parent's four uniform partitions, not a proof that every imaginable factorization or algorithm fails.

Embed in the earlier nine-group control: g=0,K={1,2,3},H={0,4,5}; unary zero exclusions all groups, main triples {0,i,j} for 1<=i<j<=3 forbid binary dot(a,xi XOR xj)=1; binary inner-product-one forbiddances among groups1..8; equality forbiddances on pairs with0; Latin forbidden triples x XOR y=z among1..8 except private {6,7,8}, where use low-bit parity forbiddance. No other active wide for the designated choice. In each context isolate zero and the three conditioned digits, then select one representative per nonempty fiber of the three context inner-product bits WITHIN EACH CLUSTER, among the remaining digits. At most 8w+4 representatives; beta<= (8w+4)/m ->0. All replacements stay within cluster (gamma=0). Main triples, unary and conditioned inequalities preserved, five free binary inequalities contribute delta_n<=5/m. The wide loss is <=|J|/m=2^-l. Thus beta,delta,gamma all vanish, even with arbitrarily slow chosen upper bound on wide loss. This is not a lower bound on optimal loss; adding a low-bit fiber can in fact remove this wide loss entirely. The example is SAT for large d: all groups1..8 equal to vector6 (even self dot, private low bit zero, XOR of two copies zero not6), choose nonzero a distinct from6 in cluster0 with low bit zero; (u,v)=(6,6) is outside baseline regions and its wide bit is zero. All main triples vanish. Complete primal graph. Easy SAT control, not a hardness instance.

For any alternative g,K, the previous raw weighted-loss lower bound applies unchanged, using only supports not modified by the new H: if g=0 and K differs, a main triple has at least one free other group; distinct nonzero replacement forms are independent, giving m^2/4 weighted loss. If g>=1 a free binary neighbor among groups1..8 gives the same weighted loss. Nonzero-to-zero costs m^2 on unary exclusion. Except for selected representatives and zero sources, all sources incur a constant normalized loss, excluding simultaneous vanishing capacity and full loss. This establishes separation of the new sufficient condition from the immediate hybrid raw-row condition across alternative coordinate choices. Other older solvers may still cover this family.

## 9. Executed finite audit

Host JS semantic reference executed, identical function committed with Node entry point. 32 passes (m=2,3; eight constraint modes; linear and dictionary options on each fixture), prescribed b0=2, source block width2, threshold either m^2 or1 and a forced contextual modular-sum map. Check self eligibility, exact heavy/light partition, original-model substitution recovery using the envelope or exact exceptions, coefficient encodings and dictionary membership, child restriction/rebase/relabel, nonzero-reference positivity, exact local membership, private flags, exclusive active frames, and complete light restricted model equality against direct enumeration. Aggregate:

    323120 direct full tuple checks
    105792 original model recovery checks
    12688 light mask checks
    1628 heavy wide exception entries, 384 light entries
    11736 original model occurrences with heavy wide failure
    3276 original model occurrences in light wide branch
    46349 rank factorizations, 73177 exact encodings, 15000 rebases
    118939 dictionary encodings, 15000 relabels
    83120 local membership checks (41560 per option)
    97292 positivity and active frame checks each
    53360 private tree headers, 365568 child choices
    3276 restricted models in each traversal.

All assertions passed. The reference checks its designated wide H plus direct other-support recovery, not all filters/coordinate choices or adaptive facility greedy. Coarse scale prescribed for finite traversal, not production. Separate baseline cancellation controls at m=4,16,64,256,1024 verify parity row diversity, identity marker rank, and exact directed differences for same-cluster sample pairs (all free columns for m<=64, sampled columns for larger sizes). Output [m,w,even small-square signatures,odd small-square signatures,marker rank,difference checks]:

    [4,2,2,2,2,128]
    [16,4,4,4,4,4096]
    [64,8,8,8,8,131072]
    [256,16,16,16,16,320]
    [1024,32,16,16,32,640]

These use J of size m/2; shrinking J is covered by the mathematical argument, not this finite experiment. The raw parity hybrid certificate fails asymptotically as shown above; small ranks at tested m do not numerically demonstrate failure for every fixed alpha. The audit uses host arrays/maps and direct enumeration, not the streaming pair census, batch sorting, actual bit-tape transfer, serialized private tree, normalized encoder/verifier, compiled original-U program or actual clock. Independent mathematical review, Lean formalization, exact-head CI unconfirmed.

## 10. Disposition

Direct permitted-pair differences replace entire raw-row factorization. This relaxes the structural condition, permits rare incompatible substitutions through an exact envelope, and replaces raw-row-pair positivity by single-reference nonzeroness. Arbitrary filters and arbitrary high-rank/high-cardinality difference matrices are not solved. Next investigate whether low average directed loss itself can guarantee a compact local representation of the chosen differences, or support a density-sensitive alternative when every enumerated pair filter fails. General arbitrary-slow full-average recovery without a certificate, unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
