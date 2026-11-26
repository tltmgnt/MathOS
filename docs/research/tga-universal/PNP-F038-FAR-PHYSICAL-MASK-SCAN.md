# F038-FAR-002 — MRA-X 2.0 / TGA Research Intelligence: physical mobile-mask audit

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE. Parent 61c4926cfd77a8cca935801124897fad15a8bd4c. This is the second targeted FAR investigation after the bounded joint feasibility report, and deliberately audits the physical premise rather than adding a new compression format. The MRA-X 2.0 product label is used for the requested research workflow (gap selection, constructive candidate, adversarial challenge, cost audit, finite verification, evidence gating and continuation decision). No separate 2.0 executable or authoritative versioned specification was located in the connected repository search; the retrieved MathOS f038_mrax_cycle.py is a v1.0 local stage-gate adapter, not a live agent controller. This cycle does not claim execution of an external MRA-X 2.0 engine, independent agent ensemble, or independent mathematical certification.

## 1. Planner and decision gate

FAR-001's highest-value next obligation is FAR-05 (physical implementation and cost). In particular its joint feasibility ledger relies on the ability to move a variable-length mask along stationary records with a fixed finite product alphabet, preserving unrelated components and paying only proportional to mask size per one-position shift.

The first target is narrower than the complete FAR worker: build a genuine fixed original-alphabet three-symbol one-head machine for a prepared product-track layout and measure its actual transitions, not merely count host-language loop iterations. Reject the inference that a prepared-layout primitive establishes a complete normalized-input machine. Do not proceed to wider recovery proofs until composition and preparation are accounted for.

## 2. Constructive candidate: precise contract

Let n>=k>=1. A stationary bit string s_1,...,s_n occupies logical cells 1..n, with stationary blank at 0 and end marker E at n+1. The mobile word initially occupies cells 0..k+1: L, mask bits b_1,...,b_k, R. The output component is initially blank. Mobile component is blank everywhere else in the active region. Start at logical cell 0, phase start. Outside the active region is irrelevant and must not be read or changed.

At each alignment i=0,...,n-k, compute

    out_i = OR_(j=1..k) (b_j AND s_(i+j)).

Store this bit in the output component of cell i. At the final alignment halt with logical head at i=n-k, mobile word at cells n-k..n+1, stationary input unchanged, output bits exactly at 0..n-k, all other active output cells blank. This is a sliding Boolean-intersection primitive, not the full original clause filter. It demonstrates actual transport and a scan with fixed finite control, preserving stationary and earlier output components.

Logical alphabet is the fixed product of stationary {blank,0,1,E}, mobile {blank,L,R,0,1}, and output {blank,0,1}: 60 symbols. No variable alphabet, register holding the mask, extra head, random access or externally supplied per-size transition table. Encode the all-blank product symbol as 2222. Encode the remaining 59 symbols as the four-digit base-three numerals 0..58, in product enumeration order. Physical alphabet exactly 0,1,2 (2 is blank). A four-cell block is fixed width independent of n,k.

## 3. Mathematical derivation: fixed transition compiler and exact clock

The logical scanner uses 12 named phases: start, scan0/1, four return phases remembering result and terminal flag, carryL/0/1/R, rewind. At an alignment:

* Start at L and move right. Read each mobile bit aligned with a stationary bit, update one-bit OR state. At R read whether stationary E is present.
* Move left over k bits to L, preserving all product symbols; write the result only to the output component at L.
* If E was present, halt at L. Otherwise erase L on the mobile component and move right with L in finite control. On each following mobile bit or R, write the carried symbol into that mobile component and carry its former symbol. On the first empty mobile cell to the right write R. Rewind left across k bits until the new L, then enter start without moving.

The scan-and-return phase, including start, R test and result write, takes 2k+3 logical transitions. Every nonfinal shift-and-rewind adds another 2k+3 logical transitions: k bit cells and R (k+1), one empty cell, k rewind bit cells and the final L transition. Shift writes ONLY the mobile component, preserving the stationary and output components even when a new mobile symbol overlaps an old output bit. The logical invariant holds by induction on alignment i: mobile bits unchanged, L at i, R at i+k+1, earlier outputs correct and stationary track unchanged. R meets E exactly at i=n-k. This proves termination, correctness, preservation, and the exact logical clock

    W=n-k+1,
    T_log=(2W-1)(2k+3).

