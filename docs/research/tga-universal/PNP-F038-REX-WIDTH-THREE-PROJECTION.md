# F038-REX-024D1B — Standalone ternary tuple projection and joint semijoin

Parent 0f100ea8852c5883a23d7c3327b2fa9bdd822320. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D1A Proctor run 45906263621](https://github.com/tltmgnt/MathOS/actions/runs/45906263621) passed.

## Interface and boundary

The fixed ternary descriptor consumes ten preencoded virtual tapes: parent and child tuple streams P,C; five initially empty work tapes A,B,S,K,O; two coordinate-mask tapes PM,CM; and an initially empty retained tuple output U. Tape count and alphabet are fixed. The parent and child input rows contain 1..4 nonempty binary fields separated by commas and terminated by semicolons. Each mask is a binary string of length 1..4, one bit per tuple field in order. Both masks must select the same number of fields, at most three. The physical finite controller validates these conditions even on empty relations, then checks that every row has the stated arity. Masks are data on tape, not compiler arguments; the same descriptor supports every legal mask pair. Actual group-ID alignment remains a caller precondition. C1 header decoding and mask derivation, full local relation generation, retained forest routing and original witness recovery are not yet compiled. The raw-selector bridge is still missing. Successful halt is at the encoded global sentinel G, not an original witness. Input encoding and output observation remain host initialization/inspection, not physical bridge operations. Only legitimate preencoded tape layouts are supported; malformed stream tests do not certify arbitrary physical bit strings.

## Projection, stable semijoin and output

Start each row at the beginning of its mask tape. Read mask bits one at a time and scan each matching tuple field. Encode a selected field's digits as 00 and 01, then append 10 as field terminator. At the final field check the row delimiter; rewind the row and emit a colon followed by the entire tuple encoded with the same field convention and a semicolon. The initial input stream is replaced by the projected records via charged scratch copy. The field terminator is a distinct two-bit token, so concatenations of variable-width fields cannot collide (e.g. (0,01) and (00,1)). These are bit-string comparisons, not numeric normalization of alternative leading-zero encodings; legitimate rank fields from C4 have a common fixed width.

The D1A stable sort, deduplication and joint-key semijoin are retained. After joining, scan O, skip the key, decode the self-delimiting payload and append the original comma/semicolon tuple to U. U preserves every retained row and the stable order among equal keys, and can serve as the next edge's relation input. PM and CM are not modified. No host tuple projection, key materialization, sorting, support lookup or retained-row decoding occurs during physical execution.

## Finite-control compaction

The generated instruction program includes labels and repeated continuations. Resolve unconditional jumps, restrict to graph-reachable instructions (every symbol branch), then refine instruction classes by operation, static tape index, write symbol or movement direction, and successor classes. Distinguish halt and reject. Iterate until the partition is stable. Verify every reachable instruction's translated operation and successor fields against its compact representative. Induction preserves each charged virtual primitive and virtual configurations; eliminating administrative labels does not remove charged primitives. This is exact instruction-level equivalence, not a global minimum ternary program. Reuse D1A's generic segmented tape compiler unchanged on the compact IR, extending the logical alphabet by a comma and using ten virtual tapes. The block width remains five physical bits.

| Metric | Value |
|---|---:|
| Generated instructions including labels |2963|
| Reachable non-jump instructions |2618|
| Compact instructions |928|
| Refinement rounds |24|
| Homomorphism checks |2618|
| Logical state definitions |12320|
| Physical nonhalting states |1063432|
| Physical transition entries |3190296|
| Original-format descriptor bits |80820836|

The new descriptor is 55.23% smaller than D1A's 180524800-bit keyed-only descriptor despite added functionality. This is a size comparison of different programs, NOT a clock-preserving quotient of the D1A descriptor. The instruction quotient is within D1B. No full uncompressed D1B ternary table was generated.

## Executed evidence

Nine named and 29 seeded principal cases, covering all 29 legal parent masks, with compatible child masks, arity one through four, separator size zero through three, empty relations, duplicates, nonadjacent fields, bit-string collision avoidance and three-coordinate parity obstruction. An independent host projection/sort/set oracle compared the exact sorted inputs, support stream, keyed output and decoded retained tuples. Independent finite-instruction interpreters compared the original and compact IR primitive clocks, all ten terminal tapes and head positions, and the physical replay's terminal virtual configuration. Ten malformed masks/tuple streams and four physical cutoffs including one step short passed. Zero observed disagreement.

| Fixture | Physical transitions |
|---|---:|
| empty |32603|
| empty parent |329555|
| empty child |1233129|
| empty separator |2064611|
| nonadjacent three |53750915|
| stable duplicates |26031235|
| variable-width no collision |8635461|
| joint-three parity |120535241|
| joint-three compatible |172207797|

Named total 384820547 transitions and 87197 virtual primitives. Seeded total 937611521 transitions and 282368 primitives. Independent original-format streaming decoder parsed every one of 80820836 bits and checked all 3190296 transition entries. Sparse interpreter reproduced nonadjacent and collision cases at exact clocks (62386376 additional transitions). Combined principal and independent physical replays: 1384818444 transitions, excluding controls and smoke. Principal virtual primitives: 369565. All current executions in JS V8. Native Python codec and exact-head current workflow unconfirmed. No complete width-three raw-selector-to-ternary witness computation.

## Resource accounting and next stage

For R total records and b maximum encoded record length, projected stream creation, validation and retained decoding add O((R+1)(b+1)) virtual operations and cells. Stable sorting dominates at O((R+1)(b+1)log(R+2)) primitives; total allocated virtual space O((R+1)(b+1)). The unchanged segmented simulation charges O(S+1) transitions per primitive with S allocated virtual cells, including right-end insertion shifts. Hence the derived bound for this compiled subkernel is O((R+1)^2(b+1)^2 log(R+2)), or O(m^8 log^3 m) for R=O(m^4), b=O(log m). This is not an end-to-end width-three raw-selector witness bound. The resource proof for the entire C4 microprogram remains conditional on full compilation, a charged bridge and original output projection. Large finite descriptor overhead remains.

Next 024D2A: compile the C1 checkpoint reader and physical ownership/coordinate-mask derivation into bounded finite instructions. Then compile mask-cursor expansion and retained-relation routing; do not substitute a host-generated command stream. Preserve D1A and C4 evidence. All four global P versus NP routes and six Omega obligations remain open. Main unchanged.

Reproduce:
```sh
for suite in small seeded; do node mathos/research/f038_rex_width_three_projection_audit.js "$suite"; done
node mathos/research/f038_rex_width_three_projection_replay.js
```
