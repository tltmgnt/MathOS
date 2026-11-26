# F038-REX-006 — Same-machine prepared multifactor elimination

System MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 39bc7418efb8d1345e81bc5f13b3d7a9a70bca36. Main unchanged. Bounded mission: integrate existing sort, membership and reduction ideas in one fixed physical worker; falsify unsafe batch boundaries. No separate autonomous agent ensemble or mathematical certification is claimed.

## 1. Contract and information boundary

For each prepared candidate c there is a finite, nonempty collection of required membership requests, each identified by a binary lookup key x encoding factor namespace and projected tuple (the machine treats x as opaque). The factor-record set contains the allowed lookup keys. Each candidate has exactly one outgoing group z. The intended batch result is H(z)=OR_{c with group z} AND_{requests of c} [x in factor records]. Candidate IDs must identify distinct candidates within the batch and be consistent with their outgoing group. Every required request must be present. Empty conjunctions require a producer-supplied true dummy request or another explicitly handled case. The machine does not validate coverage of required factors, namespace correctness, candidate-to-group consistency, or role consistency across alternate keys.

Raw contiguous binary record grammar from REX-005: key bits and payload bits v encoded by token 0v, divider 10, record terminator 11. First key is x followed by role (0 factor, 1 request), common nonempty width k including the role. Payload: three reserved bits (membership, candidate, outgoing), then two fields each encoding a k-bit alternate key by payload-bit pairs 0v terminated by payload-bit pair 11, then arbitrary binary ID/data suffix. These nested field pairs are inside the payload encoding, not raw record delimiters. Every record, even a factor, supplies all three flags and both fields. Candidate and outgoing alternate keys begin with 1 for requests and 0 for factors. Fixed-width padding and namespace construction are the producer's responsibility. Factor rows may use any role-zero alternate keys, and their scratch flags are not reduced. Input order arbitrary. Empty list allowed.

Output retains all records, transformed into stable outgoing-key order. Original lookup key is in the first alternate slot, candidate key in the second, outgoing key is now the primary key. All nonflag data survive these reversible swaps, including ID suffix. For requests the membership flag is overwritten by actual membership; after candidate sort, only the last request in each equal candidate group carries its AND result, all earlier candidate flags zero. After outgoing sort, only the last request in each equal outgoing group carries its OR result, earlier outgoing flags zero. A zero flag does not distinguish a nonrepresentative row from a representative with false result; consumers can identify group representatives from the key order, or collect positive outgoing flags as a relation. Absent outgoing groups are not explicitly enumerated. Factor scratch flags are untouched. The worker does not emit an original SAT witness.

## 2. Fixed one-tape construction

Use REX-005 shared 29-symbol logical alphabet, five-cell physical encoding, inherited compiler and stable sorter. The worker has one raw preparation and one final serializer. All phases below run under one fixed three-symbol physical descriptor, not host-mediated invocations.

1. Stable sort by lookup key + role and attach membership via latest-factor equality as in REX-005.
2. Reinstall left sentinel. For each record mark its start, mark the current primary digit and current first alternate-field digit, and shuttle using finite control to swap them. Advance both cursors. Require field terminator exactly when key terminates; restore cursor marks. This checks field syntax and width. Preserve reserved flags and other field/ID. Mark rightmost key digits and enter a second copy of the fixed radix worker at makeE, using the existing aligned source and R sentinel. No raw conversion at this boundary.
3. Scan candidate-sorted records. Skip role-zero rows. Maintain a marker F for previous request and Q for current request. Compare complete keys using digit cursors (D is end, unlike the initial role-suffix comparison). For equal keys read previous candidate flag, clear it, AND with current membership; for a new group just copy membership. Write result at current candidate flag. Move F to current row and continue. Thus only last row of each group retains its reduction.
4. Swap primary with second alternate field (skip first field by its nested pair grammar). Enter third stable radix sort by outgoing key. Same transfer mechanism, no external preparation.
5. Repeat previous-group reduction with OR instead of AND, reading candidate flag and writing outgoing flag. Clean markers, serialize entire retained record region, halt at first output bit.

