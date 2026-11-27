# F038-REX-024D5Z — GAC completeness barriers and complete fixed-nine rank enumeration

Parent 1e39b3b2726c21c20b14ad25841a9959986e7a83. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5Y closure

Exact-head [Proctor 46007490129](https://github.com/tltmgnt/MathOS/actions/runs/46007490129): all fifteen jobs passed, including both native descriptors, twelve physical regression/quotient/cutoff jobs, and audit/governance.

## Explicit infinite barrier family

For every m>=2, nine rank variables z_0,...,z_8 range over {0,...,m-1}. Impose equality z_0=z_j for each j=1,...,8 using negative binary clauses forbidding every unequal pair. Impose a separate ternary mask on groups 0,1,2 forbidding the diagonal tuples (a,a,a) for a=0,...,m-2. The UNSAT variant also forbids (m-1,m-1,m-1). These are legal normalized optional clauses; the inherited one-hot/cumulative/pin clauses are unchanged.

Every value has support in each equality factor (use equal ranks) and in the ternary factor (choose another coordinate unequal, possible since m>=2). Thus full GAC starting from full domains deletes nothing and reaches a fixed point after one pass in BOTH variants. Equality implies every satisfying assignment must be diagonal across all nine variables. The SAT variant has exactly one rank solution (m-1)^9; the UNSAT variant has none. The original witness for the former is obtained by the normalized witness map and validated. When m=2, the unique solution requires nine flips from the first-rank tuple; when m>=3, it requires a rank not in the first two. Therefore neither full GAC nor any Hamming-radius extension restricted to the first two ranks is complete. This is a specific refutation of a proposed search restriction, not a complexity lower bound for general SAT, and not a claim that the two formulas are indistinguishable when their actual constraints are examined.

Finite independent checks: m=2,3,4,5, SAT/UNSAT pairs (8 selectors), 532 local support checks, 564678 exhaustive rank tuples for m=2,3,4, plus independent prefix-pruning exact reference on all eight. D5S and experimental short-probe hybrid both refuse every case in bounded/full modes at logical IR level (16 paired comparisons, eight SAT false-negative comparisons and eight UNSAT refusal comparisons). These are not separate actual physical-transition replays of every family member. The all-m proof follows from the explicit equality/diagonal construction.

## Complete candidate controller (separate D5S branch of architecture)

Retain the D5S FIFO physical selector producer and canonical run stream, 20-tape GAC worker and original witness projection. Replace the first/second-rank radius-two candidate controller with a full mixed-radix odometer. Initialize each nonempty surviving domain by marking its first allowed bit x. Maintain exactly one x per domain; 1 denotes other allowed ranks, 0 disallowed. On failed candidate, scan from the last group to find its x, restore it to 1, advance to the next allowed rank and mark x; if none, reset that domain to its first allowed rank and carry to the preceding group. Overflow of the first group terminates with refusal. Each attempt starts Q and D at their proper origins and validates all active scopes by the inherited exact candidate worker. Passing candidate emits original witness.

Proof invariant on genuine canonical streams: each GAC deletion is sound (a global satisfying assignment provides a supporting tuple for every one of its values in each factor), so bounded or full GAC retains all satisfying assignments; empty domain certifies unsatisfiability. The candidate odometer enumerates the surviving Cartesian product exactly in lexicographic order: initialization gives its minimum, increment gives its successor or exhaustion, membership is maintained because 0 never changes. Candidate validation checks every active relation, with universal scopes skipped and early suffix shortcut only after the selected tuple has passed. Unary masks already constrain the domains. Thus the worker accepts exactly when a surviving assignment satisfies every relation, and returns the lexicographically first such assignment. Exhaustion implies no satisfying assignment under the genuine normalized-family/canonical-stream precondition. This is a source-level completeness argument for the fixed-nine normalized family; original producer, compiled lowering, all-input time accounting and admissibility obligations remain conditional or finite-audited. It is not a solution to arbitrary-width/global SAT or an all-input mechanically verified theorem.

A separate exact host reference uses prefix pruning only on factors whose entire scope has been assigned. It counts solutions and returns the lexicographically first original witness; no host witness, pruning decisions, or domain hints are used by the actual physical odometer.

## Executed audit

325 distinct selectors, 650 bounded/full executions, including all 256 ternary masks, 60 seeded random formulas (m=2,3), and nine named cases. Exact host reference agrees in every case: 578 valid original witnesses, 72 UNSAT refusals, eight SAT gains over radius-two worker (four named fixtures in both modes), no lost witnesses or status discrepancies. 578 exact successful worker-clock comparisons and 20034 BigInt resource arithmetic checks passed.

| fixture (alternating pins) | rank solutions | old result | complete result | bounded worker clock |
|---|---:|---|---|---:|
| empty m2 |512|halt|halt|183212644|
| radius-three-last |216|refusal|halt|291377490|
| known-radius-three |216|refusal|halt|1404792242|
| chain |16|halt|halt|300018380|
| barrier-sat m2 |1|refusal|halt|3957692186|
| barrier-unsat m2 |0|refusal|refusal|not measured|
| third-rank-barrier m3 |729|refusal|halt|840413034|

Third-rank-barrier restricts only last three groups by equality/diagonal exclusion, leaving first six free; lex solution has final three ranks 2. This enables a shorter test of third-rank search than full m3 all-nine barrier. The all-nine m2 SAT barrier requires exhaustive 512-candidate traversal before the final tuple succeeds. These worker costs are source-level exact accounting, not observed end-to-end original raw-selector halts.

## Exact original-format physical evidence

Radius-three-last m2 uses clauses [-7,-13],[-9,-15],[-11,-17] and pins [0,0]. GAC stays nonempty and full, any satisfying assignment flips at least three rank coordinates, old radius-two controller refuses. Both new modes start from original raw selector and pass original/quotient replay and cutoff:

| mode | t | head | span | worker clock |
|---|---:|---:|---:|---:|
| bounded |324589826|45728|46523|291377178|
| full |324589826|45728|46523|291377178|

BridgeAt=32043831, workerAt=32744098, outputAt=324121276, projection=468550, N=1871, 26355 IR primitives. Witness 1010101010100101011111111110000, ranks (0,0,0,0,0,0,1,1,1); exact host witness match and original raw clause validation. Cutoff 324589825 TIMEOUT without witness in both modes. New workflow registers twelve physical jobs (including full all-nine SAT/UNSAT barrier and third-rank barrier), two independent original-format native radius-three-last descriptors, audit and governance. Current-head CI unconfirmed.

## Descriptor and resource limits

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |6932|2520782|1878491|142765320|7562346|
| full |6931|2518502|1876768|142634372|7555506|

Four-bit segmented lowering, 20 tapes, producer 287874, bridge 279, projector 74, blank halt 1. Both below 2^21. The complete controller is smaller than D5S radius-two and D5Y hybrid, but this is a different algorithm/storage architecture, not an all-case speedup.

At most m^9 complete candidates. On genuine input with inherited dense stream bound S, each complete attempt scans at most the fixed 120 scope records and their masks, rank copies/rewinds and odometer operations; conservative source-level cost <=65536 S per attempt (inherited D5S macro slack, not a machine-checked bound). Full GAC at most O(m) rounds; bounded fixed number. Allow N<=S+35m+1479<=2S and T<=65536 S(m^9+(full?m:1)), W<=(20N+12)T+6, total<=2^20 m^9 L^2 using inherited producer/bridge/projector allowances. Since L>=4096m^3, m^9<=L^3, the conditional fixed-nine physical bound is O(L^5), not cubic. This is polynomial because nine is fixed, not because the unrestricted input's variable count can be arbitrarily large at fixed exponent. Complete host tuple enumeration itself can be O(m^9) tests using constant-count relation lookups (assuming RAM membership cost), but does not charge physical scanning or satisfy the original cubic admission rule. No cubic resource claim for complete search, no practical admission, no unrestricted result.

## Separate short-probe hybrid experiment

D5Y field scan originally wrote scratch then tested length. New short_probe_ir scans original tokens without scratch and on token 17 rewinds and collects. Short fields never allocate scratch; long ones pay extra probing. Six named fixtures in both modes matched D5Y status, witness, and framed stream; sample bounded all-active primitives 140014 -> 126682, worker clock 1342551652 -> 1333717208 (pins all zero); chain 325309624 -> 324091088, sparse m5 466695582 -> 467363510 regression. Quotient grew to 2111002/2109279 (166769162/166633045 descriptor bits), crossing 2^21 again. Combined original/quotient/cutoff physical test timed out at tool level, so no new actual physical replay claim. Retain as experimental, do not adopt as preferred hybrid. No direct online deposition, padding elimination or interval skipping implemented. D5Y stays preferred hybrid, D5S remains fast incomplete baseline, complete odometer retained separately for completeness.

Next D6A: replace full candidate enumeration with sound partial-assignment pruning or structural decomposition, prove exact search pruning and resource accounting, measure physical cost on explicit barriers, and confirm D5Z native/physical CI. Keep unrestricted/global routes blocked; no main or PR #248 changes.
