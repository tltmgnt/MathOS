# F038 — Adaptive sublinear quotients, outlier repair and local-payload amortization

PNP_RESOLUTION_STATUS = OPEN. Parent 49ccba92d83afc7f80addcb3977da037ca7815f4 (growing quotients). Mathematical machine-existence derivation conditional on the inherited original-tape spatial-frame and vanishing-occupancy constructions; executed standalone semantic regression, not a compiled original-U machine, Lean proof or independent review. Parent combined statuses and PR-triggered workflow runs were empty; push CI unconfirmed.

## 1. Result

Use the inherited nine-group normalized selector family, n=19m-7, L=Theta(m^3), arbitrary negative cross clauses on one through three distinct groups and the fixed one-hot/OR/pin/guard extension. For each group, suppose there exists a partition into at most B_0(m) nonempty classes. Suppose the raw selected-clause tables admit Boolean predictions constant on the corresponding Cartesian class cells, with total normalized Hamming error Delta_0 (sum over all 129 supports). Neither the partitions nor predictions are supplied to the machine.

There exists ONE fixed deterministic original three-symbol single-tape witness machine, correct throughout this family, with visited span O(m^3 polylog m), such that along ANY sequence satisfying

    B_0/m -> 0,   Delta_0 -> 0,

its runtime is o(m^9)=o(L^3). Thus eventual exact stage 3 ceil(log2 L) coverage follows. The number of classes can be m/log log m or arbitrarily more slowly sublinear; no fixed growth exponent, fixed class bound, rate of error decay, supplied partition or maximum-diameter promise is needed. This strengthens the parent polynomially sublinear, fixed-alpha result. It does NOT cover arbitrary linear quotient complexity.

The machine chooses its own B and majority error Delta as described below. Put beta=(B+1)/m. In the small-error, small-beta regime its charged time is

    O(m^7 polylog m
      + B^9 (1+log(2+m/B))^a
      + m^9 Delta^(1/2) (1+log(1/Delta))^a
      + m^9 beta^(5/7) (1+log(2+1/beta))^a).

Here a is a sufficiently large fixed integer, not a parameter of the input. The Delta term is zero at Delta=0. Outside this regime the procedure is still exact, and the inherited unconditional O(m^9) solver can be used. No numerical exact-clock threshold or new general SAT theorem.

## 2. Convert average error to small diameter by isolating outliers

Use the parent's weighted raw signatures S_g(a): for each support H containing group g, include the m^(|H|-1) bits indexed by other digits, weighted by m^(3-|H|). Thus each section has total weight m^2. Let d_g be weighted Hamming distance.

Fix any proposed partition/prediction system with error Delta_0. For group g and digit a, let E_g(a) be the weighted Hamming error between its true signature and the predicted signature obtained by replacing each raw table bit by its prediction on the proposed class cell. All digits in one class have IDENTICAL predicted signatures on these aligned sections. If Delta_{0,H} is the normalized error on support H, then

    sum_a E_g(a) = m^3 sum_{H containing g} Delta_{0,H}
                 <= m^3 Delta_0.

For positive Delta_0, call a digit exceptional if E_g(a)>sqrt(Delta_0)*m^2. At most sqrt(Delta_0)*m digits in each group are exceptional, by the displayed sum. Split each exceptional digit into its own singleton and retain the nonempty remainders of the old classes. The new partition has at most B_0+sqrt(Delta_0)*m classes per group (and at most m). Every nonsingleton class has weighted diameter <=2 sqrt(Delta_0)*m^2 by the triangle inequality through the common prediction. At Delta_0=0 all true signatures equal their predictions, so no repair is necessary. This is only an existential certificate for the next step, not a subroutine requiring access to the proposed partition. It also applies if its predictions are not majorities.

## 3. Uniform adaptive partition detection

