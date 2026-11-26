# F038-REX-001 — MRA-X 2.0 + RE-X: bidirectional TGA and physical interface audit

System MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 28d03986a850a3ccea7fa820678dfc5b593c8c27 (SEP-003).
This mission implements the user's requested reverse-engineering integration as a local executable research prototype, not a separately deployed multi-agent system or independently certified theorem prover. No changes to main, earlier claims or the existing global graph.

## 1. Implemented bidirectional intelligence kernel

mathos/proof_analysis/rex.py interoperates with the original immutable Claim records and analyze function. Each derived claim has an OR of explicitly authored nonempty AND prerequisite routes. Open leaves are not true; established_external leaves are assumed background, not proof-checked by RE-X. The entire graph is validated before traversal, even unused routes: missing dependencies, invalid state/route combinations and dependency cycles are rejected.

Forward closure starts at the externally established leaves and repeatedly includes any derived node with a completely known prerequisite route. Record the layers and final closure K+. This terminates on a finite acyclic graph. It does not perform arbitrary mathematical deduction. Backward discovery computes inclusion-minimal residual sets for each target:
- Known node: the singleton family containing the empty set.
- Open leaf: the singleton family containing that leaf.
- Derived node: for each route, take all unions of one residual set from each prerequisite, then union the families across alternative routes and remove strict supersets.

Proof of correctness relative to the authored model: in a topological order, a node can be reached after hypothetically completing a set of open leaves iff the set contains some minimal residual returned by the recurrence. This is immediate at a leaf. At a derived node, satisfying one AND route is equivalent to satisfying all prerequisite residuals, hence containing their union; OR allows any route. Removing strict supersets preserves that characterization. The forward closure is the special case with no additional leaves; compare against the backward result containing an empty set. The implementation also checks exact equality of residuals with the original TGA analyzer. The research frontier is the union of minimal residual sets; their intersection identifies tasks shared by every MODELED route, not mathematically necessary conditions for every possible proof. Direct route traces retain route-specific residuals, including alternatives that become dominated in the global minimal antichain. The graph is never modified.

This is a concrete implementation of backward prerequisite discovery and forward evidence closure, but the prerequisites must still be supplied by mathematical research. RE-X does not discover arbitrary inference rules, verify supplied axioms or synthesize proofs from a desired conclusion. Exact antichain enumeration may be exponential in the number of open leaves; no general polynomial graph-analysis performance or research-efficiency improvement is claimed.

Research Energy Optimization: authorize_one accepts an explicit mapping of task IDs to positive integer effort costs and a nonnegative integer budget. Only open frontier tasks explicitly included and affordable may be selected, at most one per call. Rank by number of minimal modeled routes touched divided by proposed effort, then lower cost and stable ID; this is a scheduling heuristic, not mathematical value, probability, runtime measurement or proof difficulty. Reserved effort is not reported as consumed work. Closed target => PRESERVE; no affordable authorized task => STOP_NO_AUTHORIZED_AFFORDABLE_TASK. No automatic follow-on research or status mutation. The F038 report uses an empty new-task allowlist and budget zero following this bounded implementation. Rejected inferences are recorded explicitly, not automatically discovered by the scheduler. Neither TECT-X nor independent mathematical review is replaced by graph arithmetic.

## 2. Reverse-engineering original U acceptance

Retrieve the actual f038_unrestricted_universal_search.py. A general descriptor begins 111, unary state count q then zero, and q*3 transitions; each gives next state in q.bit_length bits (q halt), two write bits (0,1,2 blank), two move bits (left,stay,right). The tape starts at index zero with encoded(n,p,C)=1^n0 followed by the clause selector. On reaching halt, tape_run reads exactly n consecutive cells from the FINAL head; if all are binary returns their little-endian integer, else None. Timeout returns None. The external valid predicate checks every selected original clause. Stage enumeration includes every descriptor length ell<=s with clock 2^(s-ell). Descriptor validity or halting is not SAT acceptance.

For the inherited normalized nine-group class n=19m-7, input length L=Theta(m^3), the selected sufficient backward route for eventual admitted SAT coverage at s=3 ceil(log2 L) requires a single fixed integrated descriptor, correct raw input recognition/physical preparation, actual sequential separator computation, original witness projection and contiguous serialization, and a uniform clock within the allocation for all admitted SAT inputs above a finite threshold. A same-program little-o(L^3) bound suffices eventually because 2^(s-ell)>=L^3/2^ell when eligible. It is not a necessary bound for every program. UNSAT/ineligible/outside normalization must not create a false witness; the external verifier guards acceptance, and a failure halt on blank can be used. This mission does not assert every SAT input is admitted, a general SAT decision procedure, or actual full stage enumeration at an enormous descriptor length.

