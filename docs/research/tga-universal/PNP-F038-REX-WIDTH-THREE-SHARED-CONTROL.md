# F038-REX-024D6M — Shared finite control and canonical skip paths

Parent D6L 2b97bb8c67306f390f2c2d7807430055bb56a726. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6L exact-head Proctor 46060708304](https://github.com/tltmgnt/MathOS/actions/runs/46060708304): 29/29 jobs passed at inspection. All jobs completed successfully. D6K remains verified 29/29.

## Runtime control simplification
Retain D6L's demand-driven append-only cache, direct-probe budget, exact checkpoint resumption, original rank words, canonical scope order and witness output. No new logical tapes. The shared rewind routine moves left once, then scans binary data left until either the permanent L sentinel (direct local block) or x marker (cached block), and moves right once. Every invocation starts after a consumed conflict row/directory or after local construction. For a direct block the leftmost boundary is L; for a cached block the nearest boundary is its own x. This includes empty newly appended blocks. Thus direct and conditioned retries can use the same routine without reading A17, and direct local construction no longer rewinds twice. The candidate trace is emitted only after both heads are aligned. Initial cached first-block and subsequent paired-boundary entry retain the D6L checks.

Canonical 00/01 literals always occupy two cells. A skip routine that discards an entire literal need not read its second bit. Retain first-bit read and second-bit read for 10 delimiter versus 11 run. Header skipping uses the same literal-length fact; fields that output data still read its value. All real validation and propagation reads are unchanged. This optimization is justified only on genuine canonical input and correctly materialized fields. No claim of equivalent malformed-stream rejection.

## Trace-preserving finite-control quotient
Let an instruction graph contain read, write, move, halt, reject and jump nodes. Define an observation tag for each named trace/control event, including componentDone. Contract chains of untagged jumps, detecting cycles. Retain the closure of entry and all event roots under ordered successor edges. Initial partition uses opcode, tape, literal write value or move direction, and observation tag. Refine by the vector of successor classes, in exact alphabet order for read nodes. Refinement is monotone: equal signatures in a finer partition imply equality in the preceding partition. The finite process stabilizes; equal class counts on consecutive monotone rounds imply no further split. Construct one representative per class and remap all successors and event roots. Verify every retained original node has the same opcode, tape, action and ordered successor classes as its representative. Unique event tags keep event identities distinct.

For equal tape contents and heads and corresponding control classes, a primitive reads the same symbol or performs the same write/move, then enters corresponding successor classes. Halts and rejects are distinct classes. Tagged jumps preserve event order; untagged jumps change no tape data, head or primitive count and are contracted only along finite chains. Induction therefore proves equality of source primitive traces up to contracted unobservable jumps, including all terminal tapes and heads and event snapshots. This proof is for this source IR model; it does not certify the physical lowering or characterize malformed raw-selector input. The quotient does not claim to minimize the entire physical machine. It preserves source primitive counts exactly; the runtime savings come from the separate skip/rewind simplification.

## Conditional resource theorem
Let S be canonical stream length, q reached blocks, P surviving prefix domain product, and D_j surviving residual domain products. D6L's append-only prefix invariant, one-build-per-demand theorem, O(S+1) cache storage and O(q(S+m+1)) construction bound remain unchanged. Source compaction is performed at controller-generation time, not per raw input. Each skipped canonical literal eliminates one read primitive; shared rewinds avoid redundant mode traversal. Candidate and prefix visit ceiling V<=4+P(1+sum D_j) is unchanged. Under inherited physical macro assumptions t=O(L^2(p+1+V)) and admitted exponent 2+(h+b)/3. No new end-to-end exponent, general cubic guarantee or unrestricted SAT reduction. Fixed-nine explicit encoding remains a restricted problem already polynomial in explicit input length.

## Independent verification
679 fixtures in bounded/full modes (1358 executions):1116 SAT,242 UNSAT. All decoded relation oracle traces, original exact witness/status, D6L/D6I parity and demand-frontier checks matched. 1358 compact-vs-uncompressed exact terminal result/primitive-count comparisons,15550 full tape/head event snapshot comparisons. Compaction local transition certificate checks12611 bounded and12605 full retained nodes, each checking all successors. 119 refinement rounds in each mode.
Inherited counts unchanged:256 probes,658 probe candidates,178 probe SAT,78 suspensions,6 exact direct resumptions;72 conditioned,288 prefix assignments,7022 graph/component checks,4520 candidates,2668 conflicts,22 prefix-only conflicts,84 first-block membership reuse events. 320 cache appends,40 deferred blocks,8 UNSAT runs with unbuilt suffix,3060 immutable-cache checks and1288 local retry rewinds. No observed correctness discrepancies. Finite testing is not a universal empirical guarantee.

## Performance
| logical primitives | D6L | D6M |
|---|---:|---:|
| aggregate |50753385|50328209|
| one-prefix m2 SAT |111037|109672|
| one-prefix m2 UNSAT |58581|57852|
| hard m2 SAT |147520|146186|
| hard m3 SAT |276710|272738|
| hard m4 SAT |587107|577125|

1358 improved,0 regressed,0 tied relative to D6L on this corpus. Aggregate reduction425176 primitives (~0.84%). These are logical primitive counts, not aggregate wall-clock or physical runtime. Hard m2/m3/m4 exact source worker transitions2439019306/4430613994/8739924316 ->2406718370/4335846976/8503585206. Larger-family physical replay not yet observed for D6M. Candidate counts and cache materializations identical.

## Separate compression measurements
| mode | generated IR | retained after jump contraction | compact IR |
|---|---:|---:|---:|
| bounded |13756|12611|9410|
| full |13755|12605|9405|

| mode | IR | original physical states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded compact |9410|3798371|3602466|284594818|11395113|
| full compact |9405|3796648|3600743|284458701|11389944|
| bounded optimized uncompressed |13756|5223960|3602466|284594818|15671880|

The separate bounded uncompressed lowering establishes the effect of source graph sharing: 1425589 fewer original physical states and4276767 fewer physical transition checks, with identical final quotient state count and descriptor bit length. This is not a claim of bit-identical numbering or identical serialized descriptor. The final physical quotient already removes equivalent finite control, so the prelowering pass primarily reduces intermediate table construction/verification resources. Compared with D6L, final bounded descriptor reduction1762332 bits; original physical states5281577 ->3798371. 20 tapes, four-bit segmented alphabet,22-bit quotient IDs; 21-bit target remains unmet. No measured compiler wall-clock or peak RAM claim.

## Physical replay evidence
| fixture/mode | halt transitions | head | span | result |
|---|---:|---:|---:|---|
| one-prefix SAT bounded |1711594396|47122|47937|SAT|
| one-prefix UNSAT full |880821458|38293|47726|UNSAT|

Original and quotient matched exact transitions, head, span and output. SAT witness0101010101010101011111111110000; observed worker1675836788 matches exact source count. UNSAT blank halt. Quotient one-short cutoffs1711594395 and880821457 return TIMEOUT/no witness. Dedicated Proctor registers29 jobs (one audit,26 physical,2 native), exact-head completion not yet verified. Main and PR #248 not modified.

## Next D6N
Investigate nondestructive lazy selected-row interval access within immutable cached masks, using exact rank/cursor and compressed-run boundary invariants. D6M deliberately prioritized finite-control sharing; physical lazy interval access remains unimplemented. Also pursue the actual physical descriptor bottleneck rather than equating IR compression with final descriptor compression. Preserve canonical lexicographic search and original-format replay. No promotion.