For each group run the inherited deterministic farthest-first traversal from digit 0, ties by smallest digit, until m centers or zero residual radius. Record its nearest-center maximum radius r_g(b) for each capacity b=1..m, padding the profile with zeros after early stopping. Let r(b)=max_g r_g(b). Choose the smallest B minimizing the integer

    b*m + r(b),  1<=b<=m.

Rerun each group to this capacity and use nearest-center classes with the earliest-center tie rule. The choice needs no external growth bound or error tolerance. The usual packing proof from the parent shows that r(b) is at most the maximum diameter of any proposed partitions using at most b classes: otherwise the b centers and one further farthest digit in the offending group would give b+1 pairwise separated points.

Apply this to the repaired partitions from Section 2, with b equal to the largest repaired class count over groups. The chosen score satisfies

    B/m + r(B)/m^2 <= B_0/m + 3 sqrt(Delta_0),

with the square-root term zero when Delta_0=0. Both terms on the left are nonnegative. The computed majority prediction has aggregate error Delta <= 2 sum_H |H| r(B)/m^2 by the parent's independent within-class resampling and coordinate telescoping lemma. Hence B/m and Delta both tend to zero on the stated promise. In particular the algorithm is not restricted to instances where a maximum-diameter certificate was supplied or existed with the original number of classes.

For physical preprocessing, enumerate and sort signature records on fixed sequential bit tapes, O(m^3) entries. Each farthest-first center compares its saved row against every digit row in a sequential aligned scan, updates the nearest-distance/label array and records the new maximum, costing O(m^3 polylog m) bit operations. There are at most m rounds per group, nine groups, plus the rerun at the selected capacity. Store only the O(m) radius profile and nearest-distance array, NOT all intermediate label assignments. Scores use O(log m) bits. Compute actual class sizes, forbidden counts f_H(c), cell sizes d_H(c), and majority bits Q_H(c)=(2f_H(c)>d_H(c)), by the parent's sorting and sequential membership scans in O(m^4 polylog m) bit operations and O(m^3 polylog m) span. Include every nonempty cell, including zero forbidden counts. Store class maps for later inverse relabeling. Initial parsing of actual normalized selector positions, guarded pins and raw conversion is inherited. The fixed-track sweep simulation charges O(m^7 polylog m) physical preprocessing moves, including the complete adaptive selection. No free indexed row lookup or supplied advice.

## 4. Aggregate recovery (inherited)

Recover all original models that fail the majority quotient by at most 129 original-selector branches, one for each nonempty false-negative support set E_H={z:F_H(z)=0,Q_H(class(z))=1}. Keep every original clause, add restrictions forcing the projection on H into E_H, and use the inherited fixed k=5 spatial-frame solver. The allowed five-join density on any superset of H is at most Delta. By the local-log density theorem the total for these constantly many branches is O(m^7 polylog m + m^9 Delta^(1/2)(1+log(1/Delta))^a) for sufficiently small positive Delta, with zero-error and zero-join cases as in the parent. Every returned witness is unchanged.

For each quotient-permitted class tuple c let n_c be the product of its nine class sizes, and v_c=sum_H f_H(c_H)*n_c/d_H(c_H). If v_c<n_c, conditional expectation gives a genuine original witness in this box, using a constant number of group passes and at most O(m^7 polylog m) physical moves for ONE such call. If no such light box exists, the total permitted assignment volume A=sum_c n_c is at most sum_c v_c<=Delta*m^9, since every counted forbidden occurrence in permitted boxes is a disagreement. Augment the original selector by all quotient-forbidden tuples; this keeps exactly the original models whose class assignment is permitted. The exception branches and augmented instance cover all original models. The next two sections remove the parent's remaining global log m overheads, which would otherwise block arbitrarily slow sublinear class counts.

## 5. Local-payload counted quotient traversal

Let Q be the least power of two >=B. Pad each class-coordinate domain to Q, with absent class labels given weight zero and explicit invalid unary records. Real class labels are consecutive from zero; let w_g(c) be their positive original class sizes. Thus sum_{c=0..Q-1} w_g(c)=m for every group. The counted quotient consists of the support records (local coordinates, f, d, majority bit), including all nonempty cells, and the invalid padding markers. Unary records include class sizes via d. No full class-tuple table is materialized.