The new F038 route splits the physical gap into REX-01 raw recognition and original semantics (host tested), REX-02 full product-track preparation, REX-03 fixed sequential bit solver and production batch cost, REX-04 general witness projection and contiguous output, REX-05 same fixed machine composition, REX-06 same-program clock/eligibility, REX-07 independent review, REX-08 unrestricted coverage or distinct uniform route. The selected local route requires the first three interface packages (01,02,04), then adds 03 and 05 for machine, 06 for restricted stage, 07 for evidence readiness, 08 for uniform evidence. All open. These authored work packages overlap prior INT/SEP packages; counts are not additive across graphs and do not measure progress. No global leaf is closed.

## 3. Constructive physical interface primitive (executed)

Rather than another host-level solver, build a fixed genuine one-head three-symbol binary payload codec. Two separate fixed machines, each 18 nonhalt states, 54 transitions, 508 description bits. Expand maps each input bit b to bbbb. Pack maps each uniform four-bit block bbbb to b and rejects nonuniform or partial blocks by halting on blank. This is a binary payload representation ONLY, not full product-track layout or projection of arbitrary product symbols. A future full compiler can reserve 0000/1111 for these two logical payload symbols if appropriate; encoding all other logical symbols, scratch tracks and control markers is still open. No claim that these codes match earlier product alphabets. Input is a contiguous binary string starting under the head, blank elsewhere; empty input allowed. Output replaces the input, starts to its left, and the final head points at its first bit (or blank for empty/failure). The algorithms do not preserve a copy of raw input and do not include unrelated surrounding data in their contract.

Unified derivation with fixed input-word width u and output-word width v, (u,v)=(1,4) or (4,1), N words. Each word uniform. Repeatedly seek the right end of the remaining input, read and erase its final u-bit word, remembering one bit and a fixed-size word counter in finite control. Move left through the remaining input to its blank gap, then across the already written output to the first blank left of it. Prepend v copies of the remembered bit, move back across output to the fixed gap and return to original start. By induction the remaining input consists of the original prefix, the output consists of the encoded original suffix in correct order, and the one-cell blank gap at index -1 separates them. When no input remains, move left through the output and halt at its first symbol. Pack checks equality as it erases each fixed word; mismatch or incomplete word halts on blank. No guarantee of intact input upon rejection.

For N>=1, let r=N-j remaining input words before iteration j (j=0..N-1). Scan right including end test u*r+1 transitions, erase u, return across remaining input to gap u*(r-1)+1, scan j*v output bits and prepend v, turn at blank 1, return across (j+1)*v output bits and gap +1. Thus cost per iteration 2*u*r+2*v*(j+1)+4. Final traversal v*N+3. Exact valid-input clock and span:

    T_(u,v)(N)=(u+v)*N*(N+1)+(v+4)*N+3
    visited span=(u+v)*N+3
    final head=-v*N-1.

Empty input halts in one transition at head zero. The output is the only remaining nonblank region on valid inputs. These are actual physical symbol transition counts, not a block-level simulation.

Compose the two machines by replacing the first halt target with the second initial state and offsetting the second table's state indices by 18. Same physical tape, same head at the phase boundary, no host reset or recopy. The combined fixed machine has 36 nonhalt states, 108 transition entries, 1120 description bits. It is an identity transducer (NOT a SAT solver). The output lies to the left of the first encoded region and all previous data are erased. For N>=1:

    T_roundtrip(N)=10*N*(N+1)+13*N+6
    visited span=6*N+4
    final head=-5*N-2.

Empty input halts in two transitions. This proves one useful same-machine compositional interface fact. O(N^2) physical time is subcritical relative to a cubic input clock for this payload operation, but says nothing about the cost or correctness of the missing separator computation or arbitrary product-track conversion.

## 4. MathOS finite verification

