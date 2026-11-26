# F038 — Three-context zero-loss covers and projected exception envelopes

PNP_RESOLUTION_STATUS = OPEN. Parent bf0caa2b6ad4c9d7a21a1969209f8eae170607d8 (stationary restriction tree). Mathematical machine-existence construction conditional on the inherited fixed-track sweep, mobile extraction and stationary-tree bounds. Executed standalone semantic regression. No compiled original-U machine, Lean proof or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push CI is unconfirmed.

## 1. Result and precise scope

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), arbitrary negative cross clauses of width 1..3 and the fixed one-hot/OR/pin/guard extension. Let F_H be the actual raw selected forbidden bit on support H. Choose a group g and a set K of THREE conditioning groups, disjoint from g. For context c in [0,m)^K and digits a,b of g define

    d_c(a,b)=sum_{H containing g} m^(2-|H minus ({g} union K)|)
                 * #{z on H minus ({g} union K):
                       F_H(a,c,z)=0, F_H(b,c,z)=1}.

Only conditioning coordinates present in H are used in its bit lookup. Every section has total weight m^2; there are 37 sections. For nonempty C_c define U_c={a:min_{b in C_c} d_c(a,b)>0}, the digits having NO zero-loss representative. Define

    beta = sum_c |C_c|/m^4,
    gamma = sum_c |U_c|/m^4.

There is ONE fixed deterministic original three-symbol single-tape witness machine correct on the entire nine-group family, such that on any sequence of SAT instances admitting beta->0 and gamma->0 for some g,K (which may change between inputs), its time is o(m^9)=o(L^3). Thus it eventually fits the exact cubic stage, with no supplied sets, contexts or convergence rates. It computes a score sigma=beta+gamma for its own choice and satisfies, for sufficiently small positive sigma,

    O(m^8 polylog(m+2) +
      m^9 sigma^(1/2) (1+log(1/sigma))^a)

physical transitions, with fixed exponent a, and O(m^3 polylog m) visited span.

IMPORTANT: gamma measures the fraction of source/context pairs with any newly forbidden context, not the preceding normalized average weighted loss delta. The theorem bypasses width-six exceptions by conservatively retaining their source/context projections. It does NOT establish arbitrary slow vanishing average-loss recovery for three contexts. The prior two-context average-loss theorem remains separate. The all-different example below shows why the distinction matters.

## 2. One width-four envelope suffices

For each context c, all representatives cover themselves since d_c(b,b)=0. Therefore C_c and U_c are disjoint. Set P={g} union K, and define a single allowed relation on P:

    A={(a,c): a in C_c or a in U_c}.

Its normalized density equals sigma exactly. Restrict the ORIGINAL model set by membership in A, retaining every original constraint. Given any original satisfying tuple x, write a=x_g,c=x_K. If a is uncovered, x already belongs to this restricted problem. Otherwise a has a representative b in C_c with d_c(a,b)=0. For every support containing g, every originally allowed context remains allowed when a is replaced by b; the nonnegative weighted sum is zero, so each individual loss is zero. All other supports are unchanged. The modified tuple y is a satisfying original tuple with y_P in A. Conversely every restricted model is an original model. Thus satisfiability and witness recovery are exact, including unique SAT, but this is not necessarily equality of the full original model sets.

A direct contextual replacement can create exceptions on H union K of width SIX. Every genuinely failed replacement for which the representative has been selected with zero loss whenever available lies over an uncovered (a,c); no such failure can occur outside that envelope. We need not identify which free digits violate a constraint, enumerate the width-six exception table, or express it in the external width-three selector. Even if many uncovered source/context pairs have no actual failing original solution, retaining them is safe. This is a stronger sparsity hypothesis on a lower-dimensional projection, not an unconditional compression of width-six relations.

## 3. Greedy selection and adaptive score

For each context let D[a,b]=d_c(a,b). Start with all m source digits uncovered. Repeatedly add the unused candidate b covering the largest number of currently uncovered digits with D[a,b]=0; ties by least digit. Update uncovered flags. For each positive round k, let u_k be the number still uncovered, and record k+u_k. Choose the smallest round attaining the minimum. The full m rounds cover every source digit by self-coverage; no risk of an empty representative set.

