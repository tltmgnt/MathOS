# F038 — Hybrid exact row factors and localized coefficient transfer

PNP_RESOLUTION_STATUS = OPEN. Parent eccf7dc96eb0f994d946ee7e6bdd7e5ea59a9f1f (local rank). Mathematical machine-existence/resource derivation conditional on inherited fixed-track encoding, sequential sorting, mobile carry shifts, pair-sliced map generation and private-stationary frames. Executed host semantic audit, not physical machine execution, independent review or Lean formalization. Parent combined status and PR-triggered workflow runs empty; push CI unconfirmed.

## 1. Result

Use the inherited nine-group normalized selector family n=19m-7, L=Theta(m^3), selected negative cross-clause bits F_B on supports of width one through three, and actual fixed one-hot/OR/pin/guard extension. Choose g and three conditioning groups K. Let beta=sum_c |C_c|/m^4 and delta=sum_(c,a,B containing g) d_B,c(a,p_c(a))/m^6 be the normalized representative capacity and full weighted directed loss of the previous notes, with nonempty contextual sets and maps into them. A wide H={g,u,v} has u,v outside K; active means its raw rows indexed by g are not identical. P=H union K, V its three-coordinate complement.

For each active wide support, partition its real row digits into a linear part and a dictionary part, using one of the following fixed uniform options: all linear; all dictionary; even digits linear and odd digits dictionary; odd digits linear and even digits dictionary. The partition is fixed for that support across ALL aligned dyadic free-coordinate squares, not selected independently at every node. Pad to M, least power of two >=m, with raw bits zero at padded free digits. For every aligned square D of side t require simultaneously

    rank_GF(2) of linear-part restricted rows <= 4*t^alpha,
    distinct dictionary-part restricted rows <= 2*t^2,

for some one of the four options, which may differ by support. Here alpha is a fixed rational in [0,1/2); concretely take alpha=3/8. No condition on other original supports, even dense arbitrary mixed/private arrays. Empty parts are permitted. This union of sufficient conditions includes both the previous row-count certificate and the previous low-rank certificate (with the same constants and any fixed alpha up to the new bound).

There is ONE fixed deterministic original three-symbol single-tape witness program correct throughout the nine-group family, whose computed full-average score sigma=beta+delta on eligible inputs yields for sufficiently small positive sigma

    T(m)=O(m^((26+2alpha)/3) polylog(m+2)
          + m^9 sigma^((1-2alpha)/6) (1+log(1/sigma))^A),
    visited span=O(m^3 polylog m).

A is fixed and implementation-dependent. At alpha=3/8 this is preparation exponent 107/12, local work exponent 35/4, density exponent 1/24. For alpha=0 the density exponent is 1/6. Along any sequence admitting an eligible configuration and competitor maps with beta_*,delta_*->0, arbitrarily slowly, the program eventually fits exact cubic stage 3 ceil(log2 L). No supplied maps, choice, factorization, rate or per-input exponent. This is not a general rank-rigidity algorithm, arbitrary low-rank-plus-noise decomposition, or unrestricted arbitrary-slow theorem. It uses a small explicit partition family.

The second advance is the physical rebase schedule: separate small transformation workspace from the full moving map. This improves the prior local exponent 8+3alpha to 8+2alpha even for the all-linear option. The previous bound required alpha<1/3, whereas the new one allows any fixed alpha<1/2.

## 2. Certificate and map selection

Test each support's four partitions across all dyadic sides. Use the prior exact echelon rank procedure on the linear rows and exact string sorting/deduplication on dictionary rows. Per scale raw payload m*M^2=O(m^3) bits, fixed logarithmic key overhead. On each square maintain at most 4*t^alpha+1 echelon rows, stop if cap exceeded; reduction costs O(t^2) sequential bit work per basis row up to logs. At alpha=3/8 test r^8<=4^8*t^3 with exact integers. Dictionary count by lexicographic comparison of complete t^2-bit strings, no hashing. Fixed sequential merge sorting compares/copies records with cost proportional to length up to logs. Total sequential bit work O(m^(3+alpha) polylog m), span O(m^3 polylog m), charged physical sweep O(m^(6+alpha) polylog m). Fixed partitions are identified from the raw source digit before constructing restricted strings. Retain only the successful partition identifiers, canonical ties. Do not require that the full matrix pass either prior whole-row certificate.

