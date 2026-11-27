# F038-REX-024D5O — Read-only run decoding and batched physical loading

Parent e3f98d0e24f77f16da67ca8374d392795f97cb7a. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

D5N exact-head [Proctor 45950608442](https://github.com/tltmgnt/MathOS/actions/runs/45950608442) passed all fifteen jobs including independent native bounded chain and full all-active replay.

## Construction

The D5N stream grammar and original normalized selector grammar are unchanged. Instead of rewriting 11 to progress markers, consume 11 once and process three additional virtual zero rows using finite-control continuations. Each continuation advances the same rank/support odometer as one literal row. A matching candidate at any virtual row skips the remaining token and enters the normal suffix scanner. No Q writes exist in the IR. Inactive-field dispatch directly consumes the delimiter rather than rewinding it. The producer now batches the short zero-run suffix (two or three literal zeros) in one shuttle; four zeros still emit 11. Failed lookahead has already identified the short run length; move right to its last zero and mark only that cell, restore it after transferring the literals. All other source bits untouched. Dense deposition remains unchanged.

## Measurements and conditional envelope

Bounded/full IR instructions 7183/7182, producer 313507, bridge 279, projector 74, workers 2298778/2296498, original states 2612639/2610359, quotient states 1948422/1946699, bits 148080076/147949128, transition checks 7837917/7831077. Both below 2^21. Short-run batching reduces copy shuttles and does not lengthen the stream; the prior P+16L producer allowance suffices under inherited macro assumptions. Read-only virtual rows do not increase per-row work; retain conservative T<=49152S or 49152mS, N<=S+35m+1479<=2S, and D5N conditional quadratic/subcubic ceilings. Thresholds 148080092/221923710. Not a mechanized resource theorem or practical cubic admission result.

73 selectors, 146 bounded/full runs; 88 accepted, 58 refused, exact preservation of all 146 streams, 10 actual producer comparisons (8 improved, 2 tied), 3 malformed refused, 20034 arithmetic checks. All 88 worker clocks improved over D5N; 82 improved and 6 tied D5M. All 512 exhaustive ternary-mask regressions passed. No universal dominance claim.

| fixture | D5M | D5N | D5O |
|---|---:|---:|---:|
| bounded chain |344996760|369411564|339634840|
| full all-active |1348388180|1248672452|1172606996|

Chain: producer 36365299, bridge 723079, worker 302074888, projection 471574, head 45782, span 46811. All-active: producer 60976353, bridge 10958635, worker 1099923738, projection 748270, head 51272, span 52301. Both original and quotient witnesses verified, cutoffs at 339634839 and 1172606995 TIMEOUT without witness. The latter cutoff was retried successfully after an earlier remote disconnection. Native/CI workflow now registered; no current-head completion claim until confirmed. No main or PR #248 edits.
