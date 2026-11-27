# F038-REX-024D5Y — In-place hybrid field conversion and restored descriptor threshold

Parent bf063c930f94a02aad9cf4ae4df9372305431cc8. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5X closure

Exact-head [Proctor 46005101959](https://github.com/tltmgnt/MathOS/actions/runs/46005101959): all 15 jobs passed, including both native descriptors, twelve physical/quotient/cutoff jobs and audit/governance. All six workflows on the exact parent head completed successfully.

## Construction and invariant

Retain the D5S original-selector FIFO producer. Its canonical 00/01/11 run-token fields with 10 delimiters enter the final logical tape (21). Unlike D5X, there is no second complete stream. The converter scans the first eleven literal fields unchanged, skips universal higher-arity fields, collects one active field's run tokens in reusable scratch (x denotes four zero rows), and applies D5X's physical heuristic: bypass gamma encoding for at most 16 tokens; otherwise expand the field in scratch, compute the headerless gap code and choose gamma only if the encoder selects sparse and twice the gap payload length is at most the run-token count.

A run fallback leaves the original field untouched, including the delimiter, and clears scratch. When gamma is chosen, rewind the original paired tokens from just after the current delimiter to just after the preceding delimiter. Rewrite the first token as xx (gamma marker), the following g tokens as 0b (gamma bits), then replace the remaining original tokens with xx padding until the original delimiter 10. For k original run tokens, selection gives k>16 and 2g<=k, so 1+g<=k. Each payload/marker replacement checks the original token is not a delimiter. Padding recognizes the unchanged delimiter and leaves it intact. Consequently every interval has exactly the original length and alignment, and all earlier and subsequent fields remain untouched. The worker recognizes a leading xx marker, otherwise uses canonical run mode, including a leading 11 run. Gamma row traversal uses the same countdown as D5X; exhausted payload followed by padding means remaining rows allowed. At Cartesian exhaustion require an empty countdown and consume paired padding before the delimiter. On passing genuine fields the exact row projection and candidate validity are preserved. This is a source-level invariant for genuine producer streams, not a comprehensive adversarial malformed-stream proof (the end scanner also accepts padding in run mode, but genuine run fields never contain padding).

The previous stream is not duplicated; scratch is cleared between fields. Mode tape 20 remains fixed and tape 19 is the gap counter. There are still 22 logical tapes and per-field token, literal, gamma and counter scratch. The physical high-water allocation is not reclaimed by clearing. Gamma fields retain padding, so the final stream length equals D5S exactly, not a compacted sparse stream. The method eliminates duplicate-stream overhead, not all temporary dense storage. True online forbidden-only deposition, direct producer framing and algebraic skipping of allowed intervals remain unimplemented.

## Executed verification

266 distinct selector fixtures (including all 256 ternary truth masks, reverse chain, dense fallback, single and two gamma-field m5 fixtures), both modes, 532 logical executions. All resulting field intervals, framing, exact independent gamma expansion, run-field preservation, compared domain words, statuses and witnesses match D5S and the independent host oracle. 524 successful original witness validations and eight matching refusals. 391 run fields and three gamma fields across the distinct fixtures. All 524 successful worker clock comparisons improve over D5X; all 524 still regress over D5S. 20034 resource arithmetic evaluations passed.

| fixture (alternating pins) | D5S worker | D5X worker | D5Y worker | N D5S/D5X/D5Y |
|---|---:|---:|---:|---:|
| empty |185257932|228022120|201430754|1841/2151/1847|
| chain |302075206|358998640|325309930|1883/2232/1892|
| third-rank m3 |295216832|351772630|317669458|1928/2286/1940|
| all-active |1099924056|2009888980|1342551958|2981/4662/2990|
| sparse m5 |251468374|540223928|466740846|2086/2654/2265|
| two sparse fields m5 |293051186|771488498|665898052|2150/2746/2329|

All-active stream remains 1432 bits instead of D5X's 1672. Measured allocated segmented logical region is reduced versus D5X on these six successful examples. D5S remains preferred execution baseline; D5Y improves the hybrid architecture, not the best prior solver.

## Exact original-format physical evidence

| mode | t | head | span | worker clock |
|---|---:|---:|---:|---:|
| bounded chain |359026546|45818|46613|325309624|
| full chain |358838252|45818|46613|325121330|

Both on raw selectors with pins [0,0], bridgeAt=32503873, workerAt=33243080, projection=473842. Both independently validated original witness 0101010101101010101111111110000, original/quotient exact replay, and cutoffs 359026545/358838251 TIMEOUT without witness. Actual worker clocks match source accounting. Both chain cases use run mode. Additional actual compiled-worker replay from a harness-provided canonical segmented stream for two m5 sparse scopes (pins [0,1,0,1,0]) took 665898052 transitions, N=2329, 46251 primitives, exact terminal layout/head, independently valid witness, and unchanged 496-cell stream. Not an original-selector m5 replay. All-active D5Y worker cost above is source-level exact clock accounting, not an observed end-to-end physical halt. Register twelve physical jobs, two native jobs and audit/governance including multi-gamma worker replay; native workflow path correction made before final evidence commit. Current-head CI success not claimed until checked.

## Descriptor and conditional resources

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |8195|2879585|2073970|157621724|8638755|
| full |8194|2877305|2072247|157490776|8631915|

Producer 287874, bridge 303, projector 74, blank halt 1; workers 2591333/2589053; four-bit segmented symbol lowering unchanged. Both quotients restored below 2^21; bounded margin 23182 states. D5X bounded quotient 2110290 and descriptor 166712914. This is descriptor compression relative to D5X, not relative to D5S.

For genuine normalized input, S is inherited dense stream ceiling and b=bit_length(m^3+1). Single stream, reusable per-field high-water scratch (token <=m^3, literal <=m^3, selected code <=m^3+1, candidate <=2m^3, counters), and mode/segment slack admit the conservative conditional region allowance N<=S+35m+1632+5m^3+4b<=3S, versus D5X 5S. Keep conditional T<=65536S(b+1) bounded or 65536mS(b+1) full; in-place rewind/write/pad linear in original field length, per-row gamma countdown O(b), under inherited source macro estimates. W<=(20N+12)T+6. Producer 4P+32L, bridge 128S^2, projection 1024S^2 and total<=2^20(b+1)L^2 bounded or 2^20m(b+1)L^2 full remain conservative. No tighter total theorem asserted. Arithmetic checked but global macro premises are not mechanically proved. Radius-two candidate search incomplete; no practical cubic admission, no P versus NP resolution.

Next D5Z: remove redundant short-field scratch/probes and mode overhead; investigate genuinely sparse physical deposition and compact framing without padding; prioritize complete search counterexamples and global completeness obligations rather than treating engineering speedups as progress toward a theorem. Confirm D5Y independent native and physical CI. Main and PR #248 unchanged.