Malformed outer record grammar, unequal initial key widths, missing reserved fields, or alternate-field syntax/width mismatch reject on blank. No preservation on rejection. These are syntactic checks, not a verifier of the required semantic promises. The initial development rule generator incorrectly offered P2 on impossible rekey cursor combinations; compiler rejected that table. Restricting rekey cursors to binary V0/V1 and U0/U1 fixed it before physical regression. Other comparison phases still use end-of-key cursor tags.

## 3. Correctness

First sort and membership are inherited. Swapping digit pairs preserves all bits and is a bijection between key and selected slot. The second sort puts every request for candidate c in one contiguous group (role prefix distinguishes factors). By induction on requests processed in this group, its last processed row holds the AND of all membership flags processed so far, every earlier row holds zero. At new group, previous reduction is final and untouched. At end all candidate groups have exactly one representative carrying their complete conjunction, including zero when infeasible. The third sort reorders intact records, so each candidate's representative remains in its promised outgoing group. The analogous OR invariant gives the disjunction of complete candidate conjunctions for each outgoing group, since all other candidate flags are zero. All loops scan sentinel-bounded finite regions and advance a record, digit or radix pass. The final physical output is a lossless permutation/rekey of all nonflag content and exact flag updates for inputs satisfying the contract.

This is an actual relational elimination operator on prepared requests, not a proof of request generation from original constraints, nor a general constraint solver. The finite tests are supplementary to the stated invariant proof.

## 4. Cross-batch falsification and recovery rule

Suppose one candidate requires two factor memberships 1 and 0. If its requests are split into two batches, independent per-batch elimination returns 1 and 0; OR gives 1, whereas complete conjunction gives 0. The actual logical worker was executed on both partial batches and on their union, reproducing these values. The worker cannot detect a missing request from grammar. Retire the inference that OR across arbitrary request chunks implements existential elimination.

Sufficient batching invariant: partition by WHOLE candidates, not arbitrary request positions. For a disjoint candidate partition C_j and complete required requests for each c,
 H(z)=OR_j OR_{c in C_j,group(c)=z} AND_{requests of c} membership.
This follows by associativity of OR over the disjoint union. Alternatively first merge partial conjunctions by candidate ID with AND and only then OR by outgoing key; this requires a distinct cross-batch protocol not implemented here. Factor records must be complete for all requested lookup keys in every batch (or an equivalently proved membership scheme). The physical producer must enforce these conditions. This is a concrete noncircular completeness requirement, not a claim that batching alone solves unrestricted F038.

## 5. Resource ledger

Let N be raw record-stream bits and k common key width. The same fixed worker uses exactly three k-pass radix sorts. The inherited transfer formulas apply to each pass independently of permutation:
 C(N)=2N^2+5N logical transitions for copying; B(N)=3N^2+5N+2 for restore/cleanup.
So the three sorts consume exactly 3k(5N^2+10N+2) logical copy+restore transitions. Other sort control is O(kN). Each swap scans at most O(N) for a key digit and total key digits O(N), so two rekey passes O(N^2). Each grouped reduction compares at most k+1 symbols per request and uses O(N) bounded cursor/flag scans per symbol or record; sum of key lengths plus record count O(N), hence O(N^2). Same for initial membership. Preparation P(N)=6N^2+15N+3 and full serialization O(N)=6N^2+21N+15, for N>0. Logical moves compile into 13 physical transitions, stays into 9. Therefore valid nonempty complete descriptor runtime Theta(kN^2), exact visited physical span 11N+12 and final head -6N-2. Empty case 11 transitions, span 5, head zero. This lower bound pertains only to this implementation.

