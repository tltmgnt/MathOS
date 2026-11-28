# F038-REX-024D6X — Adaptive two/four-row zero batching

Parent D6W 0b5ce906d6c3711c3e735ef481073e89dc35156b. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6W exact-head Proctor 46086277864](https://github.com/tltmgnt/MathOS/actions/runs/46086277864):29/29 jobs succeeded, confirmed after initial observation of28/29.

## Mechanism and proof
Retain D6W ordinary shared deposits, covered-triple classification, compact loader, D6V four-row batching and D6T worker. On a covered triple first test C+3<=M. If false, test C+1<=M with the same finite LSB-first carry/comparison mechanism initialized to1 rather than3. If true, reclassify to the scope's two-row lookahead; otherwise ordinary processing. A two-row lookahead checks all16 raw bits before mutation. Failure at any one or premature blank restores delimiter/head without writes and falls back to ordinary processing. Four-row failed lookaheads still use ordinary fallback; no three-row or mixed-bit batch implemented.

For z=0,1,2,3 ungrouped leading zeros in the reverse-order packed block 0^z R, two greedy ordinary zero deposits yield respectively 00R,000R,101R,0101R. Thus new leading word lengths are2,3,3,4 and insertion length is2,2,1,1. The short deposit rewrites exactly the original z leading zero cells, in reverse order, to the last z digits of the new word. It queues the remaining one or two digits in reverse order. Shared finite ternary FIFO states keyed by remaining separator count and queue carry the prefix through the farther-left mask region; when all original delimiters crossed, flush into fresh blanks. This preserves all older mask bits, intervening separators and other blocks by the same emit-oldest/enqueue-scanned invariant as D6V. Return across all130 separators; consume both validated selector words using inherited workspace shifts, increment C once then advance3. Fit ensures no rank carry between the two rows. All mandatory selector bits checked and consumed. By induction over validated rows, packed masks and canonical stream match D6W on genuine inputs. Failed lookaheads mutate nothing. This is a source-level proof, not a complete mechanically checked whole-program proof.

## Verification
Independent boundary audit executes actual ternary rows:2234 joint fit decisions,1008 four-row tails,2688 failed-one and2688 truncated four-row probes,1008 two-row tails using independently repeated greedy updates,1344 failed-one and1344 truncated two-row probes. Total12314 checks,2146768 executed transitions. All84 triple scopes covered. Inherited exhaustive ordinary-deposit relation rerun against D6V:130 roots,147660 predecessor states mapped to24456 shared states,442980 checked rows,10 exits, identical write/move/exit. All3120 ordinary boundary cases also rerun,2277520 transitions per machine. Twelve genuine m2 compact-checkpoint fixtures match exact canonical streams and preserve masks and bounds; all12 improve vs D6W. Three tested malformed inputs match refusal classification/head symbol (not exact clocks). No global malformed equivalence claim. A combined verification call timed out; separated ordinary audits and physical replays completed.

## Executed producer profiles
| fixture | D6W producer | D6X producer | four successes/attempts | two successes/attempts |
|---|---:|---:|---:|---:|
| one-prefix m2 SAT |20752935|11592550|0/0|335/336|
| hard m3 SAT |247237621|168769386|0/0|745/771|
| hard m4 SAT |396058219|393225105|1313/1344|25/50|

Aggregate12 m2:248580426 ->139457781,12 improve,0 regressions. Also beats D6U aggregate247886922. No universal runtime dominance; fit overhead and failed probes can hurt on other distributions. Mixed m5 D6X not replayed. The selected m3 result is producer-only, not a new end-to-end physical result.

## Physical resource measurements
| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6W bounded |917145|869349|63462481|2751435|
| D6X bounded |933732|883821|64518937|2801196|
| D6W full |916834|869038|63439778|2750502|
| D6X full |933421|883510|64496234|2800263|

Producer states189515 ->206102. Original bounded +16587, quotient +14472, bits +1056456. Both original and quotient retain20-bit capacity including terminal ID; original bounded margin114843. No codec change or compiler wall-clock/RAM measurements.

## Actual end-to-end physical replay
| fixture | D6W halt | D6X halt | head | span | unchanged worker |
|---|---:|---:|---:|---:|---:|
| bounded one-prefix SAT |94563720|85403335|9217|38703|72356196|
| full one-prefix UNSAT |69371448|60223260|388|38704|47714773|
| bounded hard m4 SAT |761897302|759064188|13796|433440|360391458|

Original/quotient agree on exact halt count, head, span, head and next symbols, exact reference witness. One-short cutoffs85403334,60223259,759064187 TIMEOUT/no witness. SAT witness0101010101010101011111111110000; hard m4 witness000100011000100010001000100010001000001001111111111111111111111000000. UNSAT headSymbol2,nextSymbol1. Worker accountants agree. Hard m4 producer393225105, bridge3662827, worker360391458, output1784798. Dedicated Proctor29 jobs configured, completion unconfirmed. Main and PR #248 not modified.

## Representation obligations and next research
The current fixed-nine explicit family is polynomial by enumeration m^9 <= (L/4096)^3 and polynomial verification. Any polynomial-time decision-preserving reduction from unrestricted SAT to this family would already imply P=NP. Batching does not supply such a reduction. For a variable-coordinate generalization, the number k of groups must be part of input; explicit ternary masks can be polynomial in k and m but exhaustive m^k no longer polynomial for unrestricted k. A scalable physical construction would need a uniform representation, compiler/descriptor resource bounds, correctness for arbitrary k, a polynomial reduction with witness correspondence, and a polynomial physical time bound without fixed-k constants. None of these global obligations is closed by D6X. Inherited conditional O(L^2(p+1+V)) and admitted exponent2+(h+b)/3 unchanged. Next D6Y: investigate three-row/mixed-row batch profitability vs control costs, or prioritize an explicit variable-coordinate representation/reduction ledger and resource barrier. No promotion.
