# F038-REX-024D5P — Batched normalization and online packed constraint deposition

Parent d8dfc8af78c4401e9236c6dc689dd24c25f0a8a2 (D5O closure). Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5O closure

Retried the outstanding full all-active quotient cutoff: at 1172606995 transitions TIMEOUT without witness. Registered original-format replay, independent native verifier, exhaustive audit and governance, and documented D5O. Exact-head [Proctor 45953003522](https://github.com/tltmgnt/MathOS/actions/runs/45953003522) completed all fifteen jobs successfully, including both native descriptors and twelve physical replays/cutoffs. This closes the prior verification backlog, not a formal resolution route.

## Batched selector consumption

The original selector grammar, raw bit order, rank classification, pins, mask deposits and final original witness layout remain unchanged. Mandatory selector words (length 2,4,8) and suffixes after an optional/pin first bit (length 1,3,7) can be validated by finite control before moving the workspace. On mismatch the head returns to the original separator and enters inherited malformed cleanup. On success clear the verified raw cells, shift the fixed-column workspace right by k cells in one right-to-left pass, and reconstruct the exact consumed bit word at its former left boundary. The rightmost-first copy is safe because all destinations are to the right of their source, so no unread source is overwritten. The prefix retains its actual selector bits, not a surrogate. Optional first bits still use the original deposition and single-cell shift. The final compressed producer stream is unchanged. This removes repeated whole-workspace sweeps on mandatory suffixes; it does not eliminate the long consumed prefix or all selector-classification costs.

For workspace width w and fixed k>1, the relocation has at most (2k+2)w+O(k) transitions, compared with the prior 4kw+O(k) one-cell shift sequence. The old bitwise path remains for k=1. Source-level cost reasoning is conditional on the inherited layout and resource macros.

## Experimental packed deposition

Keep the batched normalizer and D5O worker. Change only binary/ternary deposition blocks. Source codes (in logical append order, which the physical loader reads from right to left):
- 0: literal zero
- 11: literal one
- 101: four consecutive zeros.

The code is prefix- and suffix-free. A new forbidden bit appends two ones through inherited insertions. A new zero inspects at most the three terminal source cells. If all three are literal zeros, replace those three cells by 101 in place, representing the old three plus the new fourth zero without a suffix shift. Otherwise append a literal zero. Multicell words end in 1, hence the three-zero test cannot straddle a codeword. All-zero detection parses this packed code before eliding universal masks. The loader emits exactly the D5N/D5O canonical run stream: 00/01 for literals, 11 for groups of four zeros, 10 delimiter; short literal batches retain their inherited meaning.

For mask length n, one count a and greedy four-zero group count K, packed source length n+a-K is between 3n/4 (ignoring rounding) and 2n. A zero-only field stores three cells per four zeros rather than four. Dense ones may double storage, and the two-insertion path costs more. This is actual online compression of deposition storage and avoided suffix shifts, not a forbidden-tuple-only sparse index. It still processes every original selector position. No global density-aware fallback is implemented; batch-only and packed producers are separate research descriptors. Keep batch-only as the conservative option.

## Architecture

| metric | D5O bounded | D5P batch bounded | D5P packed bounded |
|---|---:|---:|---:|
| producer states |313507|313502|370042|
| original states |2612639|2612634|2669174|
| quotient states |1948422|1948498|2004798|
| descriptor bits |148080076|148085852|152364652|
| transition checks |7837917|7837902|8007522|

Full-mode original states 2610354 (batch) / 2666894 (packed), quotient states 1946775 / 2003075, descriptor bits 147954904 / 152233704, transition checks 7831062 / 8000682. Both share unchanged read-only 20-tape D5O worker (bounded 2298778 states, full 2296498), four-bit symbol encoding, bridge 279, projector 74, blank halt 1. All four quotients remain below 2^21. Batch-only saves five original producer states but slightly increases the quotient; packed increases descriptor length. No descriptor compression milestone claimed.

## Conditional resource bounds

Unchanged canonical stream and worker give N<=S+35m+1479<=2S and prior T<=49152S bounded, <=49152mS full. Four-bit worker W<=(20N+12)T+6. Batch keeps prior producer allowance P+16L (P=256L(131L+2176)+2^40); the mandatory batch macro scans the workspace once per word instead of repeatedly, with bounded validation/return overhead covered by the inherited macro slack. Packed uses a deliberately looser producer allowance 4P+32L: source block extents at most double, at most two inherited insertions per deposited bit, each traversing at most doubled block extent; fold paths add fixed lookahead/return slack, and the emitted stream never expands beyond the inherited stream bound. The factor-four argument charges the entire prior producer ceiling rather than claiming a tight cost. It is an inherited source-level estimate, not mechanized all-input macro verification.

With I<=128S^2, O<=256S^2 and S<=L/16, batch retains t<=2^16 L^2 bounded, t<=2^12 L^(7/3) full. Packed conservatively t<=2^18 L^2 bounded and t<=2^14 L^(7/3) full, using m<=L^(1/3)/16. Sufficient cubic thresholds: batch 148085868 / 221932374, packed 152364670 / 228350577. 40068 exact arithmetic evaluations across four variants passed. None constitutes practical finite cubic admission. Full GAC and radius-two repair remain incomplete satisfiability search.

## Executed evidence

The independent online-code oracle enumerated all 8190 nonempty binary words of lengths 1..12: exact decode and canonical run encoding, length identity, 2385 fold events, 8056 expanded words, maximum ratio 2. This is a local codec model audit, not exhaustive physical producer replay. Ten genuine raw selectors compared actual D5O, batch and packed producer streams bit-for-bit against the canonical oracle (30 runs). Fourteen malformed selectors refused in all three (42 runs). Batch improved all ten producer clocks; packed improved nine relative to batch and regressed on all-active. All active-mask truth patterns were not physically enumerated.

| fixture | D5O producer | batch producer | packed producer |
|---|---:|---:|---:|
| empty m2 |35435361|33833689|33622653|
| chain m2 |36365299|34763627|34629309|
| third-rank m3 |316167425|309241111|307678971|
| all-active m2 |60976353|59374681|62048277|

Producer span for m3 third-rank 164960 -> 164386 (packed); all-active 40344 -> 40380, demonstrating the density cost. Exact whole original-selector physical replays, pins [0,0]:

| fixture | D5O | batch | packed |
|---|---:|---:|---:|
| bounded chain |339634840|338033168|337898850|
| full all-active |1172606996|1171005324|1173678920|

Both bounded chains: head 45782, span 46811 (batch) /46613 (packed), worker 302074888, valid original witness 0101010101101010101111111110000. Exact quotient and one-short cutoffs passed for both (338033167 and 337898849 TIMEOUT without witness). Full all-active actual physical runs also passed original witness and exact worker clock (1099923738), head 51272, span 52301 / 52337; quotient and cutoff registered but not executed interactively. CI now registers 24 physical jobs, four independent native jobs and audit/governance; no D5P current-head completion claim until confirmed.

Next: implement a truly sparse forbidden-tuple or cost-aware deposit strategy with safe dense fallback; reduce redundant empty blocks and prefix shuttles; evaluate a smaller shared producer controller and independently audit global resource macros. Confirm all four D5P native descriptors and physical matrix. No edits to main or PR #248.
