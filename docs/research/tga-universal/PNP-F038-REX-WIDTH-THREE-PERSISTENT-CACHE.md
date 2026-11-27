# F038-REX-024D6K — Persistent residual block cache and local rewind

Parent D6J a43fe2ed87b531d28cb6e9bec509d3011ae44e33. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6J exact-head Proctor 46053000629](https://github.com/tltmgnt/MathOS/actions/runs/46053000629): 25/25 jobs passed. D6I 23/23 and D6H 19/19 remain verified.

## Physical controller
This branch is an alternative to D6J materialized slicing, not a combination of slicing and caching. It starts from the D6I original-mask validator, keeps bounded direct probe, exact direct checkpoint continuation and first-useful-prefix structural admission. Only admitted conditioned execution uses the persistent cache. Retain 20 logical tapes. A25 remains the blank probe-budget terminator. A26 is the cache construction flag.

Once a prefix is admitted, initialize rank words and clear CQ/CD. In increasing least-coordinate order, discover residual components using actual graph edges. Append marker x to each of CQ/CD before each block, followed by its original run-coded active factors and scope directory in canonical scope order. Internal tokens are binary, hence x is an unambiguous block marker. The final block ends at blank. Empty blocks, if present, have adjacent markers or a marker followed by blank. The prefix-only pair (0,1) is included in the first block only. Unaries remain applied to surviving domains. Every active higher-arity factor belongs to exactly one block (or the prefix-only first-block case). No host partition certificate, rank-dependent slicing, projected tables or cached satisfiability.

When the cache is complete, reset membership for the first prefix branch. At the first block of every prefix tuple, rewind both cache tapes to their first marker and advance one cell. Subsequent blocks enter immediately after the paired next marker; a successful block validates through its end and leaves both heads at corresponding boundaries. The validator uses original scope IDs and original full rank words, including fixed prefix ranks. On residual candidate retry, move both heads left once, then rewind to the nearest x and advance once. A conflict has consumed a forbidden literal and its directory entry, so this reaches the current block's beginning even if CD was pointing at the next marker or final blank. A prefix-only conflict advances the prefix rather than changing a fixed rank. At prefix change, reset the ranks and restart at the first block; the cache remains immutable. The graph and canonical Q/D remain unchanged. First-block membership reuse survives, but all blocks now avoid mask reconstruction. The revised controller removes the initial prototype's per-candidate global block ordinal scan; sequential boundary access and local rewind suffice.

## Source-level correctness and resources
For genuine normalized canonical input, sound GAC and correct lowering, D6I's residual factor partition and prefix lexicographic theorem apply without modification. Each cached field exactly reproduces its corresponding canonical field. All prefix and candidate tuples are tested against their original relations. Cached block order is identical to increasing least-coordinate component order; the paired marker and cursor invariant makes every retry enter the same block, and every successful transition enter the next. Immutability ensures the same relation is used for every prefix. Thus conditioned and nonconditioned traces, exact canonical SAT witness and UNSAT results are preserved. This is a source-level argument, not a mechanically certified physical macro theorem.

Let S be canonical stream length, S_j original local stream plus directory lengths, P=product of surviving prefix domain sizes, D_j=product of residual block domain sizes. With fixed nine coordinates, total cache storage is O(S+1): each active field appears once, each block contributes two markers, and all scope IDs have constant width. One-time materialization (including scanning Q/D once per block and appending at cache ends) is O(S+m+1). Graph closure and rank reset over each prefix cost O(m+1) because the number of edges is bounded independently of m. First block rewind can cost O(S+m+1) per prefix branch. Within a block, retry rewinds only that block, with validation and last-coordinate extension O(S_j+m+1). Let C_aj be local visits. Conditional primitive cost after admitting a prefix is O((p+1+P)(S+m+1)+sum C_aj(S_j+m+1)), p GAC passes, including initial direct probe. This preserves the previous worst-case envelope, but removes repeated O(S+m+1) local materializations per prefix/component. No claim of a lower end-to-end asymptotic exponent: physical tape span still includes canonical input and the entire cache. Combined visit bound V<=4+P(1+sum D_j) remains unchanged; under inherited physical assumptions t=O(L^2(p+1+V)), admitted O(L^(2+(h+b)/3)) with h prefix size and b largest residual component. General connected fallback O(L^5). Fixed-nine explicit encoding is already polynomial; unrestricted SAT reduction and universal cubic admission remain open.

## Independent audit
679 fixtures in two modes (1358 executions):1116 SAT,242 UNSAT. Exact decoded relation oracle, original witness/status, full candidate/conflict/prefix/component traces and D6I/D6J parity all matched. 256 probes,658 probe candidates,178 probe SAT,78 suspensions,6 exact direct resumes. 72 conditioned (16 one-prefix,56 two-prefix),52 SAT and20 UNSAT. 288 prefix assignments,7022 component/graph checks,4520 candidate/local checks,2668 conflicts including22 prefix-only conflicts. 84 first-block membership reuse events.

Each of 72 conditioned runs builds exactly one immutable cache of all residual blocks; 360 block builds total. Summed across runs, cache mask tape lengths18180 symbols and directory tape lengths8966 symbols (markers included; not simultaneous peak storage). Independent oracle reconstructs entire cache from decoded relations and checks both tapes at completion. Further3060 immutable-content checks cover886 cached component entries and2174 cached candidates. Of those candidates,288 first-block entries,598 sequential later-block entries,1288 local retry rewinds. Auditor compares actual block-start head positions and exact selected segment bytes with independent oracle; direct checkpoint preserved. No observed discrepancy. Finite tests only.

## Comparative performance
| logical primitives | D6I | D6J | D6K |
|---|---:|---:|---:|
| total 1358 executions |55342459|55400063|51876507|
| hard m2 SAT |246967|247759|158412|
| hard m2 UNSAT |249703|249779|160290|
| hard m3 SAT |572670|554422|289754|
| hard m3 UNSAT |583192|561308|295671|
| hard m4 SAT |1218591|1099413|603551|
| hard m4 UNSAT |1233951|1106865|614759|

D6J comparison:44 improved,1096 regressed,218 tied. Aggregate reduction3523556 primitives, about6.36%. Most cases regress slightly because nonconditioned paths incur extra dispatch and mode checks; eager cache construction can also cost more on early failing prefixes. Hard instances dominate aggregate savings. The initial global-block-ordinal prototype (cde039318b44a894671b62bd22d0d0ef95638c13) used897766 logical primitives on hard m4 SAT; local-boundary revision uses603551.

| hard SAT domain | D6I exact source worker | D6J exact source worker | D6K exact source worker |
|---|---:|---:|---:|
| m2 |4185324994|4121308344|2674871514|
| m3 |10278626610|9814485296|4718418806|
| m4 |22926806712|20844546480|9112116022|

D6J-to-D6K hard m4 worker reduction about56.3%. Candidate counts unchanged. By contrast m2 one-prefix SAT worker1816215694 ->1932252928, and one-prefix UNSAT logical65796 ->110591. The cache deliberately trades eager construction and original mask validation for avoiding repeated materialization. No universal speedup; no optimal selection rule. Physical lazy slice access is still unimplemented; D6J remains the sliced alternative.

## Physical lowering and replay
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |14099|5381760|3723744|294175780|16145280|
| full |14098|5379480|3722021|294039663|16138440|

Four-bit segmented encoding,20 tapes,22-bit quotient IDs. Bounded descriptor reduced10717851 bits (~3.52%) relative to D6J but larger than D6I; 21-bit target unmet.

| fixture/mode | exact halt transitions | head | span | classification |
|---|---:|---:|---:|---|
| one-prefix SAT bounded |1968010788|47126|47941|SAT|
| one-prefix UNSAT full |1782816682|38293|47786|UNSAT|

Original and quotient match transitions, head, span and expected witness; one-short quotient cutoffs1968010787 and1782816681 return TIMEOUT/no witness. SAT witness0101010101010101011111111110000, exact observed worker1932252928 matches source accounting. UNSAT blank halt. Hard m2 original physical attempt exceeded interactive limit; no hard-family physical halt is claimed yet. Dedicated Proctor schedules one audit,26 physical mode/fixture jobs,2 native jobs (29 total), including hard m2/m3/m4 SAT. Hard m4 replay newly registered with 30-billion transition budget; completion unconfirmed. Native exact-format ledger verifies descriptor and original verifier/cutoff. Main and PR #248 untouched by these changes.

## Next D6L
Reduce ordinary-path overhead; develop an adaptive lazy per-block materialization policy that avoids eager work on rejected prefixes while retaining local boundary reuse. Compare against D6J sliced and D6K original-mask cache. Investigate physical lazy interval access and finite-control sharing. Preserve independent trace and native parity. No promotion.
