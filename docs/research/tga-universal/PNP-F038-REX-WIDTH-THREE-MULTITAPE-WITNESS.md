# F038-REX-024C4 — Charged width-three original Boolean witness recovery

Parent 5adc15a65fb0cc298be05c8f37d81a593c29b33b. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [C3 Proctor run 45905102524](https://github.com/tltmgnt/MathOS/actions/runs/45905102524) passed.

## Implemented interface and boundary

Preserve C3 and its verified C1 single-tape producer. The new worker consumes the literal marked C1 checkpoint snapshot and uses 176 fixed tapes (C3's 155, one pin tape, nine chosen owner-rank tapes, nine selected-row tapes, and two Boolean output tapes). No host-generated ranks, rows, separator keys, domain size, or assignment are supplied. The only host handoff is the unchanged snapshot observer; its creation and input loading are not charged physical bridge operations. This worker is a charged finite-controller multitape microprogram, not a compiled transition table. Its legitimate C1 checkpoint precondition remains. Structural refusal or admitted UNSAT emits no witness, and cutoff never publishes a partial witness. A successful run writes exactly n=19m-7 bits on X and positions its head on the first bit. This is the original Boolean bit layout, but on a multitape output tape, not the original single-tape interpreter interface.

## Charged selection

After C3 finalizes every retained relation and checks independent roots, visit bags in reverse elimination order. Each later neighbor's owner has already been selected. On the current relation tape scan rows sequentially; compare the complete separator fields, in sorted group-ID order, against the chosen owner-rank tapes, rewinding each relevant rank tape before comparison. A matching row is rewound by scanning backward to the previous semicolon or left sentinel, then copied to its selected-row tape, and its owner field to the previously empty chosen rank tape. Stop at the first compatible row in the actual retained stream order. For roots the condition is vacuous. No key enumeration, random access or host decoding of unbounded ranks occurs. Every bit read, write and unit head move is charged. The fixed nine-group header data is finite-control information. The selected-row tapes are evidence storage, not required for subsequent comparison.

Correctness by reverse elimination induction: for a root a retained row exists by the decision pass. Every nonroot's later neighbors occur in its parent bag, and their owner values agree with the parent row by induction and running intersection. Since the parent row survives the child's semijoin, there is a retained child row agreeing on the entire separator. The first such row exists and its owner rank extends the partial assignment while preserving all bag agreements. Every selected factor belongs to its earliest eliminated variable's bag and is satisfied by the chosen tuple. Thus all nine recovered ranks jointly satisfy the original latent factors. This argument is constructive but not mechanized.

## Charged Boolean translation

During load copy the actual pin block 36 into a fresh tape in original order. For each group ID 0..8, copy the selected MSB-first rank backward into the LSB-first binary counter lane. Compare to M=m-1, then enumerate the second binary lane from 0 to M. Output X_g,i=1 exactly when i equals the chosen rank; for i>0 output Y_g,i-1=1 iff the chosen rank is <=i. Comparison scans from least to most significant bit, updating its finite comparison result on each differing bit. Physically append the nine X blocks, nine Y blocks, all m pins and two zero guards, in that order. Check pin length against the unary domain tape. Rewind X to its first bit. Every original assignment bit is constructed on tape. The observer reads this tape only after completion; neither the original verifier nor expected assignment controls the worker.

## Resource audit

C3 local generation and bottom-up merge dominate at O(m^4 log^2 m) charged operations and O(m^4 log m) visited cells. For selection, each of nine retained relation tapes is scanned at most once until a compatible row; each row has at most four fields and each comparison rewinds at most O(log m) bits. The selected row is copied once. Thus selection adds O(m^4 log m) time and O(log m) cells for the fixed number of chosen/selected tapes. Translation adds O(m log m) time and O(m) output/pin cells. The whole worker retains O(m^4 log^2 m) time and O(m^4 log m) space.

For original selector length L=Theta(m^3), a standard quadratic sweeping simulation of the fixed-tape worker alone would give O(L^(8/3) log^4 L). This is still conditional on a concrete finite-controller compiler, charged bridge from the existing C1 single-tape checkpoint (do NOT quadratically simulate C1), and final ternary projection to the original halt-head interface. It is not a measured single-tape clock, explicit finite-stage guarantee, or unrestricted SAT result.

## Executed differential verification

Eleven completed original-selector producer/worker pairs across m=2,3,4. Ten admitted cases: seven SAT, three UNSAT; one satisfiable K5 structural refusal with 96 models. Compare exact local and retained streams to independently decoded original factors and stable support filtering, then compare every selected row to an independently computed first-compatible row in reverse order, every rank to the owner projection and every physically written witness bit to the original layout and clause verifier. Exhaustive m^9 latent model counts independently verify decisions, including 262144 assignments for m=4. Zero observed disagreements.

| Fixture | m | C1 transitions | Worker steps | Models | Result |
|---|---:|---:|---:|---:|---|
| empty |2|26776221|398854|512|witness|
| K4 |2|26798486|508030|160|witness|
| greedy trap |2|26957865|1168424|52|witness|
| joint-three UNSAT |2|27517677|438938|0|no witness|
| joint-three SAT |2|27517709|462948|128|witness|
| disconnected UNSAT |2|27517709|460775|0|no witness|
| unary UNSAT |2|26776221|397017|0|no witness|
| K5 SAT refusal |2|27879500|116890|96|refusal|
| greedy trap |3|273187601|10173528|6816|witness|
| forced four-bag |3|272976247|2075560|1|witness|
| forced four-bag |4|1526876345|5232769|1|witness|

Totals: 1055758 raw bits, 2290781581 C1 transitions, 21433733 worker operations (25786 selection and 15508 translation), 34 semijoins, 1242 candidate tuples, 709 local rows, 698 live rows, 63 selected rows and 293 original Boolean bits. Do not sum the separate machine-model clocks as a single-tape runtime. Eight exact budget cutoffs including load, selection, translation boundaries and one step before completion, and four malformed checkpoint controls passed. Exact joint-three SAT worker completion 462948. Current executions in JS V8. Current exact-head CI unconfirmed at commit.

The new m=4 fixture forces ranks (3,2,1,0,3,2,1,0,3), with a genuine four-variable K4 bag on groups 0,3,6,8. Physical producer completes in 1526876345 transitions, worker in 5232769 steps, all 69 Boolean bits valid. This is a complete m=4 producer/snapshot/multitape witness execution, not an original-format ternary witness run. It does not complete the earlier width-two m=4 test.

## Next bounded stage

024D1: design and implement the actual fixed-controller transition compilation / charged sweeping simulation and checkpoint bridge, preserving the native width-two witness and quotient. A trace-driven emulator that takes host-generated commands is not a substitute for a standalone machine. Explicit finite stage admission and all unrestricted routes remain open. Main unchanged.

Reproduce:
```sh
for suite in small larger four controls; do
  node mathos/research/f038_rex_width_three_multitape_witness_audit.js "$suite"
done
```
