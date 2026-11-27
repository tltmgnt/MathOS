# F038-REX-024D5U — Integrated physical gap roundtrip and independent decoder budget

Parent 564c59605b9ecdfb320d8417b5084def67970242. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5T closure

Exact-head [Proctor 45995783569](https://github.com/tltmgnt/MathOS/actions/runs/45995783569) passed both jobs: standalone physical gap/header audit and full normalization checkpoint/governance audit.

## Construction and limitations

The original raw selector enters the unchanged D5S FIFO producer. Its canonical run-coded stream crosses the actual physical bridge to an extended worker. The first eleven fields are literal and are scanned without change. Universal higher-arity fields (delimiter alone) bypass the codec. For each active field, expand canonical 00/01/11 tokens into a single temporary literal mask R, adding an independent unary authorization cell B per emitted bit. Splice D5T encoder IR with tape renumbering and finite-control continuation instead of its standalone halt, retaining the actual gamma length header, sparse/literal mode decision and payload C. Clear literal mask and counter/candidate scratch, then invoke the spliced decoder. No host-computed gap list, length, or density decision is used in the original-selector execution.

Before every decoder output write, require and advance one authorization cell on B; the successful exit additionally requires B blank. An oversized coded header cannot authorize excess output; an undersized decoded length cannot produce a successful exit. This enforces the independently counted original field length, not a universal bound on computation from arbitrary malformed headers. Header parsing remains linear in the coded input length; there is no independent wall-clock watchdog. The code's field boundary is the scratch tape's blank; the original stream retains its fixed 10 delimiter. This is field-local framing, not a new persistent external gap-stream format.

First prototype uses 21 tapes, retains original stream S and builds second canonical stream Q. Final in-place prototype reuses Q=S (20 tapes), and reuses six otherwise uninitialized domain tapes as temporary R/C/N/G/K/B before original GAC initialization. After decode, rewind two-cell tokens to the prior delimiter and reconstruct the canonical run token sequence at its original location, checking each symbol before rewriting that same symbol. This catches content/length disagreements without overwriting a subsequent field on genuine canonical producer streams. Clear all scratch before advancing to next field and before original worker entry. Physical allocated high-water extent can remain larger even after clearing. No second complete stream is allocated in the in-place variant.

The final worker still consumes the original canonical run stream; the gap code is temporary and never replaces the deposited mask store. This is genuine original-selector physical integration of the encode/decode roundtrip, not direct forbidden-only deposition, persistent compressed-stream GAC, or a performance optimization over D5S. The input remains intact, and one field's literal and candidate payloads coexist during encoding. D5S is the preferred measured execution baseline.

## Correctness and budget evidence

262 genuine selectors, including all 256 domain-two ternary masks and six named fixtures, in both bounded/full modes. Compare status, witness, entire canonical stream and all 18 non-output worker tape contents to D5S. 524 executions: 518 accepted with independently validated original witnesses, six refusals. All matched. No complete SAT decision claimed; radius-two repair remains incomplete.

Fault-inject the actual spliced decoder by entering at budgetEntry and replacing only the success continuation with halt. Keep the actual decoder instructions and independent budget guards. For every binary mask of length 0..8, test genuine header/payload with exact budget and an extra cell, plus one-cell-short budget for nonempty masks. Four additional physical fault-injection cases include oversized header, short/long authorization and exact budget. 1536 checks (512 successful, 1024 refused), no output longer than its budget. Four of these checks ran the actual compiled ternary machine and checked expected accept/refuse exit; exact output and length checked in the logical IR. This is not a full malformed-selector or arbitrary-memory adversarial proof.

## Measured resource tradeoffs

Alternating pins; exact worker clocks and allocated segmented logical region N from source accounting:

| fixture | D5S clock | copy integration clock | in-place clock | N baseline / copy / in-place |
|---|---:|---:|---:|---:|
| empty m2 |185257932|214604010|200984068|1841 / 2148 / 1841|
| chain m2 |302075206|347745150|332854172|1883 / 2249 / 1912|
| third-rank m3 |295216832|358725870|342430374|1928 / 2351 / 2004|
| all-active m2 |1099924056|1475980162|1427672244|2981 / 4450 / 3015|

In-place reduces allocated region versus copy on all four named successful examples. All 518 accepted in-place worker comparisons regress versus D5S. The roundtrip is deliberately retained as an integration/equivalence checkpoint rather than deployed as the faster path.

## Descriptor accounting

| variant | tapes | bounded quotient states | bounded descriptor bits | full quotient states | full descriptor bits |
|---|---:|---:|---:|---:|---:|
| D5S |20|1901324|144500628|1899601|144369680|
| D5U copy |21|2075057|157704336|2073334|157573388|
| D5U in-place |20|2032023|154433752|2030300|154302804|

All remain below 2^21. In-place has 8469/8468 IR instructions, original states 2802872/2800592, worker states 2514644/2512364, producer 287874, bridge 279, projector 74, blank halt 1, transition checks 8408616/8401776. Four-bit segmented lowering. Copy variant remains experimental and has only bounded chain exact physical replay (381543726, head 47246, span 48041) plus quotient/cutoff, not a registered independent native descriptor.

## Conditional resource accounting

Let S be the inherited dense canonical stream ceiling, L original selector length, m domain size and b=bit_length(m^3+1). Current-field mask length at most m^3. Scratch consists of R<=m^3, C<=m^3+2b, temporary gamma candidate K<=2m^3, unary authorization B<=m^3, two counters N/G<=b each, plus fixed separator/blank slack. Bound their allocated high-water independently even when reused, add to baseline:
 N <= S+35m+1479+5m^3+4b+32 <= 3S.
 The D5T per-field primitive allowance plus parsing, verification, rewind, clear and budget overhead is charged conservatively with 2048(b+1)S additional primitives. This yields T<=S(49152+2048(b+1)) bounded or S(49152m+2048(b+1)) full. The proof is conditional on inherited macro estimates and the source-level field-local cost argument, not mechanized. W<=(20N+12)T+6. Keep producer P'=4P+32L and bridge 128S^2; projector 256S^2 remains sufficient for N<=3S and witness length n+1<=S under inherited projection bound. With b<=H=ceil(log2 L), b+1<=4m, S<=L/16, m^3<=L/4096, the conservative checked totals are t<=2^18(b+1)L^2 bounded and t<=2^18 m L^2 full. Thus bounded O(L^2 log L), full t<=2^14 L^(7/3). Unlike D5S the bounded quadratic constant-only ceiling is not asserted. 20034 exact arithmetic evaluations passed. No new cubic admission threshold or finite practical cubic admission claimed.

## Original raw-selector exact physical execution

Pins [0,0], unchanged D5S producer:

| fixture | D5S | D5U in-place |
|---|---:|---:|
| bounded chain |335773414|366559760|
| full all-active |1168994058|1496750886|

Bounded chain: producer 32503873, bridge 723079, worker 332853926, projection 478882, halt head 45898, span 46693, witness 0101010101101010101111111110000. Full all-active: producer 57363415, bridge 10958635, worker 1427671998, projection 756838, halt head 51408, span 52437, witness 1010101010101010101111111110000. Original and quotient both match exact halt clocks, head/span and valid witness; one-short cutoffs 366559759 and 1496750885 TIMEOUT without witness. Actual worker clock matched source accounting on both. Registered twelve physical jobs, two independent original-format native jobs and audit/governance; no current-head CI success claim before confirmation.

Next D5V: avoid roundtrip on the production path, investigate physically persistent sparse fields and direct tuple-support iteration or true online forbidden-gap deposition; benchmark before choosing the architecture. Continue retained-prefix and all-input macro proof work. No edits to main or PR #248.
