# F038-REX-002 — Fixed two-track compiler and existential OR recovery primitive

System MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 9b19147014e9ef8dae8aa018a228da98048b7cc3. Bounded continuation of REX-001, targeting the actual physical interface and one separator primitive. No automatic scope extension, theorem promotion, or claim to execute a separately deployed MRA-X agent ensemble. Main unchanged.

## 1. Backward contract and mission boundary

The original U interpreter starts with contiguous raw binary selector input, one head, and alphabet {0,1,2} (2 blank). It decodes a fixed description and runs a charged number of physical transitions; at halt it reads n consecutive binary cells starting at the final head, returning no candidate on blank or timeout. Its separate original-clause verifier decides whether that candidate is a valid witness. The full SEP-003 host solver has not been compiled. The backward chain requires raw preparation, fixed logical computation, contiguous witness projection, same-machine composition, and a uniform same-program clock. This mission implements a genuine fixed-rule compiler for one logical tape with two colocated tracks and a prepared existential OR worker, not independent multitape heads, sorting or SAT discovery. Acceptance criteria: explicit block invariant and costs, actual descriptors, exact tape output, sparse projection, invalid-input controls, selector acceptance replay and no status promotion.

## 2. General fixed logical-rule compiler

Use the full product alphabet {blank,0,1}^2 with three additional control symbols L,R,X (12 symbols total). The all-blank product is coded 2222; every other symbol has a distinct four-cell binary word (enumerated deterministically). The leftmost cell is the aligned physical head position for each logical block. Input contract: raw contiguous binary string starting at head, blank elsewhere; finite strings including empty. Preparation consumes the input right-to-left, writes its corresponding (b,blank) blocks to the left of a fixed gap, and halts that phase at the first aligned block. No supplied prepared layout or host recopy. For N>=1 raw bits the prepared start is -4N-1, the last block ends at -2, and only the prepared block interval is nonblank.

Compiler accepts a finite deterministic list of rules (state,read,next,write,direction), with initial logical state init; ready and reject are reserved terminal states. Alphabet and direction validated, duplicate state/read rejected; terminal direction must be stay, reject must write all-blank. Rules omitted from the table fail locally by writing a blank at the current physical head and halting, not by asserting UNSAT. A fixed worker is compiled once, independently of raw input length. This is an effective finite-state construction with O(number of logical states plus rules) physical states for the fixed alphabet/width, since partial word/control fields have bounded ranges. The descriptor contains actual three-symbol transitions, not an interpreter instruction encoded as a single pseudo-transition.

One logical step: read four cells from the aligned head (first three advance right, fourth writes the new last cell and moves left); rewrite the other three cells right-to-left. A stay ends aligned after exactly 7 physical transitions. A move left/right ends aligned at the adjacent block after exactly 10 (three additional moves after the final write-and-move). All other blocks remain unchanged. Thus induction simulates any supplied fixed logical worker's ordinary transitions, including new blank blocks and nonblank writes, with at most ten physical transitions per logical transition. Missing/invalid logical codes halt on blank. The logical reject action clears the entire current block and halts aligned. Finite tests exercise every combination of 12 read symbols, 12 write symbols, and 3 directions, including blank; adjacent blocks preserved.

The ready contract is a separate proof obligation for a supplied worker: head at the first block of a contiguous nonblank product-symbol interval (or all tape blank for empty), immediately followed by R, with blank everywhere else. No interior all-blank blocks, no other control markers inside the product interval. The serializer erases R, then processes product blocks right-to-left, retaining the second component only and skipping blank second components. Each block is erased as it is read; emitted bits are prepended to the left of the fixed gap. Final head points at the first emitted bit, or blank if output empty; only emitted contiguous bits remain. Witness-only product symbols (blank,0/1), both-track symbols, and input-only symbols (0/1,blank) are supported. This is not a global output-contract validator for arbitrary logical rules. A worker that never reaches ready/reject, leaves extraneous data, has an internal blank, or emits the wrong witness has no successful-computation guarantee from the compiler. For an actual SAT solver the ready contract and exact n output bits must be separately proved.

Earlier in this cycle f038_rex_track_compiler.js implements a narrower three-cell tagged alphabet demonstration (complement and prefix XOR). It is retained as a regression milestone. The separate f038_rex_product_tracks.js supersedes its limited tag alphabet with the complete two-track product and configurable logical rule table. Neither is independent multi-head simulation. The latter tests prefix OR, grouped OR, empty projection, and sparse projection. Do not confuse the two compiler alphabets.

