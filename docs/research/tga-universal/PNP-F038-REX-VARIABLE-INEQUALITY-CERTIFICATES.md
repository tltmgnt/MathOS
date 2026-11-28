# F038-REX-024D7R — Certified local inequalities and nonnegative linear combinations

Parent D7Q: 9287bdde3cad2f926a687f74d2528418009a7d52. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Local support theorem

For a nonempty allowed Boolean relation S of arity n<=3 and nonzero normal a, the exact supporting inequality a*x<=max_{z in S} a*z holds for all models. Enumerate all primitive integer normals in [-2,2]^n (at least one coefficient has magnitude one), including both signs. There are 2,16,98 normals for n=1,2,3 respectively. Sort coordinate indices, permute coefficients, and omit zero coefficients. Empty relations give 0<=-1.

In fact these supports describe the complete local real convex hull at this arity. For full dimension three, each facet contains three affinely independent Boolean vertices; its normal is a cross product of two difference vectors, with entries of absolute value at most two. Divide by the gcd to get a primitive normal in the portfolio, with the correct orientation. Full dimension two uses a perpendicular to an edge difference, and dimension one uses +/-1. For a lower-dimensional nonempty hull, the D7Q bounded primitive affine nullspace basis, used with both signs, defines its affine span. Project the span injectively onto a subset of coordinate axes of size equal to its dimension (choose independent coordinate columns). The projected hull is full-dimensional in dimension at most two, with Boolean vertices, so its supporting facet normals lift by zero-extension into the same portfolio. These equations and facet inequalities suffice; a point hull is given by its affine span alone. This argument concerns each factor separately, not the convex hull of global satisfying assignments.

## Positive combination certificate

Take checked source inequalities a_j*x<=b_j and positive integer multipliers m_j. Their sum is A*x<=B. On the Boolean box, min A*x=sum_i min(0,A_i)=L; the same minimum holds on the continuous box [0,1]^k. If L>B, no model exists. Equivalently, append the implicit box inequalities -x_i<=0 for positive A_i, with multiplier A_i, and x_i<=1 for negative A_i, with multiplier -A_i. This cancels every coefficient and derives 0<=B-L<0, a nonnegative Farkas certificate. All arithmetic in aggregation and the checker is exact BigInt. The checker evaluates every original allowed tuple for each source inequality, verifies scope membership and coefficient/multiplier bounds, independently sums coefficients and RHS, recomputes the box minimum, and requires a strict gap. It need not trust source tightness, search, metrics or selection order.

## Bounded deterministic discovery

Enumerate source supports once. Partition factors by incidence-connected components. For each component start at the all-half rational point (store twice the point). For each factor select its most violated inequality at the current point, breaking equal positive violation by least L1 norm then enumeration order. Add selected rows with unit multipliers to the accumulated combination. Check the box minimum after each round; if not contradictory, choose the minimizer of the accumulated linear form (zero for positive coefficients, one for negative, half for zero). Repeat up to a configured 32 rounds per component (0..256 allowed), or stop if no source is violated at the current point. The point is just a search proposal; feasibility of this point is not a SAT conclusion. Repeated rows share one multiplier in the certificate. This is a restricted deterministic search, NOT a complete LP feasibility algorithm, and no convergence theorem is asserted. The adapter maps checked contradictions to the inherited empty unary factor and passes the exact original residual to an optional inherited fallback on UNKNOWN; without callback it returns UNKNOWN with identity expansion. No predecessor modules modified.

Local support enumeration is constant-sized per factor. For k coordinates, f bounded-arity factors, c incidence components and R rounds, the naive incidence scans cost O(k+f^2) in the worst case (sum of squared incidence degrees), source construction O(f), and round work O(R(f+ck)) including dense coefficient arrays and box-minimum scans. Storage O(k+f) words, up to 98f source inequalities, with at most 98f distinct certificate terms and multipliers at most R. Exact integer magnitudes O(Rf) for the producer's aggregate and polynomial bit overhead. Checker work O(k+f) for the produced proof in the abstract word model (or linear in explicit term count and coordinate support), with BigInt bit overhead. These bounds exclude predecessor/fallback, certificate discovery outside this portfolio and physical execution; general LP, integer programming and SAT completeness are not claimed.

## Executed evidence

