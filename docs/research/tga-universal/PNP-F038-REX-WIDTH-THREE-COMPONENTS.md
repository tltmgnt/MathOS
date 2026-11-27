# F038-REX-024D6D — Physically guarded component decomposition and max-component root bounds

Parent 7e6b1bab874c301e83ce38e60186eb8d2764f0f9. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Previous checkpoint

D6C exact documentation-head [Proctor 46022675631](https://github.com/tltmgnt/MathOS/actions/runs/46022675631): all fifteen jobs passed. D6D executable changes and regression tooling are recorded on the separate component branch. Main and PR #248 unchanged.

## Physical partition admission and search

Retain the D6C prefix-ordered producer, canonical run-coded stream, 20-tape worker, GAC and direct conflict-row extension. Specialize the solver to the fixed partition C0={0,3,6}, C1={1,4,7}, C2={2,5,8}. This is not an arbitrary connected-component discovery algorithm in the physical machine. Before loading the domains, scan the scope directory and corresponding fields. Every crossing pair or triple must have the universal-field marker 10; any active crossing relation refuses. For a scope entirely within a component, skip its tokens and continue. Require exact scope-directory and stream exhaustion. The guard uses only genuine producer tokens and the fixed scope directory, not a host-supplied graph certificate. Malformed streams are not covered by an all-input proof.

After sound GAC on the admitted input, initialize one selected surviving rank in each group. Reuse tape A's flag as the three-valued component selector. Scan the directory for the selected component only; other component masks are skipped. A failed selected tuple uses the inherited direct last-coordinate row extension, but suffix resets and carry affect only coordinates in that component. If a component exhausts, refuse. On success, retain its selected ranks, move to the next component and validate its first candidate. After all three components succeed, emit the combined original witness. There is no external selection of ranks or component witnesses.

Source-level correctness under genuine normalization, canonical stream and correct lowering: no active relation crosses the partition. Unary constraints are local. Thus the solution set is exactly the Cartesian product of the three local solution sets. Sound GAC retains every satisfying assignment. The inherited direct-extension rule skips only locally impossible prefixes; restricting reset and carry to the current component preserves increasing lexicographic order in its local coordinates. Each component therefore finds its lexicographically first satisfying rank tuple or exhausts. If any is empty the admitted formula is UNSAT. Otherwise their combination is globally satisfying and lexicographically first in the original interleaved coordinate order: at the first differing coordinate, the corresponding component's lex minimum cannot be larger than the alternative. Witness projection is unchanged. The physical blank refusal for an outside-class input is indistinguishable from an admitted UNSAT refusal at the terminal symbol alone; the host ledger explicitly labels these separately. A crossing SAT input is NOT classified as UNSAT. No general fallback dispatch is implemented; use D6C separately for general normalized instances.

## Component and certificate theorem

For any disconnected finite constraint graph with component sizes s_i and at most m values per coordinate, independent exhaustive search needs at most sum_i m^(s_i) local complete candidates, rather than product_i m^(s_i). This is a general source-level factorization fact; the physical implementation here only covers the fixed three-triple partition. Its unconditional candidate ceiling on admitted genuine inputs is 3m^3, regardless of first-factor functionality, compared with m^9 for general enumeration.

Let r_i be the number of roots under the stronger D6C first-active-factor certificate restricted to component i, and r_max=max_i r_i. Apply the same charging argument to the three coordinates of each component: each root coordinate contributes at most m^(r_i) failed trials, and each determined coordinate at most 3m^(r_i), plus at most one successful local trial. Thus C_i<=min(m^3,1+9m^(r_i)); summing gives C<=min(3m^3,3+9 sum_i m^(r_i))<=min(3m^3,3+27m^(r_max)). This is a bound on complete candidate visits, not physical work per visit. Functional certificates are independently checked by host reference, not used for the actual physical guard or branching. The fixed-partition admission itself does not require any functionality.

Under inherited macro assumptions use N<=S+35m+1479<=2S, T<=131072 S(C+(full?m:1)+1), W<=(20N+12)T+6. Charge the physical crossing guard within one extra S-scaled allowance; component scans still traverse the full stream, so no reduced per-trial scan cost is claimed. Use producer 4P+32L, bridge 128S^2, projector 256S^2, S<=L/16 and L>=4096m^3. With C<=3m^3, total<=2^21 m^3 L^2<=512L^3. For r=max(1,r_max), C<=3+27m^r and C+m+1<=30m^r for m>=2; (20N+12)<=41S. Same total allowance <=2^21 m^r L^2 follows and gives:

| admitted class | conditional total bound |
|---|---|
| max component roots <=1 | 131072 L^(7/3) |
| max component roots <=2 | 8192 L^(8/3) |
| all admitted three-triple partitions | 512 L^3 |

These are conditional source-level physical bounds and exact arithmetic audits, not mechanical macro proofs or actual cubic admission. General fixed-nine D6C still has conditional O(L^5) worst-case cost. No unrestricted SAT reduction or P versus NP theorem.

## Independent audit and measurements

434 fixtures, 868 logical mode executions. Independent union-find decomposition reference enumerates true connected components and checks exact solution count and original lex witness against the existing exact host oracle on all fixtures. Admitted 652 mode executions: 606 valid SAT witnesses and 46 exact UNSAT refusals. Outside-class 216 mode executions: one SAT fixture for every crossing scope (108 scopes), tested in both modes; all guard refusals occurred before domain initialization/candidate attempts. Outside-class refusals are not counted as UNSAT. Independent relation-based trace oracle matches 2736 candidate visits and 902 conflict scopes. All 652 admitted executions satisfy audited max-component root bounds, with observed max-root counts [0,24,26,602] for r=0,1,2,3. 20034 domain/mode arithmetic evaluations per envelope (general partition and 1/2/3 maximum roots), 80136 in total. No correctness discrepancies in the executed cases.

| independent equality triples (alternating pins) | m | D6C trials | D6D trials | D6C worker clock | D6D worker clock |
|---|---:|---:|---:|---:|---:|
| SAT |2|46|18|1149574474|921521390|
| SAT |3|187|33|4599003252|1629523556|
| SAT |4|478|48|13935099340|2707134056|
| SAT |5|not compared|63|not compared|4426007888|
| empty formula |2|1|3|183311428|419632964|

SAT and UNSAT equality-triple cases have identical trial counts within each m, for both schedules. These worker costs are exact source-accounted clocks, not observed raw-selector m3..5 physical halts. Among 604 paired successful worker comparisons, 10 improve and 594 regress; two m5 SAT mode runs are unpaired. The guard and repeated full-stream scans dominate easy inputs. D6C remains the general baseline, and D6D is a specialized structural option rather than a uniform acceleration.

## Original-format observed physical execution

Pins all zero. Bounded m2 equality-triple SAT and full m2 equality-triple UNSAT separately executed original and quotient tables and exact one-short cutoffs. The initial combined SAT replay exceeded the interactive tool limit; separate actual replays succeeded.

| fixture/mode | physical transitions | head | span | result |
|---|---:|---:|---:|---|
| triple-2-sat bounded |957070224|46006|46819|SAT |
| triple-2-unsat full |950632628|38297|46664|UNSAT |
| cross-sat full |103614892|38227|46143|OUTSIDE_CLASS |

SAT witness 0101010101010101011111111110000; worker 921521072, N=1927, 79638 primitives, bridgeAt=34147955, workerAt=35066490, outputAt=956587562. SAT cutoff 957070223 TIMEOUT with no witness. UNSAT bridgeAt=34226129, workerAt=35144664, blankAt=950632627; cutoff 950632627 TIMEOUT without witness. Cross-sat is independently satisfiable, but the guarded specialized machine refuses; original and quotient halt clocks match. Interactive cross-sat cutoff not executed. New matrix registers twelve physical original/quotient/cutoff jobs (including both modes of cross-sat and m3 SAT), two native descriptor jobs (pinned bounded SAT and full UNSAT/cross-class refusal), and audit/governance. Current-head completion unconfirmed.

## Descriptor accounting

Initial unrolled guard and dispatch crossed the 2^21 quotient threshold. Shared scanner and directory-based admission restore 21-bit state numbers, at extra scan cost. Final producer 287874, bridge 279, projector 74, blank halt 1; four-bit segmented lowering, 20 tapes.

| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |8009|2871206|2055718|156234572|8613618|
| full |8008|2868926|2053995|156103624|8606778|

Both quotient sizes below 2^21. Descriptor increased relative to D6C (152774140 bounded bits). The choice to use fixed interleaved triples avoids general partition state explosion but leaves arbitrary graph decomposition unimplemented. Online forbidden-only deposition and actual macro/admission proof remain outstanding.

Next D6E: develop physical discovery or checked selection of multiple partitions, distinguish OUTSIDE_CLASS from UNSAT or implement a sound general fallback, and reduce repeated full-directory scans; verify D6D exact-head CI. Keep formal global routes blocked.
