# F038-REX-024D5X — Run-aware hybrid persistent constraint execution

Parent 24be39f9d0cb2d599cd94072f1c6e6a822f99a84. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5W closure

Exact-head [Proctor 46002036401](https://github.com/tltmgnt/MathOS/actions/runs/46002036401): all fifteen jobs passed, including both independent native descriptors, twelve original-selector physical/quotient/cutoff jobs, and audit/governance. The previously timed-out interactive full all-active case completed in CI: t=4395453052, head=59404, span=60433, valid witness 1010101010101010101111111110000. The quotient and one-short cutoff passed under the same job.

## Physical hybrid design

Retain the original D5S FIFO producer and its canonical token stream. D5W always attempted gap encoding for active scopes, selecting against literal length; this could expand previously run-compressed fields and add expensive countdown work. D5X selects against the actual run-token count and uses a conservative fixed heuristic. On an active field collect compact tokens in scratch: 0/1 literal bits, x for four allowed tuples. For at most 16 tokens, directly select run mode without invoking the gamma encoder or expanding the dense mask. For longer fields, expand into one temporary literal mask, invoke the physical headerless encoder, and compare its gamma payload length g against the compact run token count k. Select gamma only if the encoder chooses gamma and 2g<=k; otherwise select run. This is a storage-based heuristic, not an exact physical-time optimizer. A longer dense field still incurs conversion overhead before falling back. The policy automatically selects modes using physical tape scans, not host hints. Literal entries are included in run mode, which can represent any mask, and long fields with no useful runs fall back to literal tokens within that mode.

The first eleven fields remain unchanged; universal higher-arity masks are delimiter 10 alone. Active fields use mode token 00 for run/literal tokens (00/01/11), or 01 for gamma payload bits (00/01); 10 terminates either. A run field has k+1 payload/mode tokens plus delimiter, while a gamma field has g+1 plus delimiter. Thus for genuine selectors, S_hybrid<=S_D5S+240 bits (at most two extra bits per active higher-arity field), including all framing; gamma selection may reduce the size. This is not an absolute storage improvement over D5S. The two full stream high-water extents still coexist; the compact token buffer adds scratch, and conversion is not online forbidden-only deposition.

The 22-tape worker keeps the mode head at its single fixed cell. At each scope entry clear the countdown and write mode; direct run token expansion uses finite-control virtual rows (no physical dense mask reconstruction), gamma mode uses the D5W binary countdown. The same Cartesian odometer bounds row traversal and checks exact field exhaustion. Passing candidates scan the complete field; forbidden selected rows retry, and the next active dispatch clears countdown. D5S retains an earlier candidate suffix shortcut, which contributes to its speed advantage. No algebraic allowed-interval skipping implemented. The source-level correctness invariant follows D5V/D5W: every virtual run row is allowed, every gap yields its specified forbidden position, all other rows allowed; projection and candidate order unchanged. Finite evidence below, not an all-input proof of global satisfiability.

## Independent regression results

265 selector fixtures in both modes, 530 logical executions including all 256 ternary truth masks, reverse chain, sparse m5 gamma selection and long dense m3 fallback; 522 valid original witnesses and eight matching refusals. All 530 framed streams equal independent oracle and all compared domain words/statuses match D5S. 391 run-mode active fields and one gamma field across distinct fixtures. 20034 exact resource arithmetic evaluations passed. 518 of 522 successful worker comparisons improve versus D5W; four regress (including empty cases). All 522 regress versus D5S. The gamma selection threshold has not been exhaustively optimized or tested across arbitrary domain sizes.

| fixture (alternating pins) | D5S worker | D5W worker | D5X worker | stream D5S/D5X | region D5S/D5W/D5X |
|---|---:|---:|---:|---:|---:|
| empty |185257932|228018366|228022120|304/304|1841/2151/2151|
| chain |302075206|412272836|358998640|334/340|1883/2243/2232|
| third-rank m3 |295216832|423663466|351772630|344/346|1928/2323/2286|
| all-active m2 |1099924056|4325801854|2009888980|1432/1672|2981/5014/4662|
| sparse m5 |251468374|557178262|540223928|432/396|2086/2627/2654|

The all-active worker recovers 53.54% of D5W's clock, but still costs about 1.83 times D5S. The sparse m5 field saves 36 stream bits compared with D5S, but physical cost still increases substantially. The D5S production-performance baseline remains preferred.

## Actual compiled physical evidence

Both original raw-selector chain executions (pins [0,0]) verified original witness, exact worker clock, quotient replay and one-step-short cutoff:

| mode | physical t | head | span | worker t |
|---|---:|---:|---:|---:|
| bounded |392800936|47178|47973|358998334|
| full |392612642|47178|47973|358810040|

Both output 0101010101101010101111111110000; bridgeAt=32503873, workerAt=33243080, projection=559522. Cutoffs 392800935 and 392612641 TIMEOUT with no witness. Both original/quotient transitions match. These chain fixtures use run mode. For gamma mode, an independent compiled-worker replay uses the canonical segmented stream for sparse m5 (pins [0,1,0,1,0]), not the original raw-selector bridge. It executes 540223928 physical transitions, N=2654, 34689 primitives, exact terminal tape/head and independently valid witness, with a 396-bit hybrid stream. It establishes physical gamma selection and direct gamma traversal, not a full original-selector m5 replay. D5X all-active worker cost is exact source-level accounting, not a new observed full raw-selector halt. CI registers twelve original physical jobs, two native chain jobs, audit/governance including gamma worker replay. Current-head success unconfirmed.

## Descriptor and conditional resources

Shared scan and scratch cleanup eliminated duplicated short-field states; fixed mode head and redundant virtual candidate reads removed. Still crosses the 2^21 quotient state boundary, unlike D5W, requiring 22-bit state numbers. No descriptor compression claim.

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |8314|2925879|2110290|166712914|8777637|
| full |8313|2923599|2108567|166576797|8770797|

Producer 287874, bridge 303, projector 74, blank halt 1, worker 2637627/2635347. Four-bit physical symbol lowering unchanged; the 22-bit state numbers are descriptor indices, not physical symbol width. Conditional D5W envelopes retained: N<=3S+35m+1600+5m^3+4b<=5S, where S is inherited dense stream ceiling and b=bit_length(m^3+1). Both streams plus mode/framing slack fit 3S; compact token buffer <=m^3, literal scratch <=m^3, selected code <=m^3+1, candidate gamma scratch <=2m^3, counters and fixed slack. Each conversion and rank scan has at most O(b) work per row/token, short-field bypass and comparison add only linear token scans. Conservative T<=65536S(b+1) bounded or 65536mS(b+1) full under inherited macro premises, W<=(20N+12)T+6. Keep producer 4P+32L, bridge 128S^2 and projector 1024S^2. Arithmetic verifies total<=2^20(b+1)L^2 bounded and <=2^20m(b+1)L^2 full. These are conditional source-level estimates; no mechanically proved global resource theorem or complete search. No practical cubic admission or promotion.

Next D5Y: reduce hybrid mode overhead and descriptor below 2^21 if feasible; avoid whole-stream duplication by direct producer framing or online deposition; evaluate run/gap selection against actual time and interval skipping; verify D5X CI. Main and PR #248 untouched.