Enumerate all 504 g,K choices. Active H detection uses actual directed count matrices. Require all active wide supports to admit a partition. Inactive H has no possible exception. Among eligible choices run full-average weighted directed greedy, taking the positive round minimizing k*m^2+F_k per context. The previous sharper entropy comparison yields sigma<=38 beta_*(1+ln(1/beta_*))+1/m+delta_*. Selection and map regeneration use the inherited pair-sliced generator, O(m^5 polylog m) per retained pair, O(m^7 polylog m) overall including actual raw parsing/pins and distance caches. No global map. Keep winning choice and partition identifiers, regenerate as needed. If none eligible use the inherited exhaustive original-record solver; no strict saving is claimed for that fallback.

As previously, search representative relation S={(a,c):a in C_c} and every exact old-zero/new-one exception E_H on H union K. Successful substitution enters S, failure enters some E_H, and all branches enforce the original constraints. This preserves witness existence, not necessarily the whole model set. At most 38 branches. The normalized exception densities sum to delta. S and narrow exceptions use inherited width-four/five stationary workers, O(m^(42/5) polylog m) preparation and local-log density exponent 1/5. No changes to external normalized syntax, pins, verifier or universal machine.

## 3. Hybrid moving representation

For a wide H use the private-stationary architecture: stationary dyadic tree on V with immutable flags for existence of a private tuple satisfying all original V-contained supports and private padding exclusions. All other original records (including P-contained constraints) move as uncompressed singleton lists O(t^3) per full tile. The exception representation at side t consists of:

* exact echelon basis B of the restricted linear-part raw row space, r<=4*t^alpha;
* exact distinct dictionary D of restricted dictionary-part strings, k<=2*t^2;
* at most t^4 map records on (g,K), storing local coordinate keys and TWO tagged row references, one for source and one for actual replacement.

A tagged reference is either a length-r coefficient vector over GF(2) or a local dictionary index. Global representative digits are not stored in the recursive worker. Both references may have either tag independently. Dictionary includes the restrictions of ALL dictionary-part real rows, and basis spans ALL linear-part real rows, not merely rows used in a local map. Padded source/context digits have no map entry; padded free columns are zero for both parts. Evaluate each reference at a free column by XOR dot product or exact dictionary bit. Exception membership is old zero AND new one, regardless of tag combination. No approximate row quotient or dropping original constraints.

Frame capacity including scratch is O(t^(4+alpha) polylog(t+2)): basis r*t^2, dictionary k*t^2, map at most t^4 records of O(r+log(t+2)) bits, original list O(t^3 polylog t). Reserve frames at positive private tree nodes. Subtree extent O(t^(4+alpha) polylog(t+2)) by summing (t/s)^3*s^(4+alpha) polylog(s+2) over dyadic s. Zero headers compact. Different projected choices reuse private frames sequentially, active ancestors distinct. Local field widths depend on t, not m.

## 4. Exact local positivity across all four tag combinations

Transpose basis and dictionary into a common column-major stream, with each column containing its r basis bits and k dictionary bits in fixed label order. A fixed sequential sort on local coordinate/label keys costs O(t^4 polylog(t+2)) bit work and fits frame space; even a local full-frame sweep simulation costs O(t^(8+alpha) polylog(t+2)). Preserve the original row-major copies or reconstruct them with another such sort. No large matrix of all coefficient pairs.

For each map record, carry its two references in a mobile O((r+log(t+2)) polylog(t+2)) workspace along this stationary stream. At each column, compute the two linear dot products as applicable by scanning the small vectors, and obtain any dictionary-referenced bit by matching its local label as the column's dictionary stream is read. No need to carry a complete dictionary row. Keep accumulators for at most two bits and the old-zero/new-one OR. Even charging a full small-workspace scan and carry shift per stationary block across the full frame, cost O(t^(4+2alpha) polylog(t+2)) per map record. Copy-in/out, return to marked record, resetting per-column counters and rewind fit this bound; tags are a fixed finite set. Over t^4 map records the positivity test costs O(t^(8+2alpha) polylog(t+2)). It is exact for E_H on the projected cube. Private zero flag or empty E_H prunes. Other constraints still checked by the original lists at singleton. This test does not assert existence of a common full satisfying witness before leaf checking.

## 5. Child reindexing and localized coefficient transfer

For each of the fixed 512 child choices locate the stationary private child header; skip zero flags. Restrict the two row components to the selected free quadrant. Compute the child linear echelon basis and transformation U from each restricted parent basis row into child coordinates, as in the prior note. Restriction is linear and the child span equals the restricted span of all original linear-part rows. Likewise restrict parent dictionary strings, intern exact duplicates by sequential sort and generate old-to-new dictionary labels. Both child caps hold by the same fixed partition certificate, including when rank drops or dictionary strings coalesce. No conversion between the parts required.

