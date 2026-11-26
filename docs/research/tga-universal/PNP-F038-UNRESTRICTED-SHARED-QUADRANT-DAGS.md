# F038 — Shared quadrant DAGs for irregular local correction rows

PNP_RESOLUTION_STATUS = OPEN. Parent e8fd3bdb89a62f7180d3e739e8307e8505d02671 (run-coded overflow). Conditional mathematical resource derivation using inherited original parsing, pair-sliced maps, fixed-track sequential sweeps, mobile carry shifts, adjacent spatial stacks and original-record fallback. Executed host semantic regression; not compiled original-U transitions, independent review or Lean formalization. Parent status and PR-triggered workflow lists empty; push CI unconfirmed.

## 1. Result

Use the inherited normalized nine-group selector family n=19m-7, L=Theta(m^3), actual negative cross-support bits F_H of width at most three, and original one-hot/OR/pin/guard extension. For chosen compressed group g and three context groups K, generated representative sets C_c and actual maps p_c(a) use self ties for selected representatives. The inherited capacity and directed loss scores are beta, delta_n, delta_w. For a wide H={g,u,v}, use the direct guard E(a,c,x,y)=(1-F_H(a,x,y))*F_H(p_c(a),x,y), or the parent's exact missing-bit correction with the additional factor (1-F_H(j_H(a,p_c(a)),x,y)). The latter center is learned by the previous approximate-class routine, not substituted into original constraints. Padding makes E false. Let R=|E|, rho=R/m^6.

Pad to M the least power of two >=m, B the largest dyadic with B^3<=m^2. On a projected six-coordinate cube D of side t<=B, construct the exact Boolean free-square row for every real source/context assignment. Represent the collection by one shared, levelled, ordered quadtree DAG:

* Zero is implicit at every level. The unique nonzero side-one node represents bit one.
* At side 2^j, j>=1, a nonzero node is the ordered tuple of four quadrant IDs at level j-1. Four zero IDs represent implicit zero.
* Intern equal tuples at EACH level, across ALL actual source/context rows in the cube, not just within a fixed source. The order is (low x,low y), (low x,high y), (high x,low y), (high x,high y).
* Keep one actual four-coordinate map record and root pointer for each nonzero row. No restriction on the number of distinct nonzero root pointers beyond the t^4 actual assignments.

Let W_DAG(D) be the number of distinct reachable nonzero nodes summed across levels, counting the terminal one once. This is intrinsic to the collection of strings, independent of numeric node IDs or insertion order. It is not rank, run count, or an estimate of an arbitrary compressed program's size. The dictionary and map fields are O(log(t+2)) bits each, since a forest of t^4 complete quadtrees has fewer than 2t^6 nonzero occurrences. Thus W_DAG<=2t^6. For dyadic 1<=C<=m^(1/32), overflow iff W_DAG(D)>C*t^4. Stop at first overflow on each dyadic path below a projected B-root. Define omega_DAG(C)=sum_(first overflow D) t_D^6/m^6, using padded volume with the real denominator. At overflow abandon the recovery guard ONLY, retaining all original constraints.

    J_DAG(E)=min_C (C^13*rho+omega_DAG(C)).

For a direct program include the parent's dense and run-coded routes:

    Q_direct=beta+delta_n+sum_H min(J_dense(Z_H),J_run(Z_H),J_DAG(Z_H)).

Enumerate the inherited finite generated-map policies, coordinate choices and logarithmically many capacities, choose exact minimum, regenerate. There is a fixed deterministic original three-symbol one-tape witness program correct throughout the family, with charged bound for sufficiently small positive Q_direct

    T(m)=O(m^(42/5) polylog(m+2)
             + m^9 Q_direct^(1/6)(1+log(1/Q_direct))^A),
    visited span O(m^3 polylog m).

The additional DAG route can be included in the complete approximate-template portfolio, with no increase in its preparation exponent 35/4 or density-saving exponent 1/12. The score minimum cannot increase for identical previous candidates, because all earlier options remain available. No pointwise runtime dominance or dominance of DAG count over run count at identical capacity is asserted. No supplied maps, DAG, capacity or convergence rate. These are conditional fixed-machine resource bounds, not a solution of the unrestricted problem.

## 2. Exact shared nodes and child restriction

