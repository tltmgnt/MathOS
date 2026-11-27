# F038-REX-024D5B — Native domain-two confirmation and exact physical clock accounting

Parent 2bf73069f9775ef87c3da787ef7365738deecc78. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Prior native workflow evidence and failure

[Exact-parent Proctor run 45928065708](https://github.com/tltmgnt/MathOS/actions/runs/45928065708), job 140274006024, concluded FAILURE. The small C++/original Python tape_run control and malformed descriptor controls passed. The actual compressed ASCII descriptor was streamed and parsed natively: 928445994 bits, 10922894 nonhalting states, 32768682 rules. The native domain-two step passed all four original-selector cases including one-step-short cutoffs, and the imported original Python pool/valid verifier passed the two SAT words:

| Fixture | Native clock | Head | Span | Result |
|---|---:|---:|---:|---|
| empty |825112955|57932|58961|verified SAT|
| edge SAT |1297519076|58877|59907|verified SAT|
| edge UNSAT |665681141|57907|58907|blank|
| K5 refusal |27879501|37913|39346|blank|

Total 2816192673 completed native principal transitions (excludes cutoffs). The forced m3 step failed with "halt witness mismatch" after the previously guessed 50000000000-transition budget. Governance step skipped. Do not call the full previous workflow passed. The new exact phase accounting below explains the insufficient budget; it is not a native replay of that failed run.

## Exact worker clock model

Implement a source-level independent finite-IR interpreter with charge accounting for the actual unchanged-symbol row compiler (D4B), not a host trace-fed transition machine. The physical width is w=5. For each logical block, unchanged right costs w, unchanged stationary a=2w-2, any left b=3w-2, changed right b. This follows from decoding w bits, the unchanged-symbol movement tails, or rewriting w bits with the final alignment move. The existing exact quotient preserves these physical clocks.

Let N count all currently allocated logical symbols including G and all separators, and let p be the marked cell's zero-based logical position. A virtual read, write or left move costs p*w+2a+p*b. A right move into existing storage adds 2b. A right move extending a segment inserts a marked blank at the old separator, shifts the suffix and writes E into a fresh block. Each suffix carry comparing adjacent original symbols costs w on equality or b on difference. If their sum is c, the growing move costs p*w+2a+(N+2)*b+c. There are N-p-2 such adjacent comparisons. All ordinary primitives return to G, and the successful halt costs a. The growth is counted exactly and preserves the full allocated terminal encoding including trailing virtual blanks and head marks.

Thus c <= (N-p-2)*b; since w<=b, growing cost <=2b*N+2a. Ordinary costs satisfy the same bound (p<=N-2). If T is the number of virtual primitives and Nmax the final allocated size (monotonically nondecreasing), the explicit physical worker envelope is (26*Nmax+16)*T+8. This is an explicit coefficient for the segmented simulator only. A uniform explicit bound for the producer and for T(m), Nmax(m) throughout the actual full worker remains open. This is not a new uniform numerical cubic-stage threshold.

## Executed phase accounting

Run the direct physical loader on the original selector, independently replay the physical bridge on its literal suffix (blank symbols represented by 2 in the observer), run the independent finite-IR exact clock counter, and execute the physical projector on the reconstructed terminal encoding. These are separate executions; the clock sum follows by the verified composition and exact lowering formulas, not a measured full native run. On all three previously completed m2 cases the predicted total clock, head, span and word match the original native replay exactly. The trailing blank is not counted as visited for SAT output span. The initial span observer was off by one and corrected before the final audit.

| Fixture | Producer | Bridge | Worker clock | Projection | Total |
|---|---:|---:|---:|---:|---:|
| empty |104551138|48370247|672161844|29726|825112955|
| edge SAT |104556548|48370247|1144561610|30671|1297519076|
| edge UNSAT |104556548|48370247|512737138|17208|665681141|
| forced m3 |1191370586|246830893|71101906698|91613|72540199790|

| Fixture | Virtual primitives | Initial N | Final N | Segment growth | Worker envelope |
|---|---:|---:|---:|---:|---:|
| empty |53728|2971|3446|475|4814673544|
| edge SAT |63657|2971|3635|664|6017241590|
| edge UNSAT |50105|2971|3441|470|4483495618|
| forced m3 |589937|6545|12252|5707|187935050224|

All four phase audits executed in JS V8 with per-instruction bound checks and original clause verification. The m3 forced case predicts physical halt head 229473, span 232294, and original word 00101010000110001000101010001111101111101111110100 (already verified in IR, now independently recovered by the isolated physical projector). Its 3807285 equal and 1529139 changed suffix carry actions are included. The exact worker clock alone exceeds the previous 50-billion budget. The fixture now sets the predicted full clock as its exact budget, with head/span expectations and the native one-step-short cutoff. Corrected full native execution is unconfirmed.

## Stage ledger and next step

For the fixed quotient ell=928445994 and predicted m3 SAT clock t=72540199790, the derived sufficient program stage is ell+37=928446031 and min coefficient ceil(stage/18)=51580336. It is conditional on the predicted clock being confirmed by native replay; not an observed first successful universal stage. The native m2 slots remain 928446024 and 928446025. The built-in covers m2,m3 at cubic stages by the earlier arithmetic, without executing exhaustive search. Uniform finite cubic coverage remains open.

Next: verify the corrected native run, extend domain-four coverage and bound every virtual resource loop and producer phase explicitly, or reduce actual compiler sweep overhead. Main and PR #248 unchanged; all four global routes and six Omega obligations remain open.

Reproduce:
```sh
for case in empty edge-SAT edge-UNSAT m3-forced; do
  node mathos/research/f038_rex_width_three_phase_audit.js "$case"
done
```
