# F038-REX-024D6L — Demand-driven residual block cache

Parent D6K 42f0c9b8be989a7c99c81f0ef29cf0bb2c092c67. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6K exact-head Proctor 46057941827](https://github.com/tltmgnt/MathOS/actions/runs/46057941827): 29/29 jobs passed at inspection. All jobs completed successfully. D6J remains verified 25/25.

## Physical mechanism and invariant
D6L replaces D6K eager cache construction with append-on-demand construction. No new logical tapes, no block ordinal, no A26 construction flag. A25 still terminates the direct-probe budget. On admission, clear both compact tapes and enter the first prefix assignment directly, rather than performing a separate preconstruction traversal. The residual graph and canonical source remain immutable.

For a fixed admitted prefix length, let B1,...,Bk be residual blocks ordered by least original coordinate. At every component-entry boundary the compact tapes contain precisely the first j blocks, for some 0<=j<=k. Each cached block begins with paired x markers; internal bytes are binary. The first residual block of each prefix tuple rewinds both tapes to their starts. Later blocks enter at the paired boundary left by successful validation. If both symbols are x, advance both heads into the existing block. If both are blank, the next required block is B_(j+1); append paired x markers at the existing head positions and scan Q/D once to append its original local mask and directory. Mixed markers reject as an invariant violation. No global search for cache ends. Once appended, rewind only to the nearest marker on each tape. This works even for empty local fields, where the immediately preceding cell is the block marker.

Each append preserves all previous cache bytes. Failed candidates rewind only their current block; advancing a prefix resets ranks and returns to the first block without erasing the cache. A block is constructed once, at its first demand. Component order cannot skip an earlier block, so no holes or host-provided indexes occur. The prefix-only pair belongs exclusively to the first block. Direct checkpoint resumption, lexicographic candidate order, sound propagation and original-format emission remain unchanged. The cache stores unsliced original masks; physical lazy access to selected row intervals is not implemented.

## Correctness
For genuine normalized canonical input, assume sound GAC and correct lowering. Induct on component entries. Initially both compact tapes are empty and the first demand appends precisely B1. If a cached block is entered, its marker and directory identify the exact original factors of that block. An unsuccessful candidate stays in the same block; a successful component ends at its next boundary. A new demand can only occur at the common blank frontier and appends the next block without altering any earlier bytes. On prefix restart the first boundary is restored. This inductively proves the append-only prefix invariant and exact relation semantics. Every visited candidate and prefix therefore agrees with the D6K/D6I logical search, so inherited completeness and canonical witness theorem apply. This is a source-level proof for the fixed normalized family, not a mechanical proof of all physical macros or unrestricted reduction.

## Conditional resource theorem
Let S denote original canonical stream length and S_j local block lengths including directory, P the product of surviving prefix domain sizes, D_j the residual domain products, and k<=8 the number of residual blocks. If q blocks are ever demanded, cache construction is O(q(S+m+1)) logical primitives, and no append performs a global cache-end traversal. Cache storage equals the sum of original local lengths for the reached prefix of blocks plus two markers per block, hence O(S+1); q<=k. No cache rebuild on prefix change. A retry costs O(S_j+m+1); first-block rewind may cost O(S+m+1) per prefix. With p propagation passes and C_aj visits, conditional logical cost O((p+1+P+q)(S+m+1)+sum C_aj(S_j+m+1)). Combined visit ceiling V<=4+P(1+sum D_j) unchanged. Under inherited physical macro assumptions t=O(L^2(p+1+V)) and admitted exponent 2+(h+b)/3. Fixed-nine explicit encoding is already polynomial; no universal cubic guarantee or unrestricted SAT reduction. Lazy construction removes work for unreached blocks but does not change worst-case asymptotic exponent.

## Independent audit
679 fixtures in two modes: 1358 executions,1116 SAT,242 UNSAT. 256 direct probes,658 probe candidates,178 probe SAT,78 suspensions,6 exact direct resumptions. 72 conditioned (16 one-prefix,56 two-prefix),52 SAT,20 UNSAT. 288 prefix assignments,7022 component/edge-list checks,4520 candidate/local checks,2668 conflicts,22 prefix-only conflicts,84 first-block membership reuses. All exact witness/status, decoded relation traces and D6K/D6I parity matched.

72 cache initializations,320 demand appends vs360 eager block builds,40 deferred blocks,8 UNSAT executions terminating with unbuilt suffix. Sum of cache mask and directory tape lengths across runs17188+8502 vs18180+8966 in D6K (not simultaneous peak storage). 320 append-frontier checks and exact appended-content comparisons,3060 cache-content checks (886 component entries and2174 candidate entries),1288 local retry rewinds. Auditor independently reconstructs each block from explicit decoded relations, checks paired append heads, validates the immutable prior cache prefix and exact appended bytes, checks every selected segment and retry cursor, and proves by finite trace comparison that built blocks equal the set of demanded blocks. No observed discrepancies.

## Performance
| logical primitives | D6K | D6L |
|---|---:|---:|
| aggregate |51876507|50753385|
| one-prefix m2 SAT |121404|111037|
| one-prefix m2 UNSAT |110591|58581|
| two-prefix m3 UNSAT |182629|137809|
| hard m2 SAT |158412|147520|
| hard m3 SAT |289754|276710|
| hard m4 SAT |603551|587107|

1136 improved,0 regressed,222 tied relative to D6K on this finite corpus. This is not universal dominance, and does not imply D6L beats D6I on every instance. In particular direct paths retain some extra dispatch overhead over D6I, and eager-vs-lazy cache initialization is not a cost-aware comparison against D6J slicing.

| hard SAT domain | D6K exact source worker | D6L exact source worker |
|---|---:|---:|
| m2 |2674871514|2439019306|
| m3 |4718418806|4430613994|
| m4 |9112116022|8739924316|

Source-accounted worker clocks, not end-to-end replays. Candidate counts unchanged. Aggregate reduction1123122 primitives. Direct physical one-prefix UNSAT halt1782816682 ->897061836; SAT1968010788 ->1742957614, verified on both exact controllers. The improvement in the UNSAT example arises from avoiding six unreached blocks as well as eliminating eager pretraversal.

## Physical evidence
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |13903|5281577|3624774|286357150|15844731|
| full |13902|5279297|3623051|286221033|15837891|

20 tapes, four-bit segmented alphabet,22-bit quotient state IDs. Bounded descriptor reduction7818630 bits relative to D6K; 21-bit target unmet.
| fixture/mode | halt transitions | head | span | result |
|---|---:|---:|---:|---|
| one-prefix SAT bounded |1742957614|47122|47937|SAT|
| one-prefix UNSAT full |897061836|38293|47726|UNSAT|

Original and quotient physical executions matched transitions, head, span and exact output. SAT witness0101010101010101011111111110000; source worker1707200006 matches observed phase. UNSAT blank halt. Quotient cutoffs1742957613 and897061835 returned TIMEOUT/no witness. Dedicated Proctor registers29 jobs (one audit,26 physical,2 native); exact-head completion not yet verified. D6L hard m4 physical replay not claimed. Main and PR #248 not modified.

## Next D6M
Investigate lazy selected-row interval access on the immutable cache, or shared finite-control paths to reduce ordinary-case overhead and descriptor size. Retain demand frontier and exact cursor invariant. Compare D6I, D6J, D6K and D6L on same corpus. No promotion.