Inductively, equal nonzero ordered tuples at level j mean equal bit matrices of side 2^j, and unequal tuples mean unequal bit matrices, since their quadrants partition the square. Zero is unique by construction. The graph of all reachable distinct nonzero submatrices, distinguished by side, is therefore canonical up to IDs. Sharing across different source digits is safe: source and context remain in actual map keys, and only the identical exception matrix is shared. This does not imply any equivalence of actual labels in original or narrow constraints.

For a dyadic child of side u=t/2, restrict and translate the four actual map coordinates. Replace each surviving root by its pointer for the selected free quadrant, dropping zero roots. Starting from this set of root IDs at level log2 u, mark reachable nonzero nodes by descending level, joining the selected IDs against the level's dictionary and emitting its child IDs. Sort and deduplicate the emitted IDs at every level. Then renumber reachable nodes in increasing old ID order at each level, bottom-up; rewrite child IDs and actual map references by exact sort/merge with the old/new ID tables. No equality comparisons of dense matrices required during restriction. Distinct nodes at a fixed level remain distinct after injective renumbering of reachable child IDs. Every submatrix of a surviving child row is already represented by a node in the parent; all unreachable nodes are removed. Consequently the resulting count is EXACTLY W_DAG(child), not a charge for irrelevant parent nodes. The cap may fail after restriction because its allowed size shrinks, even though no new nodes are introduced.

All data are explicit sequential records of fixed arity, with local size/ID fields. The reachability and renumbering passes cost O((W_DAG+t^4) polylog(t+2)) sequential bit work and space on fixed multitapes: at each level sort/merge the relevant node IDs, child records and map entries; even scanning the whole parent payload at every level adds only log(t+2). No random access or nonlocal pointer chasing is assumed. Use temporary parent-size scratch before appending the compact child or its overflow header. Actual child payload need not have a constant-factor lower bound. Positivity is exactly a nonempty map list (each root nonzero), since real source/context entries and free one bits exclude padding. This is positivity of E on the projected cube, not compatibility with original clauses.

A nonoverflow frame with original records has O(C*t^4 polylog(t+2)) bits, including O(t^4) map entries and O(t^3) original singleton records. Set local capacity to min(C,2t^2) and clip again at each child to min(current,2u^2), which is exactly min(C,2u^2); since W_DAG<=2t^6, this changes no cap test. IDs, counters and capacity fields thus use O(log(t+2)) local bits, never log m on small frames. Per fixed child local sweep simulation and per-bit shuttles across the adjacent frame charge O(C^2*t^8*(1+log(t+2))^A) physical moves including original record restriction, renumbering, tests, cleanup and return. There are a fixed number of children (64 for census, 512 for full search). Append one child adjacent to its stationary parent, process and pop before next. Active frame capacities sum geometrically, O(C B^4 polylog B). Constant-width blocks encode fixed finite product components over actual tape symbols 0,1,2, not an input-dependent alphabet or extra physical heads.

## 3. Root construction: incremental sharing has a real cost

Inherit O(m^5 polylog m) physical pair-sliced generation for a retained context pair and all values of its third coordinate. Enumerate K coarse B-blocks first, regenerate relevant pairs, filter to the block, and keep at most m B^3<=m^3 actual map records. Total pair generation O(m^8/B polylog m). Attach actual center metadata (if approximate mode) by inherited sequential sort/merge. Obtain exact R independently by summing directed/missing-bit pair weights over all actual assignments, not from DAG size.

For each projected B-root, extract the <=B^4 actual map entries and the restricted m B^2 raw bits for all real row labels (old, target, center); zeros on padded free coordinates. Sort map entries by source and target. Process one source at a time. At most m distinct actual target labels, each with one center fixed by source/target. Using sequential sorted requests/merges against the restricted raw cache, compute all its requested actual E strings. Copy/duplicate only O(m B^2 polylog m) bits. Build their full quadrant occurrence lists by scans and sorting on (target,level,quadrant address) local records: at most O(m B^2) occurrences, all nonzero descendants of some nonzero row; discard zero leaves and all-zero parents, use zero IDs for omitted nodes. Process levels bottom-up. At each level, translate occurrence children by the IDs just assigned at the previous level, sort equal ordered tuples together, merge with the existing level dictionary for previously processed sources, assign stable IDs to newly encountered tuples. Prior IDs never change. Emit source map root references using actual labels, not canonical labels as replacement values. Local row roots from this source use at most B^3 map entries. No dense matrices of all B sources retained simultaneously.

