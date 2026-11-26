# F038-REX-024C2 — Charged sequential separator projection and merge kernel

Parent e64e23fd9f265cd4e88131597cb547a26ae40d64. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [C1 native Proctor run 45903756013](https://github.com/tltmgnt/MathOS/actions/runs/45903756013) passed.

## Machine model and interface

The new seven-tape microprogram consumes two streams of records, each with a binary key, colon, binary payload and semicolon. An optional finite projection configuration (arity 1..4, mask for each side, equal selected cardinality <=3) instead accepts comma-separated nonempty binary rank fields ending in semicolon. It physically derives the projected key and complete tuple payload. Each digit is encoded 00 or 01, each field ends 10. Consequently equality preserves joint field boundaries, even for variable-width fields; an empty separator produces an empty key. The caller must supply correctly aligned coordinate masks, in increasing common variable-ID order, and the rank validity precondition if these are bag ranks. This is not yet physical header resolution.

Tape contents are accessed only by charged read/write/unit-head-move primitives. Each operation costs one step; separate simultaneous multitape transition accounting would only change a constant factor. Seven tapes P,C,A,B,S,K,O are fixed; alphabet on legal inputs is binary, punctuation, left sentinel, run delimiter and blank. The simulator also rejects malformed symbols. Initial input loading is the initial configuration; final observations and instrumentation (steps, phase ledgers, pass counters and max positions) do not control the computation except the external test cutoff. The host implementation represents a finite-controller microprogram, not an emitted finite transition table. The configuration is bounded finite control, not an input-sized indexing structure.

Projection scans each tuple twice, first emitting selected field encodings and then all fields as payload. The scratch tape is copied back sequentially. Sorting starts from singleton runs delimited by |. Split alternating whole runs onto two scratch tapes, clear the original, merge corresponding pairs using bitwise lexicographic comparisons and restore both heads to their record starts by scanning left to the preceding delimiter. Copy the lesser record, taking the left on ties; append one run delimiter after each pair. Repeat until at most one run remains; finite flags detect this condition without unbounded run-size counters. The two sorted inputs are processed separately using the same scratch tapes.

Child deduplication compares each key with the previous emitted key on K; a new key is copied into K and appended to S with empty payload. The join scans sorted parent and S: smaller parent key is discarded, smaller support key advances S, equal keys emit the entire parent record without advancing S. This preserves duplicate parent rows and stable order among equal keys. Empty streams and empty separators are handled without special host logic. All copies, rewinds, comparisons, clearing and projection movements are counted. No host sorting, uncharged indexed lookup, or host array length drives the kernel.

## Correctness and resource bound

Stable merge preserves sorted order and row multiplicities by induction on passes; each pass pairs adjacent runs of the previous pass, halving their count rounded up. Thus exactly ceil(log2(max(1,R))) passes for R input rows. Dedup retains precisely the distinct child keys. The merge semijoin retains exactly parent rows whose entire projected key occurs in the child relation. A supported key is never consumed merely because one parent row matched it. In particular, independent coordinate supports cannot substitute for joint supports. When used bottom-up on a running-intersection forest, the operation implements one edge's intersection with the child's feasible projection; repeated edges finalize subtree feasibility before their parent propagates.

For R total rows and b maximum encoded record size (including projection), each pass performs O(R) comparisons of at most O(b) bits, and O(Rb) copying, clearing and rewind moves. Projection and singleton-run creation cost O((R+1)(b+1)); dedup and semijoin cost O((R+1)(b+1)). Therefore the charged kernel time is O((R+1)(b+1) log(R+2)), total visited tape cells O((R+1)(b+1)) with constant tapes. For width-three bags R=O(m^4), b=O(log m), the kernel is O(m^4 log^2 m) and O(m^4 log m) visited cells. A quadratic sweeping single-tape simulation of this kernel alone has conditional O(m^8 log^4 m) bound, or O(L^(8/3) log^4 L) with L=Theta(m^3). This is not a compiled ternary machine, not a bound on the as-yet-unimplemented full factor expansion/handoff pipeline, and not a finite selector-stage guarantee. The C1 proposal for that whole pipeline remains a conditional design argument.

## Executed standalone tests

395 kernel cases (256 exhaustive paired subsets of four keys with duplicates, 128 seeded variable-length streams, 11 named controls), plus 5 scale runs, all compared with an independent host sort/set oracle. Stable duplicates, empty inputs and separators, nonadjacent three-field masks, variable-width collision avoidance and disjoint parity keys tested. Six exact budget cutoffs including one step short; ten malformed-stream refusals. No observed disagreement. Standalone kernel suite: 11,412,018 charged steps; 3,615 parent rows, 3,498 child rows, 1,267 retained rows, 2,479 distinct keys counted across cases. Scale suite:

| m | Parent rows | Child rows | Retained rows | Distinct keys | Charged steps | Visited cells |
|---:|---:|---:|---:|---:|---:|---:|
|2|16|8|8|4|113749|1812|
|3|81|42|42|14|1291030|13142|
|4|256|128|128|32|4501407|40866|
|5|625|315|315|63|17495681|130691|
|8|4096|2048|2048|256|133848121|850472|

Scale total 157,249,988 charged steps. The m=8 case executed 12 parent merge passes and 11 child passes. These are completed kernel computations, not complete original raw-selector witnesses.

## Host-orchestrated checkpoint integration

Four original m=2 selectors were executed through the actual C1 physical machine. Host code extracted bag rows from physical masks, resolved parent owner IDs, and passed tuple streams and bounded masks to the kernel. It decoded each actual semijoin output for the next edge. Every output word and feasible relation matched the independent factor and support oracle. The host checked root feasibility against all 512 latent assignments per fixture.

| Fixture | Producer transitions | Charged kernel steps | Edges | Models |
|---|---:|---:|---:|---:|
| Joint-three UNSAT |27517677|34687|3|0|
| Joint-three SAT |27517709|52594|3|128|
| Greedy trap SAT |26957865|669996|8|52|
| Disconnected UNSAT |27517709|52594|3|0|

The joint-three obstruction uses owner x=a XOR b and x=c, followed by the opposite parity condition on a,b,c. All local relations are nonempty, both parity supports project fully onto every proper subset, and no full triple agrees. The first three-field semijoin removes every parent row; emptiness propagates to the component root. The same-parity variant has 128 models and all roots remain feasible. The disconnected UNSAT case retains feasible other components but fails an independent unary root.

Integration totals: 109,510,960 charged C1 single-tape transitions (distinct from kernel primitives), 809,871 kernel steps on 17 edges, 151,656 raw input bits. Across 400 standalone calls and 17 integration calls, 169,471,877 completed charged kernel steps. This excludes smoke, malformed, cutoff and repeated runs. Host orchestration, relation generation from masks, header decoding, root testing and tuple re-encoding are NOT charged physical operations. Do not add these producer and kernel counts and call the sum an end-to-end single-tape runtime.

## Next bounded stage

024C3: physical all-scope mask expansion into full-tuple streams and a fixed-multitape forest controller. Resolve C1 parent/ownership fields on tape, generate local relations without host tuples, manage retained relations and invoke the merge kernel with physically derived projections. Then compile a charged single-tape ternary simulation and implement top-down witness recovery. All four global routes and six Omega obligations remain open. Main unchanged. Current executed tests run in JS V8; exact-head workflow unconfirmed at commit. 

Reproduce:
```sh
node mathos/research/f038_rex_width_three_merge_audit.js kernel
node mathos/research/f038_rex_width_three_merge_audit.js scale
node mathos/research/f038_rex_width_three_merge_forest.js
```