JavaScript compiler/audit retrieved and rerun in the tool runtime. Three original-format descriptors decode entry-for-entry and have valid transition ranges. For every binary string of length 0..8 (511 strings), execute both separate machines on their required input, compare complete tape output, cleanup, head, exact clock and visited span. Execute the composed descriptor on the original raw binary string (no host reinitialization) and check the same properties.
- 1,022 separate executions; 346,600 physical transitions.
- 511 same-tape composed executions; 346,600 physical transitions.
- 18 separate and nine composed one-step-short timeout controls.
- 1,016 malformed pack inputs of lengths 1..9, exhaustive nonuniform/partial controls, all halt on blank; 14,090 physical transitions in these controls.
- Separate larger scaling controls [N,expand steps,pack steps,expand span,pack span]: [16,1491,1443,83,83], [32,5539,5443,163,163], [64,21315,21123,323,323], [128,83587,83203,643,643], [256,331011,330243,1283,1283].
Counts exclude scaling and timeout executions from the exhaustive totals. All assertions passed. No physical hardware measurement.

Second-language replay: the committed f038_rex_codec_replay.py (Git blob 304dc958245971d17bd13ffdb82e6f1c7bce5d9d) was copied locally with matching hash. Extracted the original Python pool, encoded, decode_tm, encode_tm, tape_run and valid functions from the repository; this is not a full repository import. The three JS-generated descriptors were copied and checked against their respective length/FNV-1a fingerprints [508,4061857747], [508,3665615828], [1120,1543086631]. All decoder roundtrips passed. Executed the exact composed descriptor on all 260 selector inputs for n=1,2 through the extracted original interpreter, with 260 one-step-short timeouts. At exact clock every run returns all-ones because it reproduces the raw unary header at its new head. Only 34 returned witnesses satisfy the original selected clauses. The satisfiable input n=2,p=1 requires x1=0; identity codec returns 3, rejected by original valid. This explicit adversarial control prevents mistaking a successful physical roundtrip for SAT discovery. No full stage enumeration was attempted.

RE-X graph engine local test: exact committed module Git blob ed8ce007f9160d0808774e3b6eee3e6b85fe24ef. Eighty seeded DAGs with five open leaves and one established background, four derived nodes, every 32 possible hypothetical open-leaf completions compared with independent topological evaluation (2,560 assignments). Residual antichain exact, no graph mutation. Four invalid graph cases rejected, eight governance checks passed. Synthetic hypothetical assignments are tests, not actual proof promotions.

Executed the new mission report and inherited SEP/global status modules from Git-blob-matched copies, with the original extracted Claim/minimal/analyze core. Global source initially differed in quotation style of the __main__ guard, corrected and hash-matched before final execution. Verified local copies: REX-001 c7eed5865216239009ad451d54917091b8e55f14; SEP-001 71b360ce6387bebe2e7ac40d5b061dce9c4eefe7; SEP-002 412afe0eb8de85128a9dfa745faf7f4a19064bfa; SEP-003 b914c274a6cecd12c674c5b6a84dc84994fae7c3; global 3eaef82e22acf88c5c2991414013e36eeb9bc6d1. All assertions passed. This is a local extracted-core replay, not full repository CI, Lean or independent mathematical review.

## 5. Status routes (executed)

Local RE-X interface 3 packages; integrated machine 5; restricted stage 6; restricted evidence 7; uniform evidence 8. All BLOCKED. Prior SEP routes retain their 4/6/6/8 modeled open packages. Global alternatives (all BLOCKED): direct SAT (direct_sat); selector (selector_algorithm, selector_preservation, selector_bit_cost); certificate (unbounded_codec, selected_bounds, machine_cost, ordinary_complete, short_proofs, discovery, decision_bridge); negative (universal_lower_bound). No common unresolved leaf in mathematical-resolution alternatives. The separate evidence gate adds independent_review to each route; only that editorial work package is common. Zero of four resolution routes closed. The graph is not a proof checker or a source of necessary mathematical conditions beyond the selected authored routes.

## 6. Reproduce and disposition

    python -m mathos.proof_analysis.rex
    node mathos/research/f038_rex_physical_codec.js
    python -m mathos.research.tga_f038_rex_001

The Proctor workflow also runs the original-module imports for descriptor replay, pinned audit output and unchanged global gate. Exact-head CI unconfirmed; no separate production ResearchOS/TECT-X/MRA-X process or agent ensemble run. No certification metrics upgraded. The generic graph scheduler and the fixed binary codec have been implemented, not the full eight-module production architecture. Advance the bounded evidence to review, preserve all prior obstructions, decompose full product layout and actual bit solver, reject identity-codec-as-SAT and backward-prerequisite-as-proof inferences. No automatic next mission: STOP_NO_AUTHORIZED_AFFORDABLE_TASK refers to the new-task budget after this completed cycle, not a mathematical impossibility or abandonment of the research project. Any new mission needs authorization, falsifiable hypothesis and resource bound. P versus NP OPEN, PROMOTION NONE.