Exactly W logical transitions stay in place (one after each nonfinal rewind and the final halt); all others move one logical cell. Logical head never leaves [0,n+1].

The compiler is a concrete finite-state implementation of fixed-width block simulation. At a block's first physical cell, read four ternary symbols, remembering the code prefix in finite control; first three reads move right, fourth stays. Decode the completed valid symbol and select logical next state, output code and direction. Write four output symbols right-to-left, moving left on the first three writes. On writing the first symbol, stay if logical stay, otherwise move one cell in desired direction and then make three further physical moves to the adjacent block's first cell. Invalid codes or logical phase/symbol pairs outside the prepared contract halt without a correctness assertion. The table is total, including all three symbols at every nonhalt state. Compiler construction enumerates reachable *control-state names* by closure of all raw-symbol transitions; it is independent of input size. For any fixed width w, valid logical stay costs 2w physical transitions, a logical move 3w-1. This gives a concrete justification of the constant-factor simulation step for this product layout, not a proof of the full higher-level movement ledger.

For w=4, the physical exact clock and visited span on valid prepared inputs are

    T_phys = 11*(2W-1)*(2k+3) - 3W,
    S_phys = 4*(n+2).

Final head index is 4*(n-k), with initial head index zero. The compiler's actual emitted machine has q=2021 nonhalt states, 6063 transition entries, and original F038 binary description length 92970 bits (3-bit magic, unary q and terminator, q*3 entries with 11 state bits, two write bits and two move bits). The committed JavaScript implements the table generator, serializes the exact description, decodes it back and executes the table with a sparse map for tape storage. During execution only one physical head, current finite state, and the symbol read at that head determine each transition. The host clock is the number of those actual transitions. Host preprocessing creates the prepared input layout; it is NOT included in T_phys and is not claimed to run on the compiled machine. Read/write of one encoded block is not treated as an uncharged primitive: every physical symbol transition is counted.

The bound is O((n-k+1)(k+1)) physical time and O(n) visited span, with constants independent of n,k. For a transported binary word, the shift phase costs O(k) even when stationary and output components overlap. This removes one limited implementation uncertainty. It does not automatically establish that a larger mobile record list with nested moving masks can be combined without extra traversals.

## 4. Alternative and critic: actual scope limits

An alternative proof strategy would simply declare a multitape mask scan to take O(nk) bit operations and then charge O(n) sweep per operation. That gives an unnecessarily expensive generic upper bound O(n^2 k) on the prepared layout. The present fixed machine avoids that penalty by physically moving the mask. This comparison is between two explicit upper-bound methods, not a lower bound on every simulator.

The most important adversarial controls are all-zero or all-one masks, internal physical blanks, both k=1 and k=n, alternating data, final R meeting E, preserving prior outputs and unrelated adjacent sentinels. A timeout one transition before the exact clock must not reach the halting state. The machine can halt on invalid encodings or violated layout contracts, so its halt is not a SAT acceptance signal; the valid-layout theorem is not a malformed-input recognizer.

TECT-X rejection registry:
- Prepared block correctness does not imply raw normalized-input preparation.
- Fixed mask transport does not prove nested mask/key/record-list composition or the complete FAR-001 filter cost.
- Exact finite transition counts do not establish exact universal-stage coverage or a general SAT bound.

The original F038 universal interpreter starts with the raw unary-header/selector-bit input at physical position zero, not this prepared layout. The descriptor can be decoded in its format, but calling the original tape_run on the raw selector is NOT a valid invocation of this primitive. No witness is emitted, and the halt head points to a block, not a normalized n-bit witness. No actual U-stage run or clock-admission result. In particular the description length 92970 is not the description length of a completed solver. Its budget in the original enumeration would be 2^(s-92970) when eligible, but this observation does not close FAR-07. No cutoff threshold or universal solver claimed.