For any competitor C_* of size h>=1 leaving u_* uncovered, the sum of its h individual marginal coverage gains is at least u-u_* at a state with u uncovered. Already selected members have zero gain. Thus if u>u_* a greedy addition reduces excess by at least a 1/h fraction; otherwise monotonicity suffices. Consequently

    u_k <= u_* + m exp(-k/h).

At k=ceil(sqrt(h*m))<=m the minimum normalized context score is at most

    sqrt(h/m)+1/m+u_*/m+exp(-sqrt(m/h))
      <= 2 sqrt(h/m)+1/m+u_*/m.

Average over all m^3 contexts and use concavity of square root. Select the g,K choice with least sum of context scores (ties by a fixed canonical order), out of 9*binom(8,3)=504 choices. The computed score then obeys

    sigma <= 2 sqrt(beta_*) + 1/m + gamma_*.

Thus sigma->0 for any competitor with beta_*,gamma_*->0. The machine computes the scores, not the optimal arbitrary representative sets. No guessed partition or promised parameters enter its control. For a constant h competitor with u_*=0 at every context, the stronger estimate k=ceil(h log m) (for sufficiently large m) gives sigma=O(log m/m).

## 4. Physical selection within O(m^8 polylog m)

The earlier two-context factorization also applies to three conditioning groups because a raw support containing g has at most two other groups. For each H containing g let J=H intersect K and O=H minus ({g} union K). Its distance contribution depends only on a,b and the J assignment, summing over m^|O| contexts with weight m^(2-|O|).

For |J|=0,1 store contribution tables indexed by (J assignment,b,a), candidate-major within each J slice. Their total size over the fixed support count is O(m^3 polylog m) bits. Enumerate explicit raw zero and one bits and sort by relevant support/context/digit keys on fixed sequential bit tapes. Aligned row scans and rewinds cost O(m^(|H|+1) polylog m)<=O(m^4 polylog m) bit time per support, with O(m^3 polylog m) span. For |J|=2 the support is exactly a triple with g and two conditioning groups; store only its raw table, not an m^4-distance table. At a fixed full context, read its m-bit vector; the contribution is m^2 when source bit is zero and candidate bit one, otherwise zero. Initial parsing, canonical record extraction, pins and all these caches take O(m^7 polylog m) physical steps via the inherited sweep simulation, and O(m^3 polylog m) span.

A global sweep overhead of m^3 for every bit step of all m^3 contexts would lose cubic slack. Instead use the inherited mobile carry-shift workspace on a fixed encoded product component, with O(m^2 polylog m) blocks. For a single context, scan the stationary original-scale tables and collect only their matching J slices (m^2 entries per cached support) and the raw bit vectors (m entries per |J|=2 support). The constant number of slices fits the mobile workspace. Keep the context digits and counters with it. Moving it across O(m^3 polylog m) stationary blocks, comparing the current record's keys, scanning or shuttling within the workspace, and appending a matching record with local cursor return cost O(m^5 polylog m) original transitions, even if a full workspace scan is charged per stationary record. Rewind to a marked local scratch origin. The shift routine is the earlier constant-track carry shift: moving a block one physical encoded position takes a scan proportional to its width while preserving stationary components. No global record-sized random access is assumed.

Run the per-context algorithm wholly inside a reserved O(m^2 polylog m) local interval. Combining slices by aligned sequential addition and producing the |J|=2 contributions from their bit vectors take O(m^2 polylog m) bit steps. Greedy candidate-major matrix scans against the uncovered vector, selected flags, winning-candidate rescan and updates take O(m^3 polylog m) bit steps for all m rounds and a deterministic rerun of the chosen round. Even charging a full O(m^2 polylog m) local sweep per bit step gives O(m^5 polylog m) physical moves. The simulated head markers and scratch are confined to this local interval; this is not the global original-scale sweep. Only the context score and, when needed, the representative/uncovered membership vectors are copied out. A per-bit shuttle across the global span for the O(m polylog m) output costs O(m^4 polylog m) per context, dominated by the m^5 bound. Clear marked local scratch between contexts. The original stationary tables are not duplicated per context.

