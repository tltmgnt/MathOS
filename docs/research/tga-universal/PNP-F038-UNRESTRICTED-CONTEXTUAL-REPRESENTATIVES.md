# F038 — Context-conditioned representatives and streamed width-four exceptions

PNP_RESOLUTION_STATUS = OPEN. Parent 31fd3ec1f3c5a92360a633de31330e76c50a5d96 (directed representatives). This is a mathematical machine-existence construction conditional on the inherited physical parsing, mobile extraction and spatial-frame resource bounds. Executed standalone semantic regression, not a compiled original-U transition table, Lean proof, or independent review. Parent combined statuses and PR-triggered runs were empty; push-triggered CI unconfirmed.

## 1. New sufficient condition

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), arbitrary selected negative cross clauses on one through three distinct groups, and the inherited fixed one-hot/OR/pin/guard extension. Let F_H(z) be the actual raw forbidden bit on support H. Fix distinct groups g,h. For every digit c of h, let C_c be a nonempty set of representative digits of g, and allow the replacement of g to depend on BOTH its old digit a and the unchanged h digit c. Define the directed distance

    d_c(a,b)=sum_{H containing g} m^(2-|H minus {g,h}|)
             * #{z on H minus {g,h}: F_H(a,c,z)=0,F_H(b,c,z)=1},

where c is omitted from the raw bit when h is not in H. Each of the 37 sections has total weight m^2. Define

    beta = (sum_c |C_c|)/m^2,
    delta = (sum_c sum_a min_{b in C_c} d_c(a,b))/m^4.

For every fixed 0<epsilon<=1, suppose some ordered pair (possibly changing between inputs) admits beta=O(m^(-epsilon)) and delta=O(m^(-epsilon)). There is ONE fixed deterministic original three-symbol one-tape witness machine, correct on the entire nine-group family, with time O(m^(9-epsilon/2) polylog(m+2))=O(L^(3-epsilon/6) polylog L) on this promise. Its description does not depend on epsilon, the pair, the sets, or masks and pins. Visited span O(m^3 polylog m). It therefore eventually fits the exact cubic stage uniformly on a promise with fixed constants. No external advice or randomness.

The machine computes a contextual representative score sigma. More generally its charged runtime is O((m^8+m^9 sigma) polylog m); this estimate requires polynomial slack (or another rate sufficient to dominate the fixed logarithmic factor). Unlike the preceding one-coordinate directed theorem, we do NOT claim arbitrary slow vanishing beta and delta suffice. This is a different, strictly more expressive substitution mechanism, not an unconditional subcubic algorithm.

## 2. Exact reduction, including width-four exceptions

Choose a deterministic minimizing map p_c(a) in C_c for each a,c. The representative relation on {g,h} is S={(a,c):a in C_c}. For each H containing g put P=H union {h}, of size 2..4, and define

    E_H={z in [0,m)^P: F_H(z_H)=0 and
         F_H(z_H with g replaced by p_(z_h)(z_g))=1}.

The support's error is measured on the entire P domain, including the context even if absent from the original support. Directly summing over c,a and the other digits shows

    sum_H |E_H|/m^|P| = delta.

For an original solution x, replace only x_g by p_(x_h)(x_g). If this succeeds, the new tuple is an original model whose {g,h} projection is in S. Otherwise a newly violated support H must contain g, since all other coordinates stayed fixed. Its old bit was zero, so x_P belongs to E_H. Therefore original satisfiability is equivalent to the OR of the original problem restricted to S and the original problem restricted to each nonempty E_H. Each branch only restricts original models, and on a successful replacement the witness may change. This is an exact existence reduction, not necessarily an equality of entire model sets. It remains exact for unique SAT, where any successful replacement must return the same model. There are at most 38 branches. Width-four E_H is not assumed expressible as a conjunction of original width-three clauses on the same groups; the streamed fusion construction below handles it without changing the external U input.

## 3. Adaptive contextual facility selection

For each of the 72 ordered pairs and each context c, use the previous directed greedy rule on d_c. Start with residual R_a=37m^2, add the unused candidate b minimizing sum_a min(R_a,d_c(a,b)), update residuals and map labels (earliest chosen on ties), and choose the smallest positive k minimizing k*m^2+F_k, where F_k=sum_a R_a after k rounds. Assign a label in round one even if a residual equals the initial bound. For each pair sum these scores over c; choose the smallest pair score with a fixed tie break. Let sigma be this score divided by m^4. It equals the computed beta+delta.

