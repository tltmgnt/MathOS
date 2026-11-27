# F038-REX-024D6T — Interior local motion continuation

Parent D6S e9d8254b41653f3dbac4a49f809a3816cad300df. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6S exact-head Proctor 46078501790](https://github.com/tltmgnt/MathOS/actions/runs/46078501790): 29/29 jobs passed, including native 20-bit descriptor verification and hard m4 physical replay. D6R remains 29/29.

## Mechanism and simulation
Retain D6N logical IR, D6R FIFO, D6S global/local entry distinction, 20 logical tapes, paired four-bit codebook, original raw producer, bridge and projector. Add optional motion flag (requires local mode, defaults on with local). Resolve jump chains. If a move's successor is read/write/move on the same tape, choose a shared directional marking root keyed by that successor's direct action root. On a non-growth move, write the new head bit at the neighboring block's final digit, then move left across the other digits to its first digit and enter the next action without crossing to the preceding block or scanning back to G. The left marking path starts on the neighbor's last digit; right marking starts on its first digit and identifies genuine unmarked data by paired prefixes. For w=4, these marking segments take3 and6 transitions respectively, compared to4 and7 before local dispatch (the right cost counts three forward and three backward steps). If the right neighbor is a D/E delimiter, retain the existing bit-serial FIFO and global reverse return to G. No local growth continuation is implemented. Cross-tape, terminal and otherwise ineligible successors also retain global entry. motion=false restores D6S.

Proof: a legal interior move changes exactly the old and new head bits, leaves all encoded block positions unchanged and sets the new logical head to p'=p+dir. The new marking path writes the same head bit and ends at the new marked block's first digit with the successor action root. Thus D6S's local-entry invariant holds for a move successor. The D/E branch remains the inherited FIFO proof and restores global entry even for an otherwise eligible same-tape successor. Read/write local edges and global scans are unchanged. Induction establishes source-level decoded simulation on sentinel-safe genuine executions under the inherited producer/bridge assumptions. Malformed physical layouts and illegal logical actions remain outside the equivalence theorem. No change in logical primitive count, candidate order or encoded terminal state.

## Exact clock
For a successful non-growth local move link, let p' be the new encoded block index. D6S crosses one extra cell after marking and returns from the preceding block to G at cost p'w, then the successor scans forward p'w. Therefore the exact link saving is 2p'w+1=8p'+1. The clock accountant charges p'w+1 to the move's removed return and p'w to the successor's removed entry; it uses old/new block counts to distinguish growth. Growth barriers preserve the D6S global endpoint. Existing read/write-link and directional marking savings remain unchanged. The safe upper bound and conditional O(L^2(p+1+V)) physical envelope remain valid (p in that expression denotes propagation passes). No new asymptotic exponent or unrestricted SAT reduction. Fixed-nine explicit normalized inputs already admit polynomial exhaustive enumeration.

## Evidence
Inherited independent macro audit expanded for local motion: 2808 single primitives,72 multiprimitive clock programs,2 immediate terminals,960 predecessor buffer/head/exit and non-increase comparisons against D6R,936 single-primitive delta checks (72 strict left savings),24 additional branch/jump programs with147 local links and8611 independently calculated link savings (including the prior D6S links). All pass. New boundary audit checks actual emitted ternary transition rows at every local marking root, for all five unmarked data codewords (including right-neighbor L as a stronger local fragment test) and two representative D/E growth suffixes per right root. It compares exact endpoint state, physical head, every buffer cell including guards, and transition count. Bounded:5011 roots,25055 interior checks,8702 growth checks,340576 transitions. Full:5009 roots,25045 interior checks,8698 growth checks,340424 transitions. Total67500 boundary checks across10020 roots. First attempted expected right-segment cost7 was wrong; actual6 confirmed by the exact path and full clock tests, and the audit expectation was corrected before commitment. This is a finite mechanically checked boundary certificate, not a full machine-checked proof for all arbitrary-length suffixes, all compiler macros or unrestricted raw inputs. D6N 1358 semantic runs inherited, CI reruns them. No new claim of 1358 physical runs.

## Resources
| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6S bounded |1000099|830372|60617160|3000297|
| D6T bounded |1015504|846292|61779320|3046512|
| D6S full |999802|830075|60595479|2999406|
| D6T full |1015193|845981|61756617|3045579|

Bounded descriptor increases1162160 bits and15920 quotient states (1.92%). Both original and quotient still fit 20-bit identifiers including terminal ID. 19-bit target unmet. No descriptor compression or compiler RAM/wall-clock claim. Logical IR9423/9418 unchanged.

## Hard-family clocks
| m | D6S SAT worker | D6T SAT worker | D6S UNSAT worker | D6T UNSAT worker |
|---|---:|---:|---:|---:|
| 2 |814084632|100874416|823871645|102405415|
| 3 |1448450000|180983007|1475693033|185472205|
| 4 |2774361247|360391458|2810561593|366142030|

Both modes yield these same source-accounted clocks and complete decoded terminal parity across12 runs. Hard m4 SAT:564720 logical steps,502895 local links (264333 movement links),1440 eligible growth barriers. Hard m4 UNSAT:574882 steps,511658 links (268651 movement links),1438 barriers. Selected hard m4 bounded SAT original physical replay completed, matches worker accounting and exact reference witness; its quotient/cutoff not yet confirmed. No blanket new hard-family physical result.

## Actual physical replays
| fixture | halt transitions | head | span | worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |108113804|47122|47937|72356196|
| full one-prefix UNSAT |82997342|38293|47726|47714773|
| bounded hard m4 SAT original only |2142778881|442498|447256|360391458|

First two: original and quotient halt/head/span/witness agreement; cutoffs108113803 and82997341 TIMEOUT/no witness. SAT witness0101010101010101011111111110000, nextSymbol2; UNSAT headSymbol2,nextSymbol1. Original worker clock matches model. Hard m4 original: bridgeAt1776939798, workerAt1780602625, outputAt2140994083; reference witness000100011000100010001000100010001000001001111111111111111111111000000. A combined three-fixture replay exceeded tool execution limit; separate selected replays and original hard m4 replay succeeded. Hard m4 full quotient/cutoff await CI. Dedicated Proctor29 jobs (one audit with boundary checker,26 physical,2 native); completion unconfirmed. Main and PR #248 not modified.

## Next D6U
Investigate the dominant unchanged raw producer phase on hard m4 (about1.78 billion transitions before worker), and whether growth barriers merit local-return specialization. Prioritize resource certificate and unrestricted reduction barrier over merely pursuing narrower state IDs. No promotion.
