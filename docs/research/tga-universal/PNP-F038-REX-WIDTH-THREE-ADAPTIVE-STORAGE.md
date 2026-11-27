# F038-REX-024D5R — Adaptive packed-prefix storage and compiled deposit/return auditing

Parent 19746cfe5d92c862243bc36c3ad41bc6eb3f444e. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5Q closure

Exact-head [Proctor 45959102030](https://github.com/tltmgnt/MathOS/actions/runs/45959102030) completed successfully, with the registered 24 physical replays, four native original-format descriptors, compiled carry audit and governance. Other workflows on that head also succeeded.

## Adaptive storage construction

Maintain the original raw selector grammar, rank classification, consumed prefix, unary masks, pin block, canonical run-coded stream and unchanged D5O worker. In each of the 120 higher-arity blocks, a mode marker is placed at the append end. Initialize all markers to zero after header relocation (not before it: an initial experimental version incorrectly positioned markers relative to the moving header separator and physically refused a valid input; corrected and replayed). Before the first forbidden bit, encode leading zeros greedily as 101 for four zeros and 0 for a remaining literal zero. The final marker is 0. On the first forbidden bit, replace the marker with the first 1 of sentinel 11 and use the joint two-cell carry insertion for the second 1 and new marker 1. Thereafter overwrite the marker with the next literal bit and insert a new marker 1; no further double insertion or packed code expansion. A zero in inactive mode folds the three terminal literal zeros in place if available, leaving marker 0 intact. Otherwise perform one single-symbol insertion.

The physical loader reads the left-edge mode marker. Inactive blocks are universal and emit only 10. Active blocks return to the right edge, parse the leading zeros and sentinel, then read the literal suffix, emitting the same canonical 00/01/11 tokens and final delimiter 10 as D5Q. The final marker is not emitted. Short prefix and suffix zero runs are batched; the same four-zero grouping is recovered across the original mask (the first forbidden bit separates prefix and suffix). The implementation uses only actual selector bits and finite control, not a host density prediction. This is monotone switching to literal fallback on first forbidden tuple, not a global optimal density classifier. It does not compress later zero runs in source storage.

For a mask of length n, let z be its leading zero count (z=n if universal), K=floor(z/4). Inactive source length is n-K+1, active length n-K+2. Hence source length <=n+2 (including marker), versus D5Q's possible 2n. Across all 120 higher-arity blocks additive worst-case overhead is at most 240 cells, before separators; not a claim of strictly smaller storage on every input. Literal suffix storage includes all remaining bits. True forbidden-tuple-only storage and retained-prefix elimination are not implemented.

## Independent actual compiled full-deposit audit

Compile with diagnostic state names, decode original physical descriptor, locate all 260 deposit entry/end paths (130 targets times two bit values). Construct synthetic valid local tape layouts with independently encoded target block, other nonempty/empty blocks, workspace and consumed prefix. Run the actual ternary transition table from deposit entry through seek, fold/switch/literal insertion, carry and return to the original workspace head. Compare every cell of the complete layout against independently constructed expected layout, including unchanged prefix, other blocks and unused blanks. Exhaust all bit words lengths 0..4 for every target/bit, plus lengths 5..8 at higher-arity targets 10,69,129. Results: 10940 executions, 123 folds, 612 switches, 10205 remaining literal/ordinary deposit paths, maximum 837 transitions, maximum observed ratio to initial layout length 2.0231958762886597. All passed. This extends D5Q's carry-only test to complete deposit/return, not arbitrary complete normalization input or a mechanically checked all-input theorem.

For a valid finite layout, seek travels left at most the total layout length, insertion carry continues left until the last separator (plus at most two flush cells) and return walks right to the original head. Local fold/mode probes add only a fixed bounded detour; hence a full deposit has linear cost in layout span by the source-level invariant, not merely the observed maximum. Header validation, classifier arithmetic, batched selector relocation and complete global producer macro ceilings remain inherited/conditional.

## Architecture and cost tradeoff

| metric | D5Q joint bounded | D5R adaptive bounded | D5R adaptive full |
|---|---:|---:|---:|
| producer states |285286|402251|402251|
| original physical states |2584418|2701383|2699103|
| quotient states |1900328|1958798|1957075|
| descriptor bits |144424932|148868652|148737704|
| transition checks |7753254|8104149|8097309|

Unchanged 20-tape worker and four-bit lowering, bridge 279, projector 74, blank halt 1. Both quotients stay below 2^21. The additional control paths increase descriptor length; adaptive storage is a bounded-expansion result rather than a descriptor compression or runtime dominance result. Keep D5Q compact batch and joint as independent alternatives.

| fixture | D5Q compact batch producer | D5Q joint producer | D5R adaptive producer |
|---|---:|---:|---:|
| empty m2 |33762697|33551661|33747468|
| chain m2 |34691771|34484571|34682214|
| third-rank m3 |309040159|307377783|307966874|
| all-active m2 |59280361|59344113|59596260|
| first-scope all-forbidden m2 |34377739|34180579|34367662|
| last-scope all-forbidden m2 |34389691|34175617|34373194|

Seven canonical raw selectors, 21 actual producer runs; all streams identical to independent canonical encoder. Adaptive improves six of seven over compact batch, regresses one; regresses all seven versus joint. Additional physical comparisons of masks 3,15,85,127 also passed. Five malformed selectors physically refused. Independent codec enumeration of 8191 binary words lengths 0..12 verified exact expansion, marker and length identity, maximum additive overhead 2. No universal runtime dominance claim.

## Conditional resource bounds

Since the canonical worker input is unchanged, N<=S+35m+1479<=2S, T<=49152S bounded or 49152mS full, W<=(20N+12)T+6. Higher-arity mask lengths n>=4; n+2<=2n, so prior conservative doubled source extent and at most two-symbol insertion allowance remains sufficient under inherited assumptions. Keep P'=4P+32L (P=256L(131L+2176)+2^40), including fixed marker initialization and extra scans in slack; no tightened global resource theorem. Conditional total t<=2^18 L^2 bounded and <=2^14 L^(7/3) full. Sufficient cubic thresholds 148868670 and 223106577. 20034 exact arithmetic evaluations passed. No practical finite cubic admission. Full GAC and radius-two repair remain incomplete.

## Exact physical evidence

Original raw selectors, pins [0,0]:

| fixture | D5Q joint | D5R adaptive |
|---|---:|---:|
| bounded chain |337754112|337951755|
| full all-active |1170974756|1171226903|

Bounded chain: producer 34682214, bridge 723079, worker 302074888, projection 471574, head 45782, span 46697, witness 0101010101101010101111111110000. Full all-active: producer 59596260, bridge 10958635, worker 1099923738, projection 748270, head 51272, span 52421, witness 1010101010101010101111111110000. Both original and exact quotient replays matched, original witness validated, worker clocks exact. Both one-short cutoffs (337951754,1171226902) TIMEOUT without witness. New workflow registers twelve physical jobs, two independent native descriptors and audit/governance; no current-head success claim before confirmed.

Next: reduce adaptive decoder/deposit controller state overhead or retain D5Q as preferred performance baseline; investigate genuinely forbidden-only storage (gap counters or direct rank tuples), audit compiled selector relocation and classification paths, verify D5R independent native/physical matrix. No main or PR #248 edits.
