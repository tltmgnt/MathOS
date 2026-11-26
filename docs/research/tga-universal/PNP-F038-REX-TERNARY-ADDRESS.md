# F038-REX-022B1 — Fixed ternary raw selector address cursor

MRA-X 2.0 + RE-X; MRA-X Omega Phase III evidence. Parent REX-022A 67db28bcd0a0ae654a6c40f046888e1d2e3885ee. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope and acceptance boundary

A fixed, directly compiled ternary one-head tape machine now reads actual original selector bits, validates the normalized dimension and exact pool length, and generates every clause address in original width/support/sign order. No host-provided n, m, clause address, factor list, or support cursor is needed. A second fixed descriptor additionally preserves the entire selector payload in a continuation layout on the same tape. These are concrete physical *subprograms*, not a compiled version of the whole REX-022A controller. The normalization predicates, local mask creation, bag records, REX-020 handoff and Boolean witness translation remain uncompiled. The choice to specialize the first compiler to the address cursor rather than implement a generic 67-tape compiler is intentional. Both machines operate over symbols 0,1,2 (blank), with movements -1,0,1.

POOL_SHAPE_OK is not SAT and not OUTSIDE_NORMALIZED's complement. The all-zero selector at valid dimension has the correct pool shape but omits mandatory normalization clauses: both descriptors accept its shape, and the inherited strict decoder rejects it. OUTSIDE_POOL_SHAPE and TIMEOUT are separate outcomes. The ordinary mode leaves a single bit (1 for shape accepted, 0 for rejected) at the halted head. The checkpoint mode halts on a blank with payload/workspace preserved on valid shape, and leaves a single 0 on rejected shape. Neither interface is a witness solver.

## Physical layout and correctness

Use the invariant [blank] [binary workspace] [blank separator] [untouched raw suffix]. Initially the workspace holds one four-bit column of zeros. A column contains one bit each of n,a,b,c, with least significant column closest to the separator (on the right). On each header one, consume the bit, slide the workspace one cell right, increment n by a binary carry scan, and extend with high column 1000 only on overflow. Finite states 0..30 record the exact initial count; 31..49 represent 31+(n-31 mod 19), so a terminating zero is accepted only at state 31. This is equivalent to n=19m-7 for integer m>=2. The header counter and the binary n track are updated once per consumed one.

The shift subroutine blanks the raw bit, copies the workspace right-to-left into the newly available space, clears the former first cell and returns to the new separator. Induction shows every unconsumed input bit stays unchanged, all four counters stay aligned, and the separator advances one original cell per input bit. For the checkpoint descriptor, after the header terminator, write the consumed bit into the former left boundary at the end of each shift. The checkpoint prefix thus consists of exactly the consumed selector bits, in original order, followed by one blank and the four-track binary workspace. Header ones are not retained as raw bits; n remains represented exactly in the workspace. On shape failure cleanup erases any remaining raw suffix, workspace and checkpoint prefix.

After header validation, width one starts at a=1, enumerating two signs per variable. Width two starts at (1,2), advances b until n, then increments a and sets b=a+1; it switches width when a=n. Width three starts at (1,2,3), advances c until n, then increments b and sets c=b+1; if b=n, increments a and sets b=a+1, ending when this b=n. The counters only need enough bits for n. The sign number ranges from 0 through 2^k-1 in finite control, negative before positive in each coordinate. This produces exactly the lexicographic pool of distinct increasing supports and its sign variants. The read state exposes the current k and sign, while a,b,c are encoded on the physical tape. At that state the next raw bit is precisely the selector for this clause. A missing bit rejects immediately; after the last address an extra bit rejects. Thus for every binary raw input the shape test accepts iff n is valid and the suffix length equals 2n+4*C(n,2)+8*C(n,3). It does not check the values of selector bits.

The physical transition generator uses fixed finite-state routines for read/write/shift, binary addition, copy-plus-one, equality, initialization and cleanup. Its state construction happens once independently of any input. The simulator decodes the serialized descriptor and only that decoded table controls tape updates. The per-address oracle is a read-only observer, not an execution primitive, and never supplies information to the machine. The dense simulator uses a bounded allocated buffer for the tested inputs; the abstract machine tape is unbounded. Binary raw inputs only: nonbinary host strings are refused before simulation.

