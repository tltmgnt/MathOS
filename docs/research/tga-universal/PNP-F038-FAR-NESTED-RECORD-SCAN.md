# F038-FAR-003 — MRA-X 2.0 / TGA Research Intelligence: nested physical scan and exact joint-filter limit

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE. Parent 5d5289c6e7fab1072f80caa92fa828e8348200ca (physical mask scan). Third bounded FAR cycle. This is an authored local application of gap selection, constructive and adversarial discovery, critic, cost, verification and impact gates, not execution of a separately versioned MRA-X 2.0 engine or independent agents. No general SAT theorem, Lean certificate or independent review.

## 1. Research decision and scope

Target PHYS-02 (nested composition), FAR-03 (safe compatibility discovery), and FAR-06 (uniform recovery). Do not add another compression encoding. Three different results must remain separate:

1. A fixed physical transition table for a nested equality semijoin on a prepared record layout. Its clock INCLUDES copying the stationary record list, moving it to the first key, inner key copying and movement, inter-key list transport, return and scratch cleanup.
2. A new exact two-free-coordinate original feasibility filter by pair-major union counting, with a conditional subcritical physical ledger. The exact union worker is NOT the compiled equality machine.
3. An asymptotic obstruction showing that even exact projected compatibility, or exact existence of a compatible correction in every root key's row, cannot generally make the previous KEY-DELETION overflow certificates tight.

The third result constrains the value of the second. Do not infer that stronger local feasibility tests automatically lead to unrestricted recovery. End the original bounded FAR mission with a review/redirection gate, not an automatic fourth cycle.

## 2. PHYS-02: explicit prepared-layout nested semijoin

Parameters Q>=1 keys, R>=1 records, k>=1 bits per word, all words the same length k. Compute for each stationary key whether at least one record equals it. Duplicates allowed; output is Boolean membership, not multiplicity. No original SAT predicate or actual selector parsing in this machine.

The stationary track contains Q consecutive key words delimited by A (first start) or L (later start), and R (key end), followed by E, then the immutable record list: D (first record start), L (later record start), k bits per record, final R. The mobile list track and inner key track and output track are initially empty. Start at the first key's A. Define H=Q(k+2), L=R(k+1)+1 (here L as a length, not the delimiter). Stationary cells 0..H+L inclusive. No external sentinels may be accessed. The stationary list remains intact at the end.

The machine seeks E and copies the record list into the mobile track in its source interval, changing D to mobile A and subsequent L to mobile D. After rewinding to the mobile A, shift the whole list left one cell at a time: seek its R, erase it, carry its symbol left through each occupied cell, preserving stationary and inner/output components, write A at the new left cell. Stop when mobile A is over stationary first A. This takes H+1 shifts. No variable-size item is stored in the finite control; carry only one symbol.

At each stationary key start, mobile A is aligned to it. Copy the k stationary key bits and delimiters onto the inner track at the first mobile record. Rewind within the inner word. Compare inner key with the parked mobile record using a one-bit equality state, and retain a one-bit OR of successes across the list. Move right through k bits, detect record end at inner R, then return left. If another record remains, erase inner L, carry it and the k bits and R right one cell into the first inner blank, rewind to the new inner L. Repeat until it aligns with mobile D, then compare. Exactly k+1 inner shifts between consecutive records. Throughout this operation the outer mobile list is stationary; it is NOT moved once per comparison or per inner shift. Stationary keys and output also remain unchanged.

At the last record, erase the inner key on the way right, then return left to mobile A. Write the OR result at the stationary key start. Inspect the stationary key end and next marker (L or E), return to mobile A. If another key remains, shift the outer list right one cell at a time using the same finite carry method, rewinding to its new A after each shift, until it reaches stationary L. Exactly k+2 shifts per next key. If no key remains, mark current start on the inner track, erase the entire mobile list by one rightward pass, return to the marker, erase it and halt at the final stationary key start. Final mobile and inner tracks blank, all original keys and records unchanged, output bits only at key starts.

Proof of invariant: a one-cell carry shift moves precisely the specified delimited word one cell and changes no other product component. Copy phases are sequential aligned transfers between tracks. By induction on record index, inner key bits remain equal to the original key, the parked list remains unchanged, and the OR state is precisely the membership result over completed records. By induction on key index, all previous output bits are preserved, and the outer list is correctly parked. Preparation stops at stationary first A; transport between keys stops at stationary L before E. Cleanup restores both scratch tracks to blank. All visited blocks lie in the original stationary layout: outer list end never exceeds its initial right end, inner word stays within outer list. Final head at (Q-1)(k+2) logical cells.

## 3. Exact movement ledger and original alphabet

