# F038-REX-024D6Q — Specialized valid-layout scanner

Parent D6P 84eaf348030d387a87865a78506c8bc0344df18f. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6P exact-head Proctor 46073573469](https://github.com/tltmgnt/MathOS/actions/runs/46073573469): 29/29 jobs passed, including both hard m4 SAT replays and native original-format verification. D6O 29/29 remains verified.

## Mechanism
Retain D6N logical controller, 20 tapes, D6O paired codebook and bridge/projector, D6P fused action and reverse aligned return. The compiler has a special=true default (only effective with paired=true); special=false restores the general D6P decoder. The original codebook fallback remains unspecialized.

Four specialized control paths use layout preconditions:
1. Entry to a nonterminal instruction is at G=0000; after its first zero, cross the remaining three digits into the target forward scanner without distinguishing full G.
2. Forward scan with t>0 counts remaining tape separators. The only delimiter reachable before the target tape is D=0001. All data blocks begin with 01,10,11; G and E cannot occur in this scan. On first 1 skip the remaining digits. On first 0, inspect the next bit: 00 identifies D and decrements the counter; 01 is ordinary data. Cross the remaining two digits. All cells are preserved.
3. At the target tape (t=0), a valid data block ending in zero is unmarked and continues the scan; a genuine marked block ends in one and is fully decoded to dispatch the existing action. The unique marked cell is reached before the next delimiter. Unused binary codes may share the unmarked continuation, but do not appear on a valid tape.
4. Reverse return starts on the last digit of a valid binary block. G is the unique all-zero code; a detected one proves it is not G, so finish crossing the remaining digits without further classification. All-zero G is decoded to dispatch the next instruction at its first digit.

These paths intentionally do not preserve general decoder rejection on all malformed binary layouts. The proof uses genuine encoded tape boundaries, exactly one marked symbol per tape, G at the left and E at the right, and the paired codebook. No new physical symbols, flags or tapes.

## Source-level exact-clock simulation
At a logical instruction boundary both general and specialized machines have the same encoded configuration and G-aligned head. For a nonterminal instruction, entry moves four digits to the same scanner root. Each non-target tape block consumes four rightward steps; the separator count changes exactly on D. Each unmarked target block consumes four steps. On the marked target both execute identical logical actions and write/move/carry macros. A non-G return block consumes four leftward steps; G consumes three leftward steps and one stationary dispatch. Thus every specialized scan segment has the same endpoint, writes (all identity), successor action and transition count as the general compiler. The unchanged primitive action preserves the layout invariant, including on suffix extension. Induct over genuine logical primitives. Terminals, producer and projector are unchanged. Therefore on genuine inputs the two physical machines agree in decoded configurations at instruction boundaries, exact clock and external halt semantics. This is a source-level proof with inherited bridge/producer assumptions, not exhaustive mechanical verification of arbitrary raw input or intermediate state IDs.

The D6P clock accountant remains applicable verbatim. For target block index p and width w=4, read/write cost 2pw+2w-1=8p+7. No runtime reduction is claimed: this pass reduces physical control states by weakening irrelevant symbol distinctions on proven valid layouts, not by crossing fewer physical cells. All inherited conditional resource envelopes are unchanged, including t=O(L^2(p+1+V)) (with p in that expression denoting propagation passes) and admitted exponent 2+(h+b)/3. Fixed-nine explicit normalized inputs already admit polynomial enumeration. Unrestricted reduction, universal cubic guarantee and P versus NP remain open.

## Independent macro verification
Three configurations: original codebook/general, paired/general, paired/specialized. 2808 total single-primitive tests (1440 reads,864 writes,216 left moves,288 right moves,72 growth and1152 reject cases included). 72 multiprimitive exact-clock programs and two immediate terminals. In the specialized configuration, 936 single-primitive tests and24 multiprimitive programs also compare exact complete physical buffers, head, exit and transition count against the same compiler with specialization disabled: 960 exact parity comparisons. All passed. These are finite tests. Inherited D6P 12 hard-family source-clock comparisons and D6N 1358 logical runs are unchanged, not new physical replays; CI reruns the inherited audits.

## Resource measurements
| mode | original physical states | quotient states | descriptor bits | transition checks |
|---|---:|---:|---:|---:|
| D6P bounded |3074615|2884057|227840507|9223845|
| D6Q bounded |2676117|2486933|196467711|8028351|
| D6P full |3073244|2882686|227732198|9219732|
| D6Q full |2674991|2485807|196378757|8024973|

Bounded final quotient reduction397124 states and31372796 bits (~13.77%). Original state reduction398498. The 21-bit state threshold remains unmet:389781 states above 2^21, plus reserved terminal-ID requirement. 22-bit IDs; four-bit symbol width and logical IR9423/9418 unchanged. No compilation wall-clock or peak RAM measurement. The general decoder remains available.

## Physical original/quotient/cutoff verification
| fixture | exact halt transitions | head | span | exact worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |994301217|47122|47937|958543609|
| full one-prefix UNSAT |519623497|38293|47726|484340928|

Exact D6P clocks and external behavior reproduced. SAT witness0101010101010101011111111110000, nextSymbol2. UNSAT headSymbol2, nextSymbol1. Original and quotient agree, cutoffs994301216 and519623496 TIMEOUT/no witness. Hard-family D6Q physical replays not yet verified. Dedicated Proctor config registers29 jobs (one audit,26 physical,2 native); completion unconfirmed. Main and PR #248 not modified.

## Next D6R
Investigate specialized carry continuation sharing or a codebook with a smaller valid-layout discriminator, to reduce the remaining ~390k-state gap. Consider an independently checked resource/correctness certificate rather than just empirical replays. Preserve exact original-format semantics and account for malformed-layout differences. No promotion.
