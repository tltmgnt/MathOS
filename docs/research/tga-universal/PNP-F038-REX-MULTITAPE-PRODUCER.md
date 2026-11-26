# F038-REX-022A — Charged fixed-path normalized selector producer

MRA-X 2.0 + RE-X; contributes to MRA-X Omega Phase III. Parent REX-021 f37aada1e084e4eb2d820dd2fa63d8a0b755dfa0. Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope and evidence classification

The bounded first physical-producer submission replaces host-generated clause tables with a fixed local-tape microprogram, using the seven ordered bags (0,1,2), (1,2,3), ..., (6,7,8). It is **not** an emitted ternary single-tape transition descriptor. The JavaScript controller implements charged stationary tape reads, stationary writes, and unit moves across a fixed collection of tapes; each access in its algorithm goes through these primitives. Only the simulator's storage, head coordinates, counters, timeout and final tape inspection use host indexing/unbounded quantities. The controller stores only finite labels, bounded indices, flags and a bounded call stack; the domain size, ranks, clause cursor and masks live on tapes. Input loading and extraction of output strings are simulator conventions, not measured moves or a same-machine handoff. The previous REX-020 physical worker is unchanged.

The fixed-path restriction is stronger than treewidth <=2. A selected negative cross clause on groups {0,8} is legal normalized input and has treewidth one, but cannot be placed on this path. OUTSIDE_FIXED_PATH is not UNSAT, and the parser continues validating the entire raw selector before returning structural refusal. PREPARED means table production, not SAT. TIMEOUT is distinct. No host-supplied m, pin bits, selector addresses, factors, or plan is consumed by the producer.

## Mathematical invariants

1. Header: starting with remainder 7, one unary m mark is appended per 19 header ones (with modulo-19 rollover); the terminating zero, remainder zero and at least two marks enforce n=19m-7, m>=2. Three identical metadata tapes contain the nine X groups (m cells each), nine Y groups (m-1 each), m pin cells and two guard cells. Their head positions encode variable indices, and first/last markers and local unary scratch tapes determine rank relations.
2. Raw-address generation: nested unit-head loops enumerate supports of width 1, then 2, then 3 in increasing lexicographic variable-index order, and finite control enumerates the 2^k signs (negative before positive). seekAfter transfers the position of the outer coordinate to the inner coordinate via unary scratch marks and advances it once. Induction over the nested loops gives exactly the SEP-003 pool order; every generated address consumes exactly one original raw selector bit. Missing/extra/nonbinary bits, absent fixed clauses and unsupported selected clauses are rejected. Fixed one-hot and OR-chain clauses are recognized by group equality, rank equality/successor and first/last markers. For a pin support (P,G1,G2), exactly one of its two sets of four sign lifts must be selected; the recovered pin is appended. Guards are required negative units. This checks both positive and zero selector bits, not only the selected-clause list.
3. Factor masks: for each bag and each of its seven nonempty coordinate subsets, append the all-negative selector bit for every rank tuple of that scope. Distinct X groups are ordered by original index, so the support traversal appends those bits in lexicographic rank order, once per tuple. A mask is therefore the exact forbidden-tuple indicator, including zero entries. A factor is replicated in each compatible bag; repeating a conjunction does not change its truth value.
4. Row cursor: at candidate z=(a,b,c), each mask head is at the lexicographic index of z projected onto its subset. When the rightmost non-overflowing coordinate i increments, a mask containing i advances one cell. A mask not containing i rewinds m^k-1 cells, where k is its number of coordinates strictly after i, because those coordinates reset to zero. For k=0 there is no movement. This proves the invariant by induction starting from all-zero ranks. A row is emitted iff all seven bits are zero. Three binary counters advance/reset with the unary rank heads; their fixed width is the bit length of m-1, built on tape. The output consists of exact REX-020 row tokens, child code 2 after root code 3, and seven nested closes. Consequently for each globally consistent rank assignment, membership of all seven rows is equivalent to all selected cross clauses. The unchanged worker then implements the corresponding restricted decision procedure.
5. Pin and Boolean witness recovery from the worker's certificate is still host-mediated in the integration audit. The audit checks a unique selected row per bag, repeated-coordinate consistency, expected forced ranks and original clause satisfaction using the inherited SEP-003 engine.

## Charged resource argument (valid normalized inputs)

Let L=n+1+2n^2+8*C(n,3)=Theta(m^3). The support traversal visits O(n^3) supports; rank tests and position transfers cost O(n) per support in the worst case. All sign processing and mask appends are bounded per support (fixed number of bags and scopes). Thus the parser takes O(m^4) local multitape primitives, including address generation, all validation and table writes. Metadata initialization costs O(m).