The existing shared dictionary may need to be scanned ONCE PER SOURCE, unlike the parent run-coded root which can intern per source independently. Stop as soon as the accumulated exact nonzero node count exceeds C B^4. All nodes inserted from nonzero requested rows are reachable (including those of the current source); adding sources cannot remove a reachable node. During bottom-up processing one can either count and stop when cap exceeded, or finish this source in temporary O(m B^2 polylog m) occurrence space then check. For a successful root the permanent dictionary has at most C B^4 nodes. For an overflowing root a bounded partial dictionary plus a single source's temporary occurrence/dictionary additions suffice. The actual map spool, raw cache, permanent/temporary node dictionaries, sorting buffers and map output fit O(m^3 polylog m) span, since C B^4<=m^(1/32+8/3)<m^3. No global width-six bit array, nor global DAG for all projected blocks.

Sequential root work is conservatively bounded by

    O((m^3+B*(m B^2+C B^4)) polylog m)
      = O((m^3+C B^5) polylog m).

This includes scanning the original-scale data to extract the root, scanning the restricted raw cache and existing dictionary per source, sorting/merging fixed-arity records over logarithmically many levels, stable-ID allocation, and emission. Bit lengths O(log m) at root, O(log B) equivalent since B=Theta(m^(2/3)). Inherited full-span sweep gives O((m^6+C m^3 B^5) polylog m) physical per root, across (M/B)^6 roots:

    O((m^12/B^6+C*m^9/B) polylog m)
      <= O(m^(803/96) polylog m).

Here 803/96=9-2/3+1/32 is strictly below 42/5. This is a slight increase over the parent's O(m^8) root generation; do not claim unchanged census preparation O(m^8). Install a successful root cache once adjacent to active worker, even charging original-scale per-bit shuttles O(m^3 C B^4 polylog m) per root, total O(C m^9/B^2 polylog m) below root generation. Overflow root uses only a header. Reuse for projected census or all private coarse choices.

## 4. Projected-only census and exact score

Traverse only the six projected coordinates. At a nonoverflow positive node generate 64 children with Section 2. At overflow add t^6 to volume subtotal and stop the path; at empty stop without charge. Empty ancestors cannot contain nonzero rows in children. First-overflow cubes disjoint, their summed padded volume exactly the union volume. Increasing C cannot increase this union, since each individual node's intrinsic W_DAG does not depend on C. No monotonicity assertion about C^13*rho+omega. The volume can be accumulated by local subtotal <=t^6 while unwinding, no need to store a global list of overflow cubes. Even ignoring pruning the local projected traversal work is

    O(C^2 * sum_(t<=B dyadic) (M/t)^6*t^8*(1+log(t+2))^A)
      = O(C^2*m^6*B^2 polylog m)
      <= O(m^(355/48) polylog m).

Root generation dominates, total census O(m^(803/96) polylog m), original-scale span. Enumerate logarithmically many capacities, all fixed map policies, coordinates/supports and (in approximate mode) logarithmically many radius/template parameters. Exact integer score for a route is

    m^6 J_C = C^13 R + sum_D t_D^6.

All score fields O(log(m+2)) bits, exponents fixed. Select minimum with fixed ties, retain only winning parameters and scalar scores, regenerate identical data. No unobserved certificate/advice. Prior alternatives remain in the portfolio and can be selected independently per support. In the full approximate mode use the parent score with min(eta_H,Lambda*kappa_H,J_dense(E_H),J_run(E_H),J_DAG(E_H)); other terms and exact missing-bit definition unchanged.

## 5. Full search and clock bound

In direct mode search representative envelope on {g} union K, exact narrow exceptions, and each selected wide route. Given an original satisfying tuple, substitute g by actual p_c(a); successful substitution yields an original model in envelope; failure on a support containing g gives the original tuple in its narrow or wide exception. In approximate mode inherit the parent's heavy-envelope and template/missing-bit containment proof. Every branch enforces ALL original constraints and padding. For a local DAG route, before overflow membership is exact; at a first overflow search the entire full tile using original constraints only. This intentionally enlarges the branch to original AND (E OR first-overflow projected membership). Every original E model survives; every accepted tuple is original, possibly outside E. No changed verifier.