The earlier one-step averaging proof applies separately for each c without metric assumptions: for a competitor of size h_c and total loss F_*c, the sum of marginal gains of its members is at least F-F_*c, so the best unused candidate decreases positive excess by at least a 1/h_c fraction. Thus F_k<=F_*c+37m^3 exp(-k/h_c). Compare with k=ceil(sqrt(h_c*m)); normalized by m^3, the context score is at most sqrt(h_c/m)+1/m+F_*c/m^3+37 exp(-sqrt(m/h_c)). Since exp(-x)<=1/x for x>=1 and the square root is concave, averaging over c yields

    sigma <= 38 sqrt(beta_*) + 1/m + delta_*.

The starred parameters refer to ANY competitor pair and sets, not necessarily those found by the algorithm. This proves the stated O(m^(-epsilon/2)) score on the polynomial promise.

To charge preprocessing, parse actual canonical raw bits and guarded pins with the inherited sequential-bit routines. Process one pair and one context at a time. Enumerate and sort the 37 restricted signature sections by (source digit, support, other digits), including absent bits. For supports not containing h, reuse their original sections; for supports containing h retain the entries at c. There are O(m^3) entries at any one context. This can be done with sequential scans of the original O(m^3) record stream and external merge sorting on fixed bit tapes. A candidate row copied to scratch can be compared sequentially against all rows, with aligned weights and counters. Building the full matrix costs O(m^4 polylog m) bit steps per c, O(m^3 polylog m) span; candidate-major matrix scans and residual updates for m greedy rounds cost O(m^3 polylog m) bit steps per c as in the parent. Save only the chosen map and set for each c, O(m^2) entries across a pair; rerun the selected pair if needed. Do NOT store the signature streams or matrices of all m contexts simultaneously. Total O(m^5 polylog m) multitape bit time and O(m^3 polylog m) span; the inherited encoded-track sweep simulation charges O(m^8 polylog m) original transitions. Fields and weights have O(log m) bits. No indexed random-access oracle is assumed.

## 4. Stream any restriction of width two through four

A useful independent resource lemma is the following. Given a distinct allowed list A of R tuples on a fixed support P of size k in {2,3,4}, streamed in chunks of at most m tuples with O(m^3 polylog m) generator span and O(m^7 polylog m) total physical generation cost, the original problem restricted to A can be solved in

    O((m^7 + (R+m)*m^(9-k)) polylog m)

physical transitions and O(m^3 polylog m) span, without storing the full A. Empty A rejects immediately after generation. The generator must yield exactly ceil(R/m) chunks, preserving a partial chunk across its internal batch boundaries. The proof uses the parent's sparse-relation fusion semantics and the later spatial stack rather than balancing a fixed-depth local solver.

For the representative branch the allowed stream S has at most m^2 entries and is enumerated directly from the selected sets. For any E_H, enumerate all m^|P| candidates in lexicographic order in batches of at most m^3. Store candidate IDs local to a batch; merge sorted (c,a) queries against the saved map to recover p_c(a); then emit two raw-bit queries on support H (original and translated), sort and merge with the canonical raw bit stream, including zero bits. Restore order by ID, retain exactly old zero/new one tuples, and yield consecutive m-entry chunks, carrying any partial chunk over to the next batch. Each batch costs O(m^3 polylog m) fixed multitape bit steps (including a scan of the map and raw tables); O(m) batches at most, so O(m^4 polylog m) bit time and O(m^3 polylog m) span. The inherited sweep simulation charges O(m^7 polylog m) physical generation moves. No dense m^4 table is materialized. The 37 supports and chosen pair are fixed in count; one stream is processed at a time. Pause the generator at a completed simulated transition with head markers and loop state intact, copy each yielded chunk to separate worker components by per-bit shuttles within O(m^3 polylog m) span, and resume after the worker finishes. This costs O(m^4 polylog m) per chunk, dominated below.

