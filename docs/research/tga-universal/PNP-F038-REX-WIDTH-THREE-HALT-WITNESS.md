# F038-REX-024D4B — Original halt-head constructive width-three witness

Parent c3bc5d47513593a36ba0fe5f8eec96c701735e16. Research branch only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. [D4A exact-head Proctor run 45923536225](https://github.com/tltmgnt/MathOS/actions/runs/45923536225) passed, including fresh standalone-worker terminal comparisons.

## Implemented original interface

Extend the physically composed D4A table with a charged single-tape output projector. Original raw selector is the only runtime input. No host decoding, tape transfer or witness construction enters the computation. On SAT the actual halt head points to the first bit of the contiguous original Boolean assignment, followed by exactly n=19m-7 bits in total and then blank. On UNSAT and structural/normalization refusal the actual halt head is blank. The independent verifier interprets n consecutive bits beginning at that head, as in the original tape_run interface; n is used only for observation, not computation. Original Python tape_run has not itself been executed on this very large descriptor.

The new row compiler distinguishes successful finite-IR halt from reject or malformed logical states by separate external exit IDs. All logical actions and the five-bit codebook are otherwise unchanged. The final composer relocates the producer, bridge, worker and projector state IDs into one fixed table. Only the producer's dedicated accepted exit enters the initializer. Only the initializer's success enters the worker. Only the worker's success enters the projector. Every other producer/initializer/worker halt goes through a single stationary blank-write transition, ensuring no Boolean word can begin at that halt head (n>=1). The projector's own error exits also write blank. This corrects inherited single-bit normalization status exits for original verifier purposes. No assertion is made about arbitrary forged encoded worker configurations; the descriptor constructs its legitimate configuration from the raw input.

## Output projection

At worker success, the head is at encoded G. Read aligned five-bit logical symbols, count 57 D delimiters, and enter witness segment X (index 57). Skip its left sentinel. Read each marked or unmarked binary content symbol. The entire encoded worker region is contiguous binary; the physical blank just after E separates it from the new raw output. To copy a bit, remember its value in finite control, temporarily blank the first bit of its encoded block, scan right to the boundary blank, scan the growing raw output and append the bit. Return left to the boundary and then left to the unique temporary blank. Restore the original block first bit and advance to the next aligned encoded symbol. The fixed codebook has the same first bit for marked and unmarked variants of each binary value. At virtual blank, scan to the end of the encoded region, step right over the boundary blank and halt without changing the scanned cell. A genuine UNSAT worker leaves X empty, hence this cell is blank. All copied blocks are restored. The first output bit is unencoded, not a virtual head marker. Output length is guaranteed by constructive worker invariants, not by a host-provided counter.

## Executed evidence

| Component | Nonhalting states |
|---|---:|
| Producer |577884|
| Physical initializer |1768|
| Worker with separate exits |10767880|
| Output projector |1893|
| Blank exit |1|
| Total |11349426|

34048278 packed physical transition entries. The streamed original descriptor uses header 111, unary q, zero and q*3 fixed-width fields. An independent parser consumed every one of 964701214 serialized bits and range-checked and compared every entry against the composed packed table. This is an executed JS original-format round trip, not a native Python decode_tm run or a single materialized descriptor file.

| Fixture | Producer + bridge + worker | Projection | Total physical transitions | Halt head | Span |
|---|---:|---:|---:|---:|---:|
| Empty SAT |825083229|29726|825112955|57932|58961|
| Nonempty edge SAT |1297488405|30671|1297519076|58877|59907|
| Empty edge UNSAT |665663933|17208|665681141|57907|58907|

Three complete original-selector replays: 2788313172 physical transitions, including 77605 projection transitions. All producer/bridge/worker clocks equal the independently verified D4A clocks. Both 31-bit physical SAT witnesses (1010101010101010101111111110000 and 0110101010101010101111111110100) passed the original Boolean clause verifier, and the cell following each word was blank. UNSAT halted on blank. The observer reads actual contiguous cells from the physical halt head, without virtual decoding. The nonempty-edge SAT replay initially hit the interactive execution timeout, then completed after reducing observer-only phase bookkeeping. The packed physical table was not changed by this optimization.

Four full-table refusal controls: empty raw input (236 transitions), small malformed input (329), wrong domain (3157), satisfiable K5 structural refusal (27879501). All bypassed the bridge, halted on blank, and added exactly one transition to their inherited refusal clocks. A blank head is sufficient for no witness even if other cells retain data.

Five isolated output-projector controls: empty output, single one, single zero, 31-bit and 50-bit words (923,1061,1061,10781,22523 transitions respectively). All exact words/heads passed. Fifteen isolated budget cutoffs (0,1,t-1 for each) returned TIMEOUT. These are synthetic encoded-output fixtures, not full domain-three raw-selector computations. No observed disagreement in completed tests. No full domain-three physical witness replay, full-table exact-budget cutoff near final halt, native Python original interpreter replay or current-head CI completion is claimed. Tests here ran in JS V8.

## Resource audit and next mission

For the restricted normalized family L=Theta(m^3), the existing producer and physical bridge cost O(L^2) time. The existing composed worker uses O(m^8 log^3 m) transitions and O(m^4 log m) span. Each of O(m) output bits performs an O(m^4 log m) shuttle, so the new output stage costs O(m^5 log m) time and O(m) additional space. The entire raw-selector-to-original-halt-head machine has derived O(L^(8/3) log^3 L) time and O(L^(4/3) log L) space on legitimate width-three instances. This uses the established restricted worker invariants; not a universal SAT bound or a mechanized proof. Structural refusal is not a proof of UNSAT. No finite cubic threshold is asserted. The descriptor overhead is very large.

Next 024D5A: independently replay the original codec/clock semantics in a memory-bounded native implementation, compress the fixed descriptor with exact homomorphism checks if practical, extend physical domain coverage, and audit explicit stage admission (ell+ceil(log2 t)) separately from asymptotic admission. Main and PR #248 unchanged. All four global routes and six Omega obligations remain open.

Reproduce:
```sh
for suite in projection empty sat unsat refusal codec; do
  node --max-old-space-size=6144 mathos/research/f038_rex_width_three_halt_witness_audit.js "$suite"
done
```
