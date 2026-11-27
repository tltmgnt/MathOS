# F038-REX-024D6O — Paired symbol lowering and exact physical clock

Parent D6N c9d16a0c2e1f8fa5376a854f320d1fc14bd76f56. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6N exact-head Proctor 46067286107](https://github.com/tltmgnt/MathOS/actions/runs/46067286107): 29/29 jobs passed, including hard m4 SAT both modes and native original-format verification.

## Codebook and rewrite
The worker still simulates exactly the D6N 20-tape logical controller; producer raw input and halt-head projection remain in the original external format. Binary width w=4. G=0000,D=0001,E=0010, physical blank=2222. For each alphabet symbol in order L,0,_,1,x, unmarked and marked codes are 4+2i and 5+2i respectively. All 14 codes are distinct. Thus marking/unmarking changes only the final digit. The bridge emits the selected codebook; the projector decodes that same codebook. The first bit of each output pair is identical, as needed by the projector's temporary blank-marker restoration. The compiler also supports the old codebook for the controlled rewrite-only comparison.

After decoding a w-digit block, the head is on its last digit. For rightward movement with different old/new codes, let j be the first differing index. Rewrite the last digit and walk left to j, preserving unchanged intermediate digits; at j write the new digit and reverse right to the next block. Total w+2(w-1-j) transitions, rather than 3w-2. Identical-symbol right movement costs w. This is minimal under the required sequential decode-first and block-boundary endpoints: the head must visit the leftmost changed digit and then reach the next block. For leftward and stationary movement, preserve unchanged digit writes while retaining the original traversal lengths 3w-2 and 2w-2 respectively (a changed stationary rewrite costs 2w-1). Paired marking/unmarking in a rightward macro costs w=4. No claim of global optimality across other decoder strategies.

For any valid logical configuration encoded as G followed by separated tapes, exactly one marked symbol per tape and an E delimiter at the end, the scanner reaches the target tape/head by counting separators. A read selects the same branch, a write changes just that marked cell, and a move unmarks the old head and marks the neighboring cell. Right extension inserts a marked virtual blank before the delimiter and carries the original suffix one cell right, preserving every logical symbol and mark. The codebook is injective and each rewrite leaves the correct encoded word at the required boundary. Return scan reaches G. Induction on logical primitives gives decoded simulation, termination classification and original-format witness under the inherited producer and projector invariants. This is a source-level proof of the macros; finite physical audit is not a complete mechanical certification of every raw input or of the inherited producer.

## Exact clock
For p=zero-based logical block index of the marked cell, N=current number of encoded blocks, w=4, a=2w-2, b=3w-2, read/write cost pw+2a+pb. Left move adds 2b. Interior right move adds C_R(hx,ux)+b. Extension costs pw+2a+Nb+C_R(hx,ux)+C_R(delimiter,h_)+sum of actual suffix carry costs C_R(old,new); the last E insertion is accounted by the return term. The accountant walks the exact logical suffix including marked cells and separators, and maintains terminal encoded tapes, heads and primitive count. Final success costs a; final reject costs a+1. This counts the worker only, not producer/bridge/output. Every primitive retains the inherited bound 2bN+2a for valid executions. The original O(L^2(p+1+V)) physical envelope and restricted exponent 2+(h+b)/3 are unchanged. No universal cubic guarantee or unrestricted SAT reduction. The fixed-nine explicit normalized family is already polynomial by exhaustive enumeration.

## Independent verification
Macro audit: 1872 individual physical executions across both codebooks, three target tapes, multiple contents and head positions. 960 reads,576 writes,144 left moves,192 right moves,48 growth cases and768 reject branches (subsets). Exact exit, head, tape contents and surrounding blanks agree with independent logical construction. Additional48 multiprimitive programs match exact clock and terminal encoding. The 12 hard-family clock comparisons (m2,m3,m4 SAT/UNSAT both modes) match complete D6N terminal tapes, heads, status and primitive counts. D6N's 1358 logical executions and 15550 predecessor events remain valid because the logical controller is unchanged; dedicated workflow reruns that audit, not a claim of 1358 new end-to-end physical executions.

## Physical resources
| configuration | original states | quotient states | descriptor bits |
|---|---:|---:|---:|
| D6N bounded |3803788|3607883|285022761|
| rewrite only old codebook bounded |3606224|3412429|269581895|
| D6O paired bounded |3171718|2980693|235474751|
| D6O paired full |3170301|2979276|235362808|

Transition checks bounded9515154,full9510903. Final bounded descriptor reduced49548010 bits (~17.38%), quotient reduced627190 states. 22-bit IDs remain; 883541 states above 2^21 (strictly fewer than 2^21 may be required by the codec's reserved terminal ID). IR unchanged9423/9418; 20 tapes, 4-bit internal symbols. No peak memory or compiler wall-clock measurement.

## Hard-family source clocks
| domain | D6N SAT worker | D6O SAT worker | D6O UNSAT worker |
|---|---:|---:|---:|
| 2 |2404230732|2403936576|2434761639|
| 3 |4313582992|4313087382|4398038139|
| 4 |8432474098|8431523030|8547390995|

Both modes match these counts. Source-accounted only, not new hard-family physical replays. Savings are small since repeated long-distance scans dominate.

## Physical replay
| mode/fixture | halt transitions | head | span | worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |1710183122|47122|47937|1674425514|
| full one-prefix UNSAT |880207822|38293|47726|844925253|

Original and quotient agree on exact halt, head, span and witness; one-short quotient cutoffs1710183121 and880207821 return TIMEOUT/no witness. SAT witness0101010101010101011111111110000 and nextSymbol2. UNSAT blank halt headSymbol2; nextSymbol1 differs from D6N because internal codebook differs, and is not part of blank-halt semantics. Worker counts match source accountant. Dedicated Proctor contains29 jobs, one audit (macro, clock, inherited semantic and governance),26 physical and2 native. Full D6O workflow completion unconfirmed. Main and PR #248 untouched by changes.

## Next D6P
Explore direct physical scanner implementation for paired codebook, preserving valid layout and exact macro semantics. Optimize actual quotient rather than source IR. No promotion.

## Follow-up boundary checks
Zero-primitive halt and reject have exact clocks and bounds 6 and 7. The reject-inclusive total upper bound now includes its additional terminal rewrite step. Three additional bounded original physical runs match exact reference and worker accounting: empty SAT t422005138 head45644 span46433 worker389356786; empty-domain UNSAT t71528860 head38219 span46117 worker39345277; cross SAT t518547020 head45812 span46603 worker485702046. These three new ledger pins await dedicated quotient and cutoff CI verification.
