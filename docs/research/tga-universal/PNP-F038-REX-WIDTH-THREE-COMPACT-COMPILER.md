# F038-REX-024D2B — Exact large-descriptor quotient and checkpoint mask-loading IR

Parent 9a610d61bbf62cea9f886282e9e621d225e36727. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D2A Proctor run 45908456169](https://github.com/tltmgnt/MathOS/actions/runs/45908456169) passed.

## Exact clock-preserving physical quotient

Apply the existing 024A typed-array partition refiner to D2A's actual packed physical table. All-symbol reachability includes all 10028156 nonhalting states. Halt is a separate class. Initial classes distinguish each read symbol's write/move output. Refine by successor classes using inverse adjacency and smaller-half splitting. Verify all 30084468 entries against the quotient mapping, including initial and halt mapping. Thus for every physical symbol a, T(s,a)=(t,w,d) implies Q(f(s),a)=(f(t),w,d). Induction preserves every charged transition, tape content, head and halting clock for any input. This is a quotient of the SAME descriptor, not a comparison of distinct programs.

| Metric | D2A | Exact quotient |
|---|---:|---:|
| Nonhalting states |10028156|4446657|
| Physical rules |30084468|13339971|
| Calculated descriptor bits |852393264|364625878|

Removed 5581499 states and 487767386 description bits (57.22328%). The description bit counts follow from the original encoding formula; neither complete descriptor was serialized or independently decoded here. Direct quotient: 27 initial blocks, 4446631 splits, 13339974 processed splitters, 171525532 predecessor visits. Typed-array storage scales linearly in the state count; the original compiler's transient string-key construction and the large quotient arrays remain a practical memory burden. No peak resident-memory measurement or native Python codec run is claimed.

A second, experimental path generalizes the interval refiner to the 24-symbol logical alphabet and quotients before ternary lowering. It checked 2257704 logical transitions; 94071 logical states became 93965, then 10016360 physical states. Full physical refinement of that table also produced 4446657 states, with 30049080 physical homomorphism checks. This prepass eliminates only 106 logical states. The committed rooted isomorphism comparison between the two final quotients is not yet executed; equal counts alone do not establish isomorphism. Prefer the direct physical quotient for current evidence. The alternative is not represented as a significant reduction in compilation peak memory.

Executed direct-quotient empty-header replay uses the 851-symbol preencoded empty-graph suffix (constructed explicitly for this smoke control). The compressed machine completed at exactly 672898103 physical transitions and span 10190, matching the D2A empty graph clock and span; checked the exact nine root route records and 504 scope-output bits. The attempted full three-fixture compressed audit exceeded the interactive tool execution timeout. The full actual-snapshot differential test and rooted isomorphism test are retained as reproducible commands but not counted as completed executions. Only the completed smoke replay is counted here. The full parent table homomorphism proof/check is independent of that replay.

## Left checkpoint loading

The new finite instruction program consumes the entire observed C1 tape snapshot with physical blanks encoded as b and the blank halt-head marker H. It does NOT receive a numerical domain size, parsed mask, pins or host-generated tuple list. Four fixed virtual tapes: I input, M bound, P pins, F mask stream. The input is a legitimate C1 checkpoint (not a general counterfeit checkpoint verifier). Snapshot initialization remains host-mediated. It reads the workspace from right to left, skipping the fixed 15-bit suffix and four lanes of each five-bit column. The remaining lane is copied as LSB-first m-1, trimming redundant high zeros by charged writes. Skip the preserved selector, traverse the 166 original blocks in their physical order, ignore the 36 edge flags, copy pin block 36 and copy all 129 masks, each followed by semicolon. The mask order and each bit's rank-tuple order match C1. Input remains unchanged. The resulting stream is not yet distributed to independent mask tapes; no local tuple generation or complete forest worker is claimed.

The finite IR has 1709 generated instructions, 1535 reachable non-jump instructions and 916 compact instructions after 516 refinement rounds. Exact reachable instruction homomorphism verified. The D1A compiler generated 832012 ternary states and 2496036 entries; direct exact physical refinement generated 377707 states with calculated descriptor length 26439494 bits (from 60736880). This compilation and quotient check executed, but **no complete ternary mask-loader replay** was performed. The two executed mask-loading cases are finite-instruction interpreter runs, with exact original/compact primitive clocks and terminal tapes/heads compared. An independent oracle decoded the original selected clauses and checked every mask bit, original pins and domain bound, also comparing the C1 checkpoint observation.

| Domain | Original C1 transitions | Snapshot symbols | Loader IR primitives | Mask bits |
|---:|---:|---:|---:|---:|
|2|26892421|39769|157620|834|
|3|273369923|165473|664005|2619|

Totals: 300262344 C1 transitions, 821625 virtual primitives, 258 masks and 3453 mask bits. Pin words 10 and 101; LSB-first bounds 1 and 01; emitted mask streams 963 and 2748 symbols including delimiters. No disagreement on these two completed IR runs. Do not add the separate model clocks and call the sum an original-format witness runtime.

The fixed-tape loader uses O(L) virtual steps and O(L) allocated cells for genuine checkpoints; each input cell is scanned a constant number of times, with fixed block count and logarithmic bound width. The unchanged segmented simulator has the conservative O(L^2) physical bound for the loader alone. The constants remain large, because every simulated operation searches and rewinds the physical region. The current physical quotient preserves clocks rather than accelerating execution. These are restricted-stage arguments, not a proof of complete width-three witness complexity.

## Next bounded stage

024D2C: improve charged physical access locality or implement a direct physical left-checkpoint loader, verify actual mask loading in a complete ternary execution, then compile independent mask cursor/tuple production. Preserve header and projected semijoin evidence. Physical snapshot bridge, complete compiled forest worker, original halt-head projection and finite cubic admission remain open. All four global routes and six Omega formal obligations remain open. Main unchanged. Current-head CI unconfirmed at commit.

Reproduce tested stages:
```sh
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_compact_audit.js smoke
node mathos/research/f038_rex_width_three_mask_loader_audit.js
```
Additional longer checks (not yet completed here):
```sh
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_compact_audit.js
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_compact_audit.js compare
```
