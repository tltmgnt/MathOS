# F038-REX-024C1 — Physical width-three bag headers and factor masks

Parent 15e999349f57fb65e5ef165aeb6a9426edae6dd4. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE. Previous exact-head native [024B workflow 45903095739](https://github.com/tltmgnt/MathOS/actions/runs/45903095739) passed.

## Physical interface and correctness

The fixed ternary descriptor (485080 nonhalt states, 1455240 entries, 33955604 bits) starts at the original raw selector, with no host graph, scope, order, neighbor or parent input. It merges the verified 023C1 all-scope deposition stage with the 024B exact width-three DFS, and constructs bag metadata physically after successful DFS. To the left of the workspace separator, retain the original selector, binary rank workspace and 166 blocks: 36 graph flags, original pins, and 129 lexicographically indexed unary/binary/ternary masks (arity first). Every optional negative selector bit is deposited in its mask, including zeros; selected scopes additionally set the deduplicated graph edges. Total mask bits B(m)=9m+36m^2+84m^3. This is the same scope and rank order as C1.

The DFS frame is enlarged from 60 to 84 bits; separator distance is 85. Its first 60 bits retain the graph, active flags, tried flags, chosen vertex, root and success bits. The 24-bit extension is initially zero, including for every pushed child. Pop erases the full frame. Thus the exact DFS graph invariant and search order are unchanged. On success, return to the root and physically populate nine headers. From each frame's choice read incident edge flags, recording up to three neighbors in increasing ID order. Write three four-bit IDs (9 sentinel), a four-bit parent OWNER ID (9 for root), seven ownership presence flags, and a transient pending marker. Parent is found by walking later frames in elimination order until the first chosen owner in the separator. Return left over frame separators until the unique pending marker; write the parent owner and clear the marker. Empty separators do not enter this search. The tenth empty frame stays zero in its extension. Structural refusal retains just the root search frame with zero extension. Malformed cleanup remains the inherited single-zero status, not original witness refusal.

For owner v and ordered neighbors a,b,c, the seven slots denote {v}, {v,a}, {v,b}, {v,c}, {v,a,b}, {v,a,c}, {v,b,c}. A slot is present iff none of its neighbor fields is sentinel. There is no four-variable factor in the original clause grammar. The slot plus the physical header identifies its mask by sorting group IDs and using the original scope order. A present slot does NOT imply that its mask contains a selected clause. All selected factors occur in their earliest eliminated variable's bag: before eliminating that variable, its other variables are still neighbors because each factor scope induced a clique. Only that bag can own it. Fill makes the separator a clique and the earliest subsequent neighbor bag contains it, giving the usual running-intersection forest. Parent is encoded as OWNER, not elimination index; the audit maps it to an index, and the future worker must resolve it physically. Slot flags are emitted physically; numeric mask IDs and bag tuple rows are not yet emitted. Successful checkpoint WIDTH_THREE_FACTORS is structural, not SAT.

## Verification

Every mask bit, every retained DFS frame, sorted neighbor field, physical parent owner and ownership slot is compared to independently decoded factors and subset-torso DP. Each selected factor is checked for unique ownership at its earliest eliminated variable. Host-only oracle enumerates every candidate tuple in each bag and compares projected physical masks against direct original factor relations. This does not constitute a physical tuple serializer. All four domain-two pin patterns, disconnected components, backtracking, unary UNSAT, arity-four bags with ternary factors, and satisfiable structural refusals exercised.

| Fixture | m | Physical transitions | Outcome |
|---|---:|---:|---|
| empty |2|26776221|headers|
| K4 |2|26798486|headers|
| K3,6 |2|26874240|headers|
| 3x3 grid |2|26846756|headers|
| two triples |2|26951334|headers|
| greedy trap |2|26957865|headers|
| K5 |2|27879500|refusal|
| subdivided K5 |2|27895988|refusal|
| K4,5 |2|26709526|refusal|
| complete SAT refusal |2|26794774|refusal|
| four-bag triples |2|26941937|headers|
| unary UNSAT plan |2|26776221|headers|
| greedy trap |3|273187601|headers|
| K5 |3|274103727|refusal|
| four-bag mixed |3|273559039|headers|

15 principal completions, 10 accepted, 5 structural refusals, 940521 raw bits, 1935 physical mask blocks, 17865 mask bits, 90 complete bag headers, 275 owned slots, 1048 host tuple comparisons, 292 pushes, 202 pops, 5460099 planner/header transitions. Principal total 1145053215 transitions. Independent sparse original-descriptor interpreter verified the entire ten-frame greedy-trap stack (26957865 transitions) and one-frame K5 refusal (27879500), including original selector, pins and all 129 mask blocks. Additional 54837365 transitions, combined 1199890580 completed transitions, excluding smoke tests and controls. Six cutoff controls (including planner boundary and one step short), eight malformed controls. Zero observed disagreements. Current tests executed in JS V8; native codec and exact-head CI unconfirmed. No complete m>=4 mask/header run in this mission. The previous 024B m=4 graph-only planning result is preserved.

## Resource argument

All-scope deposition costs Theta(L^2) worst case, O(L) span, from C1. Each graph operation is charged within fixed-sized frame walks; at most sum_{d=0}^9 9!/(9-d)! search nodes, ten frames of 84 bits plus delimiters. Header pass is constant in m because every neighbor and parent scan is over nine vertices/frames. Consequently the physical preparation still has Theta(L^2) worst-case time, O(L) span, O(log L) binary workspace plus constant graph/header storage. This is restricted to nine latent groups.

## Design-only alternative to the naive wider worker

Do not extend D1's explicit key enumeration with per-digit full-word shuttles: at arity four that yields the conservative O(L^(11/3) log^2 L) upper bound, not subcubic. Proposed fixed-multitape sequential sort/merge route:

1. For each owned scope of size k<=3 in a bag of size r<=4, read its mask sequentially in rank-tuple order. For each mask bit enumerate all m^(r-k) free-coordinate assignments using binary odometers and emit fixed-width full-tuple records with that forbidden flag. Sort these records by full tuple on fixed work tapes via bottom-up merge passes. Merge the at most seven streams, OR the forbidden flags, retain allowed rows. Each stream has exactly m^r records (including zeros); no uncharged indexed mask lookup.
2. For each child, project its feasible rows to the joint separator (size <=3), sort and deduplicate keys. Sort parent rows by the same key, retaining their full tuple fields, and sequentially semijoin against the support stream. Preserve each child's finalized feasible relation. Multiple children give monotone filtering. Roots must all be nonempty. For witness selection traverse in reverse elimination order, read the selected parent key and sequentially find one compatible child row. Recover each owner's rank and translate to original bits.
3. A record has O(log m) bits. With a fixed number of tapes and bags, sequential record generation, comparison, rewind, copying and merge passes can be implemented with O(m^4 polylog m) multitape steps: e.g. binary counters for run lengths and bitwise records give conservative O(m^4 log^3 m). A fixed-alphabet fixed-tape single-tape sweeping simulation can in principle charge O(T^2) time and O(T) span, giving O(m^8 log^6 m)=O(L^(8/3) log^6 L), strictly subcubic asymptotically. This is a design-level target, conditional on a concrete multitape implementation, a charged producer/worker handoff and ternary compiler. It is not a tested descriptor, an explicit uniform clock, or a cubic-stage guarantee. No host sort or RAM lookup is being counted as a physical tape action.

Next 024C2: implement and measure a sequential fixed-multitape merge kernel with exact joint-key semantics, then compose it with the physical producer. Preserve native width-two witness and quotient. All four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in small larger controls; do node mathos/research/f038_rex_width_three_factors_audit.js "$suite"; done
node mathos/research/f038_rex_width_three_factors_replay.js
node mathos/research/f038_rex_width_three_factors.js --descriptor > /tmp/width3-factors.desc
python -m mathos.research.f038_rex_width_three_factors_codec /tmp/width3-factors.desc
```
