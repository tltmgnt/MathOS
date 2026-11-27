# F038-REX-024D6A — Sound conflict-prefix pruning and a subcubic conditional barrier-family envelope

Parent 297960c1a756f609b6e20bb07a4e6256c19f05ee. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5Z closure

Exact-head [Proctor 46010126601](https://github.com/tltmgnt/MathOS/actions/runs/46010126601): all fifteen jobs passed, including both native descriptors, twelve original-selector physical replay/quotient/cutoff jobs and independent complete rank audit/governance. The prior all-nine SAT and UNSAT barriers now have exact original physical clocks 3993378260 and 3967610500 respectively, identical in both propagation modes.

## Physical conflict-directed lexicographic skipping

Keep the complete D5Z rank odometer, original D5S FIFO producer, canonical run-coded stream, 20 logical tapes and GAC schedule. When an exact selected tuple fails an active binary or ternary factor, the current D scope record is already consumed. Inspect R2 to determine arity (one rank cell for pair, m>=2 for triple); rewind D five cells for pair or four for triple to its last four-bit group identifier. Read this identifier to choose a conflict target h=max(scope). Reset every domain after h to its first surviving value; increment domain h with the inherited carry logic toward group 0. If carry exhausts the first domain, refuse. The prefix before the incremented group remains unchanged. No host-supplied conflict, rank or shortcut is used during actual physical execution. The failure path has extra finite control to reset suffix domains and select the target; successful first candidates do not traverse it.

Soundness: for current assignment z, all candidates sharing prefix z_0,...,z_h fail the same factor, because its scope is contained in that prefix. Lexicographically, these candidates form a contiguous block. Setting the suffix to minimum and incrementing the prefix implements exactly the next block's first assignment (or exhaustion). Every skipped assignment lies in the known-invalid block. GAC deletions are sound under the inherited genuine-stream precondition; thus skipping preserves all solutions, lexicographic first witness and UNSAT exhaustiveness. This is source-level proof, not a mechanized universal verification of the compiled machine. No arbitrary malformed-stream guarantee.

## Independent execution and trace audit

335 fixture entries (including repeated m2 barrier fixtures), 670 bounded/full logical executions, 588 valid original witnesses, 82 exact UNSAT refusals. Independently compute complete exact answer and lex witness from normalized relations. Additionally construct a host conflict oracle from the independent GAC domain oracle, order factors by arity and lexicographic scope, and compare every actual candidate rank vector and failed D record at logical IR trace checkpoints. Verified 2464 candidate visits and 1876 conflict records. Sum of eliminated candidate positions across all executions 49271806, including both modes and repeated fixtures. These are counts of skipped rank combinations, not physical transitions. Host trace hooks are diagnostic only; compiled machine does not use them.

Of the 580 successful paired clock comparisons against D5Z, 214 improve, 360 tie, 6 regress. The eight additional successful m3..6 star runs are not paired against the full D5Z odometer (cost and IR limit). All 670 agree with independent exact search. 20034 domain/mode arithmetic evaluations check each of the general and star-specific resource envelopes, including large BigInt boundary sizes.

| fixture (alternating pins) | D6A candidates | skipped | D5Z worker clock | D6A worker clock |
|---|---:|---:|---:|---:|
| radius-three-last |4|4|291377490|242350926|
| known-radius-three |4|165|1404792242|230553470|
| barrier-sat m2 |12|500|3957692186|351921756|
| third-rank-barrier m3 |15|12|840413034|625186014|

These are exact logical-worker clock accounting figures, not the observed end-to-end raw-selector clocks.

## Equality-star structural bound

For the D5Z equality-star SAT and UNSAT families, full GAC leaves all m ranks and every candidate either fails an equality (0,j), fails the ternary diagonal factor, or is the unique SAT witness. The scope order checks equality factors in increasing j before the ternary factor. At first failed equality (0,j), the root a and all leaves before j equal a, and leaf j differs. There are at most m(m-1) such prefixes for each j. Strictly increasing conflict-prefix search never visits the same failed prefix twice. A fully equal candidate occurs at most once for each a; there are at most m diagonal trials, including a possible witness. Thus for either variant and either propagation schedule,
 
    candidates <= 8m(m-1)+m = O(m^2).

This bound applies to this structural family, not every normalized selector. The tested exact trial counts are:

| m | exhaustive Cartesian size | D6A SAT trials | D6A UNSAT trials |
|---:|---:|---:|---:|
|2|512|12|12|
|3|19683|33|33|
|4|262144|64|64|
|5|1953125|105|105|
|6|10077696|156|156|

The equality-star proof does not rely on extrapolating the finite measurements. A separate exact expression for the observed trial counts is not claimed.

For general genuine normalized streams, inherit dense stream ceiling S and physical region allowance N<=S+35m+1479<=2S. Charge at most 131072 S logical primitives per complete candidate including validation, conflict lookup, suffix resets, carry and scan restarts, plus inherited propagation allowances. This conservative macro premise remains conditional. Then T<=131072 S(m^9+(full?m:1)), W<=(20N+12)T+6, and total<=2^21 m^9 L^2 under inherited producer 4P+32L, bridge 128S^2 and projector 256S^2 allowances. General conditional O(L^5) remains; no worst-case improvement theorem for arbitrary fixed-nine normalized selectors.

For equality-star only, substitute proven candidate count C=8m(m-1)+m. Since C+m<=8m^2, same conditional macro premises and L>=4096m^3 give total<=2^20 m^2 L^2<=4096 L^(8/3). Derivation: S<=L/16, N<=2S and S>=1936 imply W<=(41S)*2^20 S m^2+6; producer 4P+32L<=140000L^2+32L; bridge/projector <=384 S^2. Their sum fits stated bound for m>=2. This is a subcubic asymptotic envelope for the explicit barrier family, NOT a general cubic admission result. Descriptor size, small input admissions, macro proof mechanization and unrestricted reduction all remain outstanding.

## Original-format actual physical execution

Pins [0,0], both bounded and full propagation modes, independently confirmed exact original and quotient halt, head/span and one-short cutoff.

| barrier | D5Z physical t (CI) | D6A physical t (observed) | head | span |
|---|---:|---:|---:|---:|
| SAT |3993378260|387607830|45986|46801|
| UNSAT |3967610500|361882686|38293|46646|

SAT witness 0101010101010101011111111110000, worker 351921438, bridgeAt=34303371, workerAt=35204738, outputAt=387126176, N=1923, 35594 logical primitives. Both exact worker clocks matched source accounting. UNSAT blank halt, bridgeAt=34381281, workerAt=35282648, blankAt=361882685; no witness. Cutoffs 387607829 and 361882685 returned TIMEOUT without witness. Parent clocks obtained from completed exact-head CI logs. New workflow registers twelve original physical jobs and two independent native descriptor jobs (each both SAT/UNSAT exact barriers), plus audit/governance. New exact-head completion not yet confirmed.

## Descriptor tradeoff

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |7500|2654686|1953203|148443432|7964058|
| full |7499|2652406|1951480|148312484|7957218|

Producer 287874, bridge 279, projector 74, blank halt 1; workers 2366458/2364178. Four-bit segmented lowering unchanged. Both quotients below 2^21. Relative to D5Z, increased states and descriptor cost in exchange for skipping; six observed worker regressions. No online forbidden-only deposition or stream compaction implemented in this mission.

Next D6B: investigate ordered structural decomposition and dynamic conflict scope selection; seek a complete search bound for a wider structural class, measure against actual physical clocks and verify D6A native/physical CI. Preserve exact source-level completeness and explicitly distinguish general worst-case and restricted-family envelopes. Main and PR #248 untouched.
