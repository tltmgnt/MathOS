# F038-REX-024D6R — Shared bit-serial suffix FIFO

Parent D6Q e10dee6568ece89a67b22e437242b9e670e1dd1a. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6Q exact-head Proctor 46075128833](https://github.com/tltmgnt/MathOS/actions/runs/46075128833): 29/29 completed successfully. D6P and D6O remain verified 29/29.

## Mechanism and invariant
Retain D6N logical controller, 20 tapes, four-bit paired codebook, D6P reverse-return alignment and D6Q valid-layout scans. Original raw producer and projector unchanged. The default serial mode is enabled only with paired/specialized layout. serial=false restores the D6Q word carry. On rightward growth, the former D/E delimiter is replaced by the marked virtual blank exactly as before. Enter physical FIFO state with the displaced delimiter as four queued bits. Each subsequent binary cell emits the oldest queued bit, appends the original scanned bit and moves right once. This is a finite physical control graph (16 possible queue states per resolved return destination); no host buffer, extra tape or unbounded storage. Shift states are keyed by the return continuation and queue, not by the initiating move instruction. All 16 queues and ordered successors are reserved before physical lowering. At the first physical blank the queue must be exactly E. Flush its four digits onto fresh blank cells, then move left to the preceding block's last digit and use D6P reverse return. Reject if the queue is not E at a blank or if subsequent flush cells are not blank. This is not a validator for every malformed layout.

Let x be the original binary suffix following the replaced delimiter, and c the displaced delimiter code. After r bit transfers, the output written so far is the first r digits of c||x, and the FIFO is the next w digits of c||x (for 0<=r<=|x|). The base r=0 holds by initialization; a transition emits the first FIFO bit and appends the next original digit, proving the inductive step. At r=|x| the FIFO is the final w digits of c||x, namely E (even if x is empty, since then the displaced delimiter is E). Flushing E therefore gives precisely c||x, shifting the whole suffix by one logical block with all marks and separators preserved. Growth inserts one logical blank, leaves exactly one head mark in the expanded tape and preserves all other tapes. Return ends at G as before. All other primitive macros unchanged. Induction on genuine logical primitives proves source-level simulation under inherited producer and layout invariants; external witness semantics unchanged. This is not a mechanical certification of unrestricted raw inputs.

## Exact physical clock
Let N be the old encoded block count, p the marked cell's zero-based block index, w=4 and R(u,v) the D6O exact right rewrite cost. The preceding word-carry growth formula was (p+N+2)w-1+R(hx,ux)+R(delimiter,h_)+sum R(a_i,c_i), over N-p-2 old suffix blocks. The FIFO traverses exactly (N-p-2)w old suffix digits, and the E flush/return alignment costs 2w-1 before the N-block reverse scan. Therefore the new growth cost is
C_growth=2Nw-1+R(hx,ux)+R(delimiter,h_).
The saving is sum (R(a_i,c_i)-w), nonnegative on genuine inputs. No change to non-growth costs or final halt/reject costs. The original clock accountant retains actual word-carry accounting for comparison; the new ledger records the same logical execution and uses the closed-form serial cost. Equal/changed carry counters remain descriptive of the old word-carry suffix, not physical FIFO operations. Runtime improvement is limited by the fraction of growth operations. The inherited safe bound (2bNmax+2a)K+a+indicator(reject), b=3w-2,a=2w-2, remains valid. Conditional O(L^2(p+1+V)) physical envelope and restricted admitted exponent 2+(h+b)/3 unchanged (p in that complexity formula is propagation passes). No unrestricted SAT reduction, universal cubic guarantee or P versus NP proof. The fixed-nine explicit family is already polynomial by exhaustive enumeration.

## Independent audit
Three configurations (original codebook/general, paired/general, paired/specialized/serial): 2808 single-primitive tests (1440 reads,864 writes,216 left,288 right,72 growth and1152 reject included),72 multiprimitive programs with exact clock,2 immediate terminals. For specialized serial configuration, 936 single primitive and24 program comparisons with same compiler with serial disabled check complete physical buffer, head, exit and non-increased transition count (960 comparisons). An independent binary suffix calculation checks the exact old-minus-new transition delta on all 936 single-primitive comparisons;16 strict savings,920 ties (8 of24 serial growth cases are final-tape zero-suffix shifts). All tests passed. An initial audit invocation retained an incorrect exact-clock equality check for a faster serial program due to a non-global replacement; the baseline arguments were corrected before commitment and the final audit passed. Twelve source clock comparisons against D6Q preserve exact encoded terminal state, classification, heads and logical steps. Inherited D6N 1358 semantic runs and D6Q evidence remain separate; dedicated workflow reruns inherited audit, not a claim of 1358 new physical runs.

## State-width milestone
| mode | original physical states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6Q bounded |2676117|2486933|196467711|8028351|
| D6R bounded |1328337|1156310|87879564|3985011|
| D6Q full |2674991|2485807|196378757|8024973|
| D6R full |1327755|1155728|87835332|3983265|

Both original and quotient physical machines now fit 21-bit state identifiers including the reserved terminal ID. The existing descriptor uses b=bit_length(q), total length4+q+3q(b+4); no change to external codec. Bounded quotient reduces1330623 states; descriptor reduces108588147 bits. 20-bit threshold (q<2^20) remains unmet; bounded excess107734 above2^20. Four-bit worker symbol width and logical IR9423/9418 unchanged. No measured compiler wall-clock or peak-memory claim. Native decoder verification for the new state width registered but not yet run to completion.

## Hard-family exact source clocks
| domain | D6Q SAT | D6R SAT | D6Q UNSAT | D6R UNSAT |
|---|---:|---:|---:|---:|
| 2 |1375602989|1371735821|1393178371|1389408605|
| 3 |2467219703|2462273307|2515679171|2510948963|
| 4 |4821742340|4815294928|4887836949|4881697883|

Both modes agree on these figures, source-accounted not new hard-family physical replays. Hard m4 SAT logical steps564720 unchanged. Savings smaller than state reduction.

## Physical replay
| fixture | original and quotient halt | head | span | worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |990747449|47122|47937|954989841|
| full one-prefix UNSAT |516306875|38293|47726|481024306|

Original and quotient match exact transitions, head, span and expected witness; one-short quotient cutoffs990747448 and516306874 TIMEOUT/no witness. SAT witness0101010101010101011111111110000, nextSymbol2; UNSAT headSymbol2,nextSymbol1. Observed worker matches source accountant. Dedicated Proctor config registers29 jobs (one audit,26 physical,2 native). Full D6R completion unconfirmed. Main and PR #248 not modified.

## Next D6S
Target the remaining 20-bit gap via specialized physical move/mark continuation fusion and possible source-to-physical local scan fusion, with independent proof and replay. Treat achieved 21-bit width as a compiler resource milestone, not closure of a complexity-theoretic obligation. No promotion.
