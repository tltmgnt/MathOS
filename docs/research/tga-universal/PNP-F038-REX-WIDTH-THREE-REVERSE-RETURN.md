# F038-REX-024D6P — Reverse return scan and fused head action

Parent D6O 8c978b9d2bd109375b427658ebdb1d99ae62ffa9. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent verification
[D6O exact-head Proctor 46070502281](https://github.com/tltmgnt/MathOS/actions/runs/46070502281): 29/29 passed. D6N remains 29/29.

## Mechanism and source-level simulation
Retain D6N's logical controller, all 20 tapes, D6O's four-bit paired codebook and external raw producer/projector. Instead of decoding each return block left-to-right then backtracking, enter the reverse scanner on the preceding block's last digit. Decode the block in reverse, using suffixes of valid codes to determine decoding states. On non-G valid blocks, move left from the first digit directly into the preceding block's last digit. At G, dispatch the next instruction while staying on G's first digit. Any logical leftward macro whose destination is a return root now stops at the preceding block's last digit, not its first. Other directions and endpoints are unchanged. Blank is not part of a valid return path. Malformed-layout rejection behavior is not claimed equivalent.

Second, fuse the head-target scanner's decoded marked-symbol branch with the logical action itself. The scanner already knows the full symbol; it can choose the read branch, write value, or move/unmark action directly. No redundant rewind and second decode of the selected block. The codebook and every genuine logical primitive's resulting tape contents remain unchanged. At a logical instruction boundary, head at G's first digit and encoded layout invariant hold. Forward scan reaches the same marked target using delimiter counts; action fusion performs the same action as the separate decoder; endpoint adjustment reaches precisely the previous block's last digit; reverse scan preserves all traversed cells and stops at G. Right growth retains original suffix carry and final E insertion, with adjusted return endpoint. Induction over primitives proves decoded simulation on valid layouts, assuming inherited producer/projector correctness. The proof is source-level, not a complete mechanical certification.

## Exact clock derivation
Let p be zero-based target block index, N old encoded block count, w=4, b=3w-2, R(u,v)=D6O right rewrite cost. A reverse return block requires w transitions, including G dispatch; a left-to-return action requires 2w-1 transitions from its initial first digit (w-1 decode steps then w left steps). Initial forward scan costs pw. Fused read/write costs 2pw+2w-1, compared with D6O pw+2(2w-2)+pb. Left move adds b-w to the new read/write cost; interior right move adds R(hx,ux)+w. Right extension costs (p+N+2)w-1+R(hx,ux)+R(delimiter,h_)+sum of suffix carry costs. Final success/reject remain 6/7. Exact accountant initially omitted w-1 steps of forward decoding on left-to-return actions; independent clock test caught it, corrected formula passed all tests. No change to logical primitive counts. Inherited safe bound (2bNmax+2a)K+a+indicator(reject), a=2w-2, retained. End-to-end O(L^2(p+1+V)) conditional physical envelope remains unchanged; no universal cubic or unrestricted SAT reduction. Fixed-nine explicit normalized family already polynomial by exhaustive enumeration.

## Independent evidence
1872 isolated physical macro cases (960 reads,576 writes,144 left moves,192 right moves;48 growth cases and768 reject branches included),48 multiprimitive exact clock tests, and2 zero-primitive terminal checks passed for the inherited macro test setup (both codebooks except the two terminal checks use the paired one). Exact physical contents, heads and exits matched. 12 hard-family source-clock comparisons match D6O encoded terminal contents, status, heads and primitive counts in both modes. Existing D6N 1358 semantic executions are inherited; the new workflow reruns their independent audit. No claim of 1358 new physical runs.

## Physical compilation
| configuration | original states | quotient states | descriptor bits |
|---|---:|---:|---:|
| D6O bounded |3171718|2980693|235474751|
| Reverse-only bounded |3143484|2952459|233244265|
| D6P reverse + fusion bounded |3074615|2884057|227840507|
| D6P reverse + fusion full |3073244|2882686|227732198|

Bounded transition checks9223845; full9219732. Final bounded descriptor reduction7634244 bits,96636 quotient states. 22-bit IDs remain; 21-bit target unmet. No measured compiler memory or wall-clock claim.

## Hard-family source worker clocks
| domain | D6O SAT | D6P SAT | D6O UNSAT | D6P UNSAT |
|---|---:|---:|---:|---:|
| 2 |2403936576|1375602989|2434761639|1393178371|
| 3 |4313087382|2467219703|4398038139|2515679171|
| 4 |8431523030|4821742340|8547390995|4887836949|

Identical in bounded and full modes on these fixtures. These are exact source-accounted counts, not completed hard-family D6P physical runs.

## Physical replay
| fixture | original and quotient halt | head | span | worker |
|---|---:|---:|---:|---:|
| bounded one-prefix SAT |994301217|47122|47937|958543609|
| full one-prefix UNSAT |519623497|38293|47726|484340928|

Original and quotient agree; one-short cutoffs994301216 and519623496 TIMEOUT/no witness. SAT original-format witness0101010101010101011111111110000 nextSymbol2. UNSAT blank halt headSymbol2,nextSymbol1. Original observed worker matches exact accountant. A combined quotient replay call timed out at the tool level; separate calls completed both fixtures and cutoffs. Dedicated Proctor registers29 jobs (one audit,26 physical,2 native); completion unconfirmed. No main or PR #248 edits.

## Next D6Q
Investigate delimiter-specific forward scanners and return paths that preserve alignment without full codeword recognition on known-valid layouts, or a smaller internal alphabet. Preserve exact replay and native semantics. No promotion.
