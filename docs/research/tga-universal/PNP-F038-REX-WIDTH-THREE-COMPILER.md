# F038-REX-024D1A — Standalone ternary compiler for keyed merge

Parent 0f8260500bd0aa40b3dabfde1bf69ec2c10fc5d7. Research branch only. PNP_RESOLUTION_STATUS = OPEN; PROMOTION = NONE. Prior exact-head [C4 Proctor run 45905791822](https://github.com/tltmgnt/MathOS/actions/runs/45905791822) passed, including the complete domain-four snapshot/multitape witness.

## Bounded implemented stage

This stage compiles the **keyed sort, deduplication and semijoin** portion of C2/C4 into a standalone finite ternary transition table. It does not yet compile the C4 tuple projection, checkpoint parsing, mask generation, forest routing, witness selection or Boolean translation. It accepts host-preencoded virtual tape segments, not the original selector or C1 checkpoint. The input encoder is initialization only; there is no host-produced command trace or input-dependent program compilation. For the entire execution the fixed descriptor reads, writes and moves on a single tape over {0,1,blank}. The host interpreter executes only packed transitions, with external cutoff and terminal observation. Success halts at the encoded global sentinel, not at an original Boolean witness; reject erases that sentinel. No universal witness admission claim is made.

## Compiler and simulation

A finite microprogram of 2295 instructions (including labels and terminal instructions) represents read branching, constant-symbol write and unit virtual-tape move. Tape index is a static instruction field. Labels resolve during compilation; unbounded keys and payloads never enter a host controller register. The stable sort is implemented using singleton runs, alternating run distribution, pairwise merges and three finite flags for number of output runs (zero, one, more than one). Comparisons read two tape symbols into finite control and rewind to the record starts; the left run wins ties. Two sorts reuse scratch tapes A and B; child deduplication compares to a previous key on K and builds S; a sorted semijoin writes O. Parent and child inputs are binary key:payload; records, including empty keys or payloads. This finite instruction program does not rely on host sorting or unbounded run counters. In particular, an empty parent or child is handled by the actual branching instructions.

The generic compiler represents each virtual tape as a contiguous segment of logical symbols: a left sentinel, cell contents (including in-band virtual blanks), and exactly one head-marked symbol. Segments are separated by D; G and E delimit the entire region. Each logical symbol has a fixed five-bit binary code, except the actual physical blank block 22222. At every instruction boundary the physical head is at G. To access tape k, cross k delimiters and find its marked cell. Read branches preserve the cell; write replaces its marked content; move unmarks the old cell and marks the adjacent cell. Moving right over D/E inserts a marked virtual blank by a rightward carry shift of the suffix: a single logical symbol is carried in finite control, ending by moving E into a previously physically blank block. Then rewind to G. Left moves at a virtual left sentinel and writes to that sentinel reject. Thus inductively on instructions the represented virtual configuration agrees with the microprogram, including the head positions and newly visited cells. Each logical transition is expanded into ternary aligned block decode, rewrite, and a bounded sequence of moves to the next block. The generated descriptor is in the original 111, unary state count, zero, transition-field encoding. The generic compiler is not yet a complete compiler for arbitrary JavaScript controllers; it accepts the explicit finite instruction representation.

One initial carry-state naming issue was corrected: punctuation in a symbol could collide with the compiler's colon-separated internal state syntax; now carry states use numeric symbol IDs. This does not affect the tape alphabet or data representation.

## Executed verification

| Property | Value |
|---|---:|
| Finite microprogram instructions |2295|
| Constructed logical state definitions |28971|
| Ternary nonhalting states |2285124|
| Physical transition entries |6855372|
| Original-format descriptor bits |180524800|
| Logical symbol block width |5|

An independent host sort/set oracle checked exact stable parent and child streams, unique support stream and semijoin output. An independent finite-instruction interpreter additionally checked all seven terminal virtual tapes and all seven heads. Eight named fixtures and 24 seeded variable-length stream pairs completed, with 115750 virtual primitive operations and 166008120 physical transitions, zero disagreements. Five malformed keyed-stream controls and four cutoff controls (including one step before completion) passed.

| Named fixture | Physical transitions |
|---|---:|
| empty |12517|
| empty parent |65121|
| empty child |216411|
| stable duplicates |5554143|
| variable keys |1632869|
| empty separator key |892055|
| joint-three parity obstruction |7288731|
| joint-three compatible |10706517|

The parity obstruction has disjoint full triple keys even though proper coordinate projections agree. The descriptor filters every parent row. On stable duplicates, output is exactly 00:01;01:10;01:11; and support is 00:;01:;. An independent streaming decoder parsed all 180524800 original-format bits, validating and comparing every one of the 6855372 transition entries. A sparse Map tape interpreter then replayed stable duplicates and parity obstruction for 12842874 additional transitions and recovered the exact terminal streams. Total principal plus independent physical transitions 178850994, excluding cutoffs and smoke. All current tests executed in JavaScript V8. Native Python original codec has not been run on this large descriptor; current-head CI is unconfirmed. The large descriptor (180.5 million bits) is a serious finite-stage listing overhead; no minimization is claimed.

## Resource argument

For fixed tape count and alphabet, let S be total allocated virtual cells (maximum visited extent on each tape) and T the number of virtual primitive operations. Each instruction locates its marked cell and returns to G with O(S) logical moves. A right-end insertion shifts the remaining suffix once, also O(S) moves. Constant-size block compilation costs O(1) physical transitions per logical move. Therefore the compiled simulation costs O((T+1)(S+1)) physical transitions and O(S+1) visited span, including the encoded initial configuration. Initial tape construction and final extraction are not part of this measured simulation; a raw-selector bridge must be separately charged.

For R records of maximal encoded length b, the keyed microprogram inherits the sequential merge bound T=O((R+1)(b+1)log(R+2)), S=O((R+1)(b+1)). Thus this implemented subkernel's derived single-tape upper bound is O((R+1)^2(b+1)^2 log(R+2)), in particular O(m^8 log^3 m) for R=O(m^4), b=O(log m). The same simulation principle could yield a full-worker bound O(L^(8/3) log^3 L) if the entire C4 finite microprogram, its space bound and a separately charged C1 bridge are implemented; that is a conditional target only. Do not apply this simulator to the already single-tape C1 producer and multiply its runtime by L. This stage is not a width-three witness machine.

Next bounded mission 024D1B: extend the finite instruction representation to physically project variable-arity tuples and retain full payloads; compile projection and merge together with finite configuration selected from header masks, then compile checkpoint parsing and the forest controller. Compress the emitted descriptor only with exact transition-equivalence verification. Physical bridge, original halt-head projection and finite cubic admission remain open. All four global P versus NP routes and six Omega obligations remain open. Main unchanged.

Reproduce:
```sh
node mathos/research/f038_rex_width_three_compiler_audit.js small
node mathos/research/f038_rex_width_three_compiler_audit.js seeded
node mathos/research/f038_rex_width_three_compiler_replay.js
```