## 3. Physical resource proof

Preparation: for N>=1, with r=N-j raw symbols remaining and j blocks already prepared, one iteration costs 2r+8(j+1)+4 transitions (right-end scan, erase, cross, prepend code, turn, return). The final leftward output-head positioning takes 4N+3. Thus

    P(N)=5N(N+1)+8N+3.

Empty preparation costs 1. Space O(N). For an arbitrary fixed logical worker of T logical transitions and visited span S logical cells, the physical middle phase costs <=10T and visits at most 4S cells up to a constant, in addition to raw preparation/serialization regions. No time claim is made for the worker itself. No overhead from an uncharged reset or host re-encoding.

For a nonempty ready interval of K product blocks, h output bits, let e_i=1 iff block i (0-based) emits a bit, and let c_i=sum_{j>i} e_j, the already emitted suffix length. The initial sweep and erasure of R, then return to first block, costs 8K+10. Processing block i costs 8(i+1)+2c_i+2e_i+4: scan/read and erase four-cell word, cross remaining product prefix and gap, traverse output suffix, prepend bit if present (two extra transitions for writing and turning), return. Final positioning costs h+3. Therefore

    O(K,e)=8K+10 + sum_i[8(i+1)+2c_i+2e_i+4] + h+3
          =4K^2+16K+2 sum_i c_i+3h+13.

In particular O(K,e)=O(K^2), uniformly, because h<=K; empty ready tape costs 1. When every block emits, O=5K^2+18K+13. In general the full composed bound is O(N^2+T+K^2) and visited span O(N+S+K). This conditional compiler theorem concerns a single logical head. The fixed multitape bit algorithm in SEP-002 still needs head-marker/sweep simulation on a sufficiently rich logical tape alphabet, or a different explicitly charged fixed one-head algorithm. The actual two-track compiler supports a fixed alphabet, not an automatic arbitrary number of tracks.

For both main workers, a successful nonempty raw string of N bits uses N product blocks, performs 2N+4 moving logical transitions and one staying terminal step. Middle phase 20N+47, empty 7. Prefix OR outputs every bit, hence the complete exact clock is

    T_prefix(N)=10N^2+51N+63, N>=1; T_prefix(0)=9.

Grouped OR emits only at group separators, so the exact clock is P(N)+20N+47+O(N,e), with positions e_i determined by tokens. For these nonempty workers final head = -4N-h-2, visited span = 4N+max(N,3)+max(h+3,5)+1. The span includes the raw right-end blank, logical marker/sweep cells, and leftmost turn. Empty input has head zero and span four. Failed token streams need not preserve the original data, but halt on blank.

## 4. Separator primitive: grouped existential OR

Token format is 00=false, 01=true, 10=end group; 11 invalid. Empty groups allowed. Every nonempty valid token stream must end with a group terminator; odd length, invalid token or unfinished group rejects on blank. The fixed logical rule table keeps one accumulator in finite control, writes its OR at the second cell of every end token, and leaves other witness fields blank. It preserves the raw input track until ready, then the same physical descriptor projects the sparse witness track to contiguous bits.

For a prepared sequence of exact membership flags for candidates belonging to each outgoing key, the resulting output bit is exactly the existential OR over that key's candidate flags. This is one part of the separator elimination operator. The host supplies the membership flags in these tests; the machine does not discover them from original factor tables, does not sort or compare keys, and does not independently reconstruct a SAT witness. A whole bag of m^4 flags would incur quadratic preparation/serialization O(m^8) before other costs. This primitive alone does not establish the production O(m^5) sequential bit ledger or the full O(m^8 polylog m) physical SEP bound. Its intended reusable contribution is the finite-state OR update inside a future streamed worker, not repeating the entire raw codec on every candidate or treating large prepared flags as free.

## 5. Executed verification

Retrieved committed JS audits executed in tool runtime. The narrower preliminary tagged-block compiler: complement 155 states/5739 bits, prefix XOR 170 states/6294 bits; each 511 exhaustive binary strings length 0..8, 376265 transitions, nine one-step-short cutoffs; larger scaling controls through length 256.