For each chunk fuse all k coordinates of P into a single coordinate whose digit is the index of its chunk entry. All other 9-k coordinates keep their ENTIRE original domain [0,m). There are r=10-k in {6,7,8} local groups, all of width m. For each selected original clause, if it does not meet P, copy it with relabeled group IDs. If it meets P, emit one local negative clause for each chunk entry matching all its specified P digits, substituting the single chunk index for those literals. The resulting width is at most three, even if an original clause contains multiple P digits. Add negative unary padding exclusions for nonexistent chunk indices. OR-deduplicate. For an in-range local tuple, each forbidden original conjunction holds exactly when a corresponding emitted conjunction holds. The local tuples biject to the original tuples with projection in the chunk, and the chunks are disjoint. No constraint of width four is inserted into the actual normalized selector. Generate the inherited fixed extension with local zero pins and reconstruct the original full assignment (including original actual pins) only after recovering a successful original tuple.

For physical extraction use the earlier mobile carry-shift workspace on a fixed encoded product track, of O(m^3 polylog m) blocks, with the original record stream stationary. Scanning it with this workspace costs O(m^6 polylog m) moves, including the local chunk comparisons. For each fixed original support, a local translated clause identifies at most one original clause: its fused index identifies the P digits and the remaining coordinates identify the other digits. Consequently only O(m^3) records are emitted even before deduplication across the fixed number of original supports. Charging O(m^3 polylog m) per emitted record for an append and return to the marked chunk-map cursor adds O(m^6 polylog m) moves; nonmatching candidates are checked by sequential traversal of the map without a global shuttle per candidate. Generate the actual local normalized selector by sequential per-position checks, O(m^6 polylog m) moves. All data are on fixed reusable components.

## 5. Local solver using the spatial stack without projection checks

The dyadic spatial frame implementation in the earlier note works for any fixed r in {6,7,8}: pad to the next power of two M, store the local selected records in each frame, translate and push one of 2^r children at a time, test the single tuple at t=1, and return a witness by adding saved offsets while popping. O(t^6 polylog(t+2)) physical steps suffice for all within-frame record scans, adjacent copying, capacity initialization, pushes and pops at scale t. Local counters and coordinate widths depend on t, not on m. No induced relation solver is invoked. Each frame has O(t^3 polylog(t+2)) span, so the full stack occupies O(m^3 polylog m). The fixed alphabet/control and adjacent-frame implementation are inherited, with r built into finite control; no new track per level. Exact leaf checks suffice for correctness without pruning.

There are at most (M/t)^r visited nodes at scale t. For r>6 the dyadic sum of t^(6-r) polylog(t+2) converges, giving O(m^r) time plus the O(m^6 polylog m) setup. For r=6 the sum is at most polylog m, giving O(m^6 polylog m). A single bound O(m^r polylog m) covers all three. This follows from the inherited frame bound, not a claim that the r=6 logarithmic overhead has been removed. Follow the local physical solver head with constant overhead on its own encoded product component; no sweep across the outer input per local transition. Preserve the paused generator and chunk map on distinct stationary components, mark used extents, clear on failure. On success use the chunk index and original coordinates to reconstruct the original witness, and emit contiguous raw n bits with the actual head at its first bit. Per-bit shuttles within the original span give O(m^4 polylog m) output time. On exhaustion halt on blank. Each of ceil(R/m) chunks costs O(m^(10-k) polylog m) including extraction and conversion, proving Section 4.

Apply the lemma to S and all E_H. Their total normalized densities sum to sigma. The constant number of stream generators costs O(m^7 polylog m). The rounding overhead for any support is at most O(m^8 polylog m) because k>=2. Add the adaptive preprocessing to obtain

    T(m)=O((m^8+m^9 sigma) polylog m).

A fixed deterministic machine implements the whole procedure for every input of this family, irrespective of the promise; all worker routines use fixed tracks and finite control. On the polynomial promise sigma=O(m^(-epsilon/2)), so the strict polynomial slack eventually dominates all fixed logarithms and the fixed description penalty. At s=3 ceil(log2 L) the actual fixed description of length ell receives at least L^3/2^ell transitions once eligible. No numerical threshold, description length or compiled transition table is supplied. The prior unconditional O(L^3) family solver with additive stage constant remains available separately.

## 6. Separation from every single-coordinate directed representative promise

Let q=2^d, d>=2, and m=q-1. Identify each digit with a DISTINCT NONZERO binary vector in GF(2)^d (digit a corresponds to vector a+1 in binary). Use g=0,h=1. For each j in {2,...,8}, select exactly the forbidden triples on {0,1,j} for which

    <x0,x1> != <x1,xj>,

where the brackets are binary inner products. For every pair i,j among groups 2..8, select exactly the forbidden pairs with inner product one. No other cross clauses. The primal graph is complete: the seven ternaries connect 0,1 to each other and all seven other groups, which have every mutual binary edge. The tuple with every vector equal to the weight-two vector 3 is satisfying because its self inner product is zero. No uniqueness or hardness claim.