Search for a light box by a spatial-frame dyadic traversal of the nine class-coordinate domains, checking only at leaves. At a node of side t, retain only records with all their specified coordinates in the local intervals, translating their digits to [0,t). Numeric payloads f,d are unchanged; a leaf with a padded digit rejects, otherwise checks all majority bits and the exact inequality sum_H f_H/d_H<1. Use fixed-length products/cross multiplication of a fixed number of integer fields. A successful leaf returns local digits which are translated by saved child bits as frames pop. Global class maps are accessed only once after success. The actual machine stops at its first light box; the full traversal below is an upper bound on cost.

Crucially, do not use fixed global O(log m)-bit fields in every frame. Use self-delimiting binary integers, local coordinate widths O(log(t+2)), and local payload lengths determined by the values present in that frame. For analysis let X be the maximum of all nine interval class weights (zero if entirely padding). Each real f,d is <=max(1,X)^3, and invalid markers have constant payload. A frame can determine its maximum payload bit length by scanning its actual records (unary records carry all class weights in its intervals). A local bound for its total record span and scratch is O(t^3 (1+log(t+2)+log(X+2))^c) for a fixed integer c. The record count is O(t^3). Header fields encode t, maximum payload bit length, relative record positions/capacity and the child bit vector using local binary counters; none needs log m bits when its local value is small. Fixed polynomial capacity functions of t and local payload bit length, including initialization of frame delimiters, are computable by binary arithmetic in polynomial time in their bit lengths plus a scan of their reserved extent. Exact leaf arithmetic on the fixed number of support payloads has cost polynomial in 1+log(X+2). The original spatial stack uses fixed encoded tracks on disjoint adjacent physical intervals; this does NOT require one track per recursion depth, class or field length.

To push a child, scan the parent's records, filter and translate by child offsets, determine the maximum child payload length in this scan, and write its locally encoded records and header to a reserved interval immediately adjacent to the parent. A quadratic bound in the parent's interval length (times a fixed polynomial in local bit lengths) suffices for this and all intermediate counters, copying, initialization and shuttles. Child maximum weight <= parent maximum weight, and side length is halved, so child capacity is bounded by a fixed constant times parent capacity. Erase a child's interval after completion, return to its parent marker and restore its loop state; transfer successful local digits before erasure. A node has 512 children, a fixed number, so all push/pop costs may be charged to the parent. No per-node access to original scale data, global addresses or original m is made. Using local payload length instead of X itself to allocate capacity only changes constants in the bound. There is one fixed alphabet, encoded by constant-width blocks over actual symbols 0,1,2, and one physical head. With a sufficiently large fixed exponent a, per-node physical time is at most

    C*t^6 (1+log(t+2)+log(X+2))^a.

This includes leaf operations at t=1. Root setup can be paid separately in preprocessing. Stack extent along one halving path is O(B^3 polylog m) because each payload length is O(log m) and the side lengths decrease geometrically.

We now average over ALL (Q/t)^9 boxes at one scale (not over random inputs). For uniformly selected intervals independently in each group, maximum weight X is at most their total weight. The expected total weight is exactly 9tm/Q, since a fixed digit-class weight is included with probability t/Q. Hence E[X]<=9tm/Q. For any fixed a>=1, the function (log(C_a+x))^a on x>=0 is concave for a sufficiently large constant C_a, by differentiating twice; it bounds (1+log(x+2))^a up to a fixed factor. Jensen's inequality, or the same elementary log-moment bound by a geometric tail, therefore gives

    E[(1+log(t+2)+log(X+2))^a]
        <= C'_a (1+log(t+2)+log(2+tm/Q))^a.

