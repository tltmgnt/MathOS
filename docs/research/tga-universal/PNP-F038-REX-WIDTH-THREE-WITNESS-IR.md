# F038-REX-024D3B2 — Standalone compiled constructive width-three witness worker

Parent b03a6eb4f5def93a6b5239cdbbcc97a6615e23f6. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [D3B1 Proctor run 45917934715](https://github.com/tltmgnt/MathOS/actions/runs/45917934715) passed.

## Implemented interface

Extend the compiled D3B1 retained forest, without changing its local generation or bottom-up merge instructions. Its final edge-dispatch blank branch now enters constructive recovery, conditional on the physically computed root decision. A zero decision halts with no witness. The input remains the literal genuine admitted D2C checkpoint header suffix and encoded mask stream on two preencoded virtual tapes. No host bag order, ranks, tuples, chosen rows, separator keys or witness bits enter the program. The producer still runs separately and its observed literal words initialize the worker. No charged physical raw-selector bridge is claimed.

There are 61 fixed virtual tapes: the original 45, nine owner-indexed chosen-rank tapes, a fixed group-dispatch tape, temporary rank tape, binary counter, X and Y output tapes, and two single-bit flags. Output X contains exactly the original 19m-7 Boolean bits, with its virtual head on the first bit. The physical halt remains at the encoded global sentinel G. The original witness-verifier interface requires a contiguous unencoded output at the physical halt head, so this is a standalone compiled original-layout witness worker, not an admitted original-selector witness program.

## Physical reverse-elimination selection

The metadata stream H is a sequence of nine fixed 20-bit records in elimination order. Its head is at the right boundary when the edge phase completes. Move left one cell; a left sentinel means selection is done, otherwise move left another 19 cells and copy that record into W. Read its owner nibble, copy the owner's retained relation to shared scratch P, retrieve its nine-bit bag bitmap from the owner-indexed table and construct an owner-only bitmap S.

For each candidate row scan the nine group IDs in increasing order using a fixed nine-symbol dispatcher and the bag bitmap. Skip absent groups; capture the owner field onto a temporary tape, and compare each other field bit by bit against its corresponding already chosen owner-rank tape, rewinding that tape before comparison. On disagreement scan to the next semicolon, erase the speculative owner rank, and try the next row. If all fields agree, commit only the owner rank to its previously empty chosen tape. Rewind H exactly 20 cells and proceed to the previous record. Stop at the first compatible row in actual retained order. No enumeration of separator keys or unbounded host variables. All reads, writes and moves are finite instructions.

For genuine C1/D2C input, the previously established subtree-feasibility invariant ensures that each root has a retained row when the decision is one. By reverse-elimination induction the later neighbors already have ranks; their joint assignment appears in a chosen parent row. Since the parent survived the child's semijoin, at least one child row agrees with that entire separator. The first such row extends the assignment. Running intersection preserves consistency and exact-once ownership ensures every original selected factor is satisfied. This is a constructive informal proof and differential evidence, not mechanized certification of arbitrary checkpoints.

## Original Boolean translation

M=m-1 remains on the bound tape from the last router pass. Traverse chosen ranks by ascending original group ID using the fixed dispatcher. Reverse each selected MSB-first rank onto a scratch LSB-first tape. Generate a width-matching binary counter from zero to M, compare the current counter with the chosen rank, and write one X bit per iteration. A physical flag becomes one on equality and remains one thereafter. Starting at the second iteration, emit that flag as the cumulative Y bit. Thus X_g,i is one iff i equals the chosen rank and Y_g,i-1 is one iff the chosen rank is at most i. Append the nine Y blocks to the nine X blocks, decode the original pin field from the unchanged D2C stream, append two zero guards, and rewind X. The expected assignment and verifier are used solely in the audit.

## Compilation and executed evidence

| Property | Value |
|---|---:|
| Generated IR instructions |25109|
| Reachable non-jump instructions |22344|
| Compact instructions |10531|
| Refinement rounds |612|
| Instruction homomorphism checks |22344|
| Logical states and roots |382962|
| Interned continuation states |10384915|
| Ternary nonhalting states |10767877|
| Packed transition entries |32303631|
| Calculated original-format descriptor bits |915269549|

The unchanged numeric row compiler constructs the actual packed ternary transition table. The original-format size is calculated, not serialized or independently decoded in this stage. Native decoder verification remains open.

Twelve distinct fixtures completed raw and compact IR, with independent original-factor enumeration and stable retained-relation oracle. All 108 local generations and 36 semijoins agree, including the first-compatible reverse choice and exact recovered rank words. Eight SAT witnesses (305 bits total) verified against the original Boolean clauses and layout; four UNSAT cases emitted no witness. The audit checks the virtual witness head, all 61 terminal tapes and heads between raw and compact IR, and the physical replays against that terminal configuration. Four IR cutoffs and two limited malformed-input controls passed. No disagreement observed.

| Fixture | m | Virtual primitives | Models | Witness |
|---|---:|---:|---:|---|
| empty |2|53728|512|31 bits|
| four-bag triples |2|133583|32|31 bits|
| greedy trap |2|1002453|52|31 bits|
| joint-three UNSAT |2|133981|0|none|
| joint-three SAT |2|164774|128|31 bits|
| disconnected UNSAT |2|155769|0|none|
| unary UNSAT |2|45768|0|none|
| mixed |3|1101199|9720|50 bits|
| greedy trap |3|9060450|6816|50 bits|
| forced ranks |3|589937|1|50 bits|
| empty-child edge |2|50105|0|none|
| nonempty-child edge |2|63657|384|31 bits|

The forced domain-three fixture recovers exactly (2,1,0,2,0,1,2,1,0). Its original Boolean word is 00101010000110001000101010001111101111101111110100. This is IR evidence, not a completed domain-three ternary replay. Total distinct fixtures: 4518566206 separate D2C producer transitions, 12555404 virtual worker primitives, 1057 candidate tuples, 754 local rows and 732 finalized rows. Do not combine producer and worker clocks as a measured composed raw-selector machine.

Three complete standalone ternary runs:

| Fixture | Physical transitions | Span | Result |
|---|---:|---:|---|
| empty |672161844|17230|valid witness|
| nonempty-child edge |1144561610|18175|valid witness|
| empty-child edge |512737138|17205|no witness|

The nonempty edge chooses rank one for group zero and zero for all others; its first candidate is incompatible with the selected parent rank and selection advances to the matching row. Its original 31-bit witness is 0110101010101010101111111110100. Both physical SAT outputs pass the original clause verifier via the exact terminal comparison; the physical UNSAT case leaves X empty. Total physical worker transitions 2329460592, representing 167490 virtual primitives. The combined larger/forced audit initially hit the interactive tool timeout; both suites completed separately. No completed physical domain-three or joint-three forest witness replay in this stage. All executions used JS V8. Current-head CI unconfirmed at commit.

## Resource audit

The selection pass copies each finalized relation once and scans it at most once, with O(log m) reads, rank rewinds and temporary erasure per candidate, and a fixed number of bags and coordinates. It adds O(m^4 log m) virtual time and at most O(m^4 log m) shared space, including scratch. Translation adds O(m log m) virtual time and O(m) output space. The full worker retains O(m^4 log^2 m) virtual time and O(m^4 log m) allocated space. The segmented single-tape compiler charges O((T+1)(S+1)) physical transitions, hence O(m^8 log^3 m)=O(L^(8/3) log^3 L) for the standalone worker with L=Theta(m^3). This excludes physical input encoding and output projection. No finite cubic-stage admission or unrestricted SAT complexity claim follows.

Next 024D4A: implement a charged physical D2C-to-segmented-worker initialization bridge, preserving the already single-tape producer (do not quadratically simulate its whole runtime). Compose actual original-format descriptor entry/exit and implement unencoded halt-head witness projection, with blank refusal/UNSAT. Audit description length and explicit finite-stage admission only after that physical composition. All four global routes and six Omega obligations remain open. Main unchanged.

Reproduce:
```sh
for suite in ir larger forced physicalEmpty physicalEdge physicalEdgeSAT; do
  node --max-old-space-size=6144 mathos/research/f038_rex_width_three_witness_ir_audit.js "$suite"
done
```