There are m^3 contexts and a fixed 504 choices. Total score selection time is O(m^8 polylog m), with the original-scale span. In the first pass save only the best choice and score, not the O(m^4) membership table of any choice. Rebuild the caches for that chosen choice if necessary. The second pass described next recomputes the greedy memberships once per valid context, in a different enumeration order, for another O(m^8 polylog m) moves. The tie rule is the same, so recomputed memberships realize exactly the selected score. All counters and fields have O(log m) bits, and the number of physical product components is fixed. These claims rely on the inherited mobile workspace and constant-track simulation routines; they are not measured transition counts.

## 5. Blockwise envelope construction and stationary tree reuse

Pad the latent domain to M, the least power of two >=m, excluding every padding digit by unary negative clauses. Choose b as the largest power of two with b^3<=m^2. Thus b=Theta(m^(2/3)), b divides M, b^4<=m^3 and m*b^3<=m^3. The choice is computed with fixed integer arithmetic.

Enumerate coarse blocks on K (the three conditioning coordinates) first. For one such block, recompute the chosen greedy membership vectors for each valid context in it, and store the allowed (a,c) records or membership bits for every real a. This uses at most m*b^3<=m^3 records; invalid context digits are skipped. No full original-scale width-four envelope is stored. For each coarse interval on g, generate the b^4 local membership flags by sequential sorting and merging candidate (a,c) queries against the saved block membership stream, rejecting padding. Each such batch has O(m^3) entries or fewer. Build the parent stationary preorder restriction tree of width four from the flags. It stores an OR of descendant flags at each node, plus reserved original-record frames of local size O(t^3 polylog(t+2)) at scale t. Tree creation including sorting, delimiters, frame reservation and copy into the worker region takes O(m^6 polylog m) physical moves by the inherited fixed sequential sweep implementation. Across all (M/b)^4 projected blocks this costs O(m^(22/3) polylog m); membership recomputation is already charged separately in Section 4. Retain one K block's membership data while processing its g intervals, then erase it and advance K. Preserve raw records and actual pins throughout.

For each projected coarse block, reuse its tree over every coarse block of the other five groups. Extract the local original forbidden records, including translated padding units, with the inherited O(b^3 polylog m) mobile workspace over the original O(m^3 polylog m) span. Filtering, translating, appending the O(b^3) retained records, returning to the tree root and initialization cost O(m^3 b^3 polylog m) physical moves per full tile. Copying per bit into the root frame is included. No repeated restriction-table construction per private block. The total over all (M/b)^9 tiles is O(m^12/b^6 polylog m)=O(m^8 polylog m).

At a full local node, read the stationary projected OR flag. Empty means reject; at t=1 accept iff the flag is one and no local forbidden record remains. Otherwise enumerate all 512 child vectors, translate only the original width<=3 records and copy them to the reserved child frame selected by its four P bits. Private choices reuse the same child sequentially after its earlier traversal clears its writable data. Immutable tree flags are preserved. Each active ancestor has distinct projected depth, so frames never alias an active ancestor. This is the parent's stationary tree traversal, specialized to width four: subtree extent O(t^4 polylog(t+2)), copying at most O(t^3) records across that extent, so O(t^7 (1+log(t+2))^a) per node, including navigation, child pushes/pops, cleanup and local digit propagation. At t=1 the cost is constant. Local fields, counters and relative delimiters use t, not global m; original offsets are only restored at the coarse root. All reserved tree regions occupy O(b^4 polylog b)<=O(m^3 polylog m) span. The outer dispatcher, stationary data, local scratch and reusable worker share a fixed finite product alphabet encoded by constant-width binary blocks of actual 0,1,2.

