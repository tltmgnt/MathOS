# F038-REX-024D5W — Integrated multi-scope persistent gap propagation

Parent 0e944efc70fd20f7987a5833a7cb177ee5379211. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Prior verification

D5V exact-head [Proctor 45999834763](https://github.com/tltmgnt/MathOS/actions/runs/45999834763) completed successfully. Some unrelated exact-head workflows were still running at inspection.

## Physical integration

Retain the original D5S FIFO selector producer, including normalization and packed deposition. Its canonical run stream enters tape 21 through the actual bridge. Convert each active higher-arity field using D5V's headerless physical encoder and temporary per-field scratch on otherwise unused domain tapes. Build the persistent stream on tape 19, retaining the first eleven fields verbatim and universal higher-arity fields as delimiter 10. For active fields, encode mode as 00 (literal) or 01 (gamma gaps), followed by payload bits represented by 00/01, terminated by 10. The paired-bit framing distinguishes payload from delimiters. The rank domains supply the exact row count; no trusted encoded length or external host hints. Clear source stream and scratch before direct GAC. Tape 21 is reused as LSB-first gap counter; tape 20 holds mode. Clearing does not reclaim allocated physical high-water extent. During conversion both streams coexist and a temporary dense mask and candidate payload are required. True online forbidden-only deposition and retained-prefix elimination remain open.

The direct persistent worker retains the D5S bounded/full propagation schedule and radius-two candidate repair. Each active scope resets the counter, consumes mode, and iterates the rank/support odometer. Gamma gaps count down to forbidden rows; after the last gap, the remaining rows are allowed. At Cartesian exhaustion require zero pending gap and exact delimiter. Literal fallback reads one payload bit per row. On candidate failure retry with counter cleared at next active scope; on passing candidate scan all rows rather than D5S early suffix skip, validating field exhaustion. No full mask reconstruction during propagation or candidate checks. The D5V local projection invariant applies to each scope; sequential domain updates and candidate order remain unchanged. This is a source-level argument for genuine streams, not a complete arbitrary-malformed-stream proof or complete SAT search.

## Executed evidence

263 original selector fixtures at logical integration level (526 mode executions), including 256 ternary masks, reverse-chain cap and contradiction/refusal fixtures. 520 valid witness outputs, six matching refusals, all 526 persistent streams match independent host framing oracle, all compared domain words and statuses match D5S. All 520 accepted worker clock comparisons regress. 20034 exact arithmetic evaluations passed. The original raw-selector bounded and full chain physical machines both executed, matched independent exact worker accounting, quotient replay and one-short cutoff:

| mode | transitions | head | span | worker clock |
|---|---:|---:|---:|---:|
| bounded |446077940|47222|48017|412272566|
| full |445888260|47222|48017|412082886|

Both have valid witness 0101010101101010101111111110000, bridgeAt=32503873, workerAt=33243080, projection=562294. Cutoffs 446077939/445888259 TIMEOUT without witness. Full all-active original physical replay attempt timed out at the tool level; no observed halt or quotient/cutoff claimed. Exact source-level worker accounting gives 4325801584 transitions, 247332 primitives, N=5014 on pins [0,0], not a completed physical run. CI registers twelve physical replay/cutoff jobs, two native chain jobs and audit/governance. Current-head results unconfirmed.

## Performance tradeoff (alternating pins)

| fixture | D5S stream bits | D5W stream bits | D5S worker | D5W worker | N old/new |
|---|---:|---:|---:|---:|---:|
| empty |304|304|185257932|228018366|1841/2151|
| chain |334|340|302075206|412272836|1883/2243|
| third-rank m3 |344|348|295216832|423663466|1928/2323|
| all-active |1432|2008|1099924056|4325801854|2981/5014|

Gamma fallback selects against literal mask length, not against D5S run-token compression or time cost. Hence persistent stream may expand relative to D5S. Rank-row scans still enumerate all tuples. D5S remains preferred performance baseline; D5W is a separate integration proof-of-concept, not a speedup.

## Descriptor and conditional resources

22 tapes, four-bit lowering; 8007/8006 IR instructions; producer 287874, bridge 303, projector 74, blank halt 1; workers 2527132/2524852 states, original 2815384/2813104, quotient 2059551/2057828, descriptor 156525880/156394932 bits, transition checks 8446152/8439312. Both quotients below 2^21.

For genuine normalized input let S be inherited dense stream ceiling and b=bit_length(m^3+1). Persistent stream adds at most two mode bits per active field beyond dense tokens (120 fields), and source stream coexists until cleared. N<=3S+35m+1600+5m^3+4b<=5S conservatively includes both high-water extents, scratch, mode/countdown and segment boundaries. The per-row gamma countdown is O(b), plus O(b) parse on gap starts; charge conversion and every propagation/candidate row by an enlarged T<=65536S(b+1) bounded or 65536mS(b+1) full. These are source-level macro allowances conditional on inherited worker estimates; not mechanically proved. W<=(20N+12)T+6, producer allowance 4P+32L unchanged, bridge 128S^2, projector 1024S^2. Arithmetic checks give total <=2^20(b+1)L^2 bounded and <=2^20 m(b+1)L^2 full. Thus conditional O(L^2 log L) and O(L^(7/3) log L); no constant-only previous full exponent ceiling asserted and no practical cubic admission. No resolution or promotion.

Next D5X: add a run-token-aware fallback to persistent framing, avoid expensive gamma scans when a run field is cheaper, explore sparse support interval skipping or direct online deposition, verify D5W CI including all-active physical replay and maintain explicit proof obligations. Main and PR #248 untouched.
