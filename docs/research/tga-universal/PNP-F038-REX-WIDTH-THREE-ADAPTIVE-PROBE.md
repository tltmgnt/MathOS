# F038-REX-024D6I — Bounded direct probe and exact checkpoint resumption

Parent D6H 2cb58808db0f1034cce317439a571ea82b6124b7. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6H final-head Proctor 46045406270](https://github.com/tltmgnt/MathOS/actions/runs/46045406270): all 19 jobs completed successfully, including both hard m3 SAT and native jobs. D6G also verified 15/15 (46041104910).

## Physical scheduling and checkpoint invariant
After sound GAC and original active-scope graph discovery, disconnected systems retain D6H direct component search. Connected systems initialize each surviving rank word to its first allowed value and run the ordinary joint lexicographic candidate engine. A20 is the probe flag, A21..24 are a four-slot failed-candidate budget. Only the fourth complete failed validation suspends the search; earlier conflicts use unchanged direct extension. SAT or exhausted search before that suspension is final. The probe bound is on complete candidates, not every intermediate rank inspected by direct extension.

On fourth conflict, CQ is positioned immediately after the selected forbidden-row token and CD after its scope record. R1..R3 and G0..G8 (logical tapes 10..12 and 1..9) retain their exact data and cursor positions. Residual graph discovery modifies Q/D, graphTape and A only; it does not alter candidate rank words, local mask/directory, or their heads. Try prefix {0}, then {0,1} only if the former does not split, exactly as D6H. If a split is admitted, clear the selected x marker in each domain word (restore allowed bit 1), reinitialize to first allowed ranks, then execute D6H prefix conditioning. This discards probe enumeration but never changes surviving domains. If neither splits, rebuild the original graph, restore all nine current membership markers, and jump directly to the saved conflict handler. No candidate replay, no rank reinitialization, no reloading compact local factors. The interrupted conflict is processed exactly once. All probe-state flags clear before normal continuation. Twenty tapes retained.

## Source-level correctness
Under genuine normalized input, canonical stream, sound GAC and correct lowering, the direct prefix probe is an initial segment of complete lexicographic search. Any returned SAT witness is the global lexicographic minimum; true direct exhaustion implies UNSAT. A suspended fourth conflict is neither acceptance nor exhaustion. If conditioning is admitted, restarting from the original surviving domain product preserves completeness and global lexicographic minimum by D6H's prefix theorem. If conditioning is not admitted, restored current membership and preserved G/R/CQ/CD data and heads imply the same direct-extension transition sequence from the failed tuple as without the pause. No skipped or duplicated candidate in the resumed branch. Graph probes use actual canonical scopes. No host plan or witness is provided. This proof is restricted to normalized inputs and relies on correct physical lowering; it does not establish malformed-input status semantics.

## Conditional resource envelope
Let h in {1,2} be an admitted prefix length, d_g surviving domain sizes, P=product_{g<h}d_g, B_j residual blocks, D_j=product_{g in B_j}d_g. At most four direct candidate visits precede conditioned execution; the combined visit ceiling is V<=4+P(1+sum_j D_j), hence <=4+m^h(1+sum_j m^|B_j|). A probe-completed connected instance visits at most four complete candidates, plus at most three direct extensions. Direct extension may scan O(m) ranks per conflict and validation costs O(S+m+1) primitives. No-split direct resumption preserves the original joint candidate ceiling (no repeated initial four); disconnected inputs retain the D6H component ceiling. Additional graph scans and reset cost O(S+m+1) for fixed nine coordinates. With p GAC passes, conditional primitive cost for admitted cases is O((p+1+P)(S+m+1)+sum_{a,j} C_aj(S_j+m+1)). High-water span remains O(S+m+1). Under inherited physical macro bounds, S=O(L), L>=4096m^3 and p<=4 bounded or <=9(m-1)+1 full give conditional O(L^2(p+1+V)); admitted exponent 2+(h+b)/3 for b=max |B_j|. Probe completion has conditional O(L^2(p+1)); connected direct fallback remains O(L^5). Constant probe overhead preserves the D6H worst-case structural exponents, but not a uniform runtime gain. No universal cubic admission or unrestricted SAT reduction; fixed-nine normalized search is already polynomial in this explicit input encoding.

## Independent audit
677 fixtures (673 inherited plus four hard two-prefix cases), both modes: 1354 executions, 1114 SAT,240 UNSAT. 252 probes,642 probe candidates,178 probe-completed SAT,0 probe-completed UNSAT,74 suspensions. 68 conditioned (16 one-prefix,52 two-prefix;50 SAT,18 UNSAT), six exact direct resumptions,1068 nonconditioned after propagation (including probe successes),218 early sound refusals. 224 prefix assignments,6762 graph/component checks,3698 candidate and local stream/directory comparisons,2040 conflicts,22 prefix-only conflicts,84 first-block reuse events. Independent decoded-relation oracle checks the full trace, exact lex witness/status and D6H parity. In each direct resumption it also compares saved tape contents and head positions on G/R/CQ/CD and restored membership. No observed discrepancy; six checkpoint tests are finite evidence, not proof for arbitrary encodings.

D6H paired primitives 58250531 vs D6I 50437375 (7813156 fewer, 13.41% reduction). 184 improved,952 regressed,218 tied. Initial restart-only D6I (228bef5e36c061535fc92fc957e6de56b679f95b) had 50552971 primitives and3722 visits; exact resumption removes24 duplicate visits and115596 primitives. These aggregate comparisons are logical primitives, not aggregate physical runtime.

| fixture | D6H SAT worker clock | D6I SAT worker clock |
|---|---:|---:|
| easy prefix star m2 |1408309184|428946310|
| easy two-center m2 |1611932914|482271660|
| easy two-center m3 |2126374778|663662892|
| easy two-center m4 |3236412646|1056983888|
| no-split residual chain m2 |1012454076|974451262|
| hard two-prefix m3 |9450537036|10278626610|

These are exact source-accounted worker clocks. Hard m3 SAT visits82 ->86 due to the four failed preliminary candidates. The budget of four is an engineering heuristic, not a proved optimal choice. Hard instances pay extra work and disconnected instances incur small control overhead; no universal speedup.

## Physical evidence
| mode | IR | original states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |13777|5238407|3592767|283828597|15715221|
| full |13776|5236127|3591044|283692480|15708381|

Four-bit segmented encoding,20 tapes,22-bit quotient IDs. Bounded descriptor grows 6041841 bits (2.18%) over D6H; 21-bit target unmet.

| fixture/mode | raw halt transitions | head | span | witness |
|---|---:|---:|---:|---|
| easy two-center bounded |519326330|47544|48375|1010101010101010101111111110000|
| unsplittable residual chain full |1009105870|47166|47969|1010011001100110011111111110000|

Original and quotient match exact oracle witnesses, transitions, head, span and output symbols; one-short cutoffs 519326329 and1009105869 return TIMEOUT/no witness. Second replay initially exceeded combined interactive limit; separate original and quotient/cutoff calls succeeded. Actual worker clocks482271660 and974451262 match source accounting. New-stage physical UNSAT and conditioned branch replays are registered in CI, not claimed already physically verified at this checkpoint.

## Verification schedule and next mission
Dedicated Proctor registers one audit,20 physical mode/fixture jobs and two native original-format jobs. Native verifier checks expected descriptor length, entries, witness validity and exact one-short cutoff through inherited C++ interpreter. Final D6I CI completion unconfirmed at publication.

D6J: physically slice selected-prefix row intervals, including runs crossing slice boundaries, preserve lexicographic rank extension and exact native replay; investigate persistent multi-block caches and domain-sensitive scheduling. Keep D6H baseline; conditional bounds are not unrestricted complexity proofs. No main or PR #248 changes, no promotion.
