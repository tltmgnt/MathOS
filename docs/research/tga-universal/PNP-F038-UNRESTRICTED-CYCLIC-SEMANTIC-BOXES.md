# F038 — cyclic overlapping masks and exact simultaneous-cut semantic certificates

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite reference checks; not a compiled original-U solver, Lean proof or independent review. Parent edf2c0f0af3c36810195738c8d1283db729fd9c5 (fixed-layout tensor barrier); exact-head CI not confirmed. This cycle changes from explicit intermediate representations to semantic rejection. No external algorithm is required.

## 1. New result

There is a nine-group normalized selector family with three independently variable ternary masks in three disjoint physical input slabs, connected by fixed equality clauses. It realizes a disjoint union of m layers of tripartite triangle problems, with exactly one full SAT assignment per surviving layered triangle. All satisfiable inputs of the family are eventually accepted at the original exact cubic stage by a fixed original-machine program with time O(L^(7/3) polylog L).

For sufficiently large m let M=m^3. On this family, the minimum alphabet of sound semantic rejection labels at either individual separated cut is exactly 2^M. However the minimum alphabet of a SINGLE label sound simultaneously at both cuts is exactly K(m)^m, where K(m) counts inclusion-maximal triangle-free tripartite graphs on three fixed labelled m-vertex parts. It is also the exact minimum cover by sound three-slab Cartesian boxes. In particular

    2^(M + Omega(m^2 log m)) <= K(m)^m <= 2^(2M).

This is stronger than the one-cut alphabet cardinality, but not a constant-factor improvement in its leading exponent from the displayed lower bound. The result concerns exact semantic rejection, not rejection of only a selected subset, nor unrestricted SAT lower bounds. For different labels at the two cuts the product of their alphabet sizes must be at least K(m)^m if both are sound; neither individual alphabet need exceed 2^M.

## 2. Physical family and exact model bijection

Use the inherited distributed layout with r=9, n=19m-7, L=n+1+2n^2+8 binom(n,3), m>=2. Group g uses one-hot variables X_g[j]=gm+j+1, 0<=g<9, 0<=j<m; use the parent's OR auxiliaries, zero pins, negative guard units and guarded pin lifts. For each pair of groups in

    (0,3), (0,6), (1,4), (2,7), (5,8)

add all negative binary clauses forbidding unequal digit choices: (-X_g[i],-X_h[j]) for i!=j. These are allowed cross-group clauses, distinct from the one-hot fixed clauses. Hence every surviving nine-group tuple has the form

    (d,a,b, d,a,c, d,b,c).

For each of the disjoint group triples (0,1,2), (3,4,5), (6,7,8), choose an arbitrary allowed mask X(d,a,b), Y(d,a,c), Z(d,b,c) respectively; select its corresponding all-negative ternary clause exactly when the allowed bit is zero. All other variable cross clauses are absent. The fixed clauses give precisely one extension for a surviving tuple. Thus the model count is exactly

    sum_{d,a,b,c in [0,m)} X(d,a,b) Y(d,a,c) Z(d,b,c).

For fixed d, interpret X, Y, Z as the edge sets between parts A-B, A-C, B-C of a labelled tripartite graph. A formula is SAT iff any layer has a triangle. This involves cyclic overlap of shared coordinates, not the earlier independent outer product or aligned two-mask intersection. Its actual witness search still has substantial exploitable structure.

Use the two cuts (between cells c-1,c)

    c1=L-8 binom(n-3m,3),   c2=L-8 binom(n-6m,3).

The normalized pool lists widths 1,2,3; within each width it orders supports lexicographically and signs in (-1,+1) order. Thus c1 is the start of the ternary support block whose smallest variable exceeds 3m, and c2 the analogous start for 6m. Every variable X-mask bit lies before c1, every Y-mask bit in [c1,c2), and every Z-mask bit at or beyond c2. All other bits, including the equality clauses and header, are fixed. Recombining the three slabs therefore gives exactly the intended independent recombination of masks. There are 2^(3M) distinct selectors with these fixed clauses.

## 3. Eventual cubic coverage on this exact family

Extract the three masks sequentially from the actual original normalized selector by enumerating supports/signs with O(log L)-bit counters. Complement the selected bits; within each stream the order is the ordinary lexicographic order on its three digits. The streams each occupy m^3 bits. Header parsing gives m from n=19m-7; no supplied streams or membership oracle are required.