Any original satisfying tuple with its P projection in A survives all flag tests along its unique path; any accepted leaf is such a tuple. On success recover original digits with offsets, reconstruct fixed one-hot/OR/guard and actual pin bits, and emit contiguous raw n-bit witness with physical halt head at the first bit. Once-only output shuttles cost O(m^4 polylog m). On exhaustion halt on blank. The procedure is correct even when the score is not small.

## 6. Local-log bound and exact clock

Put R=|A|, rho=R/m^4=sigma. R>=1 because each context has a representative. At scale t, the number of passing full nodes is at most min((M/t)^9,R*(M/t)^5). Each visited node below the coarse roots has a passing parent and at most 512 siblings/children per parent, so its count is bounded by a fixed constant times the same expression. Mandatory coarse roots have total work O((M/b)^9*b^7 polylog b)=O(m^9/b^2 polylog m), dominated by m^8 polylog m.

Sum descendant work over all dyadic scales (extending beyond b only increases the bound):

    sum_t min(M^9/t^2,R*M^5*t^2)*(1+log(t+2))^a.

The crossover is t0=M/R^(1/4). Below it the second term decays geometrically towards smaller t, above it the first decays geometrically towards larger t. The local logarithms multiply these tails by at most a fixed polynomial in the scale index, whose geometric weighted sum converges. Rounding to a neighboring dyadic t changes constants. The bound is O(M^9/t0^2*(1+log(t0+2))^a), equivalently O(m^9 rho^(1/2)*(1+log(1/rho))^a). No global log m multiplies the small-density term. The unpruned sum O(M^9 sum_t t^(-2)*(1+log(t+2))^a)=O(m^9) also shows unconditional cubic-order time on the family, with the prior additive stage-constant interpretation only.

Combining the score selection, block recomputation and extraction proves the stated runtime. If beta_*,gamma_*->0, the adaptive inequality implies sigma->0 and the normalized time tends to zero. Since L=Theta(m^3) and the machine's finite description length ell is independent of the instance, its clock at 3 ceil(log2 L) is at least L^3/2^ell once eligible. The o(L^3) bound eventually fits it. No computed ell, numerical threshold, compiled machine or actual stage run is claimed. The uniform bound implies an existential positive lower bound on the computed score for sufficiently large actual exact-cubic SAT misses, if any. It does not prove their existence.

## 7. Strict separation from two-context directed compression

Let q=2^d, m=q-1, with digits identified with distinct nonzero vectors in GF(2)^d. For all pairs i<j in {1,2,3}, forbid triples {0,i,j} exactly when <x0,xi+xj>=1. For j=4..8 forbid triples {0,1,j} when <x0,x1> differs from <x1,xj>. For every binary pair among groups 1..8 forbid inner product one. No other cross clauses. The primal graph is complete. The tuple with all vectors equal to the weight-two vector 3 is satisfying (its self inner product is zero). This is an easy SAT control, not asserted unique or hard.

For g=0,K={1,2,3}, partition a by (<a,x1>,<a,x2>,<a,x3>). Choose a nonzero representative from every nonempty fiber, at most eight. This preserves every raw bit involving g at the fixed context, hence gamma=0 and beta<=8/m. The sharper greedy comparison yields sigma=O(log m/m), so the conservative charged bound is O(m^(17/2) polylog m)=O(L^(17/6) polylog L).

For every possible two-context choice for g=0 at least one of 1,2,3 is not fixed. Pick a main triple with that group and another of 1,2,3. For distinct nonzero a,b there are q/4 vectors w satisfying <a,w>=0,<b,w>=1. If the other group of this triple is fixed to c, at least q/4-1 such w are realizable as c+x with x nonzero, and each loss has weight m. If both are unconditioned, each w has q-2 ordered nonzero decompositions, giving q(q-2)/4 losses. Other fixed context coordinates do not affect this raw support. For any g>=1, choose a binary neighbor among 1..8 not equal to g or either conditioning group. Its section alone gives mq/4 loss for distinct a,b. Thus every distinct source/representative pair, at every two-context assignment and for every choice of g and conditioning pair, has directed loss at least

    D_min=min(m*(q/4-1), q*(q-2)/4, m*q/4).