## Resource theorem

Let L be the original input length. For valid dimensions the workspace is exactly 4 bit_length(n) cells after the header. Each shift and each counter operation takes O(log n) physical transitions; a fixed bounded number of counter operations per sign group suffices. At least the full workspace is traversed per selector bit, so for valid pool shape the actual scanner cost is Theta(L log n)=Theta(L log L), using L=Theta(n^3). Initialization, header processing and terminal cleanup are included. For arbitrary finite contiguous binary input the work is O(L log(L+2)+1), since at most L bits are consumed and the final checks and cleanup take O(L+log(L+2)+1). Total visited span is O(L+log(L+2)+1); active binary workspace is O(log(L+2)+1). The checkpoint retains O(L) selector bits but does not increase the asymptotic transition bound. These arguments concern the two emitted descriptors, not the full producer or normalization checking.

## Executed evidence

Descriptor mode | States | Serialized bits
---|---:|---:
Shape | 11499 | 632449
Checkpoint | 11609 | 638499

Both descriptor lengths are fixed independently of m. Actual original inputs were generated by the exact inherited SEP-003 encoder. Every address in the first suite was compared with the inherited pool generator, including all signs, physical cursor position and current raw bit. The second suite compared the physical payload byte-for-byte and verified final counter values and separator positions, plus absence of extraneous nonblank symbols.

m | Raw bits | Selector addresses | Shape transitions | Checkpoint transitions | Work bits
---|---:|---:|---:|---:|---:
2 | 37914 | 37882 | 3938318 | 3938295 | 20
3 | 161851 | 161800 | 19733813 | 19733786 | 24
4 | 428744 | 428674 | 60186092 | 60186061 | 28

Three shape runs: 628509 raw bits, 628356 address comparisons, 83858223 transitions. Three checkpoint runs: 628509 raw bits, 628356 preserved payload bits, 83858142 transitions. Combined six runs: 1257018 original input bits and 167716365 transitions, with no observed address or payload disagreements. The two suites reuse the same fixtures, not six distinct inputs. Ten malformed controls across the two modes, six timeout controls (including one-step-short for each descriptor), two exact-budget controls, and two all-zero-selector counterexamples passed separately. Controls are not included in the headline transitions. At m=2 the exact clocks are 3938318 and 3938295. No REX-020 worker execution was performed in this cycle; checkpoint output is not prepared bag grammar.

Development: the initial compiler generated duplicate write-state definitions due to checking the wrong state key; corrected before successful tests. The implementation was executed in a V8 environment using retrieved exact-parent modules. Native Node and Python replay are added as remote regression gates, not claimed executed locally; direct container access to GitHub failed DNS resolution. No independent formal certification or exact-head CI confirmed. The original universal interpreter uses a witness-only interface; on valid normalized dimensions, neither a one-bit shape output nor a blank-head checkpoint constitutes an n-bit witness. Descriptors exceed the original stage indices on tested inputs; no original selector admission claimed.

## Governance

ADVANCE fixed physical raw address generation, shape checking and selector-payload continuation. PRESERVE REX-022A full charged multitape producer and REX-020 physical worker. DECOMPOSE physical normalization clause classification, pin checking, forbidden mask deposition, row serialization, and same-machine handoff. RETIRE interpreting pool shape as normalization or a checkpoint as a solved input. STOP after this bounded address subprogram. All global mathematical routes and formal Phase III gates remain open.

Next bounded mission: F038-REX-022B2 — compile physical normalized clause classification and validation using the address cursor and preserved selector bits, including mandatory one-hot/OR-chain/guard/pin clauses and unsupported cross-scope rejection; retain a physical continuation layout for forbidden masks. Do not promote the selector until the complete fixed descriptor and original witness clock are verified.

Reproduce:
```sh
node mathos/research/f038_rex_ternary_address.js
node mathos/research/f038_rex_ternary_address.js --checkpoint
node mathos/research/f038_rex_ternary_address.js --descriptor > /tmp/address.desc
node mathos/research/f038_rex_ternary_address.js --descriptor --checkpoint > /tmp/checkpoint.desc
python -m mathos.research.f038_rex_ternary_address_replay /tmp/address.desc /tmp/checkpoint.desc
```

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