On a fixed multitape bit machine, scan layers d in order. For each a, read the next m-bit row of X(d,a,*) and of Y(d,a,*) into two scratch tapes, leaving their main stream heads at the next row. Scan the m^2 entries of Z(d,*,*) sequentially in b,c order. For each b, read the corresponding X row bit once, scan the Y row in c order against the current Z row, and rewind the Y scratch row before the next b. Test for three one bits. Rewind the Z layer (not the whole stream) for the next a, except at the last a where the head stays at the next layer. Clear/reuse the scratch rows. Counters and local operations cost polylog L per entry. This costs O(m^4 polylog L) total time and O(m^3 polylog L) total visited space on each tape, including input and all reusable scratch. On success reconstruct the nine one-hot choices above, the OR bits, zero pins and zero guards; on exhaustion halt on a blank.

Use the charged fixed-track one-tape simulation from PNP-F038-UNRESTRICTED-DISTRIBUTED-HYPERCLIQUE.md: initial raw block expansion O(L^2), a fixed number of sweeps of the O(m^3 polylog L) coded interval per simulated transition, and output into a fresh contiguous raw region at cost O(n*m^3 polylog L). Thus original three-symbol time O(m^7 polylog L)=O(L^(7/3) polylog L), with finite control independent of m and the masks. The final head is placed on the first raw witness bit as in the original tape_run; no changed verifier or U. This is a machine-existence argument, not a transition-table compilation. With j=ceil(log2 L) and fixed description length ell, 2^(3j-ell)>=L^3/2^ell eventually dominates the runtime bound uniformly across masks.

Accordingly at sufficiently large m the EXACT stage rejection relation on this family equals the set D of triangle-free layered triples. Soundness excludes every UNSAT selector, while the fixed program covers every SAT selector. We do not assert this equality at the small sizes used in reference tests.

## 4. Exact one-cut versus simultaneous-cut certificate counts

Order allowed masks by componentwise inclusion of edge sets. D is downward closed. Every member extends to a maximal member by adding edges while remaining triangle-free. A maximal layered triple is precisely one that is maximal independently in each layer, so there are K(m)^m of them.

A sound three-slab box is a product of three collections of masks contained in D. A box cannot contain distinct maximal triples P,P': some mask of one has an edge absent from the corresponding mask of the other; substituting that entire mask into the other maximal triple creates a triangle (adding that one edge alone would already create one, and any other edges removed belong to the same pair of parts and cannot be needed for that triangle). Alternatively, fix the other two masks: the unique largest compatible mask on the remaining pair consists of all edges not closing a path of length two. If P is maximal then its remaining mask equals that largest mask. Thus any larger-in-some-coordinate substitution violates D. Conversely the downward box of each maximal triple is contained in D and the boxes cover D. Minimum box count is exactly K(m)^m.

The same exact count applies even to the weaker simultaneous-cut label rule: for any two members with the same label, both crossed pairs at c1 AND both crossed pairs at c2 must be rejected. This rule does not assume arbitrary three-way splicing. If two distinct maximal triples differ in the X mask, take the one with some new X edge and substitute its whole X into the other maximal triple, preserving the latter Y,Z: a triangle results by the largest-compatible-mask fact. This is a c1 crossing. If X is the same but Z differs, use the analogous c2 crossing. If X,Z coincide, maximality forces Y uniquely by the same fact, so they cannot be distinct. Hence any sound simultaneous-cut label is injective on the maximal triples. Conversely label each rejected triple by any maximal extension; sharing that label places both triples and all their crosses in the downward box. This proves exactness for overlapping certificates or a label function, even with noncomputable labels. A fixed-width label needs at least ceil(log2 K(m)^m) bits; for arbitrary finite binary strings without prefix requirements at least floor(log2 K(m)^m) bits are required in the worst case.