For each full B tile extract all original width<=3 records by inherited mobile O(B^3 polylog m) scratch over original-scale stationary data, O(m^3 B^3 polylog m). Copy cached root locally O(C^2 B^8 polylog m), including root tests and cleanup. Across (M/B)^9 tiles total O((m^12/B^6+C^2*m^9/B) polylog m)<=O(m^(403/48) polylog m). This remains below 42/5, as do the new root and projected census charges. Narrow/envelope stationary width<=5 worker at nested b'=Theta(m^(3/5)) remains O(m^(42/5) polylog m), local density exponent at least 1/5. Keep B-sized K spools across nested projected blocks as in parent. At singleton true guard and empty original list characterize restricted original model. Restore actual digits while unwinding, reconstruct actual pins/one-hot/OR/guard extension, emit contiguous n raw bits with physical halt head at first bit; failure halt on blank. Once-only O(m^4 polylog m) inherited output.

At a first overflow of side t, the original-record unpruned spatial stack costs O(t^9): at scale s there are at most (t/s)^9 nodes at O(s^6*(1+log(s+2))^A0) physical moves, and the local-log geometric sum converges. No global log m multiplier. There are at most (M/t)^3 private full tiles for that projected overflow. Thus total fallback O(M^3 sum_D t_D^6)=O(m^9 omega_DAG). Initialization of overflow child original records charged at parent or mandatory root. Nonoverflow positive full-node count at side t <=min((M/t)^9,R*(M/t)^3). Child tests charged at positive parents, roots separately. With local C^2*t^8 local-log work, crossover t0=M/R^(1/6) gives O(C^2*m^9*rho^(1/6)*(1+log(1/rho))^A) for R>=1, no positive descendants for R=0. Set X=C^13 rho, then C^2 rho^(1/6)=C^(-1/6)X^(1/6); log(1/rho)=log(1/X)+13 log C. Negative capacity power absorbs all fixed log C powers uniformly near zero. Add overflow volume to obtain O(m^9 J_C^(1/6)*(1+log(1/J_C))^A). All branches fixed in number. This gives Section 1's bounds conditional on inherited physical routines. No global log m multiplying the new score-dependent term.

If rho->0 and lim_(C->infinity dyadic) limsup_(m->infinity) omega_DAG(C)=0, then fix a sufficiently large finite C first, eventually under production cap, and C^13 rho->0. Hence J_DAG->0, no prescribed convergence rate. This does not establish that arbitrary vanishing rho implies tight overflow. On Q->0, time o(m^9)=o(L^3), span O(L polylog L). A fixed actual original program of description length ell receives >=L^3/2^ell transitions at exact stage 3 ceil(log2 L) once eligible; little-o eventually fits. No compiled ell, numerical threshold or actual U-stage execution.

## 6. Strict separation from dense and run-coded certificates on generated maps

Modify the parent's slab control by introducing a checkerboard mask, so actual raw run weight becomes large but repeated quadrants share exactly.

Let m=2^d, r=floor(9d/10), q=2^r, T=[m/2,m/2+q), B=2^floor(2d/3). Let N be the least power of two >=2*r*log2(d) for large d, S=B/N dyadic. Then S^3>=m eventually and S>=2, N=O(d log d). Use g=0,K={1,2,3}. Force target f(c)=m/2 plus r interleaved low input bits from c1 and c2 by a unary support excluding outside T and two binary supports checking their respective output bits. All narrow bits vanish at f(c). In every aligned K B-cube f covers all q labels uniformly. Optional unary zero exclusions on other groups. Let h_a(x,y)=binary dot(a,x) XOR lowbit(y). In each aligned x B-block use N consecutive slabs of length S numbered i. Sole wide H={0,4,5} has the following raw forbidden bits:

* a outside T: one on m/4<=y<m/2, equal to h_a on m/2<=y<m, zero elsewhere.
* b in T: on y<m/4, one iff i<2r, i mod 2 equals bit floor(i/2) of b-m/2, AND x mod 2 equals y mod 2. On m/4<=y<m/2 equal to h_b; zero on y>=m/2.

No other cross supports. Easy SAT family: choose nonzero contexts, a=f(c), nonzero x and y>=m/2, other digits nonzero. Not hardness.