This also holds for a=0. Since Q>=B, the right side is O((1+log(t+2)+log(2+m/B))^a). Summing node costs over the complete dyadic traversal bounds time by

    O(Q^9 sum_t t^(-3)
            (1+log(t+2)+log(2+m/B))^a)
      = O(B^9 (1+log(2+m/B))^a).

The last sum is geometric times a fixed polynomial in the dyadic scale index; factor out (1+log(2+m/B))^a. This is an actual resource bound of the proposed implementation, not a claim that every leaf has constant-size payload. Very large classes increase individual leaf cost but are rare in the uniform class-coordinate census. When B/m->0, the normalized quotient traversal time tends to zero because x^9 log^a(2+1/x)->0. This remains true even when B=m/log log m.

## 6. Local-log augmented search

If the counted traversal finds a light box, use one conditional expectation call and halt with the valid original witness. Otherwise use the parent's augmented instance, relabeling digits by consecutive class order with original digit tie order, regenerating fixed layout clauses and preserving actual pins. Invert the group permutations and reconstruct auxiliaries on success. Preparation costs O(m^7 polylog m).

With M the least power of two >=m, there are at most B+1 exceptional intervals per coordinate (class/padding boundaries, excluding wholly padded intervals). Every passing nonexceptional tile of side t is wholly within a permitted class box, because a forbidden quotient cell on a support of width<=3 is detected by a five-group superset test. Thus the parent's occupancy inequality is

    nu_5(t) <= Delta + 9(B+1)t/M.

Use its LOCAL-log scale split with e=13/2, retaining t, not m, in the logarithm. For beta=(B+1)/m sufficiently small, choose dyadic t=Theta(beta^(-2/7)) for the analysis. This tends to infinity as beta tends to zero; no scale selection by the machine is required. Its time is bounded by

    O(m^6 polylog m
        + m^9 [Delta + beta^(5/7)(1+log(2+1/beta))^a]).

Both terms in brackets tend to zero even for arbitrarily slow beta and Delta convergence. This is the other essential local-log improvement. Do not replace the final logarithm by log m. Combine with preprocessing, exception recovery and the local-payload traversal. All invoked original-scale subroutines use their fixed reusable product components, followed at constant overhead per local physical transition, with marked extents and cleanup as in the parent. Their stationary data and reusable scratch plus the spatial stack fit O(m^3 polylog m). The actual machine uses one finite description, with the adaptive rule built into fixed control; it does not depend on a sequence, B_0 or Delta_0. For large beta or Delta a fixed constant gate can instead call the unconditional cubic-order solver. This does not affect the eventual small-error conclusion. A successful witness is output contiguously in raw n bits with halt head at its first bit; on exhaustion halt on blank.

The clock at stage 3 ceil(log2 L) for fixed description length ell is at least L^3/2^ell once eligible. The established o(L^3) bound eventually fits that exact allocation. A necessary condition for any sequence of actual exact-cubic SAT misses is that the adaptive score B/m+r(B)/m^2 is eventually bounded below by some positive constant: the displayed uniform bounds tend to zero as this score tends to zero, apart from a once-only o(m^9) preprocessing term. In particular no subsequence of misses can admit partitions with B_0=o(m) and Delta_0=o(1). No existence of such misses is asserted.

## 7. Near-linear representation separation control

Generalize the parent's inner-product example. Let d grow over positive integers, q=2^d, m=4qd+1. Digit zero is special; other digits are 1+2l+tau with type tau in {0,1}, label l in [0,2qd). Define the vector c(l)=0 for even l and floor(l/2) mod q for odd l, viewed as a d-bit vector. On the nine-cycle edges allow (0,0) or opposite-type nonzero digits with distinct labels. On every noncycle pair allow all pairs involving zero, or two nonzero digits with binary inner product c(l)*c(l')=0 and unequal actual digits. Select the complements as binary negative clauses; no other cross constraints. Cycle zero-status propagation and odd-cycle two-coloring show that the only solution is all zero; every pair excludes entries. This is an easy complete-graph unique control, not a hardness example.