## 5. MathOS verification: executed evidence

The fixed compiled machine was executed in the JavaScript tool runtime; all final assertions passed. The committed source is standalone, Node-compatible, with a --description mode emitting the exact serialized program. Exhaustive run: every binary stream of length n=1..6 and every nonempty-length binary mask k=1..n (including all-zero masks). 10,668 inputs, 20,052 output windows, 3,409,992 actual physical transitions in this exhaustive set. For every run compare every output against direct Boolean intersection, every stationary symbol against the input, final mobile position and bits, untouched surrounding sentinel blocks, exact halt head, visited extent, exact clock. For 21 all-zero stream/mask combinations (one for each n,k) verify one-step-short timeout. Table decoder roundtrip verifies all 6,063 transitions. A separate table-range census found 3906 left, 1188 stay, 969 right entries (these are counts of table entries, not dynamic move frequencies).

Scaling cases [n,k,W,physical transitions,logical transitions,visited span]:

    [32,4,29,6810,627,136]
    [64,4,61,14458,1331,264]
    [128,4,125,29754,2739,520]
    [64,8,57,23446,2147,264]
    [128,16,113,86286,7875,520]
    [256,32,225,330238,30083,1032]
    [512,64,449,1291230,117507,2056]

All exact formulas checked, not a fitted asymptotic exponent. Twelve independent adversarial edge cases (n,k)=(17,1),(17,17),(33,16),(65,32), each with zero/one/opposite-alternating patterns, also verify exact timeout at T_phys-1. The preceding exhaustive counters exclude scaling, edge and timeout executions. The physical interpreter executes a real fixed transition table, not the full original FAR worker. It is not a hardware measurement. The finite tests support the invariant and exact clock derivation but are not independent formal proof.

A separate Python replay/gate module is committed: it imports the actual original F038 decode_tm/encode_tm, consumes the JS description, independently constructs prepared blocks, interprets six finite cases, checks the exact outputs, span and clock, and refines the TGA graph. The workflow invokes both interpreters and the unchanged global gap module. This Python replay and graph run are CI tasks, not claimed executed in the present tool runtime unless separately reported. Exact-head CI remains unconfirmed. No Lean proof or independent reviewer. No raw selector input integration, full filter composition, or actual SAT decision executed.

## 6. TGA Research Intelligence: obligation refinement and evidence gate

FAR-05 is refined into four independently auditable work packages:

PHYS-01: fixed alphabet compiler and mobile mask primitive review (transition table exists, mathematical invariant/clock derived, finite checks pass; independent review open).
PHYS-02: nested mobile key/mask/record-list composition (not implemented).
PHYS-03: raw normalized selector preparation and output reconstruction (not implemented for this primitive).
PHYS-04: complete root/descendant physical ledger for the same composed machine (not implemented).

The new Python evidence graph replaces FAR-05's open leaf with an AND route over those four OPEN nodes. FAR-01/02/03/04/06/07/08 retain their existing review status, and the restricted and uniform evidence gates remain BLOCKED in the authored graph. This is an evidence dependency model, not a theorem or authorization for status promotion. The global tga_pnp_resolution_gap.py and previous FAR-001 graph remain unchanged. The graph module explicitly checks blocked status and refuses the rejected inferences above.

Decision: CONTINUE_ONLY_COMPOSITION_AUDIT. Within the original three-cycle FAR mission ceiling, the next cycle should implement an actual parked record-list scanner with a nested movable key or mask, including list preparation and all returns, or document why the claimed composition overhead is invalid. A measured or proved supercritical movement overhead must trigger redesign/stop. Do not create another representation format, claim uniform low-loss recovery, or assign a numerical likelihood of P vs NP success. After the bounded mission, independently review the accumulated lemmas and physical cost ledger before investing further.

FAR-05 not closed. FAR-06 and FAR-07 remain blocked; independent review outstanding. General SAT, unbounded B_3, unconditional eventual exact cubic coverage, and P versus NP remain OPEN. Prior finite cubic interval 52..233 and Lean census 1603 not recounted. No promotion.
