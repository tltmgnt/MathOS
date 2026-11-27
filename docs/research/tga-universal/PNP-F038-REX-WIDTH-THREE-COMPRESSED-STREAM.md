# F038-REX-024D5M — Producer-side universal-mask elision and density-adaptive execution

Parent c2de7a3391fc302564b21abb9eb5aa826c4ced62. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Prior verification

D5L exact-head [Proctor 45947164278](https://github.com/tltmgnt/MathOS/actions/runs/45947164278) completed all thirteen jobs successfully, including both independent native descriptors, ten original-selector physical replays and quotient cutoffs, original Python clause verification and governance. Full reverse-chain physical replay job 140334404488: 4036784504 transitions, head 54276, span 55305, nine sweeps, stable; bounded counterpart job 140334404503: 2179027568 transitions, four sweeps, not stable. Both emitted valid original witnesses. All other workflows on that head also completed successfully.

## Construction and invariant

The direct producer continues to validate the same original raw normalized selector, initialize and deposit the same dense constraint masks, and preserve pins/unary fields. Only the subsequent physical mask loader changes. For each higher-arity source block j=46..165, scan left from its right separator until a 1 or the left separator. On a 1, return right to the original separator and copy the entire block exactly as before. On reaching the left separator without a 1, use the existing Done shuttle to append only the field delimiter 10. This is a physical read-only test of the actual deposited mask, not a host-provided index or a changed input grammar.

The new stream has exactly 131 delimited fields. The first eleven retain their complete contents, including bound, pins and all nine unary masks. A higher-arity field is empty if and only if its forbidden mask is all zero; otherwise it retains every bit. Let A be the set of non-universal binary/ternary scopes, with arities r(h). Its raw stream length is
    S_c = 2(b+10m+131+sum_{h in A} m^{r(h)}) <= S.
The codec is injective on canonical streams for a given m: expand each empty higher-arity field to m^r zero bits. In particular no forbidden bit is removed. The worker dispatch tests the first token; an empty field skips only the scope record and delimiter, whereas a nonempty field invokes the existing propagation or validation code. This is per-scope automatic density adaptation, without an explicit global density heuristic or alternate-machine choice. The activity tape and indexing prepass disappear, reducing logical tapes from 21 to 20. The generic bridge still copies a contiguous binary stream and the projector still validates the original halt-output layout. Normalization/deposit workspace itself remains dense and shared compact normalization is not implemented.

For nonempty domains a universal relation has identity support projections and always accepts the chosen candidate. Therefore the compressed bounded/full modes retain the corresponding D5L sweep order, stopping condition, support changes, candidate order and witness/refusal result on genuine producer streams. The claim is a source-level argument plus finite tests, not a mechanized equivalence theorem. Full convergence still only establishes GAC; bounded radius-two first/second-rank candidate search is incomplete.

## Measured architecture and envelopes

| metric | D5L bounded | D5M bounded | D5M full |
|---|---:|---:|---:|
| logical tapes |21|20|20|
| encoding bits |4|4|4|
| IR instructions |7030|6978|6977|
| original states |2497848|2474571|2472291|
| quotient states |1873921|1857873|1856150|
| descriptor bits |142418000|141198352|141067404|
| transition checks |7493544|7423713|7416873|

Producer grows by exactly 240 states to 230707 (two detection states per higher-arity block); bridge 279, projector 74, blank halt 1. Workers 2243510 and 2241230 states. Both quotients remain below 2^21.

Retain D5L's dense length S for a uniform conservative bound. Removing 120 data cells and three segment overhead blocks gives N<=S_c+35m+1479<=S+35m+1479<=2S. On a successful path the new dispatch replaces index operations and inactive scans by fixed-size skips, and active mask work is unchanged. Thus the prior conditional primitive ceilings T<=32768S (bounded), T<=32768mS (full) still suffice. The four-bit compiler yields W<=(20N+12)T+6. Bridge and projection ceilings are inherited, with no larger encoded region. The extra producer detection reads/returns cost at most twice the original higher-arity mask length plus 240 fixed transitions, <=L. All skipped copy shuttles are removed; retained shuttles traverse no longer output prefix than before. Charge P'=P+L<=35000L^2 (inherited P=256L(131L+2176)+2^40); arithmetic verified. Therefore retain t<=2^16 L^2 (bounded) and t<=2^16 m L^2<=2^12 L^(7/3) (full). These rely on inherited normalization/deposit/loader macro costs and source-level physical compiler accounting, not a mechanically certified theorem.

Sufficient cubic admission thresholds: bounded H>=141198368, full H>=ceil(3(141067404+12)/2)=211601124. Neither demonstrates finite measured cubic admission.

## Executed evidence

68 distinct original selector fixtures checked (same named/seeded set as D5L), 136 mode runs: 78 successful original witnesses, 58 refusals. All compressed mode status/witness results matched the corresponding D5L controller and independent domain/candidate oracle; all 68 stream codecs matched the canonical dense expansion. Five actual producer streams independently replayed and compared bit-for-bit; three malformed selectors physically refused. All 78 successful exact worker accounting comparisons improved versus D5L; no regression in this sample. 20034 arithmetic checks across both envelopes, including explicit detection overhead. No general performance dominance claimed.

| fixture | old stream | new stream | D5L bounded worker | D5M bounded worker |
|---|---:|---:|---:|---:|
| empty m2 |1936|304|905168946|185257932|
| ternary-chain m2 |1936|352|1279354488|306433186|
| ternary-three-rank m3 |5510|380|5115765100|305295812|
| reverse-chain m2 |1936|368|2058360018|575415568|
| all-active m2 |1936|1936|1546275234|1227796008|

Worker accounting uses alternating pins. All-active incurs extra producer read cost (100023249 versus 100021617), but removes the old index/extra tape overhead. Against D5K's dense worker 1222025940 it remains slightly slower (about 0.47%). Thus no separate global dense/sparse selector is implemented or claimed.

Fresh actual whole physical original-selector execution, pins [0,0] for m2:
| phase | D5L bounded | D5M bounded | D5M full |
|---|---:|---:|---:|
| producer |100021617|37294107|37294107|
| bridge |19740475|793675|793675|
| worker |1279354170|306432868|306244952|
| projection |906274|476110|476110|
| total |1400022536|344996760|344808844|

Both D5M original and quotient replays matched the original witness 0101010101101010101111111110000, head 45872, span 46901 and exact worker clocks. Both one-short cutoffs passed. Additional bounded ternary-three-rank m3 original physical replay (pins [0,0,0]): t=628994848, head=170089, span=172904, producer=322022518, bridge=909931, worker=305276540, projection=785859, valid original 50-bit witness. Its quotient/cutoff is registered, not yet independently confirmed at this writing. D5M new workflow registers twelve physical replays and two native jobs, including the pinned m3 clock, plus independent audit and governance. Do not claim current-head CI/native success before confirmation.

Next: compress active masks themselves (e.g. forbidden tuple run coding or direct sparse deposits with safe decoding and dense fallback), further reduce normalization/deposit shuttles, evaluate independent proof of resource macros, confirm D5M native and physical matrix. No main or PR #248 edits.
