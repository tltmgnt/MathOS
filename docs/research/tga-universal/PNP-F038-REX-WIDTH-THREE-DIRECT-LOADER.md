# F038-REX-024D2C — Direct physical checkpoint mask loading

Parent afc0e8eca4d4033a2709ab3cd4dff51cc0e7584b. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Previous exact-head [D2B Proctor run 45910364516](https://github.com/tltmgnt/MathOS/actions/runs/45910364516) passed.

## Implemented boundary

Instead of running the D2B four-tape loader through the expensive segmented simulator, extend the C1 single-tape producer directly at its successful header-completion transition. The new fixed ternary descriptor starts at the original raw Boolean selector. It constructs the same graph, all 129 masks, exact width-three elimination stack and bag metadata, then physically appends a bound/pin/mask stream. There is no host checkpoint handoff in this computation. The generic D2B compiled loader remains a separate, not fully replayed program.

Let h denote the original blank workspace separator. The successful C1 stack has ten 84-bit frames, each followed by a blank, ending at h+850. Leave all of this and the entire left checkpoint intact. Append a contiguous binary stream beginning at h+851: first the canonical LSB-first binary representation of M=m-1, then m original pin bits, then the 129 scope masks in canonical order. Encode each data bit b as 0b and terminate each field with 10. Token 11 is unused. There are exactly 131 terminated fields. The machine halts at the original blank h, not at the stream. Thus this is not a Boolean witness interface; in particular inherited malformed normalization cleanup still uses a singleton status bit and must not be promoted as an original witness program.

## Charged traversal and restoration

Starting at h, skip the 15 group-suffix cells and access the M lane in each five-bit column from right to left. To copy a bit, temporarily replace that one bit by blank, remember its value in finite control, move right to h, cross ten frame separators, scan the existing output to its first blank, append 0b, and return across ten frame separators to h. Scan left through the workspace to the temporary blank, restore b and advance one cell left to the next column. At the left workspace boundary the bound is complete. Scan the output backwards, erasing trailing 00 pairs (redundant high zero digits), retain the last 01 pair, and append 10. The m>=2 precondition guarantees that this 01 exists.

The left checkpoint has 166 blocks in right-to-left order, after the workspace and selector separators. Block j's right delimiter is the (j+2)nd blank strictly left of h. Blocks 0..35 are empty or singleton edge flags; block 36 is pins; blocks 37..165 are the canonical scope masks. Count each blank separately, including adjacent blanks. Enter the target block from its right delimiter. For each bit, temporarily blank it and remember the bit, cross exactly j+3 original separators to h, append its encoded pair, return to h, cross j+2 separators leftward and scan left to the temporary blank. Restore the bit and advance left. Because the temporary blank is inside the target block, not any of the intervening delimiters, and there is exactly one such marker, this is unambiguous even at the first or last bit. Upon reaching the original left delimiter, return to h, append the field terminator, and enter the next block. No numeric input-sized pointer, uncharged cell access or host data controls this procedure. All shuttles and restoration are actual ternary transitions. Structural refusal never enters the loader; inherited malformed behavior is unchanged.

For a legitimate accepted checkpoint, induction over source bits and then fields proves that the output is precisely the specified stream and all source cells are restored. This is a constructive resource/correctness argument, not mechanized certification of arbitrary forged checkpoint tapes. The descriptor itself starts on the original selector and performs normalization before reaching the loader.

## Executed evidence

577883 nonhalting states, 1733649 entries, 42185463 serialized descriptor bits. Loader entry 363075 is observer-only metadata. The initial source had a duplicate local compiler identifier, corrected before execution.

| Fixture | m | Inherited producer clock | Combined physical clock | Added loader transitions |
|---|---:|---:|---:|---:|
| empty |2|26776221|104551138|77774918|
| four-bag triples |2|26941937|104728446|77786510|
| greedy trap |2|26957865|104759830|77801966|
| unary UNSAT |2|26776221|104551138|77774918|
| satisfiable K5 refusal |2|27879500|27879500|0|
| mixed |3|273559039|1191953378|918394340|

The inherited producer clock includes its final halt step; the new loader entry is exactly one step before that inherited successful halt clock. Combined clock is loader-entry clock plus loader transitions. The refusal clock is unchanged.

Six principal raw-selector runs (five successful streams, one correct structural refusal), 351421 raw selector bits, 1638423430 charged single-tape transitions including 1229532652 loader-phase transitions, 655 terminated output fields, 645 masks, 5955 mask bits and 13254 encoded stream bits. Every complete stream agrees with an independent original-factor oracle. All four domain-two pin patterns, nonconsecutive ternary factors, a greedy backtracking plan and a normalized unary contradiction were covered. Entire preserved checkpoint and exact literal prefix through the final frame delimiter match C1 in every case. Seven cutoff controls include the exact loader-entry boundary and one step before completion. Five malformed controls preserve the inherited exact refusal clocks. The independent sparse interpreter decoded all 1733649 original descriptor fields, replayed the nontrivial four-bag triple fixture in exactly 104728446 transitions, verified the output and preserved selector/blocks and total nonblank accounting. Combined principal plus independent completed physical replay count: 1743151876, excluding smoke, control and separate baseline producer runs. No observed disagreement. All current tests executed in JS V8; native Python decoder and exact-head CI remain unconfirmed.

## Resource audit and next stage

The preserved C1 region is O(L), with L=Theta(m^3). The output has 2*(bit_length(m-1)+m+9m+36m^2+84m^3+131) bits, hence O(L). The source and output remain in O(L) visited span. Every copy or terminator operation performs O(L) movements across original blocks, selector, workspace, fixed frame stack and growing output. There are O(L) such operations. The bound scan and trim are within the same bound. Thus the complete loader stage costs O(L^2) physical transitions and O(L) space; combined with C1's O(L^2) preparation, the measured descriptor is a direct raw-selector-to-mask-stream computation with the same asymptotic upper bound. This does not prove a numerical speedup against the uncompleted generic D2B loader on the same fixture, and does not establish the full worker's subcubic bound.

Next 024D3A: compile charged independent mask-head/tuple expansion from the physically generated bound/pin/mask stream, resolving the actual canonical IDs and bag membership metadata. Design a physical transfer to the retained-relation worker without host snapshots. Preserve the width-two witness and width-three direct-loader evidence. Full domain-four direct-loader replay, complete ternary forest controller, original halt-head Boolean witness, finite cubic admission, all four global routes and six Omega obligations remain open. Main unchanged.

Reproduce:
```sh
for suite in small larger controls; do node mathos/research/f038_rex_width_three_direct_loader_audit.js "$suite"; done
node mathos/research/f038_rex_width_three_direct_loader_replay.js
```