Output uses 7m^3 candidate rows, O(log m) counter/emission work per row, and O(m^3) total mask rewind work: carry i=1 occurs O(m^2) times with at most one reset coordinate, carry i=0 occurs O(m) times with at most two reset coordinates, carry i=2 cannot rewind any lower coordinate. Even the deliberately conservative bound O(m^5) would suffice for a subcubic simulation; the amortized bound is O(m^3). Hence P=O(m^4) primitives overall. Output length N=O(m^3 log m) and maximum tape span S=O(L+N)=O(m^3 log m) for a fixed number of tapes.

A standard one-tape sweep simulation of the fixed multitape controller (store tracks and head markers, locate active heads, update and move markers by sweeps) takes O(S) per primitive. The fixed product alphabet can in principle be encoded in constant-width ternary blocks; raw input setup and conversion of a completed output track to a contiguous raw stream can be implemented with O(S^2) shuttling. This gives the **derived, not executed** valid-input upper bound O(P*S+S^2)=O(m^7 log m)=O(L^(7/3) log L)=o(L^3). The REX-020 worker retains O(N^2)=O(L^2 log^2 L). A combined producer/worker bound is thus subcubic in principle for this fixed path, but no descriptor, concrete compiler, single-tape tape-layout handoff or physical witness translator has been implemented or certified. A uniform bound covering arbitrary malformed raw input lengths is not established here. Descriptor size and the original universal stage clock remain unverified. This is not a proof of original-selector admission or a new P versus NP result.

## Executed verification

The independent fixture generator and direct per-bag forbidden-clause oracle exercise empty, unary-forced and seeded mixed unary/binary/ternary masks at m=2,3,4,5; compare the exact output bytes and pin bits. Results: 12/12 completed, 4,565,922 raw bits, 69,342 prepared bits, 33,931,134 charged multitape primitives. Thirty malformed controls (including pin sign lifts, both pin signs and malformed-over-unsupported priority), one unsupported control and one cutoff passed. Early cutoff controls at 0,1,66,67,100 primitives were also verified by the inherited integration audit. An early cutoff initialization bug was found and fixed before final verification.

The inherited original SEP-003 encoder/decoder and REX-020 encoder/descriptor were loaded from the exact parent. Six separately constructed original-input cases were compared byte-for-byte with host reference rows and passed through the unchanged physical worker. SAT cases force the maximum rank in all nine variables. Counts below separate producer primitives from actual ternary worker transitions; host transport and witness reconstruction are excluded.

| m | Outcome | Raw bits | Prepared bits | Producer primitives | Worker transitions |
|---|---|---:|---:|---:|---:|
| 2 | SAT | 37,914 | 245 | 302,802 | 1,591,842 |
| 2 | UNSAT | 37,914 | 221 | 302,724 | 486,708 |
| 3 | SAT | 161,851 | 308 | 1,225,831 | 2,503,920 |
| 3 | UNSAT | 161,851 | 275 | 1,225,720 | 712,986 |
| 4 | SAT | 428,744 | 308 | 3,172,963 | 2,503,920 |
| 4 | UNSAT | 428,744 | 275 | 3,172,852 | 712,986 |

Three translated witnesses checked against every original selected clause. Totals across six integration cases: 1,257,018 raw bits, 1,632 prepared bits, 9,402,892 producer primitives and 8,512,362 physical worker transitions. The worker descriptor remains 8,127,684 bits. Dense table production was tested but dense physical worker completion was not attempted in this cycle. Across the two suites (18 completed producer runs, not a claim of disjoint sample populations): 5,822,940 raw bits, 70,974 prepared bits, 43,334,026 charged producer primitives. Counts are simulated operations rather than hardware timing, and exclude malformed/timeout/unsupported controls.

## Governance and next gate

ADVANCE charged local-tape microprogram and fixed-path correctness argument. PRESERVE exact width-two theorem and unchanged REX-020 worker. DECOMPOSE REX-022 into concrete finite-state compiler, single-tape ternary descriptor, actual descriptor replay and same-tape handoff. RETIRE treating local multitape primitives as original physical transitions or fixed-path coverage as width-two coverage. STOP after this bounded first submission. No change to original selector, global mathematical claim states or formal acceptance gates; all four global routes remain open. Phase III mechanized proof and physical/logical equivalence remain open. No independent certification, Python differential replay, native Node execution or exact-head remote CI is asserted from the V8 audit.

Reproduce from this branch:
```sh
node mathos/research/f038_rex_multitape_producer.js
node mathos/research/f038_rex_multitape_producer.js --integration
node mathos/research/f038_rex_multitape_producer.js --produce < normalized.raw
```

Next mission: F038-REX-022B — compile the bounded controller into a fixed single-tape ternary descriptor, verify individual transition accounting and validate tape-level handoff, without promoting the original selector stage.

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