Restrict and translate the four-coordinate map keys and the original residual records. For linear references replace c by cU over GF(2); dictionary references use the exact old-to-new label map. The representation preserves all child old/new row bits. Copy the necessary parent data into child-local scratch by per-bit shuttles over at most parent subtree extent. Payload and distance each O(t^(4+alpha) polylog t), charge O(t^(8+2alpha) polylog t). Intermediate parent-size data fit a fixed multiple of the child capacity because the side ratio is two. Parent remains intact until return.

The important new bound concerns multiplication by U. The previous proof applied a full-frame sweep to the entire sequence of coefficient multiplications, charging t^(8+3alpha). Instead keep U, a single map record, input/output coefficient accumulators and local counters in a dedicated small stationary subinterval of O((r+1)*(r'+1) polylog(t+2))=O(t^(2alpha) polylog(t+2)) blocks (for alpha=0 the logs account for local coordinate widths). For each map entry copy the input record from its marked position into this interval, transform its linear references, then copy the output record to the translated output stream. Even per-bit shuttles across the entire parent/child-local frame cost at most O(t^(4+2alpha) polylog(t+2)) per entry, because a record has O(t^alpha polylog(t+2)) bits. The output stream has a marked append cursor and its positions can be found by scans included in the same bound. A fixed sequential bit routine computes cU by aligned XOR of rows into the accumulator, O(t^(2alpha) polylog(t+2)) bit steps per reference. Simulate only this small subinterval during that multiplication, not the entire frame. Its physical cost O(t^(4alpha) polylog(t+2)) per entry is dominated by the record shuttles for alpha<1/2. Across t^4 entries total O(t^(8+2alpha) polylog(t+2)). Clear small scratch per entry, retain U across all entries.

Dictionary relabeling can be done separately by two sequential sort/merge passes on reference labels, restoring map-record order by the translated coordinate key; pass through linear references unchanged. Total bit work O(t^(4+alpha) polylog t), span the same, physical sweep O(t^(8+2alpha) polylog t). Rank factoring, transformation construction and dictionary restriction/sorting fit this charge too: rank bit work O(t^2*(r+1)^2 polylog t), dictionary bit work O(t^4 polylog t), plus frame scans and original-list translation. All copies and temporary scratch use child/parent-local intervals. A fixed number of tape components suffices and no input-dependent tracks or free indexed access. Actual encoding inherited as constant-width physical blocks over 0,1,2.

Including all fixed children, positivity, delimiters, filtering, clearing, pop/return and witness offsets, the local cost is O(t^(8+2alpha)(1+log(t+2))^A). At singleton true private flag, nonempty exact E_H and empty original residual list characterize exactly an original restricted model. Every original restricted model survives its unique path. Private choices and projected choices reuse frames only after clearing; no active ancestor alias. This improves the all-linear rebase upper bound as well. No claim that the bound is optimal.

## 6. Coarse preparation and span

Choose b largest dyadic with b^3<=m^2, b=Theta(m^(2/3)). b divides M. Since alpha<1/2, b^(4+alpha)<=m^((8+2alpha)/3)<m^3. Enumerate K coarse blocks first and retain maps for all real sources in their contexts (m*b^3<=m^3 records). Regeneration O(m^8/b polylog m), including per-pair output shuttles as in the parent.

For each projected six-coordinate coarse block extract m*b^2 raw bits for all real source and representative rows, including representatives outside source intervals. Factor linear rows and reduce them against the final basis, and intern dictionary rows exactly. Join the global source/representative labels in the relevant b^4 map records to their corresponding tagged representations, translate keys and discard global labels. Sequential bit work O(m*b^(2+alpha) polylog m + b^(4+alpha) polylog m) <= O(m^3 polylog m), including sorting/merging. Thus physical sweep O(m^6 polylog m) per projected block, O(m^12/b^6 polylog m)=O(m^8 polylog m) total. Keep a copy of the root representation across private coarse choices.

For every full coarse tile, extract private-only original records and padding units, O(m^3 b^3 polylog m) physical moves by mobile scratch. Evaluate private candidate tuples at all dyadic subblocks by local sequential cache scans, serialize the private tree with reserved frames as in parent. Output extent O(b^(4+alpha) polylog b), moving b^3-size cache along output cursor O(b^(7+alpha) polylog m) physical moves per tile, dominating private candidate tests. This upper bound allows rebuilding the private tree for each full tile. Extract residual singleton lists O(m^3 b^3 polylog m); copy root exception frame and residuals into private root using original-scale shuttles O(m^3 b^(4+alpha) polylog m). Clear worker after traversal. All original-scale data plus the reserved tree and scratch use O(m^3 polylog m) span. No global sweep during local recursion.

Sum across (M/b)^9 full tiles. Root copy/extraction O(m^12/b^(5-alpha) polylog m)=O(m^((26+2alpha)/3) polylog m). Tree serialization O(m^9/b^(2-alpha) polylog m), dominated. Mandatory root tests O(m^9/b^(1-2alpha) polylog m)=O(m^((25+4alpha)/3) polylog m), also dominated since 2alpha<1. All earlier preparation terms are below the copy exponent, including the narrow solver's 42/5. Unlike the prior general alpha analysis there is no separate larger root exponent. Once-only output restores latent digits and actual pins, reconstructs original one-hot/OR/guard witness, emits contiguous n raw bits with physical halt head at first bit; exhaustion halts on blank. O(m^4 polylog m) once, dominated.

## 7. Density sum and exact clock

For R=|E_H| and rho=R/m^6<=sigma, positive full nodes of side t number at most min((M/t)^9,R*(M/t)^3). Private pruning only reduces this. Visited nonroot nodes have positive parents, so their counts satisfy the same upper bound up to a fixed factor. Root costs separately charged. Let e=8+2alpha<9. The local-log work is bounded by

    sum_(t dyadic) min(M^9*t^(e-9), R*M^3*t^(e-3))
                    *(1+log(t+2))^A.

For R>=1 the crossover t0=M/R^(1/6) yields geometrically decaying tails, with exponents 9-e and e-3, dominating polynomial growth in local log. Thus work O(m^9 rho^((1-2alpha)/6)(1+log(1/rho))^A). No positive traversal if R=0. The unpruned sum is O(m^9). Combining constant-many wide branches and inherited narrower ones gives the displayed theorem since (1-2alpha)/6<=1/5. Under the competitor promise sigma->0 by the sharper greedy comparison; all preparation is polynomially subcritical independently of sigma. Thus T=o(L^3) at original-scale span. For the fixed actual machine description length ell the exact stage 3 ceil(log2 L) allocates at least L^3/2^ell transitions once eligible. The little-o bound eventually fits it. No compiled machine description, numerical cutoff or actual U stage run supplied.

## 8. Separation from both whole-row certificates

Let m=2^d, all binary vectors as digits. For sufficiently large d take k=floor(log2(d-1)), q=2^k, and f(u) the k-bit integer extracted from bit positions 0,3,...,3(k-1). Let J=[0,m/2^l) for l positive and slowly growing (e.g. l=floor(log2(log2(d+2))) eventually), so J contains [0,2^(3k)) for large d. Set

    F_H(a,u,v) = bit_(1+f(u))(a) * 1{v in J},  if a even,
                 1{v=a AND u!=a},             if a odd.

Even and odd refer to least significant bit. For even rows in an aligned u interval of side t=2^s, at most ceil(s/3) selected bits vary, giving rank <=2^ceil(s/3)<=2*t^(1/3)<=4*t^(3/8). Free v restriction cannot increase rank. Odd rows with a outside the v interval are zero, and at most t other rows remain, so dictionary count <=t+1<=2*t^2. Both hybrid caps hold at every scale.

At square [0,t)^2 with t=2^(3k), all q feature labels occur and all q-bit assignments to bit indices 1..q occur among even a. Hence at least 2^q distinct rows; ratio to any constant times t^2 diverges as d grows. The previous whole-row quadratic dictionary certificate fails. At root, all m/2 odd rows are nonzero and have disjoint v support, so they are linearly independent over GF(2). Whole-row rank >=m/2 fails not just the previous alpha<1/3 criterion but every fixed alpha<1. Even rows need not be independent of odd rows for this lower bound. Thus this is a genuine hybrid representation separation, not merely a better bound for the same low-rank family. For the linear part alone rank is q at the selected square, of order t^(1/3), so the older alpha<1/3 bound also fails there. Finite controls below test smaller component matrices; the asymptotic claims use these exact counting proofs.

Embed in the prior nine-group algebraic control g=0,K={1,2,3},H={0,4,5}. Unary zero exclusions all groups, main triples {0,i,j} for 1<=i<j<=3 forbidding <a,xi XOR xj>=1, binary inner-product-one forbiddances among groups 1..8, equality forbiddances on pairs with 0, Latin forbidden triples x XOR y=z among groups 1..8 except V={6,7,8}, where use low-bit parity forbiddance. No other g-containing wide support. Isolate zero and the three conditioned digits and choose one representative for each nonempty fiber of the three inner products with the conditioned digits among other nonzero sources. At most 12 representatives; beta<=12/m, delta_n<=5/m. Any replacement row has at most m*|J| selected free pairs if even and m-1 if odd, so every directed wide loss <=m*|J|+m. Hence delta_w<=2^-l+1/m->0, without assuming a polynomial decay rate. This is an upper bound, not a lower bound on the best achievable average loss. Family SAT for large d: take groups 1..8 all equal to 6, a nonzero even digit distinct from 6 with bit_(1+f(6))(a)=0. Self dot zero, Latin and private parity pass, main triples vanish, wide bit zero. Complete primal graph. Easy SAT control, not hardness.

For alternative g,K the earlier lower bounds remain: if g=0 and K differs, some main triple has at least one free coordinate; independent binary forms for distinct nonzero a,b give weighted loss m^2/4. If g>=1, a free binary neighbor among groups 1..8 gives same weighted loss. Nonzero-to-zero loses m^2 on its unary bit. Apart from selected representatives and zero sources, each source then incurs constant normalized loss on some section, excluding simultaneous vanishing capacity/full loss. Thus this control separates the hybrid sufficient condition from both preceding whole-row conditions even if alternative coordinate choices are allowed. No claim of separation from every earlier solver or that the optimal loss actually vanishes slowly.

## 9. Executed finite validation

Host JS audit executed in tool runtime, identical function committed with Node entry point. Sixteen fixtures m=2,3, eight modes, forced b=2, forced modular-sum maps and even/odd partition. Tests exact linear encoding, dictionary interning, child restriction and independent rebasing/relabeling of tagged references, all four source/replacement combinations, positivity, private flags, exclusive frame reuse, original residual translation and exact restricted model equality. Totals: 161,560 direct full tuple checks, 26,680 private headers, 260,678 active-frame and positivity checks each, 147,060 exact local membership checks, 13,399 positive nodes, 11,650 singleton checks, 895,488 child choices, 4,104 coarse tiles, 7,506 restricted models in each traversal. 265,654 rank factorizations, 502,746 exact linear encodings, 116,832 coefficient rebases, 458,078 dictionary encoding checks, 62,472 dictionary relabels. Tag-pair membership checks (linear/linear, linear/dictionary, dictionary/linear, dictionary/dictionary): 63,256; 32,376; 34,360; 17,068. All assertions passed.

Separate finite component controls use parity hybrid rows with spaced-bit features and no v cutoff (J=full domain), choose feature positions that fit in each small d. Verify hybrid caps at every aligned square and root rank lower bound. [m,max linear rank,max dictionary count,full rank,aligned squares]:

    [4,1,2,3,21]
    [8,2,4,6,85]
    [16,2,8,10,341]
    [32,4,16,20,1365]
    [64,4,32,36,5461]

Symbolic exponent controls [d,q,log2(t),old dictionary bound exceeded,old rank bound exceeded]:

    [64,32,15,true,true]
    [128,64,18,true,true]
    [256,128,21,true,true]
    [512,256,24,true,true]
    [1024,512,27,true,true]

These are arithmetic comparisons not enumerations of enormous matrices. Host uses arrays/maps, direct bit comparisons and recursive objects. It does not implement all-choice certificate selection or every partition option, actual bit-tape sorting, localized physical multiplication, stationary serialization, compiled U transitions, normalized encoder/verifier or exact clock. No measured transition counts, independent review, Lean formalization or exact-head CI confirmation.

## 10. Disposition

Hybrid exact row factors admit wide supports failing both the previous whole-row rank and cardinality certificates. Localized coefficient transformation extends the strict rank exponent range from alpha<1/3 to alpha<1/2. Arbitrary residual arrays are allowed. However the fixed partition family is restrictive, and arbitrary high-rank, high-cardinality matrices may fail every option. Next investigate computable finer partitions or factorization of the actual selected row-difference predicate, rather than requiring all raw rows to satisfy one of these certificates. General arbitrary-slow full-average recovery without a structural certificate, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
