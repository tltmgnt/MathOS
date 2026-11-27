# F038-REX-024D5L — Sparse physical propagation and full-convergence mode

Parent 4068cf21f38ae92e72183b2943c67b4d5e73ac8b. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## D5K prior verification

Exact-head [Proctor run 45944591207](https://github.com/tltmgnt/MathOS/actions/runs/45944591207) completed all seven jobs successfully. Independent native original-format replay, Python original clause verification and governance passed. All five physical replays and quotient/cutoff checks passed. Ternary-three-rank m3 physical replay: t=6969014689, head=195739, span=198554. Native ternary-chain: t=2235614856, head=53792, span=54821.

## Physical sparse index

D5L uses 21 logical tapes, with a new 120-cell activity tape C between propagation scratch and the input stream Q. After unary initialization, a physical prepass consumes the canonical 36 binary and 84 ternary mask fields. Each entry is 1 exactly when at least one forbidden tuple token (01) is present, otherwise 0. This is computed from the actual producer stream by finite IR, not a host-supplied annotation or a graph oracle.

During either support propagation or final candidate validation, C and the static scope table D are reset together. Each scope consumes one activity bit. For inactive fields the worker advances over the fixed-size scope record and reads the field to its delimiter, but never initializes rank cursors, projects supports, updates domains or performs tuple-by-tuple candidate checking. Active fields follow the existing D5K algorithm. The stream is still dense and fully traversed as needed; the optimization does not claim sparse physical storage, constant-time random access or avoidance of every mask read.

Correctness: all-zero forbidden masks represent the universal relation. For nonempty domains their support projections equal the participating domains, so skipping them is an identity update. A universal relation also admits every candidate tuple. Empty unary or updated domains already trigger refusal before a later identity update could matter. Consequently the bounded variant has the same per-sweep domain changes, stopping condition, candidate ordering and accepted witness as D5K on genuine normalized streams. This equivalence is argued at source level and checked on finite fixtures, not an all-input mechanically verified bisimulation.

## Two independently compiled modes

Bounded retains D5K's four-sweep cap. Full repeats the same sparse generalized arc consistency (GAC) sweep until a complete unchanged sweep. Both retain at most 46 radius-two first/second-rank candidate attempts and final checks of every represented constraint. Full convergence is not complete SAT search; the radius-three SAT refusal remains. The full mode guarantees a GAC fixed point for nonempty paths under the inherited normalized-input semantics. Each changing sweep removes at least one value and never restores one, so at most 9(m-1) changing nonempty sweeps and one unchanged sweep are required. A reverse-chain fixture requires nine sweeps rather than the bounded four, and the full domain words match the independent oracle.

| metric | D5K dense bounded | D5L sparse bounded | D5L sparse full |
|---|---:|---:|---:|
| IR instructions |6940|7030|7029|
| logical tapes |20|21|21|
| logical width |4|4|4|
| original physical states |2455137|2497848|2495568|
| quotient states |1841457|1873921|1872198|
| descriptor bits |139950736|142418000|142287052|
| all-transition checks |7365411|7493544|7486704|

Both new quotients remain below 2^21. Producer stays at 230467 states, bridge 291, projector 74, blank halt 1; worker 2267015 (bounded) or 2264735 (full). Smaller full descriptor results from removing the bounded budget-control path, not universal dominance.

## Conditional resource accounting

Use prior L, H, m, S with S>=1936 and 168m^3<=S<=L/16. New storage adds a fixed 120-cell activity index and three segment overhead blocks to D5K, so N<=S+35m+1602<=2S. Prepass scans the tokens once and appends 120 bits, with <=16S primitive allowance. The scope-index read/advance and reset add fixed work per scope/sweep; inactive mask scanning is no more expensive than the old per-row support macro. Retain a conservative 256S allowance per sweep, with slack for the 120 indexed dispatches and resets, and 256S per candidate attempt. These rely on inherited source-level macro estimates, not mechanically verified costs. Bounded T<=32768S covers four sweeps, 46 candidate attempts, index construction, counter traversal and setup/output. Full T<=32768mS covers <=9(m-1)+1 nonempty sweeps and the same fixed candidate/setup costs. For four-bit lowering W<=(20N+12)T+6<=2097152S^2 in bounded mode and <=2097152mS^2 in full mode. With prior P<=35000L^2, I<=128S^2 and O<=256S^2, the bounded aggregate <=2^16 L^2 and full aggregate <=2^16 m L^2 <=2^12 L^(7/3) using L>=4096m^3. These are conditional successful-path ceilings, not unrestricted complexity claims. The unchanged producer and generic compiler premises remain inherited.

Cubic admission: bounded ell=142418000, sufficient H>=ell+16=142418016. Full ell=142287052 and ceil(log2 t)<=12+ceil(7H/3); ell+12<=floor(2H/3) suffices, yielding H>=ceil(3(ell+12)/2)=213430596. Thus full propagation gives a subcubic envelope but a larger sufficient admission threshold than bounded. Neither threshold makes measured inputs admitted at cubic stage.

## Executed finite evidence

68 original raw-selector cases (8 named and 60 seeded) checked against independent support and candidate oracles in both modes; all bounded status/witness results equal D5K. 92 complete activity indices checked against actual decoded forbidden relations, 39 witnesses in each mode, 28 empty-domain outcomes, one other refusal, one bounded cap case; full gained/lost zero witnesses on this sample. 78 successful exact worker clock and storage accounting checks, 20034 arithmetic evaluations across both envelopes. Bounded sparse worker improved clock on 22 of the 39 successful cases, not all. Nonempty domain words matched the corresponding independent oracle. This audit differs from the D5K fixture set (includes all-active and empty-unary), so raw totals are not direct cross-mission coverage comparisons.

Worker clock accounting, pins alternating [0,1,...]:

| case | active scopes | D5K dense | D5L bounded | D5L full |
|---|---:|---:|---:|---:|
| empty m2 |0|1229603364|905168946|905168946|
| ternary-chain m2 |3|2115024316|1279354488|1279166572|
| ternary-three-rank m3 |1|5636883658|5115765100|5115575546|
| reverse-chain-cap m2 |8|3957204778|2058360018|3916116954|
| all-active m2 |120|1222025940|1546275234|1546275234|

The all-active case shows overhead from index construction, extra tape and cursor traversal. The full reverse chain takes nine sweeps rather than four; bounded and full results are not assumed identical. The new modes do not dominate D5K in every case. The shared compact normalization controller is still unimplemented; D5I's direct producer is unchanged.

Fresh whole physical original-selector replay on the ternary-chain fixture with pins [0,0], independently compiled modes:

| phase | D5K dense | D5L bounded | D5L full |
|---|---:|---:|---:|
| producer |100021617|100021617|100021617|
| bridge |19693963|19740475|19740475|
| worker |2115023998|1279354170|1279166254|
| projection |875278|906274|906274|
| total |2235614856|1400022536|1399834620|

Both D5L original and quotient executions validated witness 0101010101101010101111111110000 at head 54284, span 55313, exact physical worker clock and one-short TIMEOUT with no witness (1400022535 and 1399834619). A combined interactive run timed out; split runs succeeded. Full reverse-chain convergence is verified at IR/oracle level; its physical replay is registered but not claimed completed. New CI registers ten physical cases, both native original-format descriptors and original verifier, and inherited governance. Do not claim D5L CI/native completion without evidence.

Next: optimize physical dense-stream traversal and scratch layout to reduce even inactive-field scans and dense-case overhead; investigate selector-preserving shared normalization; confirm D5L native and full-convergence physical replay. No main or PR #248 edits.