469 exhaustive formula comparisons:324 SAT,145 UNSAT,1457 satisfying model occurrences. All 276 local relation types, 192 seeded mixed formulas, one named multi-round fixture. Independently checked 25239 local supports, all nonempty supports attain equality on an allowed tuple; checked all 2120 candidate Boolean tuple occurrences (1060 excluded), with exact local Boolean model preservation. All 145 UNSAT cases were independently refuted by this restricted search; all 324 SAT cases remained UNKNOWN. This corpus is not a general completeness result or incremental improvement over the inherited solver. 27 refutations used more than one counted round (count across components), 100 had nonzero box minimum, six malformed certificates rejected.

The named six-coordinate fixture is refuted in two rounds with three distinct proof terms (one repeated multiplier), aggregate box minimum -1 and RHS -2; one round is UNKNOWN. Zero-round adapter passes the exact original residual to its fallback. An actual D7Q fallback on the prior 31-coordinate exact-one family succeeds with a 31-row GF(3) certificate after D7R UNKNOWN, demonstrating compatibility rather than an LP refutation.

## Prior equality-source obstruction eliminated

On k cyclic coordinates use k triples {i,i+1,i+3} requiring at least two ones and k triples {i,i+4,i+9} requiring at most one. For the tested sizes all scopes have distinct coordinates. At the all-half point the maximum violated primitive support with minimum L1 norm is the negative sum <=-2 for each lower factor and positive sum <=1 for each upper factor. Each coordinate occurs three times in both families. Summing one inequality per factor gives 0<=-k. Under arbitrary independent coordinate complements the all-half point and L1 tie rule are invariant, and the chosen full-support normals transform by sign flips plus RHS translation. The aggregate remains 0<=-k. Thus the specified raw regular family has a one-round certificate (assuming at least one permitted round); no statement about arbitrary extra constraints or predecessor rewrites.

|coordinates|factors|complemented|predecessor|support tests|proof terms|bound|
|---:|---:|---|---|---:|---:|---|
|31|62|no|yes|6076|62|0<=-31|
|31|62|yes|yes|6076|62|0<=-31|
|127|254|yes|yes|24892|254|0<=-127|
|1001|2002|yes|raw|196196|2002|0<=-1001|

All four independently checked, one component and one round each. Three actual relational/affine predecessor runs retain all coordinates, zero affine rows. Largest test uses raw structural input, not full preprocessing or unreduced physical execution. No complete assignment enumeration for these large decisions.

## Physical replay

Actual D7R adapter on the raw 31-coordinate prior obstruction: original/minimized agreement, UNSAT in 2092 transitions on the ten-symbol contradiction stream, independent exact clock 2092 and one-short cutoff 2091. Descriptor unchanged:3683 states,180471 bits. No new measured paired physical saving; host discovery and checker excluded.

## New integrality limitation

Modify the lower family to require at least ONE, retaining the upper at-most-one family on different scopes. At k=31 every coordinate still occurs three times in each family. All models would obey 3*sum x>=31 and 3*sum x<=31, hence 3*sum x=31, impossible over Boolean integers. However the all-one-third rational vector lies in every local convex hull: on every triple it is the uniform mixture of the three exact-one tuples, which are allowed by both tables. Thus no nonnegative combination of ANY valid local real inequalities and box constraints can contradict this fractional point, not just the implemented search. All 62 local relations have full affine dimension and do not forbid complementary row pairs, so local integer equalities and the D7L balance source screen supply no information. The actual relational/affine predecessor run retains 31 coordinates, no equations. Independently verify the fractional point against all 6076 support inequalities using exact numerator arithmetic. D7R returns UNKNOWN after 32 rounds,194432 support tests,992 selected rows. Separate inherited tree refutes in 5088 charged units,63 nodes,13 leaves,12 splits,38 units. This is a limitation of local LP relaxation, not an unresolved full-pipeline barrier or a general SAT lower bound.

Integer rounding would already resolve the example: divide the two summed inequalities by three and round the RHS downward in <= orientation. This yields sum x>=11 and sum x<=10. Both follow from integrality, not continuous convex feasibility. The audit verifies the regular degrees and the resulting incompatible integer bounds; it does not automatically discover a rounding proof.

## Next

D7S: certified bounded cutting-plane rounding and aggregate inequality composition. Implement nonnegative sums followed by exact integer division/floor when all left coefficients are divisible by the divisor, independently check each step and its earlier dependencies, and discover the two regular-family sums automatically. Investigate limits of restricted rounding and bounded proof discovery, not unrestricted cutting-plane proof search or an assumption of polynomial integer programming. General SAT, direct raw-selector normalization, on-tape inference and complete physical accounting remain open.

All five new audit sections executed in connector JS. One runner invocation omitted the require stub and was retried successfully; no repository code defect resulted. Main and PR #248 untouched. Remote Proctor completion unconfirmed.
