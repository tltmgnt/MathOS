# F038-REX-024D5Q — Compact normalization blocks and joint packed deposition

Parent edc485c941bc0e25ed255234bff529dd08a7eaa4. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5P closure

Exact-head [Proctor 45955401174](https://github.com/tltmgnt/MathOS/actions/runs/45955401174): all 29 jobs completed successfully, including all four native original-format descriptors, 24 physical replay and quotient/cutoff jobs, independent audit and governance.

## Construction

The width-three planner stopped using the 36 edge-flag blocks in D5I, but the producer's deposit, return, loader and cleanup controllers continued to count them. Remove the unused separators and renumber all 130 live blocks (pin 0, masks 1..129). Remove unreachable DFS/planner source and edge helpers. This preserves raw selector classification, retained prefix, deposited pin and scope bits, and canonical run-coded output. Empty edge flags are not new constraints or hidden assumptions. Only their unused storage/routing is removed. Both compact-batch and compact-packed producers were executed; the joint packed producer then replaces the compact-packed double insertion of 11 with one two-symbol carry pass. Compact-packed remains an intermediate experimental file, not a fifth/sixth descriptor in the registered matrix.

The packed code remains 0/11/101 for zero/one/four zeros. At a forbidden-bit deposit, after writing the first 1 at the old separator, write the second 1 in the next left cell and retain the displaced separator and symbol in finite control. A state Double(j,c,d) stores two outstanding symbols and the remaining count of old separators. Reading symbol a writes c, shifts carry to (d,a), and decrements j if a is blank. Once the farthest old separator is read, flush the remaining two symbols to unused blank cells and return through the same separator count. For the final block (J=0) the second 1 and new blank are written directly. Invariant: the processed suffix equals the original suffix shifted by two cells with two leading ones; the unread suffix is unchanged, and the carry is exactly the two symbols displaced but not yet written. This is a source-level macro invariant, supported by independent actual compiled transition tests. No host-supplied density hint or preprocessing.

The batch-only and joint packed machines are separate static descriptors. Despite cheaper insertion, packed source storage can still expand to twice the literal length. No automatic density classifier/fallback, forbidden-tuple-only sparse store, or retained-prefix elimination is implemented.

## Architecture

| metric | D5P batch bounded | D5Q compact batch bounded | D5P packed bounded | D5Q joint bounded |
|---|---:|---:|---:|---:|
| producer states |313502|240746|370042|285286|
| original physical states |2612634|2539878|2669174|2584418|
| quotient states |1948498|1897774|2004798|1900328|
| descriptor bits |148085852|144230828|152364652|144424932|
| transition checks |7837902|7619634|8007522|7753254|

Full-mode original states 2537598 (compact batch) / 2582138 (joint), quotient states 1896051 / 1898605, descriptor bits 144099880 / 144293984, transition checks 7612794 / 7746414. Intermediate compact-packed producer has 288646 states. Both final producers retain the same D5O 20-tape worker, 4-bit lowering, bridge 279, projector 74 and one blank halt. All four quotients remain below 2^21. Optional compile(true) state names are host diagnostic metadata; no descriptor change.

## Independent actual carry audit

The compiled descriptor is decoded into its actual ternary transition table. Locate DoubleFirst and Return0 by diagnostic names for all 120 higher-arity targets. Start at DoubleFirst just after the first insertion write, with an independently constructed arbitrary binary/blank suffix and known separator count. Verify exact suffix preservation, the two inserted ones, final separator and return head using actual transitions until Return0. Exhaust all ternary words of length 0..8 followed by a separator, the J=0 empty case, and two additional suffix families at each J=1..119. 10080 cases, all 120 target distances, maximum observed 240 transitions; no discrepancies. This tests the local carry path, not arbitrary full producer input or a mechanized global theorem.

Separate producer audit: 8190 short binary words in the existing independent online-code model, 40068 exact arithmetic evaluations across four descriptors, seven normalized fixtures (21 actual producer comparisons), five malformed selectors (15 actual refusals). All streams matched the independent canonical run encoding. Compact batch improved all seven compared with D5P batch; joint improved six and regressed one relative to compact batch. An earlier larger combined audit timed out; the reduced registered audit executed successfully.

| fixture | D5P batch producer | compact batch | joint |
|---|---:|---:|---:|
| empty m2 |33833689|33762697|33551661|
| chain m2 |34763627|34691771|34484571|
| third-rank m3 |309241111|309040159|307377783|
| all-active m2 |59374681|59280361|59344113|
| last-scope-dense m2 |34461259|34389691|34175617|

Joint all-active improves over D5P packed (62048277) and intermediate compact-packed (61945317), but remains 63752 transitions slower than compact batch. Producer state reduction and quotient descriptor reduction are substantial; runtime improvements of the whole machine are modest because the worker dominates. No universal dominance theorem.

## Conditional envelopes

Stream and worker unchanged, so N<=S+35m+1479<=2S, T<=49152S bounded or 49152mS full, W<=(20N+12)T+6. Keep D5P conservative producer allowances P+16L (compact batch), 4P+32L (joint), with P=256L(131L+2176)+2^40. Removed empty blocks shorten fixed separator walks; the joint carry replaces two full traversals by one with two-symbol flush. Do not claim tight new global resource bounds or mechanically verified normalization macro costs. The prior conditional total bounds remain 2^16 L^2 / 2^12 L^(7/3) for compact batch, 2^18 L^2 / 2^14 L^(7/3) for joint. Sufficient cubic admission thresholds 144230844, 216149838, 144424950, 216440997 respectively (batch bounded/full, joint bounded/full). No finite measured cubic admission. Radius-two candidate search remains incomplete.

## Exact whole physical replays

Original raw selectors, pins [0,0]:

| fixture | compact batch | joint |
|---|---:|---:|
| bounded chain |337961312|337754112|
| full all-active |1170911004|1170974756|

Chain: both head 45782, spans 46775/46577, worker 302074888, witness 0101010101101010101111111110000. Original and quotient executions matched, cutoffs 337961311/337754111 TIMEOUT without witness. All-active: both head 51272, spans 52265/52301, worker 1099923738, witness 1010101010101010101111111110000. Actual original physical runs and exact worker accounting passed; quotient/cutoff for full all-active registered in CI, not yet executed interactively. New Proctor registers 24 physical jobs, four independent native jobs and audit/governance. Do not claim current-head CI completion until verified.

Next: genuinely adaptive deposit/forbidden-only storage with dense fallback, investigate shared controller compression and consumed-prefix cost, extend independent local macro auditing to selector relocation and complete deposit/return traversal. Confirm D5Q native and physical matrix. No main or PR #248 edits.
