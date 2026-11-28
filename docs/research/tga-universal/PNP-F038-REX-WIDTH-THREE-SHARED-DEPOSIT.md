# F038-REX-024D6W — Shared ordinary deposition and covered-only batch admission

Parent D6V 3e0bee014b7defb2831a525d613e70cdf660588d. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6V exact-head Proctor 46084264664](https://github.com/tltmgnt/MathOS/actions/runs/46084264664): 29/29 jobs passed, including native and both hard m4 SAT physical jobs.

## Implemented refinements
Retain D6V storage arrangement, four-row all-zero batch, compact stream loader, logical IR and D6T worker. Ordinary scope deposits previously duplicated return scans, one/two-trit carry states and selector consume continuations for each scope. The new scopeConsume roots are keyed only by selector width and bit. Return scans share final continuation and separator index; single/double carry graphs share continuation, remaining separator count and carry trit(s). Scope-specific entry and fold probes remain. Pins retain their inverted selector mapping. No new tapes or alphabet symbols. The second refinement first classifies the triple scope. Only strictly increasing X-group triples enter the C+3<=M rank fit scan, then reclassify to the corresponding ordinary or batch root. Noncovered triples retain their original D6U paths. Fit comparison and batch implementation are unchanged. For covered triples reclassification incurs extra work; m<4 still has no successful batch. No broader mixed-row batching or storage relocation implemented.

## Exhaustive local transition relation
The independently compiled D6V and D6W emitted ternary tables are compared without running a particular input. Seed pairs at all130 ordinary scope/pin roots (flag0). Traverse all three possible read symbols at each paired control state. Require identical write and motion fields, recursively pair successor states, and require the mapping from old state to new state to be functional. At exits require identical named continuation, including six selector shift roots, two pin shift roots, clean0 and BROKEN. The check covers147660 predecessor states mapping to24456 new states,442980 transition rows,10 exits. This establishes a finite control homomorphism on this ordinary-deposit region: for any starting tape and head at a paired root, induction on physical transitions gives identical tape writes, movements and matching control boundaries until a matched exit; infinite local paths also stay related. It is stronger than finite fixture replay for this region, but stops at exits and is not a proof of whole-program normalization or worker correctness. Only the ordinary region and flag0 are certified. No claim of malformed-layout equivalence of the entire D6W machine.

Independent constructive packed-mask boundary audit: all130 roots, both selector bits, all four zero-tail lengths and three older suffix patterns. 3120 tests (24 pins,216 unary,2880 packed;360 folds). Both tables agree with independently constructed complete buffers, exact continuation, head and clock; 2277520 transitions per machine. Initial auditor expected entry at old delimiter, but both shift continuations actually begin one cell right with consumed selector replaced by blank; fixed expected head/buffer before commitment. The separate D6V batch boundary checker rerun on D6W gives8618 checks (2234 fit,1008 successful tails,2688 failed-one,2688 truncated),1257272 physical transitions. Genuine corpus of12 m2 cases preserves all130 masks, bound, erased workspace and canonical stream; three malformed inputs retain tested refusal classification/head symbol, not exact clock.

## Adaptive admission proof
The new preliminary scope classifier uses the same group tuple test as D6V. For covered triples the old fit test is performed on unchanged workspace and original delimiter; reclassification chooses the same scope. For other triples, D6V's fit result did not alter their classification, so skip it. Thus no selector or mask changes, no skipped mandatory validation, and identical logical row advancement. Together with the ordinary-region relation and inherited batch invariant this proves source-level preservation of canonical streams on genuine normalized inputs. On hard m4:48455 triple classifications,1437 fit scans,47018 avoided fit scans;1344 lookahead attempts,1313 successes, same5252 batched rows and3939 eliminated shuttles as D6V. Producer396058219 vs398972932. On mixed m5 producer2310979655 vs2317092626, raw893465, canonical stream450, head60, span902186. Mixed m5 producer only; no full m5 solver replay. Combined profile exceeded execution limit; separated checks succeeded.

## Resources
| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6V bounded |1040079|869269|63456641|3120237|
| D6W bounded |917145|869349|63462481|2751435|
| D6V full |1039768|868958|63433938|3119304|
| D6W full |916834|869038|63439778|2750502|

Producer312449 ->189515, original states -122934, bounded original 20-bit headroom131430 including reserved halt. Final quotient +80 and descriptor +5840: most duplication was already removed by quotient minimization. Do not describe this as final descriptor compression. No new codec, no compiler wall-clock/RAM measurements.

## Actual end-to-end original/quotient/cutoff
| fixture | D6V halt | D6W halt | head | span | worker |
|---|---:|---:|---:|---:|---:|
| bounded one-prefix SAT |94744163|94563720|9217|38703|72356196|
| full one-prefix UNSAT |69551891|69371448|388|38704|47714773|
| bounded hard m4 SAT |764812015|761897302|13796|433440|360391458|

All three original and quotient executions agree on halt, head, span, head/next symbol and exact reference witness. One-short cutoffs94563719,69371447,761897301 TIMEOUT/no witness. SAT witness0101010101010101011111111110000; hard m4 witness000100011000100010001000100010001000001001111111111111111111111000000. UNSAT headSymbol2,nextSymbol1. Worker accountant matches all three. Hard m4 phases producer396058219, bridge3662827, worker360391458, output1784798. Aggregate small m2 producer250745742 ->248580426,12/12 improve vs D6V, each180443 saved. Still57792 extra per fixture vs D6U (aggregate247886922); 0.28% residual aggregate regression. Dedicated Proctor29 jobs configured with new relation and boundary auditors, inherited worker/graph audits rerun; completion unconfirmed. Main and PR #248 not modified.

## Complexity and unresolved representation barrier
The fixed-nine explicit normalized representation is already polynomial-time decidable by enumerating m^9 assignments and evaluating the explicit masks. For genuine raw length L>=4096m^3, m^9 <= (L/4096)^3, and even a full O(L) input verification per assignment is polynomial. Therefore a polynomial-time decision-preserving reduction from unrestricted SAT to this particular family would already imply P=NP independently of the recent physical compiler optimizations. This is a conditional implication, not an impossibility proof or a reduction construction. D6W changes physical constants and control representation, not that barrier. The inherited O(L^2(p+1+V)) conditional physical envelope and admitted exponent2+(h+b)/3 are unchanged. No unrestricted SAT reduction, universal cubic guarantee or proof of P vs NP.

## Next D6X
Investigate adaptive shorter batches for m2/m3, or a storage schedule eliminating remaining long prefix shuttles. Prioritize a formal representation/reduction obligation inventory and extend local table certificates to other macros; distinguish engineering evidence from closure of global complexity obligations. No promotion.