For each outside source and any target, directed difference equals checkerboard on the r selected slabs times the low y region. Its weight D0=m^2*r/(8N); put zeta=r/(8N)->0 at order 1/log d. Distinct outside/outside loss D_s=m^2/8 by independence of the two distinct h forms on x and independent low y bit. Distinct inside/inside directed loss m^2/16 plus Hamming distance times m^2/(8N); the middle h part contributes probability 1/4, and each differing bit contributes one new checkerboard slab in every B-block. Summed inside-to-inside losses independent of candidate in T since each bit balanced. Target-to-outside nonnegative plus unary narrow penalty m^2.

Actual unpenalized full-average greedy first facility f(c) unique: equal summed wide losses among T, zero narrow at f, positive narrow total for other targets, and outside candidates have summed wide loss >=(m-q-1)D_s from outside sources alone, eventually greater than full sum to f because q/m,zeta->0. Extra candidates in T cannot strictly improve outside-source losses, since their wide loss remains D0 and narrow nonnegative. Extra outside candidates can improve only their own source by <=D0<m^2 (other outside sources incur D_s>=D0, inside incur unary m^2 while current loss <=m^2). After first facility and while only T facilities selected, outside-source maps remain f by earliest-selected tie. At the first outside facility marginal below m^2, all subsequent marginals nonincreasing, so the best positive greedy round never includes an outside facility. Selected self ties do not affect outside sources. Thus actual C_c subset T and p_c(a)=f(c) for every outside source; extra inside facilities permitted. Beta<=q/m, delta_n=O(q/m), delta_w<=zeta+q/m, all vanish. For any maps outside nonself loss >=D0 eventually, self fraction<=beta, hence delta_w>=max(0,1-q/m-beta)*zeta. Genuine slow loss, not a lower bound on SAT runtime.

Consider every projected B-root wholly outside T in source, wholly inside [0,m/4) in free y. Per source, all q distinct nonzero checkerboard slab patterns occur. Parent dense cap <=m^(1/32)*B=o(q), so every such root overflows. For the run-coded certificate, every one of r S active x coordinates has exactly B/2 separated y runs, and adjacent active x coordinates have different traces (opposite parity); separated slabs cannot merge across an empty gap. Thus for each row weight >=r S B/2, and summing B sources and q distinct rows gives

    W_run(D)>=q*r*B^3/(2N).

The ratio to maximum allowed C B^4 is >=q*r/(2N*m^(1/32)*B)->infinity. Thus BOTH parent certificates overflow on projected volume fraction at least (1-q/m-2B/m)/4, uniformly over their capacities. This is not a separation from their complete adaptive solver across other maps/radii. For the same null-template candidate the all-target union also has nonvanishing density from the outside targets on high y region: for x!=0, both dot values occur among outside labels (size >m/2), so any old-zero high-column has some outside target setting it. And fixed positive log-power penalty on delta_w does not vanish for zeta=Theta(1/log d).

By contrast for a source interval wholly outside T, all actual E patterns are independent of the source once f(c) is fixed. At aligned scale t<=S, a free square lies within one x slab and one y band, so every restricted row is zero or the same checkerboard (at singleton perhaps zero); all nonzero rows share one node per nonzero level, W_DAG<=1+log2 t. At t>=S, the free square is partitioned into t/S aligned x slabs, and y is entirely in one band because t<=B divides m/4 for large d. If y is outside the low region all rows zero. Otherwise all S-square nonzero patterns are the SAME checkerboard (S even, aligned). Below side S their reachable nonzero nodes share globally. Above side S and for a fixed target row, identical y intervals give equal matrices, so at scale 2^j>=S there are at most t/2^j distinct nonzero submatrices (one for each x interval). Summing across these scales and all q target rows, and adding the common lower-level nodes, gives

    W_DAG(D)<=2q*t/S+1+log2 S
              <= 2m*t/S+1+log2 S
              <= 3t^4

for sufficiently large d, using S^3>=m and t>=S (indeed m*t/S<=S^2*t<=t^3). The much stronger sharing across sources is essential to this simple count. The same bound holds if only a subset of target labels is used in a child; no need to know their global bits in a descendant. At fixed C=4 no overflow on outside-only source roots or descendants. All other first-overflow cubes lie within roots whose source intervals meet T, whose total fraction <=q/m+2B/m. Therefore

    Q_direct <= beta+delta_n+4^13*delta_w+q/m+2B/m ->0.

