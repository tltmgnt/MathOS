# F038-REX-024D6J — Physical conditioned mask slicing

Parent D6I 2397ada0e261997c4b0d5cc6feee191d472d7042. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6I final-head Proctor 46049628378](https://github.com/tltmgnt/MathOS/actions/runs/46049628378): 23/23 jobs passed as of this checkpoint, including both hard m3 SAT and native jobs. D6H verified 19/19 (46045406270).

## Physical selected-row construction
Retain D6I four-candidate direct probe, exact checkpoint continuation, canonical stream, GAC, first-splitting prefix admission and original lexicographic witness output. When conditioning is admitted, materialize a different compact local constraint stream: a scope of original arity r with k of its first coordinates fixed has m^(r-k) rows, rather than m^r. Here k depends on the scope, not simply on the global separator length h. Factors not touching the prefix are copied unchanged.

For a sorted scope and fixed ranks a_0,...,a_(k-1), define width W=m^(r-k), prefix index I=sum_i a_i m^(k-1-i) and start offset I W (zero-based). Its selected row interval is [I W,(I+1) W). The implementation derives this interval without host arithmetic or certificate: the original rank odometer scans Q, with one-hot copies of the fixed ranks in scratch R0/R1, and lengths m for remaining coordinates (one-symbol dummy R2 for pairs). Membership in the interval is exactly the conjunction of the first k one-hot cursor bits. A before/inside state machine stops rank stepping when the interval ends; it skips remaining source tokens to the field delimiter.

An original literal token 00/01 contributes its bit iff its row is selected. A run token 11 contributes four allowed rows. Count the overlap of its logical rows with the interval using finite control, preserve 11 for overlap four, emit 00 repeated for overlap one, two or three, and omit it for overlap zero. If the interval ends within a run, the entire original token has already been consumed; the remaining virtual rows contribute nothing. Exactly one 10 delimiter follows the sliced field. This is clipped original-run encoding, not global recompression of adjacent output zero literals. No source token or original domain is changed.

Compact CD stores original IDs for residual coordinates and aliases 9,10 for fixed original IDs 0,1, respectively. These are four-bit IDs, valid only on compact directory CD, not on original D. Original record arities remain intact. Alias loads a singleton one-hot word "1", so candidate iteration over the sliced mask has dimensions 1 on fixed axes and m on free axes. The pair-vs-triple discrimination through R2 length remains valid: a triple's last ID is always residual because h<=2, hence R2 length m>=2; a pair has dummy R2 length one. A conflict at last alias 10 is the prefix-only pair (0,1), which advances the prefix. Alias 9 cannot be a last coordinate of a genuine active higher-arity factor. All ordinary residual conflicts use unchanged direct last-coordinate extension. After a selected forbidden literal the remaining ranks of the last residual coordinate are still contiguous, and the inherited extension stops at domain exhaustion.

Slice contents depend on the selected prefix, so first-block reuse now preserves membership/closure only. On first-block failure, advance prefix and reset residual ranks as before; rebuild the compact mask and aliased directory instead of reusing stale slices. A19 still marks first-block membership reuse and first-block-only prefix-pair inclusion. It no longer means the compact stream itself is reusable across different prefix tuples. Repeated validation within the same block and prefix uses the same sliced stream. All 20 tapes retained. D6I checkpoint resumption is unmodified on direct/nonconditioned paths.

## Source-level correctness
On genuine normalized input, sound GAC and correct lowering, row order is lexicographic in sorted scope coordinates, so the interval of all tuples with fixed first k coordinates is contiguous. Literal and run overlap rules yield exactly the bits of that interval in original order. Mapping fixed coordinates to singleton axes produces a bijection between residual tuples and rows of the sliced relation. Therefore sliced validation accepts exactly the original factor under the selected prefix. No active factor is removed; prefix-only pair is explicitly retained as a one-row factor with both IDs aliased. The original conflict scope and last residual coordinate are preserved under alias decoding. Direct last-coordinate extension remains sound and complete on the new mask. Correct rebuild on prefix change prevents stale conditioning. All D6I candidate, conflict, prefix and component traces remain identical under decoded aliases, thus canonical witness and UNSAT conclusions follow from the inherited theorem. The proof is source-level; mechanical end-to-end lowering verification and unrestricted normalization are still open.

## Conditional resource theorem
For a factor of arity r and k fixed scope coordinates, the sliced logical row count is exactly m^(r-k). A literal contributes at most two bits per row; including delimiter, the output field length is <=2 m^(r-k)+2. Clipped runs can expand a token at a boundary, so the sliced physical stream is not claimed always shorter than its original encoded stream. Each run represents at most four rows; construction scans at most the original logical row count, plus skipped suffix tokens. Amortized odometer rewinds cost linear work in rows for fixed arity, so total materialization cost remains O(S+m+1) per prefix round for fixed nine coordinates, where S is the original stream length. The sum of local sliced lengths S_aj is O(S) per round, including prefix-only pair once; not necessarily <=S in bits due to run clipping.

Let P=product of surviving prefix domain sizes and D_j=product of residual component domain sizes. D6I's candidate and prefix ceilings are unchanged: C<=4+P sum_j D_j and V<=4+P(1+sum_j D_j). Conditional logical work is O((p+1+P)(S+m+1)+sum_{a,j} C_aj(S_aj+m+1)), where p is propagation passes. Initial direct probe and final fallback retain their inherited costs. High-water span O(S+m+1) includes original stream, local slices, domains and rank scratch; removing rows does not remove the original input or guarantee smaller physical span. Under inherited physical macro bounds and S=O(L), L>=4096m^3, t=O(L^2(p+1+V)) in admitted cases, hence O(L^(2+(h+b)/3)), b=max residual component size. Conditional cubic for h=1,b<=2 or h=2,b=1; connected fallback O(L^5). The smaller local row exponent does not by itself lower the end-to-end physical exponent because materialization, propagation and original-format tape traversal remain. No universal cubic guarantee, unrestricted SAT reduction or P versus NP proof.

## Independent audit
679 fixtures, both modes (1358 executions):1116 SAT,242 UNSAT. 256 probes,658 probe candidates,178 early probe SAT,78 suspensions,6 exact direct resumptions. 72 conditioned (16 one-prefix,56 two-prefix),52 conditioned SAT and20 UNSAT. 288 prefix assignments,7022 component/edge-list comparisons,4520 candidate/local mask/directory comparisons,2668 conflicts including22 prefix-only conflicts. 84 first-block membership reuse events. All exact status, original lexicographic witness, candidate/conflict traces and D6I parity matched. Two extra m4 hard-family fixtures, SAT and UNSAT, were included; no m5 claim.

The independent projection oracle decodes each relation into explicit rows, calculates the offset and width arithmetically, compares to independent tuple filtering, clips input-token coverage, and compares both exact output token stream and its decoded logical rows. For the 6570 sliced record validations (candidate-weighted, not distinct builds), full logical rows239550 -> selected39900; original run-coded bits223464 -> sliced67740. Counts of overlapping original four-zero runs by overlap size 1,2,3,4 are548,3584,412,4200. Left-boundary clips2182; right-boundary clips2396; both boundaries34 (included in both earlier counts). No discrepancy, including partial runs and one-row prefix-only constraints.

| metric | D6I | D6J |
|---|---:|---:|
| paired logical primitives |55342459|55400063|
| hard m3 SAT primitives |572670|554422|
| hard m3 UNSAT primitives |583192|561308|
| hard m4 SAT primitives |1218591|1099413|
| hard m4 UNSAT primitives |1233951|1106865|

40 improved,54 regressed,1264 tied. Aggregate logical cost increases57604 (~0.104%). The tied direct paths preserve exact primitive counts. Candidate visits are unchanged. Reductions in repeated mask processing do not always offset rebuilding slices on new prefix tuples.

| fixture | D6I worker clock | D6J worker clock |
|---|---:|---:|
| hard two-prefix m2 SAT |4185324994|4121308344|
| hard two-prefix m3 SAT |10278626610|9814485296|
| hard two-prefix m4 SAT |22926806712|20844546480|
| two-center unary m4 SAT |4573612800|4302279588|
| family two-root m3 SAT |3009530556|4295700744|

Exact source-accounted clocks, not all end-to-end physical executions. m4 hard logical/worker evidence is new; no m4 end-to-end replay. The ordinary two-root m3 family shows substantial regression. This stage is a verified physical representation change with mixed performance, not a universal speedup.

## Physical original-format evidence
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |14778|5496494|3859413|304893631|16489482|
| full |14777|5494214|3857690|304757514|16482642|

Four-bit segmented alphabet,20 tapes,22-bit quotient IDs. Bounded descriptor increases21065034 bits (~7.42%) over D6I. 21-bit target remains unmet; only 334891 states of margin below 2^22 in bounded quotient.

| fixture/mode | transitions | head | span | result |
|---|---:|---:|---:|---|
| two-prefix prefix-only-pair SAT bounded |2132191546|47692|48525|SAT|
| one-prefix UNSAT full |1001662036|38293|47726|UNSAT|

Original and quotient executions agree on exact transitions, head, span and witness. One-short quotient cutoffs2132191545 and1001662035 return TIMEOUT/no witness. SAT witness1001010101010101011111111110000 matches exact reference and worker2094931574 matches source accounting. UNSAT blank halt at head38293. Verified in separate calls. D6J dedicated Proctor registers25 jobs (audit,22 physical,2 native); final completion unconfirmed. Inherited hard-m3 fixture physical replay is registered; no m4 physical runtime claim.

## Next D6K
Investigate a prefix-independent original local-mask cache plus lazy conditioned cursor or non-destructive indexed slice reuse. Compare materialization vs repeated validation cost before selecting the sliced path. Reduce finite-control duplication, preserve checkpoint exactness and alias scope identity, and quantify descriptor tradeoff. No main or PR #248 changes; no promotion.
