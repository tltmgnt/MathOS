# F038-REX-024D6N — Nondestructive last-axis interval preseek

Parent D6M 4920c1545eb8db4aca23e91fbbde836297156794. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6M exact-head Proctor 46064051895](https://github.com/tltmgnt/MathOS/actions/runs/46064051895): 29/29 jobs passed at inspection. All jobs completed successfully. D6L remains verified 29/29.

## Immutable interval access
Retain D6M shared finite control, lazy append-only cache, original scope IDs and rank words, direct-probe budget, exact checkpoint resumption and canonical emission. No new tape or data flag. This is a sequential interval preseek, not random-access indexing or physical removal of mask rows. It applies to every direct or conditioned candidate factor validation; GAC propagation is unchanged.

For a pair, let the rank dimensions be (m,m,1), and for a triple (m,m,m). Each fixed pair of outer row indices (i,j) defines a contiguous last-axis interval of length d (1 for pairs, m for triples). Its zero-based logical row interval is [(im+j)d,(im+j+1)d). The first two rank words contain one selected marker (bit 1) each. Thus only one outer interval can contain the selected candidate row. At interval entry, read the first two cursor bits once (short-circuit on first 0). If unmatched, enter preseek state: skip the literal's two cells without reading its value, or consume one four-allowed-row run token. Advance last-axis rank cursor for every represented logical row. If matched, enter inner state and read only the last-axis rank cursor; selected literal value determines pass or conflict. Unselected literal values are skipped. At every last-axis wrap, rewind it and carry through the second and first axis as necessary, then recompute the outer-match state. After the selected row passes, retain the inherited suffix skip. On a forbidden selected literal, enter exactly the original retry with CQ just after the literal, CD at the scope end, and the same three rank cursors.

## Compressed-run invariant
A 11 token represents four allowed rows. Consume its physical two cells once, then process its remaining virtual rows in finite control. For each virtual row, retain the current outer-match state while R2 does not wrap; on wrap, advance outer cursor(s) and re-evaluate the outer match. A run can cross several outer intervals, especially the dummy length-one pair axis. An allowed selected virtual row jumps directly to the existing suffix skip with the token already consumed. No virtual row can produce a conflict. When all four rows are consumed without selection, return to the appropriate ordinary token state. Canonical token lengths and row counts are preconditions; malformed-stream rejection equivalence is not claimed.

## Source-level correctness
Induct on the logical row cursor, including virtual position within each consumed run. At a row boundary the new controller has identical CQ/CD and R0/R1/R2 contents and heads as D6M, except the cached outer-match state is held in finite control. Between wraps the first two cursors are unchanged, so their match value is invariant. Therefore skipped unmatched intervals cannot contain the selected row; skipping unselected literal values cannot change acceptance. Rank advancement is identical. At wrap the outer-match state is refreshed before the next logical row, including inside runs. A selected passing literal or virtual row reaches the same suffix cursor as D6M; a selected forbidden literal reaches the same conflict cursor. Thus suffix traversal, direct last-coordinate extension, probe checkpoint resumption, cache frontier, candidate order and terminal witness/status are preserved. Induction over factor dispatch and candidate visits yields the inherited normalized-family correctness theorem. D6M source quotient equivalence still applies. This is not a mechanical proof of all physical macros.

## Conditional cost
For a ternary field, before/through the selected row the outer comparisons occur once per visited last-axis interval, rather than once per visited row. In a full traversal their maximum drops from m^3 to m^2 outer-match evaluations. The inner rank comparison is confined to the matching outer interval. Pairs have d=1 and gain only unselected literal-value skipping; no factor of m reduction in pair outer comparisons. Each skipped literal saves its second-bit read. All logical rows before the selected row still incur cursor advancement, and physical tokens still require sequential traversal; the selected passing row skips the suffix as before. No claim of O(m^2) total ternary validation, no random access and no local mask length reduction. Worst-case O(S_j+m+1) candidate cost remains. D6L cache storage O(S+1), build O(q(S+m+1)), and V<=4+P(1+sum D_j) unchanged. Under inherited physical macro assumptions t=O(L^2(p+1+V)), admitted exponent 2+(h+b)/3. Fixed-nine explicit encoding already admits polynomial exhaustive search; unrestricted SAT reduction, universal cubic admission and P versus NP proof remain open.

## Independent verification
679 fixtures in two modes (1358 executions),1116 SAT,242 UNSAT. All original oracle classifications and lexicographic witnesses, full candidate/conflict/prefix/component traces and D6I parity matched. New exact D6M terminal parity (all tapes and heads, status, excluding step count) on1358 executions and15550 full tape/head event snapshots. Also1358 compact/uncompressed exact terminal comparisons including primitive count and15550 compact/uncompressed event snapshots. Local compaction verifies12635 bounded and12629 full retained instructions after119 refinement rounds. Inherited counts unchanged:4520 candidate comparisons,2668 conflict comparisons,7022 graph/component checks,72 conditioned runs,320 append checks,40 deferred blocks,3060 immutable cache comparisons,1288 local retries,6 exact direct resumptions. No observed discrepancy. These are finite tests, not universal empirical guarantees.

## Performance
| logical primitives | D6M | D6N |
|---|---:|---:|
| aggregate |50328209|50242835|
| one-prefix m2 SAT |109672|109615|
| one-prefix m2 UNSAT |57852|57825|
| two-prefix m3 SAT |175726|174387|
| hard m2 SAT |146186|145979|
| hard m3 SAT |272738|270257|
| hard m4 SAT |577125|564720|
| hard m4 UNSAT |587890|574882|

750 improved,608 tied,0 regressed relative to D6M. Aggregate reduction85374 primitives (~0.17%). Hard m4 SAT logical reduction12405 (~2.15%). Candidate counts, cache bytes and all event tape/head snapshots unchanged.
| hard SAT domain | D6M exact source worker | D6N exact source worker |
|---|---:|---:|
| m2 |2406718370|2404230732|
| m3 |4335846976|4313582992|
| m4 |8503585206|8432474098|

Source-accounted clocks, not completed D6N hard-family physical replays. Physical savings are smaller than logical savings on hard m4 (~0.84% worker reduction). The remaining cost is sequential token and rank movement; this is an incremental optimization, not the full indexed slice access originally proposed.

## Physical lowering
| mode | generated IR | compact IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|---:|
| bounded |13793|9423|3803788|3607883|285022761|11411364|
| full |13792|9418|3802065|3606160|284886644|11406195|

20 tapes, four-bit segmented alphabet,22-bit quotient IDs. Bounded descriptor increases427943 bits (0.15%) over D6M; additional control costs5417 states. 21-bit target unmet. No final descriptor compression claim.

## Physical replay evidence
| fixture/mode | halt transitions | head | span | result |
|---|---:|---:|---:|---|
| one-prefix SAT bounded |1710415528|47122|47937|SAT|
| one-prefix UNSAT full |880341452|38293|47726|UNSAT|

Original and quotient matched exact transitions, head, span and output. SAT witness0101010101010101011111111110000; observed worker1674657920 matches source accounting. UNSAT blank halt. One-short quotient cutoffs1710415527 and880341451 returned TIMEOUT/no witness. Relative D6M reductions1178868 and480006 physical transitions respectively. Dedicated Proctor config registers29 jobs (one audit,26 physical,2 native); final completion unconfirmed. No main or PR #248 modifications.

## Next D6O
Target physical lowering rather than accumulating source control: investigate shared segmented scanner continuations and/or a certified alternative symbol encoding. Preserve exact original-format witness semantics and establish physical resource trade-offs. Full random-access conditioned slice indexing remains unimplemented; D6N establishes sequential preseek only. No promotion.