Fixed logical alphabet: stationary _AL01RED (8), mobile _AD01R (6), inner _L01R (5), output _01 (3), product 720. Encode all-blank as 222222 and the remaining 719 product symbols by six-digit base-three numerals 0..718. Physical alphabet {0,1,2}, 2 blank, width w=6. The actual compiled table follows the preceding block interpreter: read six symbols remembering prefix, rewrite six right-to-left, move to adjacent block start if required. Valid logical stay costs 12 physical transitions; move costs 17. No uncharged block transition. All raw-symbol control transitions enumerated by finite-state closure, total table. Invalid layout has no theorem guarantee. Host initial encoding of the stationary prepared layout is NOT a compiled raw-input parser.

Exact data-independent logical counts (no early exit on a match):

    P = H+1 + L + (L-2) + 1 + 2L(H+1)    # initial seek, copy, rewind, stay, left transport
    K = 2k+2                               # copy key and rewind
    J = R(2k+2)+(R-1)(k+1)(2k+3)           # compare/return, inner shifts
    E_key = k+2+L-2                        # erase key, return to list start
    N = 2(k+2)                             # write result, inspect next key, return
    S = (Q-1)(k+2)(2L-1)                   # outer shifts and rewinds
    F = 2L-1                              # erase list, return, halt

A left outer shift costs 2L including the stationary check state at its new A; a right shift costs 2L-1 with the next action charged to the next phase. An inner right shift costs 2k+3, with the next comparison/shift counted separately. Compare/return from inner L to L costs 2k+2. The single final halt, initial list rewind stay, and H+1 left-shift stays give exactly H+3 stays. Thus

    T_log = P+Q(K+J+E_key+N)+S+F,
    T_phys = 17*T_log-5*(H+3),
    visited span = 6*(H+1+L).

For Q,R,k>=1 this is O(Q R (k+1)^2) physical time and O((Q+R)(k+1)) span, including preparation and cleanup on this prepared layout. In terms of record-bit stream lengths the product cost is O(H*L). In particular copying and comparing a small inner key while the large list is parked does not force a move of the entire list per bit comparison. The measured program has 156493 nonhalt states, 469479 table entries and 10485035 description bits in the original F038 encoding format. This is a fixed program independent of Q,R,k. It is much larger than the prior mask primitive; do not confuse description size or simulated host time with an integrated solver's clock. The original universal tape_run supplies raw selector bits, not this prepared record layout, so it cannot invoke this primitive correctly as a standalone SAT program. It outputs track membership rather than contiguous original witness bits.

## 4. Constructive discovery: exact union rather than bounded joint pair enumeration

Keep the normalized nine-group family and definitions of A={g} union K (four actual key coordinates), P=A union {x,y} (six projected coordinates), wide guard E on P, and previous side-t cubes. Let X,Y be the independent original allowed extensions in the current intervals for actual key z; reject if A-incompatible or either empty. The former FAR-001 test rejected a whole rectangle covered by any individual support, and performed exact enumeration only if min(|X|,|Y|)<=C. Its counterexample consists of complementary pair masks.

A stronger test is possible without enumerating t^2 candidate pairs and rescanning the O(t^3) original list for each pair. Every original support contained in P involving both x,y has at most ONE coordinate from A (width<=3). Sort its selected forbidden records into a single stream by (x,y), each carrying either no key constraint (support {x,y}) or one A coordinate and its forbidden digit. For each fixed actual z, scan this stream, count a pair once iff x in X, y in Y and at least one record in its (x,y) group matches its optional A digit. This is exact union count U, not the sum of support cardinalities. Multiple matching supports and duplicate records count once. Unlisted pairs have no joint forbidden record. Define

    V_exact(D,z) = [A-compatible] AND [|X|*|Y| > U].

This is EXACT feasibility for original constraints supported in P at fixed key, not arbitrary nine-group SAT or private-coordinate feasibility. All original models survive; smaller intervals can only shrink the feasible pair set, so child truth implies parent truth. No correction row is changed: discard only references of infeasible keys. Therefore all previous intrinsic dense/run/DAG statistics and first-overflow unions cannot increase compared to the bounded filter for the same capacity. Root mass is now independent of C. The score with V_exact is no larger than the preceding bounded joint score. Full recovered branch set remains original AND (E OR first-overflow membership) by the same witness preservation and fallback argument. All original constraints retained.

Conditional physical cost ledger, distinguishing it from the compiled equality worker:

* At each node sort the O(t^3 polylog(t+2)) local projected original records by pair using sequential bit sorting and local sweep simulation, O(t^6 local-log) physical, no indexed access.
* For each of at most t^4 actual keys, compute X,Y by the inherited O(t) candidate scans of the O(t^3) record list with a small moving key, O(t^4 local-log).
* Move O(t polylog t) bits of masks, the O(log t)-bit key, previous pair, union counter and one-bit hit along the parked pair-major list. At each record compare the optional key field, check mask membership by a local scan within the carried masks, update hit; at pair change flush hit to count. Per-record comparison, mask lookup, carry and return O(t polylog t); O(t^3) records, hence O(t^4 local-log) per key. No global random access, no t^2-bit rectangle expansion. Counters fit local O(log t). This is a proposed fixed-track composition, not an executed transition machine for this whole operation.
* Position and move the O(t^3 local-log) original-list scratch along the O(t^4 local-log) map stream; charge O(C t^7 local-log) including moves across cap-sized frame. Total O(t^8+C t^7 local-log), absorbed by existing O(C^2 t^8 local-log) local worker. Child scratch may use parent-sized interval before compacting. All prior dense/run/DAG clipping and local-width IDs retained.

Root extra costs O(m^6 B^2+m^9/B^3+m^9/B^2) polylog m, B largest dyadic B^3<=m^2, as in interval filtering. Projected-only census O(C^2 m^6 B^2 polylog m) plus previous root build O(m^(803/96) polylog m). Full coarse prep O(m^(403/48) polylog m) and narrow/envelope prep O(m^(42/5) polylog m). Fixed root-filtered density rho_B bounds positive descendant counts, and first-overflow original fallback costs O(m^9 omega). With score J=min_C(C^13 rho_B+omega), inherited local-log dyadic estimate gives O(m^9 J^(1/6)(1+log(1/J))^A) near zero, and same complete direct bound O(m^(42/5) polylog m + m^9 Q_exact^(1/6) local-log) / span O(m^3 polylog m), CONDITIONAL on full inherited physical primitives. The former naive t^9 scan estimate is not inherent to exact projected joint feasibility. This does not remove the need for a vanishing score. No general exact projected filter compiled here; no formal or independent audit of the entire bound.

## 5. Adversarial track: key-only feasibility is insufficient even when exact

Use the preceding permuted-field obstruction (7b886ee) at m=2^d, B=2^floor(2d/3). For fixed J with density zeta=Theta(1/log(d+2)), every nonself directed row has density p=zeta(1-zeta) and pair loss D=p*m^2. The prior probabilistic proof fixes J and chooses a common free-column permutation for simultaneous dense/run/DAG overflow at every coarse root. Its high-probability permutation event can be strengthened as follows.

For every nonself pair (a,b) and every aligned free B-square, let x0 be the first physical x digit of that B interval; expose its B columns (x0,y) for y in the square. Under a uniform common permutation this is a sample without replacement. Probability it contains no directed difference one is <=(1-p)^B. There are <=m^2*(m/B)^2<=m^4 tests. Because p*B grows exponentially in d up to slow logs, the union failure probability tends to zero. Intersect with the prior simultaneous high-probability events; a single permutation exists satisfying all. This uses the inherited proof awaiting independent review; no random solver or supplied advice.

Modify the narrow predicates exactly as in FAR-001, with one escape x at the start of EVERY B interval, S_x={0,B,2B,...}; unlike FAR-001, DO NOT add the binary y-escape gate. For x outside S_x, original support {g,x} excludes high-bit-zero source, and {g,1,x},{g,2,x} force the corresponding bits of f(c) (interleaved target with high bit one). For x in S_x all these predicates are vacuous. No further cross supports except original field wide bit. The target f(c) has zero narrow directed loss from every source, while every other candidate has positive narrow loss from source f(c) outside escape. Wide sums to every target equal. The actual greedy first facility is uniquely f(c), and every second marginal <=D<m^2, since only the candidate's own source can improve. Nonincreasing marginal gains imply actual best round singleton. Thus beta=1/m, delta_n=0, delta_w=(1-1/m)p->0 genuinely slowly. Context B-cubes cover all m/2 targets. No change to the raw directed guard.

Now for every real nonself map key in every projected B-root, the strengthened event supplies an actual directed one at x0 in S_x. Old wide bit zero, narrow predicates vacuous, private digits unconstrained. Hence it is an ORIGINAL E witness, not merely a projected feasibility flag. Self keys have zero E and are irrelevant. Every source/context key carrying a nonzero correction row has such a compatible correction at every B-root. Consequently any filter that ONLY deletes whole map references and is required to preserve EVERY original E model cannot delete any nonzero row reference at those roots. Even a hypothetically exact test of existence of original E completion for each key cannot shrink the root collection. This is stronger than the failure of independent or bounded joint feasibility. It is NOT a claim against algorithms allowed to select just one witness or modify row bits.

All three unfiltered root representation lower bounds from the prior proof therefore remain after ANY such safe key deletion. For all allowed C, omega_dense=omega_run=omega_DAG=1 and the root-filtered mass remains the raw E mass for this example. The exact feasibility filter cannot make these scores vanish, even with perfect local P feasibility. Yet the actual original-compatible E set is contained in x in S_x, so its true expanded density <=1/B->0 (indeed polynomially small). This is a sharp distinction between key eligibility and cell eligibility. A row may be necessary even if almost all of its bits are irrelevant. The example is deliberately easy SAT and is not a lower bound on SAT, the complete approximate portfolio, other coordinates or any algorithm that tests pointwise feasibility. The asymptotic simultaneous overflow is a mathematical existence argument, not demonstrated by the finite controls below.