The constructed generated maps defeat both earlier local certificates, but are handled by the shared quadrant DAG even with irregular checkerboard traces and slow wide loss. It is a strict relaxation of the sufficient conditions on these maps; deliberately easy family, including unary-excluded outside sources, so no claim of lower bound or separation from older complete solvers.

## 7. Executed host audit

Standalone JS function executed in the tool runtime, committed with Node entry point; revised and rerun to add first-child overflow and complete finite greedy rounds. Twenty passes at m=2,3, five raw modes, prescribed maps and direct center=a or prescribed center=0 (not necessarily a learned center), B=2,C=1. Compare shared DAG node count to direct rebuilding, exact projected membership/positivity, disjoint first-overflow volume and complete original AND (E OR overflow membership) model sets. All main cases pass without overflow. Counts including separate controls:

    22,358 root builds (including direct reference rebuilds)
    283,265 child recodings
    856,460 new node internings, 1,169,770 existing-node hits
    2,902,777 implicit-zero results, 492,831 reachable node relabels
    62,656 exact projected membership checks, 21,706 positivity checks
    41,600 projected volume checks
    2,626,560 full padded tuple checks
    9,656 recovered original model occurrences, exact set agreement.

Exhaust every one of 65,536 binary 4-by-4 matrices and its four aligned child quadrants: 262,144 comparisons (each tests four child bits and reachable node recoding). Independent synthetic local guard with 256 distinct nonzero 4-by-4 patterns at 256 map keys has 272 DAG nodes, exceeding C*t^4=256; its children have at most 7 nodes. It can be realized in a larger domain by distinct replacement labels outside the source interval, but is not a complete normalized selector in this regression. Fallback model count with private inequality constraint is 196,608 vs 49,200 exact guard model occurrences. This is direct local enumeration, not integrated overflowing-root traversal in the main fixtures. Embed the 4-cube into an 8-cube with the other keys absent and free bits zero outside its quadrant: parent 528 nodes <=4096, first child 272>256. This independently exercises first-child overflow, not full 8^9 search.

Checkerboard slab controls at B=16,32,64 with finite parameters verify distinct root patterns, canonical run weights over B identical source copies, shared DAG counts and aligned local node count upper bound. Output [B,r,N,S,q,root DAG nodes,aggregate run weight,max local W_DAG/t^4,aligned squares]:

    [16,4,8,2,16,24,18688,1,341]
    [32,5,16,2,32,60,175104,1,1365]
    [64,6,16,4,64,93,3248128,1,5461].

These finite parameters are not the asymptotic q,N,S choices. Arithmetic controls at d=64,128,256,512 verify S^3>=m and the log-ratio test q*r/(2N*m^(1/32)*B)>1, not enumeration of huge instances. Full finite greedy controls compute all directed pair weights, check exact outside-target D0, then all positive greedy rounds for every possible target and verify actual best round has only T facilities, all outside sources retain first target. Output [m,q,D0,outside pair checks,greedy rounds,max best capacity]:

    [32,8,48,192,256,1]
    [64,16,128,768,1024,1].

All revised assertions passed. The host uses indexed arrays/maps, recursive objects and direct dense bit generation; it does not implement production one-source bounded-cap root construction or sequential dictionary merges, cap-short-circuit memory, adaptive all-choice scoring, physical carry shifts, serialized tape frames, normalized encoder/verifier, compiled U transitions or exact universal stage. Main regression uses prescribed maps, not production maps. Synthetic overflow controls test counts separately, not an integrated physical fallback. No measured physical transition counts, independent review, Lean formalization or exact-head CI confirmation.

## 8. Disposition

Shared aligned quadrants permit exact compression even when both row diversity and canonical run counts are high. The certificate is computable at original-scale span with a modest additional root-generation cost (803/96), still below the direct preparation exponent 42/5. The density/overflow bound remains rate-free. Arbitrary sparse rows can still have many distinct submatrices, and no general implication from small average loss to tight DAG overflow is established. Next investigate whether sparse exceptions imply tight projected overflow after combining shared DAGs with local algebraic/column factorizations, or exhibit an explicit obstruction to that implication. General arbitrary-slow full-average recovery, unconditional exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census 1603 unchanged, not freshly recounted. Promotion NONE.
