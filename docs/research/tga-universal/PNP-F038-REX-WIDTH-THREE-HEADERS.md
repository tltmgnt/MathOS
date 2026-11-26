# F038-REX-024D2A — Standalone physical header suffix reader and separator routing

Parent c96073066d608684546b93275c265cd3dee7c38e. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Previous exact-head [D1B Proctor run 45906789577](https://github.com/tltmgnt/MathOS/actions/runs/45906789577) passed.

## Implemented boundary

The finite instruction program consumes the actual right-of-halt suffix of the C1 physical checkpoint: H marks the original halt separator, each 84-bit frame ends in a blank represented by data symbol b. The host copies this contiguous suffix from the observed tape (including any visited trailing blanks) and initializes the generic D1A segmented tape encoding. It does not decode any header or supply a graph, order, scope IDs or coordinate masks to the program. This is a narrower, explicit suffix handoff, NOT a physical checkpoint bridge or full checkpoint parser: the left workspace, selector, masks and pins are not transferred to this program. The input precondition is a genuine C1 checkpoint, not an arbitrary authenticated certificate. It checks some frame grammar, but does not verify DFS correctness, frame count, owner uniqueness, header consistency or absence of trailing data on arbitrary counterfeit suffixes. Structural refusal rejects on the first frame status without emitting accepted metadata.

Nine fixed virtual tapes: I input, H normalized headers, B bag/scope bitmap scratch, S separator bitmap, T owner-indexed bag table, W temporary record, R route output, F scope IDs, Z seven-symbol slot dispatcher. The same finite program is independent of domain size and graph. All reads/writes/moves are actual microprogram instructions. No host runtime header decoding or command sequence.

## Physical outputs

Each accepted bag emits a 45-bit record on H: owner ID (4 bits), three ordered neighbor IDs (12), parent owner ID (4), seven ownership flags, nine group-membership bits and nine separator-membership bits. The nine records retain the elimination order. The terminal empty frame is not emitted. Read each owner/neighbor nibble in finite control and set the appropriate bit of B/S using a bounded walk. Sentinel 9 denotes absent neighbor. The program writes each bag bitmap into the owner-indexed 81-bit T table (9 bits per owner). This avoids retaining input-dependent graph data in the host controller.

Second pass copies each header to W, reads its owner and parent, then scans the child bitmap and separator bitmap together in ascending group-ID order. Emit one separator-membership bit for each present bag variable. Resolve the parent owner by walking to its entry in T, copy the parent's bitmap to B, repeat the same scan using the unchanged child separator S. R contains records owner(4), parent(4), child coordinate mask, colon, parent coordinate mask, semicolon. Root parent 9 gives an empty parent mask and all-zero child mask. Nonroot masks are precisely the common sorted separator coordinates required by D1B. Parent is still represented as owner ID; a future relation controller can use owner-indexed relation tapes rather than converting to an elimination index.

For each of seven slot flags on W, absent slots emit eight ones (255). Present slots create a nine-bit canonical scope bitmap by setting the owner and the slot's specified neighbor positions. A fixed finite decision tree maps that bitmap to the C1 zero-based mask index (arity 1,2,3, lexicographic group order). IDs range 0..128. A physical seven-symbol dispatch tape Z lets all seven slots share the same decoder and advances after each emitted ID. F contains exactly 9*7*8=504 bits on legitimate accepted input. This is actual canonical scope-ID resolution, not merely a list of potential factors. A present scope may still have an all-zero mask. The fixed lookup in the generated transition table is bounded finite control, not a host indexed lookup of variable-size data.

Correctness for genuine C1 output follows from its verified header invariant: every factor is owned at its earliest eliminated variable; every later neighbor of a bag is included in the parent bag. Setting bitmaps by ID and scanning in ID order yields exact sorted coordinate masks. The scope bitmap contains exactly the indicated slot's variables; the decoder uses the same canonical scope order as C1. The independently decoded original clauses are used only in the oracle, not in computation.

## Compilation and executed evidence

| Metric | Value |
|---|---:|
| Generated IR instructions |11234|
| Graph-reachable non-jump instructions |10870|
| Compact instructions |4912|
| Refinement rounds |178|
| Instruction homomorphism checks |10870|
| Logical state definitions |94071|
| Ternary nonhalt states |10028156|
| Packed physical transition entries |30084468|
| Implied original-format description bits |852393264|

The exact D1B instruction compactor preserves charged virtual instructions, including their operation, tape index, symbol or movement direction and successor classes. The unchanged D1A compiler expands the compact IR to the actual ternary transition table, which is executed using packed transitions. The initial design duplicated the scope-ID decoder seven times and had 13150 compact instructions; sharing it through Z reduced this to 4912 after output-head initialization was corrected. The first full empty-frame smoke replay hit a 500-million cutoff, then completed at 672898103 transitions. This is a measured cost, not a complexity failure. The descriptor remains exceptionally large. Its bit length is calculated from the generated table; the full 852393264-bit original encoding was NOT serialized or independently decoded in this mission. Native Python original-codec verification remains open.

The producer was executed on seven actual original selectors. For each, compare original and compact IR at exact primitive clocks and all terminal tapes and heads on accepted runs; compare all output header, owner table, route and scope streams against an independent oracle using C1 frames and original selected factors. Three of these cases also execute the actual generated ternary table, matching all accepted terminal virtual tapes and heads, and refusal status. Four additional cases execute finite IR only. Refused terminal virtual tapes are not compared because reject erases the global sentinel; refusal means no accepted metadata, not UNSAT.

| Fixture | m | C1 transitions | Virtual primitives | Ternary transitions | Scope IDs / edges |
|---|---:|---:|---:|---:|---:|
| Greedy trap |2|26957865|31011|1010897771|44/8|
| Empty |2|26776221|20953|672898103|9/0|
| K5 refusal |2|27879500|305|2407717|0/0|
| K4 |2|26798486|23649|not run|19/3|
| Nonconsecutive triples |2|26951334|23938|not run|17/4|
| Greedy trap |3|273187601|31011|not run|44/8|
| Subdivided K5 refusal |2|27895988|305|not run|0/0|

Totals: 436446995 C1 transitions across seven runs, 131172 virtual primitives (independent of physical producer clock), 1686203591 completed ternary header transitions across three runs, 133 present scope IDs and 23 routed edges compared across five accepted metadata cases. Two accepted physical header runs, one physical structural refusal; three additional accepted IR runs and one IR refusal. Four physical cutoff controls (0,1,100,500000000), five malformed suffix IR controls. No observed disagreements. Counts exclude smoke and cutoff reruns; never sum separate producer and worker clocks as a complete raw-selector solver. Current executions used JS V8; exact-head CI unconfirmed. No physical domain-three header replay or full compiled width-three witness in this mission.

## Resources and next stage

For a genuine checkpoint the header suffix, scope index range and every output are bounded by the fixed nine-group structure. The entire header-reader computation therefore has a constant bound in m, but very large constants under segmented head search and suffix expansion. This does not make a full physical bridge free: transferring the left selector/mask workspace of O(L) cells is a separate obligation. Full worker simulation with growing relations must still be charged. D1B's derived O(m^8 log^3 m) bound is for the compiled projected semijoin, not yet the full witness.

Next 024D2B: reduce the excessive finite compiler overhead (shared instruction dispatch or exact transition quotient with memory-bounded storage), then compile physical left-workspace bound and mask loading and cursor-based relation generation. Use the physically generated canonical IDs and route masks, not host-created relation streams. Preserve D1B, C4 and native width-two witness evidence. Physical bridge, original halt-head projection, finite cubic admission, all four global routes and six Omega obligations remain open. Main unchanged.

Reproduce:
```sh
node --max-old-space-size=6144 mathos/research/f038_rex_width_three_headers_audit.js physical
node mathos/research/f038_rex_width_three_headers_audit.js ir
```
