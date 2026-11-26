# F038-REX-010 — Fixed physical Boolean path lifecycle

MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 63da91cb558ac3308f9d40b06c9ac2cbf4f26997. Main unchanged.

## Bounded mission and contract
REX-009 left host transfers, persistent history and physical witness assembly open. This cycle deliberately selects the narrow Boolean path class as a first complete same-tape lifecycle, rather than claiming arbitrary bounded-width plan compilation. Hypothesis: the structural left-to-right path plan can be implemented by a fixed finite-control worker with persistent predecessor records, without a host generating requests or transferring messages. Acceptance: actual three-symbol transition descriptor independent of chain length, exact forward messages and history checked on physical tape, actual backward witness recovery, exact charged clocks and differential reference checks. Stop after bounded audit. No separate autonomous agents deployed.

Input is raw binary contiguous at head zero, blank elsewhere. For n>=1 vertices the first two bits encode unary allowed values 0,1 at vertex 0; every following six bits encode a binary edge in order 00,01,10,11 and the next vertex unary mask 0,1. N=6n-4. Thus arbitrary Boolean unary and adjacent binary factors, including empty relations, are supported; repeated factors would require conjunction into masks by a producer, not supplied in this contract. This is not the original F038 selector grammar, arbitrary graph or arbitrary domain. The fixed plan is left-to-right; for n>=2 every nonfinal reference bag has 4 candidates and outgoing bound 2, final bag 2 candidates and nullary bound 1. n=1 only the final bag. Total candidates 4n-2, peak 4 for n>=2. The order is peak-optimal for an explicit path with edges (first elimination touching an edge costs at least 4), and is implicit rather than an arbitrary externally supplied plan.

## Construction and proof
Let U_i(b) be unary membership and E_i(a,b) the edge mask from i-1 to i. Initial message M_0(b)=U_0(b). For i>=1,
 M_i(b)=U_i(b) AND OR_{a=0,1}(M_{i-1}(a) AND E_i(a,b)).
 Store p_i(b)=least compatible a, or 2 if none (including U_i(b)=0).
Inductively M_i(b) is precisely feasibility of the prefix with final digit b; extending a prefix checks only the next edge and unary mask. This proves the forward recurrence for any finite chain. Choose least feasible final digit, reject on blank if none. Follow predecessor records backward; every selected predecessor is feasible and satisfies the corresponding edge, hence yields a full satisfying witness. Choosing least predecessors gives the least assignment in reverse-coordinate lexicographic order. This is standard path dynamic programming implemented physically, not a new general SAT algorithm.

Reuse the actual REX block compiler with 30 logical symbols and five-cell blocks, blank 22222. Raw input is consumed into binary block symbols, no external setup. Initial unary symbols tagged I/B; four raw edge bits read in finite control along with previous two feasibility bits. Each unary cell is rewritten to T(u,p), retaining its raw bit and predecessor tag. Only the two new feasibility bits continue in finite control. All edge bits remain intact. On final blank, write R and step left; backward phase reads appropriate predecessor, attaches chosen output bit at second unary cell per vertex (O or W tag), traverses four intervening edge cells, and continues to initial marker. Ready head at first aligned block; sparse serializer retains one witness bit per vertex in original coordinate order and erases all other data. No host reset, re-encoding, intermediate factor copy, or supplied membership decisions. Original data and history persist until final serialization; success leaves only witness. Valid UNSAT and malformed streams halt on blank without necessarily cleaning residual data. Malformed lengths reject, no semantic UNSAT inference from malformed input. Two history slots per noninitial vertex, finite control independent of n.

