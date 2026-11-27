# F038-REX-024D6E — Automatic physical component admission and complete general fallback

Parent 675ffcef61686b51ec235e399d69354390984406. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; MRA-X Omega obligations 0/6.

## Prior checkpoint

D6D exact-head [Proctor 46028751351](https://github.com/tltmgnt/MathOS/actions/runs/46028751351) completed all fifteen jobs successfully, including the previously outstanding m3 physical cases, both native jobs, audit and governance.

## Construction

Retain the prefix-ordered FIFO producer, canonical run-token stream, 20 logical tapes, sound GAC and D6C direct-extension search. The D6D specialized partition is {0,3,6}, {1,4,7}, {2,5,8}. The physical pre-scan uses the actual scope directory and corresponding constraint fields. On the first active crossing field it stops the guard, sets path flag 1 and rewinds Q to initialize the general solver. If all crossing fields are universal, it sets flag 0 and initializes the specialized component solver. The pre-scan does not delete any constraints. Neither path relies on host-supplied admission or witness data.

A's first cell stores the path flag; the original change flag and four budget cells move one cell right. During candidate search the second cell carries the component selector (0/1/x). A shared route macro reads the first cell and restores the second-cell head. Candidate dispatch loads every active factor in general mode and only the selected component's factors in component mode. Conflict extension remains shared. Suffix reset and carry test the path flag: general mode resets/increments the ordinary lexicographic coordinate order; component mode restricts them to the component. After successful general validation emit the witness; after successful component validation move to the next component or emit after the third. No separate full worker or duplicate stream is required.

Soundness under genuine normalized/canonical producer and correct lowering premises: the guard selects component mode only if every active relation is contained in a fixed partition block. The D6D product-factorization and local lex-minimum argument therefore applies. Otherwise the D6C complete direct-extension search applies to the unchanged full relation set. In both paths GAC preserves every satisfying assignment, failed-prefix skips exclude only infeasible assignments, and lexicographic search terminates by strict increase on a finite product. Consequently every genuine normalized input is handled by one complete path, with the original lexicographically first witness or an exhaustive UNSAT refusal. Outside-class inputs no longer have a separate admission refusal in this combined machine. This is a source-level argument, not a mechanically verified all-input proof of the producer and lowering. Malformed streams still may refuse; a blank terminal symbol alone does not classify arbitrary malformed raw inputs.

This is automatic selection of one fixed partition versus the complete general solver, NOT general graph component discovery or multi-partition selection. No repeated-directory scan reduction was implemented.

## Independent audit

705 distinct fixture entries, 1410 logical mode executions. 1360 valid original SAT witnesses, 50 correct UNSAT refusals; all match independent exact search and D6C lex witnesses/statuses. 610 component executions, 800 general fallback executions (782 SAT and 18 UNSAT). All 120 singleton-active pair/triple scopes and every domain-two truth mask on a local and a crossing ternary scope are tested, plus 60 seeded mixed instances and named barriers. Independent route reference uses actual normalized relations. Independent component/general trace oracles agree on all 3426 candidate visits and 906 failed scope records; the physical path flag matches the host partition predicate on every run. 20034 arithmetic cases per envelope (general and component), 40068 checks. No observed correctness discrepancies.

| fixture (alternating pins) | path | D6C worker clock | D6E worker clock |
|---|---|---:|---:|
| empty | component |183311428|420199762|
| crossing SAT | general |194911174|200695710|
| chain | general |297537692|304152578|
| equality-star SAT m2 | general |423600568|434879230|
| equality triples m2 SAT | component |1149574474|930366100|
| equality triples m3 SAT | component |4599003252|1645186132|

These are exact source-accounted worker clocks. Across 1360 paired SAT executions against D6C, 4 improve, 1356 regress, none tie. D6E prioritizes complete automatic dispatch, not uniform acceleration; D6C remains the simpler general-performance baseline and D6D the smaller specialized baseline.

## Actual original-format evidence

All pins zero. The previously satisfiable crossing fixture [-1,-3] refused by D6D now returns a valid witness through general fallback. Both modes executed original and quotient tables and one-short cutoffs. Separately executed bounded component SAT and full general UNSAT original/quotient/cutoffs.

| fixture | mode | physical transitions | head | span | result |
|---|---|---:|---:|---:|---|
| cross-sat | bounded/full |233530292|45652|46443|SAT |
| triple-2-sat | bounded |965915186|46010|46823|SAT |
| barrier-unsat | full |281941536|38293|46650|UNSAT |

Cross SAT witness 1001101010101010101111111110000, bridgeAt=31728929, workerAt=32370124, outputAt=233065522, worker=200695398, N=1856, 15622 logical primitives. Component SAT witness 0101010101010101011111111110000, bridgeAt=34147955, workerAt=35066490, outputAt=965432272, worker=930365782, N=1928, 80049 primitives. General UNSAT blank halt, bridgeAt=34381509, workerAt=35282876, blankAt=281941535. Exact quotient replay matches each observed halt and layout; budgets 233530291, 965915185, 281941535 respectively produce TIMEOUT without witness. Registered 12 physical replay jobs, two independent native descriptor jobs and audit/governance. New exact-head CI not yet confirmed.

## Conditional resources and descriptor cost

For genuine normalized input choose C=3m^3 on the component path or m^9 on general fallback. Reuse inherited S<=L/16, L>=4096m^3 and N<=S+35m+1480<=2S. Charge path scans, route tests, suffix resets and carry under enlarged conditional T<=262144 S(C+(full?m:1)+1), W<=(20N+12)T+6; producer 4P+32L, bridge 128S^2 and projector 256S^2. With these conservative source-level macro premises total<=2^22 m^3 L^2<=1024L^3 on the fixed-partition path and total<=2^22 m^9 L^2=O(L^5) otherwise. The extra factor two in macro allowance is a conservative engineering decision, not a measured optimal constant. Arithmetic passes do not discharge the macro premises. No complete cubic bound for all normalized inputs, practical admission, unrestricted reduction or P versus NP resolution. The D6D max-component root counting theorem remains applicable to the specialized path but a tighter D6E root-specific physical envelope was not audited here.

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |8837|3129312|2192484|173206240|9387936|
| full |8836|3127032|2190761|173070123|9381096|

Producer 287874, bridge 279, projector 74, blank halt 1; worker 2841084/2838804. Four-bit physical lowering unchanged; quotient state indices now need 22 bits (both exceed 2^21). Descriptor increased relative to D6D, reflecting shared route-dependent reset/carry and dispatch logic. No descriptor compression claimed.

## Next D6F

Discover arbitrary component membership from actual active scopes (or implement a checked multi-partition selector as intermediate step); reduce repeated full stream scans, shared reset-state duplication, and route overhead. Compare against both current baselines and preserve general fallback. Confirm D6E exact-head independent native/physical CI. Keep all global routes blocked. Main and PR #248 unchanged.
