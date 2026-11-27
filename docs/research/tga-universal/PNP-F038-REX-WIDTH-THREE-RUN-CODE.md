# F038-REX-024D5N — Active-mask run coding and reversible physical decoding

Parent 58f4d0b0238d66d276c4668cc48d2838f2050a60. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Prior verification

D5M exact-head [Proctor run 45948697768](https://github.com/tltmgnt/MathOS/actions/runs/45948697768) completed all fifteen jobs successfully: twelve physical replays and quotient cutoffs, two independent native descriptors, and audit/governance. The bounded m3 third-rank clock 628994848, head 170089, span 172904 was independently confirmed in both original-format native and JS physical replay. Both all-active m2 modes clocked 1348388180 transitions (head 53792, span 54821).

## Active-mask codec

Preserve the original normalized raw selector grammar and D5M universal-mask elision. For each non-universal binary/ternary field, greedily encode each group of four consecutive zero bits as 11; otherwise emit literal 00 or 01. Token 10 remains the field delimiter. First eleven fields retain the original literal encoding. The producer probes up to three cells to the left of the current zero in its right-to-left source-block scan; a failed probe returns to that zero for literal copying. On success it marks the fourth zero temporarily blank and uses one inherited copy shuttle for 11, then restores that zero and continues. The other three source zeros are untouched. This is actual physical mask-loader compression, not host preprocessing. The original dense normalization and deposition workspace is unchanged.

For each maximal zero run of length r in an active field there are floor(r/4) run tokens. Let K be the sum over all such runs. The stream length S_r=S_c-6K<=S_c<=S; universal relations remain empty fields. A tokenwise expansion (11->00 00 00 00) is exact, so the code is lossless on the genuine canonical streams. Literal fallback is local to each token, not a separately selected density mode or a universal speedup. A field without a four-zero run keeps the D5M representation exactly.

## Reversible decoding

The four-bit logical alphabet and 20-tape layout are unchanged. To avoid a decompression tape, a run token on Q has four progress states: 11, x0, x1, xx. The first three zero emissions advance the odometer while leaving Q at the first cell of the partially consumed token; the fourth restores 11 and advances to the next token. Propagation sees precisely the same lexicographic tuple sequence as D5M. If the selected candidate matches any zero in a run, the worker restores 11 (if needed) and skips the whole remaining token before suffix traversal. A forbidden candidate can trigger a retry only on a literal 01, where no pending run exists. Empty-field dispatch distinguishes 10 from 11 by inspecting the second cell. All successful/rejected genuine streams tested retain their original compressed bytes. The accepted witness and refusal semantics remain those of the bounded or full GAC controller, with incomplete radius-two search. No complete SAT/UNSAT decision is claimed.

## Architecture

| metric | D5M bounded | D5N bounded | D5N full |
|---|---:|---:|---:|
| logical tapes |20|20|20|
| symbol width |4|4|4|
| IR instructions |6978|7046|7045|
| original states |2474571|2527007|2524727|
| quotient states |1857873|1892836|1891113|
| descriptor bits |141198352|143855540|143724592|
| transition checks |7423713|7581021|7574181|

New producer 259027 states, bridge 279, projector 74, blank halt 1; workers 2267626 and 2265346. Both quotients remain below 2^21. The descriptor grows relative to D5M; this is a storage/runtime tradeoff, not a descriptor compression result.

## Focused independent resource accounting

The failed producer probe checks at most three additional cells and returns to the original zero, costing at most six extra transitions per literal zero; a successful probe costs three extra moves per group of four and replaces four copy shuttles with one. Retained shuttles see no longer output prefix than before. Add D5M's universal-detection overhead and fixed entry/return slack; charge P'=P+16L, where inherited P=256L(131L+2176)+2^40. The new finite lookahead oracle enumerated all 8190 nonempty binary words of lengths 1..12, confirming exact expansion and extra cost <=6n for each word, max observed 36. This oracle checks the local counting argument, not the entire actual physical normalization/deposit compiler.

The run decoder replaces the four-primitive literal token read by at most eight primitives per emitted zero. The extra dispatch lookahead costs three primitives per scope; suffix scanning consumes fewer or equal tokens. A conservative extra allowance of 8S per sweep or candidate attempt covers those increments (B=36m^2+84m^3<=S/2; 120 scopes, S>=1936). Bounded 4 sweeps plus 46 attempts add at most 400S; full <=9(m-1)+1 sweeps plus 46 attempts add at most 256mS. Existing D5M source-level ceilings retain slack; use enlarged T<=49152S bounded and <=49152mS full. There is no additional tape allocation, N<=S_r+35m+1479<=2S. Thus W<=(20N+12)T+6<=2097152S^2 bounded or <=2097152mS^2 full. With inherited bridge/projection ceilings and P'<=35000L^2, retain conditional t<=2^16 L^2 bounded, t<=2^12 L^(7/3) full. Arithmetic checked 20034 times across both modes. All original normalization/deposition and lowering macro premises remain conditional; no mechanically certified global resource theorem.

Sufficient cubic thresholds are H>=143855556 bounded and H>=215586906 full. Both increase compared to D5M. No finite cubic admission demonstrated.

## Executed evidence

73 distinct selector fixtures, 146 bounded/full mode comparisons against D5M and the independent support/candidate oracle: 88 valid witnesses, 58 refusals, 146 exact terminal stream restorations. 68 fixtures compressed further; all four possible selected-row positions inside a run checked explicitly, plus a no-run literal-dense fixture. Ten actual physical producer streams compared bit-for-bit to independent codec, three malformed selectors refused. Additional exhaustive IR audit: every one of 256 ternary truth masks at m2, with and without unary restrictions (512 cases), matched D5M status/witness and restored stream, 383 accepted and 129 refused. All 88 successful mode clock/storage accounts checked; 32 improved and 56 regressed in worker clock against D5M. No general dominance.

| fixture | D5M stream | D5N stream | D5M bounded worker | D5N bounded worker |
|---|---:|---:|---:|---:|
| empty m2 |304|304|185257932|202262892|
| ternary chain m2 |352|334|306433186|331620340|
| third-rank m3 |380|344|305295812|329956256|
| reverse chain m2 |368|368|575415568|616700224|
| all-active m2 |1936|1432|1227796008|1157211552|
| literal dense m2 |320|320|276169550|301789466|

Worker figures use alternating pins. New physical original-selector replay with pins [0,0]:

| phase | bounded ternary chain | full all-active |
|---|---:|---:|
| producer |36596889|79754313|
| bridge |723079|10958635|
| worker |331620022|1157211234|
| projection |471574|748270|
| total |369411564|1248672452|
| halt head |45782|51272|
| span |46811|52301|

Both physical and exact quotient replays validated original witnesses and matched head/span/clock, with one-short TIMEOUT and no witness at 369411563 and 1248672451. Exact worker clock matched source accounting. Compared with D5M, chain total regresses, all-active total improves; the decoder overhead makes D5M preferable on many fixtures. These are separate research descriptors, not a replacement of D5M.

New workflow registers twelve original-selector replays, two native jobs and the focused independent audits. New CI/native success is not claimed before confirmation. Direct sparse constraint deposition and shared compact normalization are unimplemented. Next: investigate direct sparse forbidden-tuple storage/deposit or an explicitly cost-aware run/literal choice, reduce decoder overhead, confirm D5N independent native and physical matrix, continue independent macro verification. No edits to main or PR #248.