TECT-X rejects the proposed implication: exact feasibility of map keys plus vanishing average loss implies tight overflow for those same key-filtered direct certificates. Future investigation, if independently authorized after the mission review, needs a genuinely different invariant: pointwise original compatibility of surviving E bits, an asymmetric raw-factor search, or another route. Do not keep escalating key-only feasibility or adding direct encodings as though this obstruction were absent.

## 6. Executed evidence

Physical machine: 5620 exhaustive executions for k=1..3, Q,R=1..2, every binary key/record list; 10572 membership outputs, 40120496 physical transitions in this set, 12 one-step-short timeout controls. All stationary and scratch symbols, output, final head, span, exact clock, and external sentinels checked. Descriptor decoded entry by entry against actual table. Scaling cases [Q,R,k,physical,logical,span,outputs]:

    [1,1,1,922,56,42,"0"]
    [4,8,3,67749,3992,324,"1111"]
    [8,16,4,404464,23807,780,"11111111"]
    [16,32,5,2266239,133342,1836,"1111111111111111"]
    [32,64,6,12088510,711165,4236,"11111111111111111111111111111111"]
    [8,8,12,1145752,67431,1308,"01001001"]

Counts are simulated physical transitions on a fixed table, not host operations or fitted exponents. Test inputs are prepared blocks; copying the stationary list to a mobile list and clearing both scratch components ARE included, but preparing raw normalized selector data is not. The exact formula holds for valid nonempty lists of equal-length words; not an empty-list API or arbitrary variable-length record parser.

Separate pair-major union host audit: 2304 exhaustive nonempty two-digit mask/forbidden-matrix pairs; former bounded C=1 filter misses 50 infeasible rectangles; exact union misses zero. 43328 local key checks, 58412 direct local pair checks, 1810 nesting checks, 90 inserted duplicate pair records, 2408 independently feasible keys without joint completion, no discrepancies. Tests include padded digits, A-only constraints, single-free supports, binary pair support and ternary pair supports with each A coordinate. This is a semantic test, NOT a physical transition count.

Finite distributed-escape field controls with fixed |J|=m/4 and seeded common column permutations (one attempt at each domain), check uniform nonself pair loss, exact P feasibility at all nonself keys/free blocks, genuine original E mass, actual first facility and all second marginals. [m,B,nonself key/free block checks,raw expanded E mass,exact P-key-filtered mass,actual original E mass,number of nonself key/free blocks with actual E at escape x]:

    [16,4,1920,2949120,2949120,761856,1114]
    [32,8,7936,195035136,195035136,23789568,6294]
    [64,16,32256,12683575296,12683575296,799014912,30937]

Every P-feasibility flag passes. Not every actual E flag passes at these finite sizes; the stronger all-E-positive event is established only asymptotically by the separate probability argument. No claim that finite controls show simultaneous root overflow. Exact context multiplicities used for expanded mass. Greedy checks total 56 unique first choices, 2632 second marginals, 5264 pair-loss checks. All final JS assertions passed.

## 7. TGA and impact decision

PHYS-02 is no longer wholly unimplemented: nested fixed-bit equality semijoin has a concrete table, exact cost and executed finite evidence. Split into PHYS-02A (prepared equality composition review), PHYS-02B (actual local support-aware masks/pair union/record composition and cost). Both remain open for the integrated evidence gate. PHYS-01,03,04 and FAR-08 remain open. FAR-03 has stronger restricted exact discovery argument; FAR-04 still conditional; FAR-06 uniform recovery blocked with new rejected key-filter implication; FAR-07 exact eventual stage blocked. The separate graph is editorial evidence bookkeeping, not proof certification. Existing global graph unchanged.

Decision: COMPLETE_BOUNDED_MISSION_REVIEW_OR_REDIRECT. The original three-cycle budget has been used as three authored investigations, not 21 external model calls. No further compression variant or automatic FAR extension authorized by this graph. Seek independent verification of the physical invariant, prior asymptotic obstruction and complete ledger; only resume on an independently scoped hypothesis that can bypass the key-only obstruction. The exact joint-filter improvement is useful as a local lemma even if the larger route is retired. No numerical likelihood of resolving P versus NP.

No normalized encoder/verifier integration, independent mathematical review, Lean formalization, full physical solver, universal-stage execution or exact-head CI confirmation. The prior finite cubic interval and Lean census not freshly recounted. Global uniform recovery and P versus NP OPEN; promotion NONE.
