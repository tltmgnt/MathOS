# F038-REX-024D3A1 — Compiled independent-mask cursor and local tuple generation

Parent f4a2e5b474a9dfb275f8612b4765f30f50cf7ec8. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D2C Proctor run 45911636571](https://github.com/tltmgnt/MathOS/actions/runs/45911636571) passed.

## Implemented boundary

The new finite instruction machine enumerates one bag's local allowed relation using independent physical mask heads. It consumes a preencoded 19-tape configuration: LSB-first canonical M=m-1 (m>=2), unary arity 1^r (1<=r<=4), 28 coordinate-projection bits (seven consecutive four-bit masks, unused coordinates zero), seven scope bitstreams, four initially empty binary rank tapes, three initially empty unary domain tapes, empty output and one empty first-combination flag tape. For each present owned scope the mask stream contains m^k bits in lexicographic rank order, with k selected coordinates (1..3), and each absent slot has a zero projection mask and empty bitstream. The input is legitimate bag data; this program is not a complete malformed mask/configuration verifier. In particular, a blank mask head is treated as unconstraining, which is correct for absent slots but must not be relied on for truncated present masks. The producer/metadata/stream router must establish these preconditions. The program currently handles one bag per invocation, not the whole forest.

The generic D1A compiler consumes compact finite IR, and the original-format ternary transition table carries out the computation without host-generated tuple or cursor commands. Initialization of the separated virtual tapes is host-mediated. In the integration audit the actual D2C stream is decoded by the observer, and the actual C1 bag headers are used to route the seven mask streams and derive the projection bits in host code. The physical canonical-ID and projection-mask machinery from D2A has not yet been composed with this cursor; no claim of direct raw-selector-to-local-relation execution is made. Expected relations are independently computed from original selected clauses rather than the mask data being tested.

## Finite controller and cursor invariant

Initialize four zero LSB-first rank counters of the width of M. Generate three unary tapes of length m by enumerating a binary rank until it equals M, writing one x to each tape per iteration. Reset that rank; start each mask head on its first data cell (or blank for an absent mask). Enumerate active bag coordinates lexicographically. At each candidate tuple z, the invariant for each present mask is that its head is at index sum(z_j*m^(k-1-i)) over its selected coordinates j in increasing coordinate order (i counts the selected coordinates from zero). Read at most seven mask heads. If none is one, physically emit the active ranks MSB-first as comma-separated binary fields with a semicolon row terminator.

Find the rightmost nonmaximal active rank c, resetting maximal lower ranks as the carry propagates, then increment c. For every slot read its four projection bits:
* if the scope contains c, the projected index increases by one (including the reset suffix), so move the corresponding mask head right one;
* if the scope omits c but contains k lower coordinates, the index decreases by m^k-1, so rewind exactly that many cells;
* otherwise leave its head unchanged.

For rewinds, k nested scans of the three unary tapes enumerate exactly m^k combinations; a physical one-bit flag suppresses movement for the first combination. All other combinations move the mask head left once. No host numeric rank, domain loop or cursor index is used. Absent slots have all-zero masks, so their heads never move. After the final candidate, every active mask is at its final data cell; advance and require blank, and finish. All mask bits and configuration words are preserved. The resulting relation contains exactly the locally allowed full tuples, in sorted coordinate order, with no duplicates. It is not yet a subtree-feasible relation or an original Boolean witness.

Correctness follows by induction on the lexicographic odometer and the above projected-index differences. The raw-IR audit observes every candidate boundary (metadata only, not a computation input) and checks all four rank counter words and seven mask-head positions against independently enumerated tuple indices. Independent raw/compact IR interpreters agree on primitive clocks, all 19 terminal tapes and heads. The ternary executions agree with those complete terminal configurations.

## Compiler and measured evidence

| Property | Value |
|---|---:|
| Generated instructions including labels |4521|
| Reachable non-jump instructions |2972|
| Compact instructions |1883|
| IR refinement rounds |45|
| Exact IR homomorphism checks |2972|
| Logical state definitions |41250|
| Physical nonhalting states |4142702|
| Physical transition entries |12428106|
| Original-format descriptor bits |327273462|

Three actual D2C raw-selector fixtures (two m=2, one m=3) were run separately through the direct loader, then all nine local bag relations for each were executed with the same compiled cursor descriptor. An additional 40 synthetic IR cases cover every arity 1..4 and every owner position for m=2,3,4,5, using nontrivial unary/binary/ternary masks. Domain-three actual bag cases are repeated in the larger IR suite; deduplicated totals below count them once. No observed disagreements.

| Fixture | D2C raw-selector clock | Candidate tuples | Local allowed rows | Cursor physical clock (9 calls) |
|---|---:|---:|---:|---:|
| m2 four-bag triples |104728446|40|24|14643919|
| m2 greedy trap |104759830|98|68|54292007|
| m3 mixed |1191953378|135|98|108813121|

The per-fixture clocks for the first two rows are sums of separate single-bag runs; see exact per-bag clocks in the audit. Totals across 27 physical bag runs: 273 candidates, 190 allowed rows, 136154 virtual primitives, 177749047 actual ternary transitions. The m3 arity-four bag generated 48 allowed rows from 81 candidates in 83059371 physical transitions. Across 67 distinct IR bag cases, 4979 candidate tuples, 2018 allowed rows, 34853 exact mask-head checks, 2230 observed backward cursor changes and 2663912 charged virtual primitives. All 40 synthetic cases are IR-only, not original raw-selector runs. The largest synthetic m5 arity-four tests each enumerate 625 candidates and cover all four owner positions.

The independent streamed original-format decoder parsed all 327273462 bits, validating and comparing every one of 12428106 transition entries. Its sparse interpreter completed a nontrivial two-coordinate mask fixture at exactly 1195509 transitions and recovered the three allowed tuples 0,1;1,0;1,1;. Four physical cutoff controls (0,1,100,1195508) withheld completion; the exact clock reproduced all terminal tapes and heads. An all-forbidden unary mask produced an empty relation in 990443 transitions. Principal plus independent sparse physical replay count 178944556, excluding empty-relation control, cutoff repetitions and smoke. Three distinct direct-loader input executions contribute a separate 1401441654 producer transitions; do not add these to the cursor clocks and claim an end-to-end solver. All tests here ran in JS V8. Native Python decoder and current-head CI are unconfirmed. Full descriptor compaction is not performed in this stage.

## Resource audit

For each bag with r<=4 there are m^r candidates. Binary rank comparison, increment, reset and output take O(log m) per candidate. A carry at c occurs at most O(m^(c+1)) times and a rewind at most O(m^(r-c-1)) unit moves including unary scan resets, since k<=r-c-1 and k<=3. Thus total rewinds are O(m^r) across a fixed number of slots and coordinates. Initial counter/domain generation costs O(m log m). The cursor uses O(m^r log m + m^3) virtual operations and O(m^r log m + m^3) allocated cells as a conservative bound including input masks, or O(m^4 log m) in the widest case. The generic segmented simulation costs O((T+1)(S+1)), giving O(m^8 log^2 m) for this compiled one-bag stage. This bound is distinct from the projected semijoin bound O(m^8 log^3 m). No full-width-three original solver complexity or finite stage admission is established.

Next 024D3A2: physically load the selected mask streams from the D2C canonical stream using D2A scope IDs and bag-coordinate metadata, emit the cursor configuration on tape, and remove the host routing boundary. Then integrate retained relation semijoins, top-down selection, original Boolean translation and the raw-selector bridge. Main unchanged. All four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in physical physical3 larger; do
  node --max-old-space-size=4096 mathos/research/f038_rex_width_three_tuple_cursor_audit.js "$suite"
done
node --max-old-space-size=4096 mathos/research/f038_rex_width_three_tuple_cursor_replay.js
```
