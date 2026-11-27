# F038-REX-024D6V — Validated four-row zero-batch mask deposition

Parent D6U b9617d62444b9f80893f9d3378eab399449b1c10. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6U exact-head Proctor 46081882892](https://github.com/tltmgnt/MathOS/actions/runs/46081882892):29/29 jobs passed, including native verification and both hard m4 SAT physical jobs.

## Measured bottleneck and new mechanism
Actual D6U hard m4 producer profiling: total1445553175, with deposit Work/Prefix left scans1391418296, other deposit states28929205, workspace shifts760250, selector batch4773482, coordinate11941671, header542, load1275135, compact6430553, other24041. Left prefix traversal alone is the dominant cost. Preserve D6U layout and compact loader; reduce the number of deposits instead of changing storage arrangement.

At class3, independently compare C+3<=M (last rank plus3 <= m-1). LSB-first add uses finite carry initialized3 and three-valued comparison determined by the last unequal digit; overflow refuses batch admission. Only strictly increasing X-group triples are eligible. A read-only lookahead checks all32 selector bits of four consecutive width-three rows. All-zero means four allowed tuples, including every mandatory suffix bit. Fit prevents crossing a coordinate group boundary. Any one or premature blank returns to the original delimiter, with no mutation, and enters ordinary single-row processing. On success use shared three-trit FIFO to insert one canonical four-zero run instead of four separate deposits. Consume the four validated words using existing eight-bit workspace shifts, increment C three times and invoke ordinary advance3 once. Raw prefix stays preserved through validation. All other selectors retain original paths.

## Packed-mask invariant
Packed masks are stored in reverse chronological order: literal0, forbidden11, and four-zero run101 (palindromic codewords). Let z in {0,1,2,3} be the count of ungrouped trailing allowed rows, physically the leading zeros of target block. Its physical content is 0^z R, where R is empty or begins with1. Appending four zeros using predecessor greedy grouping must produce 0^z 101 R, since the number of trailing ungrouped zeros is unchanged. The batch probes z by traversing at most four cells. It rewrites only the old z leading zero cells to the last z digits of 0^z101; the first three digits are queued in reverse order at the left delimiter. The shared FIFO traverses the farther-left suffix, including separators, emitting oldest queued trit and enqueueing the original scanned trit. Count old separators down to zero, then flush remaining3 trits into fresh blanks. This shifts the entire farther-left region by3, preserves all other blocks and yields exactly 0^z101R. Return counts the unchanged130 separators to the raw/workspace regions. No additional tapes, physical alphabet or unbounded host storage. This argument covers arbitrary finite genuine suffixes, not malformed internal layouts. Induction over validated rows proves identical packed masks and canonical stream; inherited normalization, worker and output semantics unchanged. The finite boundary audit is not a complete mechanized proof.

## Phase and resource bounds
Successful batch replaces four deposits with one. It incurs bounded lookahead, three-trit shift, four ordinary workspace batches and rank advancement. For a genuine input with L raw cells and P packed extent, each deposit remains O(L+P+1); batching reduces the number of traversals on zero-heavy runs, not the worst-case exponent (no successful batch is guaranteed). Conditional O(L^2(p+1+V)) envelope and admitted exponent2+(h+b)/3 unchanged. The fixed-nine explicit family is already polynomial by exhaustive enumeration; no unrestricted SAT reduction or universal cubic guarantee. On small domains m<4 the additional fit scan adds overhead. No claim of universal dominance.

## Independent evidence
Boundary audit on actual ternary emitted rows:2234 rank fit checks, including binary widths through128 bits and boundary values;84 triple-scope roots;1008 successful batch checks (all four trailing-zero counts and three older suffix patterns per root);2688 failed-one lookaheads and2688 truncated lookaheads (all32 positions at all84 roots). Total8618 checks,1257272 executed transitions. Full buffers, guard cells, head and continuation state checked. Twelve m2 genuine fixtures independently preserve all130 packed masks across compaction, bound, erased region and exact canonical stream; all match D6U, but each costs238235 extra transitions. Aggregate247886922 ->250745742 (12 regressions). Three tested malformed raw inputs have predecessor refusal classification and head symbol; refusal clocks not asserted equal. Additional mixed m5 producer fixture (5 negative triples) passed exact canonical stream at t2317092626, head60, span902186, stream450, raw893465. No end-to-end m5 worker replay claimed. Inherited D6T macro and boundary checks and D6N logical audit are rerun by dedicated CI, not new physical test counts.

Hard m4 profiling:1344 admitted lookahead attempts,1313 successful batches,5252 rows batched,3939 eliminated deposit shuttles. Total producer398972932, with phase counters deposit-traversal21146248 (left Work/Prefix), deposit-mask883199 (includes old return), batch-traversal342536500 (both Work/Prefix and BackPrefix/BackWork), batch-mask7154967, batch-probe84782, fit3004210, normalization16457338, load1275135, compact6430553. Categories are named-state counters with different grouping from D6U profile; do not subtract categories as identical cost definitions. Total measured reduction1046580243. Unsuccessful initial combined trial exceeded tool execution limit; subsequent separated runs completed.

## Physical resource measurements
| mode | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6U bounded |1015533|846321|61781437|3046599|
| D6V bounded |1040079|869269|63456641|3120237|
| D6U full |1015222|846010|61758734|3045666|
| D6V full |1039768|868958|63433938|3119304|
Producer states287903 ->312449. Bounded adds22948 quotient states and1675204 descriptor bits. Original and quotient still fit20-bit identifiers including reserved halt; original bounded margin8496. No compiler wall-clock or peak-memory measurement.

## Actual original/quotient/cutoff replays
| fixture | D6U halt | D6V halt | head | span | unchanged worker |
|---|---:|---:|---:|---:|---:|
| bounded one-prefix SAT |94505928|94744163|9217|38703|72356196|
| full one-prefix UNSAT |69313656|69551891|388|38704|47714773|
| bounded hard m4 SAT |1811392258|764812015|13796|433440|360391458|
All three agree on original/quotient halt, head, span and exact reference witness; one-short cutoffs94744162,69551890,764812014 TIMEOUT/no witness. SAT witness0101010101010101011111111110000; hard m4 witness000100011000100010001000100010001000001001111111111111111111111000000. UNSAT headSymbol2. Hard m4 phases producer398972932, bridge3662827, worker360391458, output1784798. Small fixtures regress because no batch admission possible. Dedicated Proctor29 jobs configured; full D6V completion unconfirmed. Main and PR #248 not modified.

## Next D6W
Investigate adaptive admission only on covered triples and broader row-pattern batching with shared finite control, or a different storage arrangement avoiding long prefix shuttles. Preserve the near-limit original20-bit capacity or explicitly report a tradeoff. The unrestricted representation/reduction barrier remains the central mathematical obligation. No promotion.
