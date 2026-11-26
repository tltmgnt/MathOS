# F038-REX-023D1 — General physical separator elimination

Parent 552ee13cbf2099f8d4d5c03f57d5900776544b43 (REX-023C2). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

Previous exact-head [C2 Proctor run 45896710409](https://github.com/tltmgnt/MathOS/actions/runs/45896710409) completed successfully, including native original-format codec replay. This cycle physically propagates subtree feasibility through arbitrary width-two elimination forests of the normalized nine-group family. The descriptor consumes the original raw selector directly, composes all C2 preparation and D1 elimination on the same tape, and emits the decision and all subtree-feasible row flags. No host supplies a decomposition, separator key, row, or continuation during execution. Host oracles only inspect results. Not an unrestricted solver and not an original Boolean witness machine.

## Physical interface

650462 nonhalting states, 1951386 transition entries, 47483730 serialized bits. Worker entry state 533704 (observer metadata). C2 accepted checkpoint has the 190-bit header, 12 scratch bits and nine variable-arity sections in elimination order; group suffix initially [19,20,20], rank lanes zero. On success of normalization and structural admission, D1 preserves every original mask, graph flag, pin, original selector, forest header, rank digit and section boundary. Each row flag remains 101 if subtree-feasible, becomes 100 if infeasible. Append one decision bit at the end of the relation word: 1 iff all roots have a feasible row, 0 otherwise. The 12 scratch bits, rank lanes and group suffix are restored. Halt on the original blank workspace separator, not on the decision bit. FOREST_SAT and FOREST_UNSAT are observational labels for this admitted-family checkpoint. OUTSIDE_WIDTH_TWO is not UNSAT; malformed single-zero cleanup remains inherited. Original witness-format admission is not claimed.

## Physical edge processing

For i=0..8 in elimination order, read the physical parent index at the fixed header offset. Root sentinel 9 bypasses edge propagation. For a nonroot, read the child record (owner, a, b) and parent record, physically sort group IDs using finite-control dispatch, derive both separator field masks, and store them and the parent index in the three inherited five-bit group words. All header indices are finite constant addresses walked by physical head moves. Child and parent masks select the same group IDs in increasing order even if the owner occurs in the middle or last field. Separator arity is one or two; an empty separator is handled by independent root testing rather than a fictitious edge.

A and B are binary lanes for the separator key. For each of the m or m^2 keys, scan the child section for a live row agreeing with all selected fields. If found, the key is supported and the parent is unchanged. Otherwise scan the parent section and clear the last bit of each matching row flag (101 -> 100). Thus multiple children monotonically intersect the feasible parent row set. Advance the binary odometer with all carry and reset moves charged. The key is not an externally supplied value. The 12-bit scratch is child index, target bag index, three-bit field mask and search/kill mode. Fixed state walkers locate sections by skipping the five-bit header and then reading aligned three-bit tokens until 110; 100/101 are flags, never section terminators. No uncharged random access.

To compare a selected rank field against a key component, parse its 00b tokens from left to right. Temporarily replace the last digit cell with blank, traverse left to the workspace separator, update C=2C+b by a physical binary carry scan, return right to the unique temporary blank and restore b. At the 010 field delimiter similarly mark its last cell, compare C to A or B by a binary lane equality scan, clear C, and restore the delimiter. A mismatch suppresses comparisons for the rest of that row. The row flag is tested only after all chosen fields have matched. All rank digits and delimiters are restored on every branch, including early successful search. Root scans use mask zero and test only live row flags. After processing all edges, scan every root for at least one live row; the first empty root gives decision zero, otherwise append one. All bottom-up row flags have already been finalized before this root pass.

## Correctness

Let R_i be the C2 relation on bag B_i and F_i the set of its rows with a satisfying compatible choice in all bags of the subtree rooted at i. For each child c of i with separator S_c, the running-intersection property makes S_c the entire shared variable interface with the rest of the subtree. Then

    F_i = R_i intersect (intersection over children c of lift_i(project_S_c(F_c))).

The projection is a set of JOINT keys, not independent per-coordinate supports. The physical algorithm's exhaustive key loop removes precisely those parent rows whose projected separator tuple is absent in the already finalized child live relation. Since parent index exceeds child index, all children are finalized before a bag propagates its own support. Induction gives exactly F_i for every bag. Different components have disjoint variable sets, so the normalized latent instance is satisfiable iff each root F_i is nonempty. C1/C2 exact-once factor ownership and running intersection establish equivalence with original normalized clauses. This is an informal constructive argument plus table replays, not mechanized certification. It does not select a globally consistent row from each bag: a live child row can still be incompatible with a particular eventual root choice.

## Charged resource bound

L=Theta(m^3); N=O(L log L) is the C2 relation-word length. At most eight edges, each enumerates at most m^2 keys and performs at most two scans of the relation region. Each scan reads O(N) physical token cells, and performs at most O(N) digit/delimiter shuttles (including any early returns). Each shuttle costs O(N+log m) since it traverses the contiguous word, not the preserved selector and masks; lane arithmetic costs O(log m). Header and section selection have bounded fixed offsets or sequential scans. The key odometer costs O(m^2 log m) per edge. Root scans cost O(N) each. Thus D1 time is O(m^2 N(N+log m)+m^2 log m+N), hence O(m^8 log^2 m)=O(L^(8/3) log^2 L). Combining C2's O(L^2+N^2) producer yields the same subcubic upper bound. Visited space O(L+N)=O(L log L), with O(log L) binary workspace and constant scratch. This is a conservative upper bound, not a matching lower bound or finite original selector clock guarantee. It is weaker than the earlier fixed-path bound: explicit key enumeration was chosen to avoid unbounded pairwise row comparisons and a new physical sorting layer. No top-down selection or Boolean witness reconstruction bound is included.

## Executed evidence

Ten completed principal original-input executions. Each compared all preserved mask bits and header fields, all emitted rank fields and every final row flag against independent decoded-factor enumeration and bottom-up support sets; exhaustive m^9 latent model counts verified the decision. Four SAT, five UNSAT, one structural refusal with 160 models. All three separator cardinalities, arbitrary roots, nonmonotone coordinate ownership, multiple children sharing a joint separator, and all four m=2 pin patterns exercised.

| Fixture | m | Models | Local rows | Live rows | Worker transitions | Total transitions | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| empty |2|512|18|18|45859|29531917|SAT|
| outside triple |2|448|25|25|92524|34376351|SAT|
| nonmonotone star |2|8|26|21|278980|39520561|SAT|
| nonempty inconsistent |2|0|16|14|74534|30968165|UNSAT|
| joint pair inconsistent |2|0|20|16|124673|34465372|UNSAT|
| disconnected UNSAT |2|0|24|24|80764|35143066|UNSAT|
| unary UNSAT |2|0|16|16|17772|29496152|UNSAT|
| K4 SAT refusal |2|160|--|--|0|26655850|refusal|
| seeded mixed |3|882|67|65|1740284|479993931|SAT|
| middle-owner joint UNSAT |2|0|37|29|656107|58051426|UNSAT|

Principal totals: 503077 original input bits, 81 bag sections on nine admitted inputs, 5556 relation bits, 249 locally allowed rows, 228 subtree-feasible rows, 106 parent-row support checks in the independent oracle, 3111497 new worker transitions and 798202791 total physical transitions. No observed disagreement. The joint-pair fixture has two disjoint supported separator sets {(0,0),(1,1)} and {(0,1),(1,0)}; both individual coordinate projections are full, but no joint assignment exists. The middle-owner variant additionally exercises nonadjacent selected fields in sorted order (mask 5), seven two-field child separators and multiple children. Every local relation in both fixtures is nonempty. The disconnected UNSAT case retains feasible rows in other components but rejects because one root is empty.

Independent sparse Map interpreter and separately written descriptor parser re-executed SAT outside triple (34376351 transitions) and joint-pair UNSAT (34465372 transitions), checking exact worker entry, full flagged word, restored masks, pins and selector, blank halt. Additional 68841723 transitions, combined 867044514 principal plus independent completions (excludes smoke tests, controls, budget repetitions). Seven malformed controls and seven cutoff tests (including worker boundary) passed. Exact outside-triple completion 34376351; worker entry 34283827. All executed current-cycle tests ran in JavaScript V8. Native original-codec regression and CI are committed but not claimed passed until observed. Complete m>=4 D1 replay remains untested.

## Next bounded mission

D2: physically select one live row per root, then traverse children in reverse elimination order and select a live row matching the already chosen parent separator. Mark selected rows distinctly, physically recover each owner's rank in original group order, and reconstruct the exact original Boolean witness in a later bounded stage if necessary. Preserve the fixed-path witness descriptor. The current row flags do not constitute a selected assignment. No formal global route closed, no promotion; all four global P versus NP routes and six overarching Omega obligations remain open.

Reproduce:
```sh
for suite in small larger joint controls; do
  node mathos/research/f038_rex_width_two_elimination_audit.js "$suite"
done
node mathos/research/f038_rex_width_two_elimination_replay.js
node mathos/research/f038_rex_width_two_elimination.js --descriptor > /tmp/elimination.desc
python -m mathos.research.f038_rex_width_two_elimination_codec /tmp/elimination.desc
```