For every nonzero context vector c at h, choose one nonzero vector from each of the two dot-product fibers <a,c>=0 and 1. Both fibers are nonempty for d>=2. Map a to the corresponding representative. Every raw bit involving g depends on g only through <a,c>; thus all directed context losses vanish. Beta=2/m, delta=0. The adaptive bound gives sigma=O(m^(-1/2)), and the conservative runtime is O(m^(17/2) polylog m)=O(L^(17/6) polylog L).

In contrast EVERY single group has large directed pairwise loss for distinct source and representative digits, even with no context compression imposed on the other groups. For g=0, in just one triple {0,1,j}, for distinct a,b the q/2 nonzero context vectors c with <a+b,c>=1 make the two allowed fibers complementary. For each such c at least q/2-1 nonzero z have <c,z>=<a,c>, so replacing a by b loses at least q(q-2)/4 contexts. For h=1 and distinct context vectors a,b, the vectors w=x0+xj satisfying <a,w>=0,<b,w>=1 number exactly q/4, all nonzero (a,b independent over GF(2)). Each has exactly q-2 ordered decompositions into two nonzero vectors; hence the directed loss on that triple is q(q-2)/4. For each j>=2, use a binary relation to another group among 2..8. Distinct nonzero a,b have q/4 nonzero partners c with <a,c>=0,<b,c>=1. The width-two weight m gives loss qm/4. These bounds all hold for EVERY ordered pair of distinct digits, not just symmetric distance or an average sampled row.

Therefore for any single-coordinate representative set C, in any group, its total normalized directed loss is at least

    (m-|C|)*q*(q-2)/(4*m^3),

which tends to 1/4 if |C|=o(m). This excludes the preceding single-coordinate directed vanishing-loss promise even for optimal sets. The new theorem covers the family with context-dependent constant-size sets. It separates THESE two promises, not necessarily all earlier sufficient conditions; in particular this control is easy and not a candidate computational lower bound.

## 7. Executed finite verification

A standalone JavaScript audit executed in the tool runtime and the same audit function was committed with a Node printing entry point. For 12 fixtures at m=2,3 and six constraint modes, using two supplied ordered pairs, it computes contextual greedy maps, exact weighted exception masses and full substitution semantics by direct tuple enumeration. Adaptive maps: 38 representatives summed across all contexts/fixtures, total weighted error 22, 38,082 original satisfying tuples, 12,845 already in representative branches, 3 failed replacements recovered by exceptions, 38,079 successful replacements, 121,170 tuple checks. These small adaptive maps produced no nonempty width-four exceptions. A deliberately forced context-dependent map tests 1,529 failed substitutions (2 multiple-exception overlaps), 86 nonempty width-four exception occurrences, and exact streamed fusion for the first nonempty width-four support in each fixture where one exists: 10 chunks, 5,295 local tuple checks, 1,524 recovered local models. The audit tests width-three translation, padding and the exact model set of each tested fused branch. Separate q=4,8,16,32 controls check two-fiber replacements on a ternary, directed loss minima on both ternary roles and a binary role, and the constant witness. The measured minimum losses are recorded in the audit output; all assertions passed.

The audit uses host indexed containers and direct enumeration, not the sequential implementation. It does not execute all-pair minimization (the mathematical algorithm charges it), the batched sorted exception generator, physical spatial frames, actual normalized encoder/verifier, or the exact stage. It does not test every width-four branch by fusion, nor establish arbitrary slowly vanishing contextual scores. No physical timings, compiled original machine, Lean proof or independent review. Exact-head CI unconfirmed.

## 8. Disposition

Context-dependent substitution now has a uniform polynomial-slack cutoff, including genuine width-four exceptions, without enlarging the external normalized clause width or materializing the global higher-order relation. Any actual unbounded exact-cubic miss sequence must eventually resist the polynomial contextual score promise, in addition to preceding necessary conditions. No such misses are constructed. Next: remove the remaining logarithmic cost on width-four exception streams (or avoid fusion by a locally computable exception-pruning interface), so arbitrary slow contextual sparsity can be handled; investigate larger conditioned coordinate sets only with explicit physical costs. Unrestricted nine-group exact cubic coverage, unbounded B_3, general SAT and P versus NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
