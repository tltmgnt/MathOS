# F038-REX-024C3 — Charged full-tuple expansion and fixed-multitape forest controller

Parent 5d7372e2a78ab2f9fe34b256a86a55ccfd52f49b. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Previous exact-head [C2 Proctor run 45904175278](https://github.com/tltmgnt/MathOS/actions/runs/45904175278) passed.

## Boundary and machine model

The C1 single-tape compiler and transition table are unchanged. An optional simulator observer exports its visited interval, including every physical binary cell and blank, with a marked blank halt head H and one additional blank at each end. This is still a HOST SNAPSHOT HANDOFF; it is not an implemented physical single-tape bridge. The observer does not generate tuples, headers, masks, separator keys or relation streams. The worker starts with this snapshot on its input tape, and accepts the legitimate C1 checkpoint format as its precondition. It is not a complete verifier of arbitrary counterfeit checkpoints. The additional boundary blanks fix a first smoke failure: a terminal blank need not have been visited by the C1 machine before halt.

The controller is a charged fixed-155-tape microprogram (one input, one binary bound, four binary rank counters, three unary domain tapes, 129 mask tapes, nine relation tapes, seven reused merge tapes, one decision tape). Tape contents are accessed only by stationary read, write and unit moves, each charged. Unbounded rank, domain and stream information lives on tapes. Header records, IDs, scope lists, field masks and loops over at most nine bags or 129 scopes are finite bounded controller information, not input-sized RAM. Host array implementations of these finite values and tape-cell storage do not create uncharged input-dependent indexing. Observation-only counters and output exports do not drive the computation. The limit is an external simulation cutoff. No finite transition table or original ternary descriptor is emitted by this worker.

The worker physically locates H, reads the ten fixed-length C1 stack frames and resolves owner IDs, ordered neighbor fields, parent owner IDs and seven ownership-presence flags. Structural refusal is recognized from the root status bit and returns no decision tape output. For a successful checkpoint, scan left over the 15-bit group suffix, then the five-bit workspace columns from right to left. Copy M=m-1's bits to a binary LSB-first tape and remove high redundant zeros. Skip the retained selector, then physically traverse all 166 blocks right-to-left, copying the 129 scope masks to their fixed tapes. No numerical m, rank width, graph, parent or selected row is passed by the caller. Generate three unary domain tapes by a binary counter from zero to M, and initialize four rank counters of the derived width.

## Sequential local relation production

Rather than generating seven lifted full-tuple streams and sorting them by the entire tuple (the C1 design proposal), exploit independent fixed mask heads. For each bag, compute the at-most-seven owned scopes from its bounded header, mapping each to a fixed mask tape and sorted-field bitmask. Reset all four rank counters and start each owned mask at its first bit. Enumerate lexicographic tuples in increasing group order. The invariant is that each owned mask head is at the bit indexed by the projected current tuple. Reject that row iff any bit is one. Otherwise physically emit the tuple as fixed-width binary fields separated by comma and terminated by semicolon.

For the rightmost nonmaximal coordinate c, reset lower rank counters and increment c. If a scope contains c, its flattened projection index increases by one: advance its mask head one cell. Otherwise if it contains k lower coordinates, its index decreases by m^k-1: rewind that many cells using k nested scans of the unary domain tapes, skipping the first combination. If neither applies, the projected index stays unchanged. Here k<=3 since the original factors have at most three variables. The first and final tuple put each owned mask at the first and last cell, respectively; verify the end and rewind. No mask is overwritten. This extends the fixed-path multitape cursor invariant to arbitrary arity-four bags, including owners in nonfirst sorted fields. The emitted local rows are actual tape writes, not host enumeration.

## Retained relation controller

Process the nine bags in elimination order. Resolve a nonroot's parent owner to its later frame index using finite header data. Derive matching sorted separator field masks. Physically copy the current parent and child relation streams to merge work tapes, invoke the C2 sequential projection/sort/dedup/semijoin routines on those same tape objects, and decode the filtered payload stream back to the retained parent tape by charged sequential reads and writes. The child tape is preserved. Scratch clearing, stream copying and output decoding are charged. There is no host serialization, sorting or tuple decoding between kernel calls. The new mergeTapes helper shares the C2 algorithm, with scratch reset and phase/pass observation callbacks, but the original C2 kernel is preserved independently.

At the end all child contributions have been processed before their parent propagates. Scan all independent root relations for emptiness; write one physical bit on the decision tape iff all roots have at least one live row. The standard subtree-feasibility recurrence is exact because C1's headers give a running-intersection forest and exact-once factor ownership. Parent tuples survive precisely when their entire separator key appears in every child's feasible relation. This is a constructive informal argument plus exact differential tests, not mechanized certification. The controller currently emits no consistent selected rows or original Boolean witness; a decision tape bit is not original witness admission.

## Charged resources

The snapshot and masks have O(L) length, with L=Theta(m^3). The load traversals cost O(L + m log m), including binary-bound extraction and unary domain generation. A bag of arity r<=4 has m^r candidate tuples. For a carry at c, O(m^(c+1)) carries rewind at most O(m^(r-c-1)) cells including nested unary head resets and scans. Their product is O(m^r); the fixed number of scopes and coordinates means total rewind/advance work O(m^r). Binary comparisons, increments, resets and rank emission cost O(log m) per candidate. Initial/final mask rewinds cost O(m^3) per bag. Total local expansion O(m^4 log m) time and O(m^4 log m) visited space, including input. Each of at most eight semijoins has O(m^4) records of O(log m) bits; C2 merge costs O(m^4 log^2 m), and charged routing/retention adds O(m^4 log m) per edge. Thus this fixed-multitape worker including parsing, tuple expansion, retained relations and root decisions has derived O(m^4 log^2 m) time and O(m^4 log m) visited cells, with a fixed tape count. No extrapolation from empirical scaling is required for that upper bound.

A standard fixed-tape sweeping single-tape simulation of the WORKER would cost O(m^8 log^4 m)=O(L^(8/3) log^4 L) time. Do not quadratically simulate C1's already-single-tape O(L^2) producer: that would invalidate the target. To compose, keep C1 intact, then physically identify the bounded checkpoint extent via its delimiters and encode it into the worker's fixed-track tape representation in at most O(L^2) time, with a fixed alphabet-to-ternary encoding. This is an unimplemented bridge/simulation blueprint, not a verified physical composition. Top-down rank recovery and Boolean emission still need implementation and a resource audit. Therefore no width-three subcubic original witness or cubic-stage admission claim is made.

## Executed evidence

All ten original selectors were run through the actual C1 physical descriptor. The new controller consumed only the raw marked snapshot; the independent oracle decoded original clauses and compared every locally generated tuple and every final retained stream, including stable row order, and all root decisions with exhaustive m^9 latent model counts. Nine admitted (six SAT, three UNSAT), one satisfiable K5 structural refusal (96 models). No observed disagreement.

| Fixture | m | C1 transitions | Worker steps | Models | Local/live rows |
|---|---:|---:|---:|---:|---:|
| empty |2|26776221|397047|512|18/18|
| K4 |2|26798486|505292|160|29/29|
| greedy trap |2|26957865|1163866|52|68/68|
| joint-three UNSAT |2|27517677|438932|0|24/14|
| joint-three SAT |2|27517709|460805|128|24/24|
| disconnected UNSAT |2|27517709|460769|0|22/22|
| unary UNSAT |2|26776221|397011|0|16/16|
| K5 SAT refusal |2|27879500|116890|96|--|
| greedy trap |3|273187601|10156937|6816|380/380|
| forced four-bag |3|272976247|2068866|1|45/45|

Totals: 627014 raw selector bits, 763905236 C1 transitions, 16166415 charged worker operations, 31 routed edges, 882 candidate tuples, 626 emitted local rows, 616 final retained rows. Counts are separate machine models and must not be combined as a single-tape clock. The parity obstruction starts with all local relations nonempty but deletes every incompatible three-coordinate parent row; the disconnected contradiction tests independent root failure. Domain-three forced mixed ranks includes rank two. Domain-three greedy trap tests larger rewind loops and backtracking headers. Six exact worker cutoff tests including load boundary and one step before completion, and four malformed-snapshot controls passed. These are limited malformed controls, not a counterfeit-checkpoint verifier. Current tests executed in JS V8; complete m>=4 snapshot/worker runs and exact-head CI remain unconfirmed.

## Next bounded stage

024C4: implement charged top-down selection over retained relation tapes, recover original owner ranks and original Boolean X/Y/pin/guard bits, then implement actual single-tape bridge and ternary simulation. Keep width-two verified original witness and quotient. All four global routes and six Omega obligations remain open; no promotion; main unchanged.

Reproduce:
```sh
for suite in small larger controls; do
  node mathos/research/f038_rex_width_three_controller_audit.js "$suite"
done
```
