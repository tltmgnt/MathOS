# F038-REX-024D5T — Physical forbidden-gap codec prototype and normalization composition

Parent 3f13a2012f1ffef7cdbc19cf015bee98c2fabca9. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5S closure

Exact-head [Proctor 45995060740](https://github.com/tltmgnt/MathOS/actions/runs/45995060740): all fifteen jobs passed, including two independent native original-format descriptors, twelve physical fixture jobs, normalization macro audit, reference gap codec, and governance.

## Standalone finite physical gap codec

D5T implements a genuine separate five-tape logical encoder/decoder (output, length counter, gap counter, candidate scratch, input), lowered by the unchanged four-bit segmented compiler into finite ternary transition tables. There is no host-supplied gap list, rank computation, or mode decision during machine execution. However, the initial segmented input layout is prepared by the test harness. This is not yet an original-selector producer replacement or a new complete solver descriptor. The inherited D5S FIFO producer and GAC worker remain unchanged.

Given a binary mask of length n, let b=ceil(log2(n+2)), and let g_i be the positive distance from the preceding forbidden position (initial position -1). The encoder physically increments two LSB-first binary counters while scanning the mask. On each forbidden bit, emit gamma(g_i) to candidate scratch and reset the gap counter. No trailing zero gap is emitted. At end, increment the length counter, emit gamma(n+1) to output, and compare candidate payload length to the original mask length using aligned physical scans. Select sparse mode 1 when candidate length <=n, otherwise mode 0 and copy original literal mask. Output is gamma(n+1), a mode bit, and payload terminated by a blank. The header charges the length metadata explicitly; the field boundary is one blank cell. No uncharged external mask length is needed by the decoder. A sequence of fields would still require composition/framing.

The decoder physically parses gamma by counting leading zero bits in the counter, writing the high one, and filling lower bits from the input. It decrements the length header to recover n. In literal mode copy exactly n bits and require blank. In sparse mode decode each gap, count down its positive value, emit g_i-1 zeros and one forbidden bit, decrement remaining length for each output position, reject a gap that exceeds the remaining length, and append the final zeros when reaching the input blank. The decoded mask is exact for each genuine encoded field. Truncated headers/gaps, wrong literal length and out-of-range positions reject. It accepts some valid but nonminimal sparse encodings; canonical minimal mode selection is an encoder property, not a decoder restriction.

## Storage and resource accounting for the standalone codec

For G=sum_i(2 floor(log2(g_i))+1), the emitted binary field length is

    B=2 floor(log2(n+1))+2+min(G,n) <= n+2b.

Plus one terminating blank. This is an output payload bound, not a peak working-space bound. The temporary candidate can reach G<=2n (sum of positive gaps <=n and gamma length <=2g), even when literal fallback is chosen; the input remains intact. The counters occupy at most b bits each plus fixed allocated blank/sentinel extent. Both the emitted stream and scratch are contiguous. A conservative logical segmented-region ceiling N<=8(n+1)+32(b+1) includes all five tapes, scratch, metadata, segment boundaries and allocated blank cells on genuine inputs. Each counter increment/decrement/reset/gamma emission or parse takes O(b) logical primitives. At most n position increments/output decrements and n gap emissions/parses are needed, with final linear copy/compare; the conservative T<=512(n+1)(b+1) is a source-level macro allowance, not a machine-checked all-input theorem. The inherited width-four primitive bound yields W<=(20N+12)T+6 = O(n^2 log(n+2)) on genuine fields. No bound is asserted for malformed adversarial headers declaring huge output lengths. The new prototype does not tighten the inherited whole-selector conditional envelopes; a physical online deposition path and decoder integration remain necessary.

## Executed gap evidence

Encoder 180 IR instructions, 31330 compiled states; decoder 232 IR instructions, 35754 compiled states. Both width four. 8223 roundtrip comparisons against independent D5S host payload reference (8191 exhaustive masks length 0..12, 24 seeded density cases, 8 physical replay fixtures including overlaps): 3576 sparse, 4647 literal. All length metadata and primitive envelope checks passed. Twelve malformed coded fields refused at logical IR level. Sixteen actual ternary transition replays (eight encoder, eight decoder) match exact worker clocks and complete terminal encoded tape/head layout, including dense fallback. These are standalone compiled-worker replays, not original-selector native replays.

| mask | n | forbidden | mode | output bits incl header | encode clock | decode clock |
|---|---:|---:|---|---:|---:|---:|
| empty |0|0|sparse|2|6608|3542|
| 00000001 |8|1|sparse|15|115640|90414|
| 11111111 |8|8|sparse tie|16|129788|90764|
| 0010000100000010 |16|3|sparse|23|240558|210284|
| alternating 01 |16|8|literal|26|363282|124166|
| 63 zeros then one |64|1|sparse|27|696508|1774240|

The short mask examples may be larger than the original raw binary mask once metadata is included. The candidate comparison ensures bounded output expansion relative to metadata-bearing literal mode, not absolute compression for every field. Physical clocks include segmented lowering but not external bridge/projector or original normalization. Sparse decoding may be slower than encoding due to emitting all n values. No performance dominance claimed.

## Complete header initialization audit

Execute actual D5S compiled header/setup transitions on every terminated unary header length 0..2463, with a fixed binary suffix. Exactly the 129 accepted lengths n=19m-7, m=2..130 reach class1 at the correct head, with five interleaved register lanes M=m-1, Y=m-2, A=B=C=0, 15 zero group bits, untouched suffix and all blank left extent. The other 2335 lengths refuse. Maximum valid clock 482678, maximum register width eight columns. The tested header bound 128(n+1)(w+1) passed. This does not exhaust unterminated or arbitrary malformed inputs.

## Complete normalization composition audit

Run actual D5S producer transitions from original raw selector through header, classification/advance/deposition and the normalized checkpoint at loadStart, then through loader and halt. Independently inspect all 130 live blocks at checkpoint: exact retained selector prefix, pin block, bound lanes, each decoded mask bit, separator/blank extent. Compare count of classifier and advance visits to binomial(n,1)+binomial(n,2)+binomial(n,3), and deposit count to 10m+36m^2+84m^3. Finally compare loader stream to independent canonical D5O run encoding. Four genuine selectors, 520 blocks, 5121 mask positions and 275593 raw bits checked, no discrepancies.

| fixture | L | header | normalization after header | loader incl halt | total |
|---|---:|---:|---:|---:|---:|
| empty m2 |37914|3094|20059936|11507933|31570963|
| chain m2 |37914|3094|20065135|12435644|32503873|
| all-active m2 |37914|3094|20285296|37075025|57363415|
| third-rank m3 |161851|5196|243880848|54992141|298878185|

Normalization dominates third-rank producer cost; loading dominates the all-active producer. Retained prefix traversal is still present and expensive. This composition audit verifies finite full paths, not a mechanically established global resource theorem. D5S whole solver still has conditional bounded t<=2^18 L^2 and full t<=2^14 L^(7/3). No change to descriptor, admission threshold or incomplete radius-two search. New workflow registers two jobs for physical codec/header and checkpoint/governance; current-head success not claimed until confirmed.

Next: integrate the physical gap codec into actual higher-arity mask loading or online forbidden-position deposition; avoid temporary dense/candidate duplication where possible; specify field framing and refusal/budget rules; measure end-to-end physical witnesses and resource costs before preferring the new codec. Continue retained-prefix and global proof work. No main or PR #248 edits.