## Exact resource ledger
All successful inputs of length N=6n-4 use N forward data steps, one forward-to-backward R write, N-1 backward moves and one final stay: 2N+1 logical transitions. Physical move cost 13, stay 9. Middle phase 26N+9. Preparation P=6N^2+15N+3. Serializer visits all N blocks, emitting at zero-based positions 1+6j for j=0..n-1; sum of emitted positions is 3n^2-2n. In inherited serializer ledger sum_i c_i equals this position sum (each emitted bit contributes to earlier iterations). Thus O=5N^2+19N+6n^2-n+15. Total successful clock
 T=11N^2+60N+6n^2-n+27.
 Final head = -5N-n-2; visited span =5N+n+max(N,4)+4. For valid UNSAT, N forward moves and one rejecting stay, no serialization; clock P+13N+9=6N^2+28N+12. Valid paths therefore have linear logical work, quadratic physical time and linear physical space, including input/output movement. No general F038 m-exponent improvement follows; this input encoding has Boolean fixed domain and path adjacency, not raw original normalized selector length L. No actual original selector stage admission or full U interpreter import/replay.

## Executed evidence
Fixed descriptor 6426 physical nonhalt states, 19278 transition entries, 334156 description bits; 147 logical states, 4410 rules, 30 logical symbols. Actual physical descriptor checked entry-for-entry. 342 valid inputs: all 4 unary masks and all 256 two-vertex masks, 48 seeded random longer paths (3..8 vertices), 32 planted-witness paths, two adversarial controls. 133 SAT, 209 UNSAT, 957 total vertices, 916477 physical transitions, 6428 logical transitions. All outputs agree with independently coded direct complete-assignment oracle; SAT checks full tape cleanup, head/span, exact clocks, physical forward and backward checkpoints including original factor bit preservation, predecessor correctness and output tags. 266 actual physical checkpoints and 482 predecessor entries checked. Valid UNSAT exact reject clock checked. 253 malformed controls (all raw strings of length 0..7 except 2, plus two longer lengths), 105728 transitions; all halt on blank. Seven additional scaling successes and one-step-short timeouts (excluded from main aggregate).
 [n,N,T,logical,span,phase counts]:
 [1,2,196,5,19,[57,61,78]]
 [2,8,1233,17,54,[507,217,509]]
 [4,20,5719,41,128,[2703,529,2487]]
 [8,44,24339,89,276,[12279,1153,10907]]
 [16,92,100171,185,572,[52167,2401,45603]]
 [32,188,406203,377,1164,[214887,4897,186419]]
 [64,380,1635739,761,2348,[872103,9889,753747]].
Adversarial path with nonempty edges {00} then {11}, all unary masks true, correctly rejected (no common middle witness). Path with sole edge {10} returns 10, not greedy all-zero witness.

Independent Python reference replay actually executed locally: 342 cases, 133 SAT, 209 UNSAT, 957 reference stages, 3144 candidate rows. The Python relational solver and direct predicate enumeration agree on SAT, and the reverse-lex minimum witness stream has FNV-1a digest 2946600415, matching the digest of actual physical results. Digest is a regression checksum, not a cryptographic or formal equivalence proof; the JS audit also checks every individual actual output against direct enumeration. Local Python replay hash d3dc85a43e0218765c9d37fed6cecb70546d00eb matches remote blob, inherited solver hash f0d633552d67fef7b3e29a6fc48a3f49c7c27091. Simulated physical transitions not hardware times. No independent human review.

## Evidence and disposition
Local modeled routes unchanged: interface 3, integrated machine 5, restricted stage 6, restricted evidence 7, uniform 8; global direct SAT 1, selector 3, certificate 7, lower bound 1. All blocked; 0/4 closed. Work packages not distance or difficulty. Status Python module committed but not freshly executed locally. Exact-head CI unconfirmed. No Lean certification.
ADVANCE complete physical path lifecycle within its contract. PRESERVE earlier general reference and prepared batch results. DECOMPOSE domain-rank counters and variable-width persistent message/record handling; next separately authorized task should target a non-Boolean path or a bounded-width branching plan, with actual physical workspace and no host handoff. RETIRE fixed Boolean path implies arbitrary bounded-width solver, and compact path grammar implies original F038 input coverage. STOP automatic expansion. Decision PRESERVE_PHYSICAL_PATH_GENERAL_LIFECYCLE_OPEN.

Reproduce:
 node mathos/research/f038_rex_persistent_path.js
 node mathos/research/f038_rex_persistent_path.js --description
 python -m mathos.research.validate_f038_rex_persistent_path
 python -m mathos.research.tga_f038_rex_010

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
