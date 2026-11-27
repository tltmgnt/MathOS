# F038-REX-024D5D — Explicit worker time envelope and domain-four native fixture

Parent f75fc88f252ff807b8f12929b66d9f4769e31bbb. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Prior CI confirmation

[Exact-parent Proctor run 45932314395](https://github.com/tltmgnt/MathOS/actions/runs/45932314395), job 140287487991, concluded SUCCESS. The domain-four direct D2C preparation completed on the original 428744-bit selector and the separate physical initialization bridge completed on the actual literal suffix. The actual generated header and mask stream agree with the independently formatted C1 checkpoint. Exact phase accounting and isolated physical projection give the following complete-clock prediction for the unchanged compressed descriptor:

| Phase | Transitions |
|---|---:|
| Direct raw-selector producer and mask loader |6899458662|
| Physical bridge |1038194513|
| Worker (exact IR lowering clock model) |292006191202|
| Physical output projection |182917|
| Sum |299944027294|

Predicted actual halt head 568801, visited span 574997, 69-bit original-layout witness 000100100100100000010010010010000001001011111111001011111111001101000. The witness has already passed the original clause oracle in the phase audit. The full native run is not yet observed. Add the exact fixture to the admission generator and run the independent native ASCII descriptor interpreter at the predicted budget and one step short. The workflow is configured for up to 90 minutes because it performs two long physical executions. No fresh native domain-four completion is claimed. The corresponding sufficient program stage, conditional on confirmation, is 928446033 and min coefficient 48865581, versus cubic stage 57. Prior native m2 and m3 results remain verified.

## Explicit source-level worker time argument

Let m>=2, b=ceil(log2 m), B=9m+36m^2+84m^3, S=2(b+m+B+131), R=4(b+1)m^4, K=(14b+17)m^4. Let N be the conservative allocated logical capacity from D5C (including all 61 tapes, sentinels and separators). These bounds apply to genuine admitted checkpoints and the existing worker, not arbitrary forged data or a growing number of groups. Charge every finite IR read, write and unit move, not jumps. Use these deliberately generous per-iteration envelopes:

* Local bag: A=1000S+1000000+10000(b+1)m^4+50N.
* Edge/root record: D=1000K(4b+1)+1000000+50N.
* Selection bag: E=10000(b+1)m^4+100000+50N.
* Translation: F=10000m(b+1)+10000+10N.

Then T <= 9A+9D+9E+F+10000. The last constant includes fixed initialization/decision/phase-boundary overhead. The following source-level accounting justifies these coarse constants; it is not a mechanically checked cost proof.

Router: bound and mask decoding use at most six primitives per two-bit data token, plus fixed delimiter actions. There are at most seven selected mask fields, each found by rewinding and scanning the source once, skipping at most 129 fields with an eight-bit counter (less than 100 primitives per decrement/test), and copying the field. Header scans/ordinal skips and fixed bitmaps/IDs are bounded by fixed 851-symbol and 9-group control. Even allowing 1000S for all scans and copies and 1000000 for fixed control/countdown/metadata leaves substantial slack. Local rank enumeration: at most m^4 candidate rows, four binary rank comparisons/resets/increments, seven mask-head reads and projection-mask lookups, and at most four rank emissions per candidate. Each comparison uses at most 8(b+2) primitives including rewinds; increment/reset/emit at most 10(b+2) each. Each of seven slot-mask seeks reads at most 28 bits and rewinds at most 28 cells. All these costs fit within 2000(b+1) per candidate. A carry at c (zero-based from most significant coordinate) occurs at most m^(c+1) times. For a rewind with k<=r-c-1 projected lower coordinates, the nested unary scans plus flag actions cost at most 64 m^k primitives: at each depth a domain rewind and scan cost at most 4(m+2), and at the leaves the bounded flag action costs less than 8. Thus all rewinds across 4 carry positions and 7 slots contribute at most 1792m^4. Unary domain construction adds at most 100m(b+1). The local candidate term covers these sums. Clearing/reusing the fixed scratch tapes and copying the final relation are covered by 50N: a whole word clear including the initial and final rewind costs at most seven primitives per allocated cell, a whole word copy at most eight including both starting rewinds, and each affected tape is cleared/copied a bounded number of times in this outer controller step. Fixed metadata also fits the constant term.

Edge: projection visits each raw row twice and writes its key/payload tokens; each row has at most 4(b+1) raw symbols and at most 14b+17 keyed symbols. Sorting uses singleton runs and at most 4b merge passes per relation, since at most m^4 rows are present. In one pass, clearing, splitting, copying and draining are linear scans of the bounded run words. Comparisons advance or rewind at most one keyed record on each input and consume at least one record per comparison. For fixed b, fewer than 20(14b+17) primitives per comparison suffices even when equal keys require full scans. At most m^4 comparisons per pass; each scan/copy/clear needs less than ten primitives per symbol, with only a fixed number of scans of each word. A conservative 100K per pass per relation covers these operations. Initial projection/singleton preparation, dedup, semijoin and payload decoding together cost less than 500K: each record is copied/scanned a fixed number of times; dedup rewinds/clears only a single previous key, and each join comparison advances at least one of its streams. Therefore the 1000K(4b+1) term covers both sorts and the other merge operations. The outer controller clears ten scratch tapes, copies child and parent, and replaces parent after the join; their complete scan/clear/copy costs fit 50N, and constant header walks fit the fixed term. A root only tests emptiness and updates the decision bit. The nine-edge term is intentionally generous even though there are at most eight actual nonroot edges.

Selection: each retained relation is copied once into scratch and its rows are visited in sequence until the first compatible row. Per candidate, at most nine bitmap/group steps and at most four rank comparisons/capture/temporary erasures, all bounded by 1000(b+1) primitives including rejection scan; the bound allows ten times that. Scratch copy/clear and fixed addressing fit 50N and the constant term. No candidate retry crosses back to a previously rejected row. Translation compares counters, increments, reverses and emits at most 9m binary ranks and associated one-hot/cumulative bits. Their charged operations fit 10000m(b+1), append and rewind of the final output fits 10N and fixed overhead. UNSAT bypasses selection and translation except for its decision test.

For a simplified uniform envelope let U=(b+1)m^4. For m>=2, U>=32, S<=128U and K<=17U. From the explicit tape capacities (11 raw-relation words, seven keyed words, seven masks and bounded remaining words), N<=512U. Substitution in the four budgets yields T<=2^24 U(b+1). In particular local<=194850U, edge<=68000U(b+1)+56850U, selection<=38725U and translation<=6683U. The D5B segmented compiler inequality gives

```
N <= 512 (b+1)m^4
T <= 2^24 (b+1)^2 m^4
t_worker <= (26N+16)T+8 <= 2^39 (b+1)^3 m^8
```

These are conservative uniform source-level worker coefficients, not tight bounds. The machine and physical clock are unchanged. The physical producer, bridge and output projection are not included in this numerical envelope. Their explicit uniform constants and a whole-machine numerical stage bound remain open.

## Executed regression

An independent raw finite-IR interpreter observes actual localDone, edge, select and translate labels and counts every charged primitive. Compare its terminal 61 tapes/heads and primitive count with the exact compact clock auditor. All input mask blocks are independently checked against original clauses; source is actual C1 checkpoint plus observer-formatted stream, not a new native replay. All five cases passed:

| Fixture | Local | Edge/root | Select | Translate | Total T |
|---|---:|---:|---:|---:|---:|
| empty m2 |43845|2027|6089|1767|53728|
| edge SAT m2 |45763|9739|6388|1767|63657|
| edge UNSAT m2 |45471|4629|5|0|50105|
| forced m3 |178415|394564|14131|2827|589937|
| forced m4 |351482|812339|15798|3347|1182966|

All 305 tape capacities, exact worker clocks and original SAT witness checks passed; the UNSAT output remains empty. No observed disagreement. All 45 local generation boundaries were observed; SAT cases have 36 chosen-row boundaries. The initial label observer missed labels reached via jumps and was corrected before final regressions. Arithmetic checks of the BigInt simplified envelopes passed for every integer m=2..10000 and five larger powers/boundaries (10004 evaluations); these are arithmetic checks, not executions of huge input instances.

| m | Explicit T envelope | Explicit physical worker envelope |
|---:|---:|---:|
|2|75908400|16609213370408|
|3|466730040|527745658129208|
|4|1375737760|4604982240768328|

The actual m4 worker clock remains 292006191202; the upper envelope intentionally exceeds it by orders of magnitude. Current-head CI and native m4 execution unconfirmed at commit.

Next D5E: confirm full native domain-four replay and exact cutoff; audit explicit physical producer and bridge constants and output projection envelope, then combine with the fixed descriptor length to derive an explicit *eventual* restricted cubic threshold if justified. Main and PR #248 unchanged. Global routes 0/4, Omega obligations 0/6.

Reproduce:
```sh
for case in empty edge-SAT edge-UNSAT m3-forced m4-forced; do
  node mathos/research/f038_rex_width_three_time_envelope_audit.js "$case"
done
p=mathos/research/f038_rex_width_three
node --max-old-space-size=6144 "${p}_admission.js" descriptor > /tmp/w3.desc
node "${p}_admission.js" fixtures | grep '^m4-forced ' > /tmp/w3-four.fixtures
g++ -std=c++17 -O3 "${p}_native.cpp" -o /tmp/w3-native
/tmp/w3-native /tmp/w3.desc /tmp/w3-four.fixtures > /tmp/w3-four.out
python -m mathos.research.f038_rex_width_three_native_verify /tmp/w3-four.fixtures /tmp/w3-four.out
```