At an individual cut the exact minimum is only 2^M. For c1, fix Y,Z and define the projected path mask R(d,a,b)=1 iff there is c with Y(d,a,c) Z(d,b,c)=1. Rejection means X is disjoint from R. Label by X for the upper bound (a sound rectangle). For the lower bound choose Z to be the identity matching b=c in every layer and let Y be the complement of X in aligned (d,a,c) coordinates. The 2^M complementary pairs are rejected. Two different X masks have at least one accepting crossed pair. At c2, use X as the identity a=b in every layer and Y the complement of Z in aligned coordinates; the same proof works. The counts concern actual fixed physical cuts, not arbitrary abstract factorization. A tuple of two separately sound cut labels is a simultaneous label and hence obeys the joint lower bound.

## 5. Maximal graph counting without an external extremal result

For a fixed pair X,Y of m-by-m edge matrices in one layer, the unique possible Z in a maximal triangle-free triple is the mask of pairs (b,c) with no common a incident in X and Y. It follows that K(m)<=2^(2m^2).

For the lower bound choose any permutation pi of [0,m) and let Z be the perfect matching c=pi(b). Choose X with pairwise incomparable columns in the coordinatewise Boolean partial order, and set

    Y(a,pi(b))=1-X(a,b).

The triple is triangle-free. Every missing X or Y edge closes a triangle with the matching edge and the complementary bit. For each missing Z edge (b,pi(b')) with b!=b', column incomparability supplies an a with X(a,b)=1 and X(a,b')=0, so that adding the edge closes a triangle. Thus the triple is maximal. Distinct choices of pi and X give distinct labelled triples. In fact these are exactly the maximal triples with Z a perfect matching: saturation forces the two incident columns to be complementary and all off-matching missing Z edges force column incomparability.

In a uniform independent random X, the event that column b is coordinatewise <= column b' has probability (3/4)^m for each ordered distinct pair. By the union bound, at least 2^(m^2)(1-m(m-1)(3/4)^m) matrices have pairwise incomparable columns. For all sufficiently large m this is positive, yielding

    K(m) >= m! * 2^(m^2) * (1-m(m-1)(3/4)^m).

Taking m independent layers, with epsilon_m=m(m-1)(3/4)^m, the logarithm of the lower bound is

    m^3 + m log2(m!) + m log2(1-epsilon_m)
    = M + m^2 log2 m - O(m^2).

The last negative term from epsilon_m tends to zero; the factorial estimate follows e.g. by integrating log x. This proves the stated asymptotic lower bound, with no claim of an exact asymptotic leading constant for K(m).

## 6. Finite checks

Independent JavaScript enumerated every pair X,Y in a single layer at m=1,2,3, constructed the unique maximal-compatible Z and counted all triangle-free triples by its subsets. It separately tested saturation in X,Y. Results (m, triangle-free triples, maximal triples, maximal triples with Z matching, incomparable-column matrices):

    1, 7, 3, 2, 2
    2, 1699, 49, 4, 2
    3, 10347433, 6825, 72, 12

For m=1,2 it directly enumerated all triples and confirmed the total; at all three sizes it checked the matching characterization counts. These are graph semantics, not actual universal stage runs. The companion Python regression also directly checks coverage and the weaker two-cut pair-splicing fooling-set property on the m=1,2 maximal triples.

Separate JavaScript checks at m=2,3 built the actual canonical normalized pool, tested both physical cuts, fixed clauses and equality clauses, extracted all three masks and compared full clause truth on every nine-group one-hot tuple against the layered triangle predicate. Across 16 selectors: 161560 nine-group tuple checks, 776 layered tuple positions, 197 satisfying tuples, 12 SAT fixtures, 2 unique SAT fixtures, zero discrepancies. The Python regression uses the original helpers and verifier on a surviving witness per SAT fixture. Python execution and exact-head CI are unconfirmed at writing. These finite checks do not establish the asymptotic cutoff or the certificate theorem by enumeration.

## 7. Disposition

Cyclic shared coordinates can increase the necessary JOINT semantic certificate alphabet beyond the disjointness one-cut barrier, even without full three-way recombination. However this family is also eventually fully covered by the exact cubic stage. This quantifies a limitation of rejection-preserving splicing arguments, not a SAT lower bound. The next task should use genuinely unrestricted nine-group constraints (not equality reductions to four latent digits), and/or a sound argument targeted at unique SAT rejection rather than every UNSAT input. No general nine-group cubic cutoff, unbounded B_3, unrestricted lower bound, or P vs NP resolution is established. Finite cubic interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
