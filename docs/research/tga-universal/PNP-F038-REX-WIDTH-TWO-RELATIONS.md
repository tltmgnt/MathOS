# F038-REX-023C2 — Physical variable-arity bag relation serialization

Parent 1e57e7e37a9d55e672b237a1b9fe44682c5fda15 (REX-023C1). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

The previous exact-head Proctor run [45896029859](https://github.com/tltmgnt/MathOS/actions/runs/45896029859) is confirmed successful, including its native original-codec regression. C2 now physically generates the actual variable-arity bag row sections from the original raw selector in one fixed ternary descriptor. It preserves the complete C1 factor-forest checkpoint, all 129 masks, pins, graph flags and original selector. This is a general width-two relation producer for the normalized nine-group family, not yet a composed general solver or Boolean witness machine.

## Interface and grammar

544469 nonhalt states, 1633407 transition entries, 39746241 descriptor bits. The compiler extends C1 with 122827 nonhalt states. The physical machine starts on the raw input at head zero; no host graph, scope, row, rank, parent or runtime index is provided. The simulator decodes the table and executes individual transitions. On success its head is the original blank workspace separator. The contiguous word to its right comprises:

* The original C1 190-bit forest word (36 residual edge bits, 9 active flags, nine 12-bit elimination records, status bit 1, nine 4-bit parent indices).
* Twelve zero scratch bits (four bag-index and eight continuation-code bits, cleared at exit).
* Nine relation sections in elimination order. Each begins 11111 and ends 110, including empty relations. Between these are zero or more permitted rows: 011, followed by r rank fields (each consists of w=ceil(log2 m) digits b encoded 00b followed by 010), followed by 101. r is the number of non-sentinel IDs in the corresponding elimination record. No nested closing tokens. The parent index and separator are given by the physical forest header; the separator consists of the later-neighbor fields, and parent 9 denotes an independent root.

Rows are lexicographic in **increasing original group ID order**, NOT the unsorted (eliminated vertex, neighbors) order of the record. This explicit design choice aligns projected rank order with C1's masks; the owner is still the first field of the original elimination record. The future worker must interpret this grammar, sort coordinate IDs for comparisons, and handle zero/one/two-variable separators. This is not the old REX-020 nested grammar.

Normalized structural refusal retains the C1 partial plan with status 0 and has no relation sections. Malformed input retains inherited single-zero cleanup. The successful checkpoint label RELATIONS_PREPARED is observational, not a SAT decision.

## Physical serialization invariant

At the start of each bag, read its original twelve-bit record via fixed addressed walks (the bag index is physically stored in the word). Decode the three IDs in finite control, sort the present IDs, mark the eliminated vertex by adding 16 to its group word, pad absent coordinates with sentinel 9, and write the three five-bit words into the inherited group suffix. A physical binary odometer uses the r active rank lanes, initially zero. For each subset of the present coordinate positions, the shared finite-control group-word dispatcher maps the subset to its original lexicographic scope-mask ID if it contains the owner; other subsets return a zero query or a no-op rotation. No mask is copied from the host. This implements exactly-once ownership of every selected factor by its earliest eliminated vertex; any selected factor containing the eliminated vertex has its other vertices in that bag if it is owned there. Scopes absent in the input have all-zero masks.

For every owned mask, maintain the invariant that its front bit (right-to-left physical order) is the forbidden indicator for the projected current tuple. Initial offsets are zero. Query the front of each owned mask; any 1 suppresses the current row, without skipping odometer updates. For the rightmost nonmaximal coordinate c, clear lower coordinates and increment c. If a projected subset contains c its flattened lexicographic index increases by one, so rotate forward one bit; otherwise if it contains k lower coordinates its projected index decreases by m^k-1, so reverse rotate that many bits. For k=0 do nothing. The one/two-dimensional rewind loops reuse cleared lower lanes, returning them to zero. The k=2 loop makes m groups of m-1 moves and m-1 cross moves, exactly m^2-1. Shared physical access routines count the fixed block separators, use finite single-symbol carries for in-place rotation, and return to the original workspace separator. An eight-bit physical return code dispatches to the actual continuation, with separate zero/one query outcomes. Because mask order is increasing group ID and bag enumeration uses the same order, this is exactly the projected lexicographic index. The argument does not require the owner to be the first sorted coordinate.

The final tuple is at the final index of every owned mask; one more forward rotation restores each mask exactly. All inactive/other masks are untouched. Thus the original masks, including those used by other bags, are preserved. Emit each allowed tuple with the inherited B4 physical rank serializer: mark and restore one digit while appending its three-bit code to the far end of the output; skip the one possible leading zero column of M=m-1. Emit field delimiters and row flag, then section close. Clear the odometer and advance the physically stored bag index. At exit restore original group suffix [19,20,20] and zero scratch. The final checkpoint is a direct physical emission, not host enumeration.

Correctness: the original forest has running intersection. Every factor is owned exactly once in a bag containing its entire scope. Therefore a choice of one emitted row per bag whose assignments agree along every parent separator exists iff the original latent constraints have a model. For disconnected roots all components must admit such choices independently. This is an informal constructive argument for the relation representation. No separator join/backtracking or original witness computation is executed by C2.

## Resources

L=Theta(m^3). At most nine bags, arity at most three, at most 9m^3 candidate tuples. The carry/rewind counts are O(m^3) in total per bag (at coordinate c, O(m^(c+1)) carries times at most m^(r-c-1) rotations); even inactive subset operations and fixed continuation-code reads are included. Each actual mask shuttle traverses O(L) preserved storage, with no free index lookup. Binary counter scans cost O(log m); every row append traverses the emitted prefix. For relation length N, N<=72+9m^3(15+9 ceil(log2 m))=O(L log L). C1 producer time Theta(L^2) on normalized inputs, C2 additional time O(L^2+N^2), visited space O(L+N), active binary counter storage O(log L). A full unconstrained triple bag can be obtained by selecting a single forbidden tuple on a ternary scope: its relation has m^3-1 rows, forcing Omega(N^2) append time. Worst-case normalized width-two producer time is therefore Theta(L^2 log^2 L). Malformed input and structural refusals do not enter relation serialization. No general worker or witness-recovery complexity is claimed.

## Executed evidence

All ten completed principal fixtures compared every mask bit, graph flag, elimination record, parent index, restored workspace and entire emitted row word to independently decoded factors and tuple enumeration. Complete row comparison includes variable arity, sorted coordinates, owner in a nonfirst coordinate, zero-row unary bag, fill edges, multiple roots, and seeded m=3 mixed ranks. Two refusals preserve their masks and emit no relation sections.

| Fixture | m | Relation bits | Transitions | Result |
|---|---:|---:|---:|---|
| empty |2|288|29486059|relations |
| outside triple |2|480|34283828|relations |
| star |2|612|39503716|relations |
| cycle |2|1134|55936039|relations |
| disconnected triangles |2|672|39188901|relations |
| K4 |2|0|26655850|refusal |
| unary contradiction |2|264|29478381|relations |
| nonmonotone owner |2|516|39070066|relations |
| dense all scopes |2|0|79393089|refusal |
| seeded mixed |3|1914|478253648|relations |

Principal totals: 503077 raw bits, 1290 mask blocks (10125 mask bits), 913 selected mask ones, 72 physically emitted parent indices and bag sections, 351 candidate checks, 5880 physically emitted relation bits, 851249577 charged physical transitions. Zero observed disagreements. Separately implemented sparse interpreter replays outside-triple input, checking the exact 682-bit word (190 header+12 scratch+480 relations), raw selector, graph flags, pins and all 129 restored masks. 34283828 additional transitions. Total 885533405 completed principal plus independent replay transitions, excluding smoke runs, controls, repeated budget runs. Seven malformed controls and four cutoff checks, exact completion at 34283828. Full m>=4 C2 runs not executed. Current reported tests executed in JS V8; new native codec and CI gates are committed but not asserted passed until confirmed.

## Next bounded mission

REX-023D1: implement a physical variable-arity elimination worker over the new forest grammar, beginning with bottom-up feasibility propagation through separators of cardinality zero, one and two; ensure independent roots are all feasible, and verify nonempty-local but globally inconsistent cases. Then recover selected rows and original witness. Preserve fixed-path B6. No promotion, no global proof route closed. All four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in small larger controls; do
  node mathos/research/f038_rex_width_two_relations_audit.js "$suite"
done
node mathos/research/f038_rex_width_two_relations_replay.js
node mathos/research/f038_rex_width_two_relations.js --descriptor > /tmp/relations.desc
python -m mathos.research.f038_rex_width_two_relations_codec /tmp/relations.desc
```