Conditional connection to SEP-002/003: for a constant number of factors per candidate and width-bounded tuple records, k=O(log(m+2)), a batch of at most m^3 WHOLE candidates plus complete relevant factor tables has N=O(m^3 polylog m), under the inherited factor table bounds. The three sorts and reductions therefore cost O(m^6 polylog m) per such batch. The earlier bag/slice ledger allows O(m^2) batches if implemented as specified (at most m^4 bag candidates per slice and at most m slices, constant-many elimination steps, other inherited static work). Then the prepared worker contributions are O(m^8 polylog m). This is not a complete physical solver bound: original raw normalized record generation, actual factor namespace/tuple encoding, complete coverage of requests, zero-scope cases, candidate-complete chunk scheduling, positive outgoing message merge across chunks, reuse of factors/history, witness extraction and full same-program lifecycle still need implementation and charge. The serializer currently emits all records, not just a compact outgoing relation. No actual exact-stage admission is claimed.

## 6. Executed verification

Compiled one fixed descriptor, independent of input width/size: 29 logical symbols, 664 logical nonterminal states, 16256 explicit logical rules, 55538 physical nonhalt states, 166614 physical transition entries, 3387822 description bits. Descriptor decode checked entry-for-entry. Eight physical runs, including empty, factors-only, request-only, mixed AND/OR with feasible and infeasible candidates in one group, all-true conjunction, missing factor keys and multiple groups with nonzero incoming scratch flags. Across these: 18 records, 12 request flags (7 positive), 8 candidate groups (4 feasible), 7 outgoing group occurrences (4 positive); 79234013 actual physical transitions and 5972245 logical transitions; 45 radix passes. Complete final tape matches stable reference with retained data/flags. An independent direct relational oracle checks candidate and group truth values from the original requests, without following sort order. 28 physical checkpoints across four handoffs (after membership, candidate sort, candidate AND, outgoing sort) checked aligned head, complete tagged tape projected to expected intermediate records, no extra nonblank scratch outside source+R. Exact sort transfer, prep, middle and serializer clocks and final head/span checked.

17 additional logical-only tests: all four membership truth patterns of two requested lookup keys with cyclic input permutations, plus duplicate requests/factors. The three split-batch adversarial replays are additional logical runs outside that count. Two physical one-step-short cutoffs; seven explicit malformed grammar/field-width cases reject on blank (264585 transitions, separate from main total). No exhaustive raw grammar sweep or new original selector interpreter replay in this cycle. The 8 physical fixtures [N,steps,logical,span,phases] are:
 [0,11,1,5,[1,9,1]]
 [28,190974,13892,320,[5127,180540,5307]]
 [28,192380,14002,320,[5127,181946,5307]]
 [56,720480,52382,628,[19659,680814,20007]]
 [200,24765181,1867611,2212,[243003,24277963,244215]]
 [192,22820763,1720945,2124,[224067,22371465,225231]]
 [96,5790285,436667,1068,[56739,5676219,57327]]
 [200,24753939,1866745,2212,[243003,24266721,244215]].
All final assertions passed in JS tool runtime; these are simulated actual physical transitions, not hardware timings. The independent oracle is independently coded by the same assistant, not external review.

## 7. Evidence gate

REX-006 updates notes on REX-02/03/04/05 but leaves all claim states unchanged. Local modeled routes: interface 3, integrated machine 5, restricted stage 6, restricted evidence 7, uniform evidence 8, all blocked. Global direct SAT 1, universal selector 3, certificate 7, universal lower bound 1, all blocked; independent review common only to separate editorial evidence gate. These counts are work packages not mathematical distance. Python status module committed and CI-gated, not claimed freshly executed locally. No Lean or independent review; exact-head CI unconfirmed.

ADVANCE prepared integrated batch elimination to review. PRESERVE previous resource results and counterexamples. DECOMPOSE actual complete request producer, whole-candidate chunk scheduling and outgoing merge, normalization/witness integration. RETIRE arbitrary split-batch OR and grammar implies coverage. STOP automatic expansion; next separately authorized task should implement candidate-complete request production from an actual bounded-width factor bag and outgoing message lifecycle. Decision PRESERVE_BATCH_ELIMINATION_REQUIRE_CANDIDATE_COMPLETENESS. No certification metrics upgraded.

Reproduce:
 node mathos/research/f038_rex_batched_elimination.js
 node mathos/research/f038_rex_batched_elimination.js --description
 python -m mathos.research.tga_f038_rex_006

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