Final full product compiler:
- Prefix OR: 371 states, 1113 transitions in table, 14844 descriptor bits; all 511 strings length 0..8 valid, 476085 executed physical transitions.
- Grouped OR: 607 states, 1821 transitions in table, 26105 descriptor bits; 511 strings, 41 valid (36279 physical transitions), 470 rejected on blank, 232975 total physical transitions. 74 emitted bits and 210 skipped cells among valid controls.
- Both combined: 1022 exhaustive executions, 709060 transitions, 26 one-step-short cutoff controls. Separate scaling tests at N=16,32,64,128 are excluded from these totals.
- 432 complete read/write/direction microstep cases, 3888 executed transitions; all 69 invalid four-cell words (81 possible, 12 assigned) halt on blank at decoding. Six invalid-rule-list controls rejected.
- Eight prepared existential bag controls over m=2,3 and outgoing widths 0..3: 150 candidate flags, 55 exact outgoing bits, 527989 physical transitions. Candidate flag formula is an independent host fixture, not actual original factor discovery. All physical output bits equal reference OR.
- Two additional generic workers (sparse witness-only projection, no output): 254 executions, 143184 transitions, full tape cleanup and head checks.

Executed original acceptance-contract replay using a second JS descriptor decoder and interpreter loop mirroring the retrieved Python decode_tm/tape_run/valid functions, starting from the emitted descriptions (not from compiler state names). All 260 original selector inputs n=1,2 replayed: prefix OR returns all-ones at exact clock, one-step-short timeout for all 260, 34 candidates pass original clause predicate; grouped OR returns blank/no candidate on 259 and one accidentally valid candidate for n=1,p=1. These are explicit non-solver controls, not a SAT success-rate estimate. Original Python replay script imports the actual repository functions and is wired into CI, but that full Python import/replay was not executed locally in this resumed cycle. The result is independently coded semantics replay by the same assistant, not independent review.

All final JS assertions passed. No measured hardware runtime, no exhaustive checks of arbitrary logical worker contracts, no universal-stage enumeration. Description lengths are far larger than the tested cubic stages, and no claim of actual stage admission is made.

## 6. TGA / RE-X status routes

The new tga_f038_rex_002.py uses the existing RE-X graph analysis, refines evidence notes on REX-02/03/04/05 and leaves every claim state unchanged. Local authored completion sets remain: interface 3, machine 5, restricted stage 6, restricted evidence 7, uniform evidence 8 packages. All blocked in the authored graph. The original four global alternatives remain blocked: direct SAT (1), universal selector (3), certificate architecture (7), universal lower bound (1). Independent review is shared by the separate editorial evidence gate. No new mathematical closure inferred from work-package counts. The Python route module is committed and workflow-gated; no fresh full Python graph execution is claimed for this cycle. Prior graph logic and status assertions were retrieved and inspected.

Governance: ADVANCE fixed two-track compiler and prepared OR primitive to review. PRESERVE normalized host solver and earlier mathematical obstructions. DECOMPOSE logical multi-head simulation, actual factor membership/sorting, full fixed sequential solver, actual witness assembly and exact stage proof. RETIRE prepared flags imply physical membership discovery, and generic compilation implies arbitrary worker output correctness. STOP automatic scope expansion; next separately authorized task should address a fixed sequential tape worker for factor membership or an explicit head-marker sweep compiler, with a charged resource criterion. The selected bounded task is now complete; the zero new-task budget in the status module prevents an automatic follow-on. Decision PRESERVE_PRODUCT_COMPILER_FULL_SOLVER_OPEN.

## 7. Reproduction and remaining gaps

    node mathos/research/f038_rex_track_compiler.js
    node mathos/research/f038_rex_product_tracks.js
    node mathos/research/f038_rex_product_tracks.js --description > /tmp/prefix.txt
    node mathos/research/f038_rex_product_tracks.js --description --group-or > /tmp/group.txt
    python -m mathos.research.f038_rex_product_replay /tmp/prefix.txt /tmp/group.txt
    python -m mathos.research.tga_f038_rex_002

The Proctor workflow pins both JS audit outputs and requires Python replay and inherited status gates. Exact-head CI unconfirmed. Independent mathematical and complexity review, Lean formalization, full raw normalized SAT computation, independent-head simulation and same-program stage proof remain open. No certification metrics upgraded. P versus NP OPEN, promotion NONE.
