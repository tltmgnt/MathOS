# F038-REX-024D5C — Native domain-three replay and explicit worker space envelope

Parent 1257cba6792f959dd6c1c085759429b4a172bb30. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Exact native verification

[Proctor run 45930176139](https://github.com/tltmgnt/MathOS/actions/runs/45930176139), job 140280735685, concluded SUCCESS. The corrected forced-domain-three run decoded the actual 928445994-bit quotient descriptor (10922894 states, 32768682 rules) and completed on the original raw selector in the independent C++ interpreter. Its exact budget and one-step-short cutoff both passed. Actual native clock 72540199790, physical halt head 229473, span 232294, 50-bit witness 00101010000110001000101010001111101111101111110100 followed by blank. The original Python clause verifier accepted it. All four domain-two native fixtures, malformed codec controls, exact clock model regressions and governance gates passed. Total five principal native executions 75356392463 physical transitions, excluding repeated cutoffs. This confirms the previous exact phase prediction, not an execution of the large description by the original Python tape_run itself. The observed sufficient quotient stage for m3 is 928446031, min coefficient 51580336, cubic stage 54. This is not the first successful universal stage.

## Faster independent exact accounting

The previous clock auditor builds a complete suffix-symbol array whenever a segment grows. Replace that observer operation with a maintained count of unequal adjacent *unmarked* symbols per virtual tape. A write changes at most two adjacent contributions. A growth adds one adjacent contribution. The head-marked symbol differs from either unmarked neighbor regardless of its underlying symbol; therefore add one correction for each neighboring equal underlying symbol at the head. Each later segment has two separator crossings, always unequal, and its interior adjacency count is its length minus one. For a suffix beginning with the current separator, sum these counts over the later tapes. The number of equal and unequal comparisons exactly determines the old carry charge, w=5 or 3w-2=13. Terminal unmarked counts are independently recomputed. All other clock and terminal-encoding calculations are unchanged. Suffix accounting is now O(fixed tape count) rather than O(allocated suffix length) per growth. This is only a faster audit; physical transitions and descriptor are unchanged.

Four genuine D2C fixtures completed both clock models with exact equality of every reported clock component, primitive count, growth, terminal word/head, and complete allocated encoded tape. All 61 allocated tape lengths satisfy the new bound.

## Explicit uniform worker storage

For m>=2 let b=ceil(log2 m), B=9m+36m^2+84m^3, S=2(b+m+B+131), R=4(b+1)m^4, K=(14b+17)m^4. The input canonical stream has S symbols: one bound field, one pin field, 129 mask fields; each data bit and field terminator uses two bits. R bounds any raw relation: at most m^4 rows, at most four b-bit fields plus delimiters. Each projected keyed record contains at most 3(b+1) two-bit tokens in its key and 4(b+1) in its payload, plus colon, semicolon and at most one run delimiter. Thus K bounds every keyed stream, including all alternating-run copies, support, and join output. The support is no larger than its child stream, and filtering never increases parent row count. Each individual sort workspace contains at most one complete relation's worth of records even when runs split. Clearing reuses allocated cells and does not accumulate another copy on that tape.

The executable BigInt envelope lists all 61 capacities in physical tape-index order: bound b, arity 4, projections 28, seven masks each <=m^3, four rank/metadata scratch words each <=max(27,b), three domain/dispatch words each <=max(7,m), output R, flag 1, header 851, stream S, ordinal 9, nine retained relations each R, metadata 180, bag bitmap table 81, owner 4, seven merge tapes each K, two separator masks each 4, retained output R, decision 1, nine chosen ranks each b, dispatcher 9, rank scratch and counter each b, witness 19m-7, Y word 9(m-1), two flags each 1. The router writes 27 bits to its reused metadata scratch, and the forest replaces it with a 20-bit record. All fixed-address walks stay in these word capacities or on their terminal blank. All sequential appends advance to one trailing blank. Counter increments stop at the domain bound. Mask cursors reset within their streams and may finish on the terminal blank. No legitimate operation allocates beyond the maximum of the previous word capacity and the new word plus one spare blank. Therefore, with c_i the stated capacities, N<=1+3*61+sum c_i (one L, one spare blank and one segment separator per tape, plus G). The physical worker span is at most 5N. This is a conservative source-level storage argument on genuine input, not a mechanized certificate. It excludes the preserved producer region and final output.

| Fixture | Exact virtual primitives | Allocated N | Explicit N envelope | Worker clock |
|---|---:|---:|---:|---:|
| empty m2 |53728|3446|8415|672161844|
| edge SAT m2 |63657|3635|8415|1144561610|
| edge UNSAT m2 |50105|3441|8415|512737138|
| forced m3 |589937|12252|43489|71101906698|
| forced m4 |1182966|25391|128741|292006191202|

Combine the envelope with D5B's (26N+16)T+8 to obtain an explicit physical worker bound in terms of virtual T and m. The uniform explicit T(m) coefficient and producer constants are still open; do not infer a numerical finite cubic threshold.

## New domain-four phase evidence

Actual original-selector C1 producer completed at 1526876345 transitions, span 435720, L=428744, n=69. Direct full D2C loader attempt exceeded the interactive execution limit. Instead take the actual C1 header and 129 physical mask blocks, and format the D2C canonical stream in the observer (not a physical transfer). All 129 mask words and the four pin bits independently agree with the original factor oracle, 131 fields and 5994 data bits, 12250 encoded stream bits. Enumerate all 4^9=262144 latent assignments; exactly one satisfies the input. The fast exact IR clock model yields 1182966 virtual primitives, 12106 allocated-block growths, 20506477 equal and 5534148 unequal carry comparisons, worker clock 292006191202 and its fixture-specific upper bound 780972859820. Initial N=13285, final N=25391; each of the 61 tape capacities is checked. The separately executed actual physical output projector consumes the reconstructed 126955-bit terminal encoding in 182917 transitions and emits the correct 69-bit witness:
`000100100100100000010010010010000001001011111111001011111111001101000`.
The original clause verifier accepts it. This is a C1 physical run, host-formatting step, finite-IR clock accounting and isolated physical projection; NOT a completed D2C bridge or a full domain-four raw-selector native replay. No observed disagreement in completed tests. The new CI also includes a separate direct D2C/bridge domain-four check and logs a predicted complete clock if that check passes; this new direct suite was not completed in the interactive environment. No full native m4 budget or measured m4 slot claimed. The built-in is not guaranteed at cubic stage 57 by its exhaustive bound (needs 72); other descriptions may succeed.

Next 024D5D: confirm the direct m4 phase result in CI, measure actual native m4 if practical, and derive the virtual time envelope by auditing the router, odometer, merge and selection loops. Main and PR #248 unchanged. Global routes 0/4, Omega obligations 0/6.

Reproduce:
```sh
for case in empty edge-SAT edge-UNSAT m3-forced; do
  node mathos/research/f038_rex_width_three_resource_audit.js "$case"
done
node mathos/research/f038_rex_width_three_domain_four.js
node mathos/research/f038_rex_width_three_domain_four.js direct
```