For q>=8 this is positive and D_min/m^2 tends to 1/4. For any two-context representatives with normalized capacity beta_2, the normalized average directed loss is >=(1-beta_2)*D_min/m^2 because every digit outside its selected set must be replaced by a distinct digit. No vanishing-capacity, vanishing-average-loss two-context promise holds on this control. The new three-context zero-cover condition does hold. This separates these specific sufficient conditions, not all preceding algorithms or all lower bounds.

## 8. Explicit limitation of projected envelopes

Take the all-different binary family, forbidding (a,a) on every pair of the nine groups, m>=9. This is SAT. For any g and any three conditioning groups, there are five unconditioned neighbors. Any replacement a->b with a!=b newly forbids the partner digit b on each such neighbor, giving strictly positive directed loss. Consequently only a itself can cover a at zero loss. For every context, U_c is exactly the complement of C_c, and beta+gamma=1 for every choice of representatives. No zero-cover compression is possible, even with optimal sets.

Nevertheless choose one representative b not among the three fixed context digits (always possible for m>=9). The conditioned binary supports never add a violation, and each unconditioned neighbor contributes exactly m for a!=b, so d_c(a,b)<=5m. The normalized average-loss parameters are beta=1/m and delta<=5/m. Both vanish, even though gamma does not. This control demonstrates the distinction between the new promise and the still-open full three-context average-loss promise. It is not a counterexample to witness search or to any earlier solver. The exact projection of possible failures may be dense even when the higher-width exception relation is sparse.

## 9. Executed finite validation

Standalone JS audit executed in the tool runtime and the same audit function committed with a Node printing entry point. Fourteen fixtures at m=2,3 across seven constraint modes with supplied g,K choices test all context matrices, greedy marginal-gain inequalities against every competitor subset, zero-loss replacement and exact existence reduction by full tuple enumeration, and blockwise membership recovery. Results: 1,925 factorized matrix-entry comparisons, 245 contextual greedy runs, 245 selected representatives, 124 uncovered source/context occurrences, 33,577 original satisfying tuple occurrences, 13,638 original models already in the computed envelope, 33,577 successful zero-loss replacements, 141,365 full-tuple checks, 119 projected coarse blocks and 369 allowed envelope entries. The small adaptive fixtures had no satisfying tuple on an uncovered source/context pair. Separate forced singleton maps tested 4,505 positive-loss original model occurrences (all 4,505 replacements failed on those fixtures); 15,825 original model occurrences were retained by their forced envelopes. This exercises the reason for the fallback; the test does not claim a full model-set union for the adaptive reduction. Algebraic controls q=4,8,16,32 checked fiber preservation and minimum one-fixed-coordinate directed loss in the main triple; at q=32 there were 923,521 source/context checks, at most eight representatives per context and minimum seven unweighted lost partner digits for distinct sources with one context fixed. The all-different controls at m=9,12,20 check the stated arithmetic loss formula with representatives outside the fixed context; they are not exhaustive nine-dimensional model enumerations. All assertions passed.

The reference uses indexed host maps and direct enumeration. It checks factorization and block memberships, not physical mobile shifts, all 504 choices, the full stationary-tree worker (tested semantically in the parent), actual normalized encoder/verifier integration, exact U stage, or actual runtime constants. No compiled transition table, Lean proof or independent review. Exact-head CI unconfirmed.

## 10. Disposition

Three conditioning coordinates are now covered under a vanishing uncovered-source fraction, using a single width-four projected envelope instead of materializing width-six exceptions. The physical preprocessing obstacle from m^3 contexts is handled by mobile local matrix extraction and blockwise recomputation. Full average-loss three-context recovery remains open: it requires handling cases with many positive but tiny losses, without imposing a dense projected envelope. The next target is a width-six restriction solver with low-cost sparse representation or an exception decomposition retaining the average-loss promise. General unconditional exact cubic coverage, unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
