# F038-REX-024D6S — Directional marking and same-cell continuation fusion

Parent D6R b81d2dbb951b70123a8f89d01a35fb7da39fbb0f. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6R exact-head Proctor 46076907446](https://github.com/tltmgnt/MathOS/actions/runs/46076907446): 29/29 jobs completed successfully, including native 21-bit descriptor verification and the hard m4 physical jobs. D6Q 29/29 remains verified.

## Three implemented compiler refinements
Retain D6N logical IR, D6R bit-serial suffix FIFO, 20 tapes, four-bit paired codebook and original producer/bridge/projector. Optional fused, blind and local switches default on with serial mode, in that dependency order. Disabling all three restores D6R lowering; earlier nonserial and nonpaired modes remain available.
1. Directional mark continuations are keyed by resolved return destination and movement direction, rather than initiating instruction. A left move unmarks the old head at its final digit and moves to the previous block's final digit rather than its first. On a genuine left neighbor that digit is zero. Write one and continue left across the remaining three digits directly into aligned reverse return. Right neighbor data is recognized by prefix 01/10/11, its head bit set to one and return begun. D/E expansion still uses full delimiter recognition and the unchanged FIFO. This saves six transitions on every genuine left move.
2. Mark-bit-only scan for writes and moves: before a target tape head, all genuine cells are unmarked. Skip the first three digits of each data block and test the last. Zero continues scanning; one dispatches the required operation. For move, replace the head bit with zero and enter the directional marking continuation. For write, retain the last bit one and write the new code's other three bits, without distinguishing the old data value. At a direct action root the selected cell is already known to be marked. Preconditions: logical writes never write L or overwrite L, and a logical left move never starts at L. This specialization is not equivalent on illegal logical operations or malformed physical layouts.
3. Same-cell read/write continuation: resolve intervening jumps in the destination. If the current primitive is read/write and the resolved successor is read/write/move on the same tape, finish at the first digit of the current marked block and enter the successor's action decoder directly. No scan back to G and out again. Other edges, including all move successors, cross-tape successors and terminal successors, retain the global G boundary. This is not fusion of logical primitive counts: each original logical operation is still simulated.

## Source-level simulation
For valid layout and a sentinel-safe logical run, allow two instruction-boundary types: G-aligned global entry or marked-block-first-digit local entry with the correct target tape. From global entry scan reaches the unique marked cell. From local entry it is already there. Blind write/move depends only on the marked bit and known operation, and leaves the same encoded data as D6R; the directional mark proof follows from exactly one marked cell per tape and paired bit codes. For growth the unchanged FIFO invariant applies. A read or write does not alter head position or region size, so a same-tape successor receives the correct aligned local entry, including after a resolved jump. Otherwise the existing reverse scanner restores G and dispatches globally. Thus each primitive preserves decoded configuration, entry alignment and next logical instruction. Induct over the genuine run. This assumes inherited producer/bridge correctness and sentinel-safe IR; finite tests are not a mechanical proof of every raw input. Invalid logical moves/writes and malformed-layout rejection behavior are explicitly outside the equivalence claim.

## Exact clock
For w=4, target block index p and D6R base read/write cost 2pw+2w-1, directional marking subtracts 2(w-1)=6 on a left move. Blind scan/write has the same physical length as the old global operation. A local entry removes pw forward-scan transitions. A read ending locally has unchanged-symbol stationary rewrite cost 2w-2, reducing its global-end cost by pw+1. A write ending locally uses the uniform changed/stationary write traversal of 2w-1 (even when data agrees), reducing by pw. For each local link the next target p is unchanged, so total savings relative to D6R are 2pw+1 for a read link, 2pw for a write link, plus 6 per left move. Right-growth cost before local-entry subtraction remains D6R's FIFO formula. Final success/reject still 6/7. The accountant resolves actual branches and jumps and tracks the local-entry flag. Existing safe upper bound and conditional O(L^2(p+1+V)) envelope (p there means propagation passes) remain valid; restricted exponent 2+(h+b)/3 unchanged. No universal cubic guarantee or unrestricted SAT reduction. Fixed-nine explicit normalized inputs already admit polynomial enumeration.

## Independent verification
Three configurations: original/general, paired/general, paired/specialized/serial/directional/blind/local. 2808 single-primitive tests (1440 read,864 write,216 left,288 right;72 growth and1152 reject cases included),72 multiprimitive exact-clock programs and2 immediate terminal tests. Against D6R serial baseline, 936 single-primitive and24 program comparisons check exact physical buffers, exits and heads and non-increased transition counts. Independent delta check on all936 single primitives:72 improve (left moves),864 tie. Additional24 branch/jump programs independently simulate logical instructions and head positions and check exact physical delta:99 local links,5739 local-link transitions saved plus left-move savings. All pass. Twelve hard-family source comparisons retain exact encoded terminal state, heads, status and logical primitive count. D6N's 1358 semantic executions are inherited and rerun by CI, not new physical replays.

## Measured compression ablation
| bounded configuration | original states | quotient states | descriptor bits |
|---|---:|---:|---:|
| D6R |1328337|1156310|87879564|
| directional only |1319045|1146842|87159996|
| directional + blind |1262675|1090864|82905668|
| all three |1000099|830372|60617160|
A separate uncommitted entry-fusion experiment reached1081455 quotient states without local fusion; not adopted. No compiler wall-clock or peak RAM measurement.

| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| bounded |1000099|830372|60617160|3000297|
| full |999802|830075|60595479|2999406|
Both original and quotient fit 20-bit state identifiers including reserved terminal ID. Existing codec length4+q+3q(bit_length(q)+4) unchanged. Bounded quotient reduction325938 states, descriptor reduction27262404 bits. 19-bit limit q<2^19 not met; bounded gap306085 states. Logical IR9423/9418 unchanged. This is a compiler resource milestone only, no global complexity obligation closed.

## Hard-family source clocks
| domain | D6R SAT | D6S SAT | D6R UNSAT | D6S UNSAT |
|---|---:|---:|---:|---:|
| 2 |1371735821|814084632|1389408605|823871645|
| 3 |2462273307|1448450000|2510948963|1475693033|
| 4 |4815294928|2774361247|4881697883|2810561593|
Same figures in both modes. SAT local links58898/111497/238562; UNSAT59697/113901/243007. Source-accounted only; attempted bounded hard m4 physical replay exceeded tool execution limit without returning a result. No claim of completed D6S hard m4 physical verification.

## Physical evidence
| mode/fixture | original and quotient halt | head | span | worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |607247935|47122|47937|571490327|
| full one-prefix UNSAT |319578101|38293|47726|284295532|
Exact original/quotient agreement and one-short cutoffs607247934,319578100 TIMEOUT/no witness. SAT original-format witness0101010101010101011111111110000, nextSymbol2; UNSAT headSymbol2,nextSymbol1. Observed worker agrees with source accountant. Dedicated workflow registers29 jobs (one audit,26 physical,2 native); exact-head completion unconfirmed. Main and PR #248 not modified.

## Next D6T
Extend local continuation to move successors (including explicit growth return handling), or investigate direct physical fusion of multi-primitive same-tape paths with a mechanically checked simulation certificate. Preserve the distinction between valid-layout and illegal-operation equivalence. The unrestricted reduction remains the mathematical blocker; further fixed-family compression is not a P versus NP resolution. No promotion.
