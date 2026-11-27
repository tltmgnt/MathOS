# F038-REX-024D3B1 — Compiled complete retained-relation decision forest

Parent 167cfeabb207aad7b1f30c1f2cfb52b13c0a419c. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D3A2 Proctor run 45914314249](https://github.com/tltmgnt/MathOS/actions/runs/45914314249) passed.

## Implemented interface and boundary

One finite instruction program now traverses all nine bags automatically, generates their local relations by the D3A2 router/cursor, then runs the D1B projected semijoin on retained relation tapes in elimination order. Input consists of the literal 851-symbol genuine admitted C1 header suffix and D2C's complete encoded bound/pin/mask stream, on two preencoded virtual tapes. All other tapes start empty. No bag ordinal, parsed metadata, coordinate masks, local tuples, relation handoffs or decision bits are supplied by the host. The program uses 45 fixed virtual tapes: 22 router/cursor tapes, nine owner-indexed relation tapes, a metadata stream, owner-indexed bitmap table, current owner nibble, ten shared merge tapes and a decision tape. The original raw selector is still executed separately by D2C, and the observer initializes the literal inputs. This is not yet a charged physical bridge or a complete raw-selector-to-decision descriptor. The admitted C1/D2C checkpoint invariant is a precondition, not an arbitrary counterfeit checkpoint validation theorem. The machine does not yet produce a Boolean witness.

## Local generation and retained elimination

Initialize an 81-bit owner-indexed bitmap table. The formerly external ordinal tape starts empty; the controller increments it physically after each completed bag. A bounded nine-count test selects the next bag or the edge phase. During each router's completion, intercept precisely the slot-dispatch blank branch, before it clears the temporary header and bag bitmap. Append the 20-bit owner/neighbor/parent record to the metadata stream, copy the owner nibble to scratch, and store its nine-bit bag bitmap in the owner-indexed table. Then execute the original cursor. Its former successful halt is redirected to copy the output to the owner's retained relation tape. Clear scratch and repeat. No host-generated commands or inter-kernel serialization. An initial hook redirected a cleanup rewind loop as well as slot completion, causing a bounded diagnostic timeout; corrected by intercepting only the dispatch branch. Also clear variable-width rank scratch before reusing those tapes for fixed-width edge metadata, so large rank widths cannot leave stale bitmap suffixes.

After nine local outputs, rewind the metadata stream, initialize the decision tape to one, and visit records in elimination order. For a nonroot, construct the separator bitmap from its three neighbor nibbles. Read child and parent owner-indexed bag bitmaps from the table. Scan each with the separator bitmap to emit the matching coordinate masks in sorted group order. Physically copy the retained child and parent into shared merge tapes; run D1B's projection, stable sorting, joint support deduplication, semijoin and retained payload decoding. On success clear and replace only the parent's relation, preserving the finalized child. The child has already received all its descendants' contributions. Every root is checked independently for emptiness; if any root is empty the decision tape is zero. All nine roots/nonroots are visited even after an empty root. The output is the decision bit on a virtual tape, together with all retained relations; the physical head halts at G, not at an original witness.

Correctness on genuine input follows from exact-once factor ownership, the D3A2 local cursor invariant, running intersection of the C1 forest, and the exact full-key semijoin. By induction in elimination order the finalized child relation contains precisely the local tuples extendible in its subtree. The parent's intersection with that child's separator support preserves exactly the tuples extendible to that child. The root relation is nonempty iff the component is satisfiable, and components are independent. This is a constructive argument with differential evidence, not mechanized certification.

## Numeric physical continuation interning

A new compiler retains D3A2's segmented logical representation and unchanged-symbol movement lowering. It first enumerates reachable logical states and their transitions, reserving physical root IDs before lowering cycles. Decode prefixes and rewrite/movement tails are constructed bottom-up; identical triples of packed ternary transitions share a state. Store rows in typed-array chunks and intern them through a numeric open-addressed hash table; hash collisions require exact equality of all three entries. The resulting packed transition table has no runtime host dispatch or input-dependent compilation. Each shared continuation has exactly the same actions and successor IDs; root IDs are kept distinct. This is not a global minimal quotient or a measured peak-memory guarantee.

| Property | Value |
|---|---:|
| Generated IR instructions |21809|
| Reachable non-jump instructions |19274|
| Compact instructions |8553|
| Refinement rounds |612|
| Exact IR homomorphism checks |19274|
| Logical state definitions and reachable roots |293318|
| Interned continuation states |8326849|
| Physical nonhalting states |8620167|
| Packed physical transition entries |25860501|
| Calculated descriptor bits |732714199|

Despite composing the full forest, the table is smaller than D3A2's one-bag machine (11765353 states), because the compiler changed. On the separate D1B projection IR, compare the previous symbol-movement compiler with the new row interning compiler via a rooted transition homomorphism. It maps all 752081 old states to 365657 new states, checks all 2256243 old transition entries for exact writes/moves and successor consistency, and covers all new states plus halt. This verifies clock preservation on that kernel for arbitrary physical inputs, not a full-table cross-check against an ungenerated old full-forest descriptor. For the composed forest the independent finite-IR terminal comparisons below test the new lowering. Full original descriptor serialization and native decoder verification were not performed; descriptor size is calculated from the syntax formula.

## Executed verification

Nine original selectors (seven domain two, two domain three) completed D2C followed by the complete raw and compact forest IR. An independent original-factor oracle checked each of 81 local outputs at its observer boundary, each of 31 actual semijoin outputs, both physical coordinate masks, child preservation, final retained streams in exact stable order, header metadata, owner table and decision versus all m^9 latent assignments. The raw/compact interpreters agree on primitive clocks and all 45 terminal tapes and heads. Four IR cutoff and two malformed controls passed.

| Fixture | m | Virtual primitives | Local/live rows | Models | Decision |
|---|---:|---:|---:|---:|---:|
| empty |2|45872|18/18|512|1|
| four-bag triples |2|125396|24/14|32|1|
| greedy trap |2|985141|68/68|52|1|
| joint-three UNSAT |2|133976|24/14|0|0|
| joint-three SAT |2|155873|24/24|128|1|
| disconnected UNSAT |2|155764|22/22|0|0|
| unary UNSAT |2|45763|16/16|0|0|
| mixed |3|1081614|98/98|9720|1|
| greedy trap |3|8990299|380/380|6816|1|

The joint-three obstruction deletes every parent row on the first edge despite four distinct supported triple keys, then propagates the empty relation. The compatible case preserves exact joint keys and all 128 models. These parity cases completed at the IR level. A first full ternary parity attempt before the scratch-clear correction exceeded the interactive execution timeout; no completed physical parity clock is claimed.

Three complete standalone ternary forest runs (all nine bags per run), including two additional one-edge fixtures, agreed with the independent IR/original-factor oracle and all 45 terminal tapes and heads.

| Fixture | D2C transitions | IR primitives | Physical worker transitions | Physical span | Decision |
|---|---:|---:|---:|---:|---:|
| empty |104551138|45872|376457458|16670|1|
| empty child edge |104556548|50100|511845408|16965|0|
| nonempty child edge |104556548|55502|830825918|17635|1|

The empty-child edge propagates an empty separator support into its parent and returns zero (no latent model). The nonempty edge retains both parent ranks, with three allowed child tuples and 384 latent models. Totals across the three physical worker runs: 1719128784 completed ternary transitions, 151474 virtual primitives, 27 local bag generations, two semijoins, 58 candidate tuples, 53 local rows and 51 retained rows. Across eleven distinct complete IR fixtures (empty counted once): 99 local bags, 33 semijoins, 922 candidates, 709 local rows, 687 final retained rows, 11825300 virtual primitives, 3327195620 separate D2C producer transitions. No observed disagreements in completed tests. The distinct producer clocks and worker clocks cannot be added as a measured original raw-selector machine clock. Current execution was JS V8; current-head CI unconfirmed.

## Resource audit and next mission

The constant nine-bag loop preserves the D3A2 local-generation bound O(m^4 log m); bounded metadata work and charged mask-stream scans are O(m^3) per bag. The at-most-eight projected merge semijoins cost O(m^4 log^2 m) virtual time and O(m^4 log m) total allocated virtual cells, including preserved relations and scratch. All copies/clears and finite metadata operations are included. The implemented segmented single-tape simulation uses O((T+1)(S+1)) physical transitions and O(S+1) span for fixed tapes and alphabet, hence O(m^8 log^3 m) for this standalone complete decision worker. With L=Theta(m^3) this is O(L^(8/3) log^3 L) for the worker, not yet a full raw-selector/witness bound. Initialization from the D2C physical tape and final original halt-head projection remain unimplemented, and no finite selector-stage guarantee follows from the derived asymptotic bound alone.

Next 024D3B2: compile reverse-elimination row selection and Boolean translation into this shared retained forest program; test larger physical width-three runs and develop the charged D2C-to-worker bridge. Native width-two witness evidence remains unchanged. All four global routes and six Omega obligations remain open; main unchanged.

Reproduce:
```sh
for suite in ir larger physicalEmpty physicalEdge physicalEdgeSAT; do
  node --max-old-space-size=6144 mathos/research/f038_rex_width_three_forest_ir_audit.js "$suite"
done
node mathos/research/f038_rex_width_three_row_compiler_audit.js
```