Partition by zero versus (type,vector): at most 2q+1=Theta(m/log m) classes. Delete only the label/digit equality exceptions in the predicates to obtain cell-constant predictions. Every row loses at most one allowed/forbidden distinction per pair from that deletion (the cycle exception has one opposite-type digit of the same label); total disagreements <=36m, so Delta_0=O(1/m). The new adaptive theorem applies. For a sharper radius certificate, two digits of one class differ on at most two entries per binary support; weighted diameter <=16m. The adaptive score is consequently O(1/log m), and both computed beta and Delta are O(1/log m). This yields o(m^9), without claiming a fixed polynomial exponent saving from this bound.

In contrast, for any fixed alpha<1, a partition into at most m^alpha classes cannot have vanishing error. On noncycle pair (0,2), restrict rows and columns to the 2qd odd-label digits, evenly divided among q vector classes with 2d digits each. Different vectors differ on exactly half of the q possible dot products, hence on qd column digits before equality exceptions and at least qd-2 after them. A class-cell prediction supplies at most B_0 distinct expanded row vectors, regardless of how columns are partitioned. By the triangle inequality each predicted row vector can approximate rows from at most one vector class to strictly less than half that distance. Thus the total normalized pair error is at least

    max(0,2qd-2d B_0)*(qd-2)/(2m^2).

For B_0<=m^alpha the ratio B_0/q tends to zero (q grows exponentially in d), and this lower bound tends to 1/16. This separates the NEW approximation promise from every prior fixed-alpha promise, even for optimal partitions, not only the computed farthest-first classes. It is not a witness-search lower bound.

## 8. Executed finite checks

Standalone JavaScript audit executed in the tool runtime, with the same audit function committed with a Node printing entry point. At m=2,3 across eight modes it computes the full farthest-first radius profiles, selects the adaptive capacity, computes counted majority cells, verifies the weighted-radius bound, and compares a recursively translated counted-quotient search for light boxes against direct class enumeration. For all capacities b=1..m it tests candidate partitions with disagreement-driven singleton repair, verifies repaired diameters and outlier counts, packing radii and adaptive score comparison. Counts: 16 fixtures, capacity sum 30, 530448 traversed nodes, 34962464 local payload checks, 529412 leaves, 35 permitted boxes, 23805 total permitted tuple mass, 35 light boxes, 127 isolated outlier occurrences across candidate partitions. The selected partitions in these tiny fixtures have zero error; the repair checks include nonzero-error candidate partitions. Separate highly nonuniform class-weight layouts verify 15 exact mean-maximum inequalities at all dyadic scales. Near-linear controls at d=2..6 verify explicit approximation disagreement counts and minimum representative row distances on the odd-label column region, as recorded in the regression. All assertions passed. The reference uses host arrays/maps, a host recursive stack, and small integer arithmetic; it tests semantics and resource-count inequalities, not the physical frame movement, local self-delimiting field implementation, asymptotic timing, actual normalized encoder/verifier or exact-stage execution. It does not rerun the parent's full exception recovery or augmented original-scale solver. No compiled transition table, independent review or Lean formalization. Exact-head CI unconfirmed.

## 9. Disposition

The fixed-alpha restriction is removed: arbitrary sublinear class counts with vanishing average error, even with unknown partitions and slow rates, now suffice. A new representation control shows why this is strictly stronger than the parent quotient promise. The remaining approximation frontier is genuinely linear class complexity with nonvanishing error at sublinear capacities, or compression outside unary class partitions. Future work should consider pair-dependent relational decompositions and other sufficient conditions in that residual. The inherited unconditional nine-group O(L^3) theorem with additive stage constant remains distinct from unconditional exact cubic coverage. Unbounded B_3, general SAT and P vs NP resolution remain OPEN. Prior finite interval 52..233 and reported Lean census unchanged, not recounted. Promotion NONE.
