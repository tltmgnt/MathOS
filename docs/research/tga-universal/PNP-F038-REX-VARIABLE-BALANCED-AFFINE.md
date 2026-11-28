# F038-REX-024D7N — Certified balanced-cardinality affine composition

Parent D7M: f4ea705f543143ba97c8c4e05bda6dae8b7a92d7. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## The even-balance theorem

For a selected subsystem of ternary factors, let sigma be a local Boolean orientation on its coordinate union. Each chosen factor forbids both normalized homogeneous rows, hence requires NAE after y=x XOR sigma. As in D7L/M, write m for the number of selected factors, w_ij for pair multiplicity, v for the number of coordinates, b(v) for the minimum same-color-pair count, and L(t)=t*b(v)-sum max(0,t-w_ij). Each satisfying assignment has weighted same-color-pair count m. When L(t)=m, all nonnegative slack terms vanish. In particular sum e_ij=b(v), so its coloring is balanced. If v=2r, exactly r normalized bits are one. Thus XOR of all v original coordinates equals (r mod 2) XOR XOR(sigma). This is a general affine equation, potentially of arity greater than three. For odd v the two permitted cardinalities differ by one; no constant full-support parity follows from balance alone. The existing D7M pair equations also follow from slack at nonthreshold pair weights. If L(t)>m the original selected subsystem is UNSAT.

Each block is oriented independently; global sign consistency is not required across distinct proof sources. All derived equations are stated in the same original coordinates and can be XOR-composed. This is an implied affine relaxation, not an exact representation of all original nonlinear constraints.

## Discovery and verification

Use all eligible ternary factors (ones forbidding at least one complementary row pair) to build incidence lists. Candidate coordinate unions are: connected components, closed coordinate neighborhoods, and every four-coordinate union of two eligible triples sharing a pair. Deduplicate unions. For each candidate, collect eligible factors contained in it, compactly renumber, and try D7L unsigned and greedy signed selection locally. Evaluate the best positive threshold. Retain strict proofs or novel implied affine rows from tight proofs. Store orientation only on selected coordinates, normalize its first bit to zero, and record original factor indices. Add local affine-hull equations from D7B, including a constant contradiction if an empty factor exists. Deduplicate rows by support and RHS; opposite RHS remains distinct.

Producer Gaussian elimination uses BigInt masks, rightmost pivots and bitset provenance. If a zero row with RHS one occurs, output its XOR combination of source row indices. The verifier independently checks selected scopes, source forbidden rows, all weights and the exact slack bound; recomputes permitted pair and even-balance rows; verifies local equations on every original allowed row; and checks the final XOR sum using a dense Boolean array. It does not trust producer pivots, rank, counters, provenance search or orientation. A strict-count proof is verified separately. Failed discovery or consistent extracted rows yield UNKNOWN, not SAT. On UNKNOWN the adapter delegates to unchanged D7M and inherited fallback on the exact original residual, without attempting general wide affine substitution. A verified contradiction maps to the inherited empty unary factor.

## Family theorem: locally signed four-regular graph blocks

Take any finite simple four-regular graph. Introduce one Boolean coordinate per edge. At each vertex include all four triples of its incident edges, as exact NAE after any chosen vertex-local coordinate signs. Each local four-coordinate block requires two normalized ones. Its four triples all share a pair with each other, so the candidate portfolio includes its support. No other vertex contributes a ternary factor wholly on that support, since distinct vertices in a simple graph share at most one edge. Exact signed NAE triples in each block admit a consistent orientation; the local signed selector recovers the block up to full complementation. Its pair weights are all two, t=2, b(4)=2, m=4, so the even-balance row is recovered. If an earlier strict-count proof is found it already proves UNSAT. Otherwise, summing the vertex rows cancels every edge coordinate twice. Whenever the XOR of all vertex-local sign bits is one, the sum is 0=1, certified by elimination. Independent global coordinate complements do not change this total parity. The same reasoning applies to an odd-sign connected component separately. This is a theorem for the specified raw encoding; it is not a general SAT completeness theorem or a claim for arbitrary predecessor rewrites or extra factors.

## Resources

There are O(k+f^2) distinct candidate unions at most (k explicit coordinates, f bounded-arity factors), with O(f^2) pair-seed attempts. Each union can be collected, sorted, locally oriented and counted in O(k+f log(f+1)+f log(k+1)+k^2) abstract operations, including pair equations; duplicate-key costs are polynomial. Per candidate, proof sources use O(k+f) words and O(k^2) possible pair rows; full even-balance rows have width at most k. With r distinct extracted equations, elimination performs at most rk row XORs, each on masks of at most k and r bits (provenance). A conservative bit bound for these operations is O(rk(k+r)), plus construction, pivot scans and serialization. All input, certificate storage, and independent verification costs are polynomial in explicit input/proof sizes; no exponential proof expansion. The candidate search is deliberately incomplete for arbitrary subsystems and orientations. No full unrestricted fallback or physical runtime bound follows.

## Executed tests

487 exhaustive small-formula comparisons, 318 SAT,169 UNSAT,1372 satisfying model occurrences. 276 local relation types, all 16 coordinate complement masks of the balanced four-bit block (six models each), 64 distinct complement masks of the prior signed K5 graph fixture, its unsigned satisfiable control (12 models), a mixed-source contradiction and Fano strict-count fixture, plus 128 seeded mixed formulas. 1200 distinct-per-instance extracted rows and 1201 proof source blocks independently checked, including every claimed equation against every satisfying assignment. 163 affine conflicts and one strict count certified; 323 UNKNOWN (318 SAT and 5 UNSAT), zero observed false refutations. Six malformed certificates rejected. The mixed-source proof combines one balance equation and four unary source equations. These counts refer to this stage only, not incremental refutations against the complete inherited solver.

| graph vertices | variables | ternary factors | tested unions | affine rows | rank | XORs / combination | predecessor processing |
|---:|---:|---:|---:|---:|---:|---|---|
|5|10|20|16|5|4|4 / 5|yes|
|5 complemented|10|20|16|5|4|4 / 5|yes|
|11|22|44|34|11|10|10 / 11|yes|
|31 complemented|62|124|94|31|30|30 / 31|yes|
|101 complemented|202|404|304|101|100|100 / 101|raw|
|501 complemented|1002|2004|1504|501|500|500 / 501|raw|

The first four tests run relational and affine predecessor processing; all coordinates remain free and zero local affine equations are extracted there. The last two verify raw input, not predecessor or physical processing. Graphs are K5 or the circulant on n vertices with offsets +/-1 and +/-2. Every instance is independently refuted without enumerating complete assignments. The D7M 10-coordinate obstruction now needs five locally oriented blocks and four elimination XORs. It is refuted before adaptive inference. The largest certificate has 501 four-coordinate balance rows, a 501-row XOR witness, 3008 local orientation proposals, and 3006 pair-seed visits. 

## Physical replay

The actual balanced adapter on the previous K5 obstruction yields the one-coordinate empty unary factor. The unchanged original and minimized machines agree on UNSAT in 2092 transitions on the ten-symbol stream; independent exact clock 2092 and one-short cutoff 2091 passed. Minimized descriptor: 3683 states,180471 bits. Only this reduced stream was replayed, not the unreduced instance; no new paired physical saving asserted. Host discovery and checking are excluded.

## New limitation: integer balance beyond affine parity

Use 16 coordinates (x,y) over GF(4), numbered 4*x+y using polynomial basis modulo z^2+z+1. Take the four vertical lines x=c, then lines y=s*x+b with s=0,1,2 and b=0,1,2,3 in that order. On each four-point line impose all four NAE triples with consistent local signs. Flip positions according to the following lists in that line order:
    [],[0,3],[1,3],[],[0,2],[1,2],[2,3],[0,3],
    [1,2],[0,1],[0,2],[0,3],[],[],[0,1],[].

Every local balance row has even RHS over GF(2). All 16 higher-order rows are recovered, rank 9, leaving 128 solutions to the affine relaxation. But the original 64-factor instance has zero models (all 65536 assignments checked). Relational/affine predecessor: 16 free, zero equations. D7L UNKNOWN; D7M fixed point; D7N UNKNOWN after 33 candidate unions, 66 orientation proposals, 96 pair-seed attempts and 33 row XORs. D7K fixed point with zero clauses, 14625 charged units. Separate inherited tree proof succeeds in 8765 units,173 nodes,14 leaves,13 splits,146 unit nodes. This is a structural limitation, not an unresolved full-pipeline barrier.

There is a stronger exact mathematical explanation. For each line the integer equation is sum signed coefficients a_i*x_i=2-number_of_flips, where a_i is -1 for flipped positions and +1 otherwise. The vector with every coordinate 1/2 satisfies all 16 equations, so rational linear consistency alone cannot refute this instance. The audit independently checks an explicit integer combination of the 16 line equations with multipliers [4,2,3,1,0,-4,-3,3,4,-2,1,-1,2,-2,0,-2]. The resulting equation is 10*x_0+2*x_15=6, hence 5*x_0+x_15=3. Neither binary value of x_0 allows a binary x_15. Equivalently, modulo five this forces x_15=3, impossible. The supplied identity is verified in the audit, not automatically discovered by D7N.

## Next

D7O: certified integer linear combinations and modular Boolean-domain inference from tight balance. Investigate exact rational/integer elimination with coefficient-growth bounds, fixed-prime modular elimination (e.g. GF(5)), and unary/small-support domain contradictions. Target automatic discovery of the above obstruction without relying on supplied multipliers, independently check source integer equations and combinations, preserve sound UNKNOWN on failure. This is a restricted polynomial inference target, not a claim that integer programming or SAT is polynomial. Raw-selector normalization, on-tape inference and complete end-to-end resource accounting remain open.

All new audit sections executed in connector JS; remote Proctor completion unconfirmed. Main and PR #248 untouched.
