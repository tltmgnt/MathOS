# F038-REX-024D7L — Certified weighted NAE pair-counting

Parent D7K: aee3eb33d5358d8140469d2960e6e6d64888c120. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Theorem and certificate

Select a nonempty set of distinct original ternary factor indices and a Boolean complement vector sigma. Each selected factor must forbid both local rows sigma|h and its complement. Hence every model, expressed in coordinates y=x XOR sigma, gives a not-all-equal coloring on each selected triple. Repeated scopes are permitted when they are distinct original factors. Let m be the selected factor count, v the number of coordinates in their union, w_ij the multiplicity of pair ij, and e_ij=[y_i=y_j]. Every model obeys sum w_ij e_ij=m because each NAE triple has exactly one same-color pair.

For integer t>0 define D(t)=sum over all unordered pairs max(0,t-w_ij), including zero-weight pairs. Every two-coloring has at least b(v)=binom(floor(v/2),2)+binom(ceil(v/2),2)=binom(v,2)-floor(v^2/4) same-color pairs. Therefore
    sum w_ij e_ij >= t*b(v)-D(t) = L(t).
A strict L(t)>m is a checked UNSAT certificate. Equivalently, this bounds the weighted cut from above; it does not solve arbitrary weighted Max-Cut. The identity follows term by term from w_ij e_ij >= t e_ij-max(0,t-w_ij). Thresholds need only be tried at distinct positive weights: L(t) is piecewise linear with breakpoints at the weights (and zero); after the largest weight its slope is negative. Zero cannot give strict contradiction.

The independent verifier checks original factor indices, distinct scopes internally, orientation bits, forbidden rows, pair multiplicities, and exact integer arithmetic (BigInt); it recomputes the deficit over all pairs and the balanced two-color minimum using a separate implementation. A forged count, repeated factor index, wrong sign or non-strict bound is rejected. It does not trust search metrics or selection policy. Contradiction maps to the inherited one-coordinate empty unary residual. UNKNOWN calls inherited D7K then D7D fallback on the unchanged original representation; no change to model or witness order.

## Discovery and resources

Try homogeneous forbidden rows first; then try compatible complementary forbidden row pairs using parity union-by-size, accepting a triple only if its relative sign equations are consistent with earlier choices. This is a greedy subset selector, not an optimal compatibility search. For pure coordinate-complemented NAE designs all relative equations are consistent, so the signed pass can recover the full design up to component-wise global complement. For factors with multiple forbidden complementary pairs, selection can be order-dependent. Split eligible triples into incidence-connected components; test each full component then remove a least-incidence coordinate and its incident triples, breaking ties by coordinate rank. At most 64 peels per component by default (0..256 configurable). This is a restricted candidate portfolio, not exhaustive subset search. Use a histogram of positive pair weights and prefix sums to compute all threshold bounds, counting absent pairs arithmetically. The checker explicitly checks the missing pairs.

With k coordinates, f bounded-arity factors, and p permitted peels, orientation uses O(k+f log(k+1)) abstract operations (union-by-size, no path compression). Each candidate weight construction and histogram sort costs O(f log(f+1)); components partition the eligible factors so total cost across at most p+1 passes per component is O((p+1) f log(f+1)+k+f log(k+1)). Storage O(k+f) words aside from explicit certificate and nested fallback. The checker uses O(k^2+f) pair operations and O(k+f) storage; exact integer bit costs are polynomial. No claim of polynomial complete SAT decision, general Max-Cut optimization, or end-to-end physical execution.

## Executed evidence

788 exhaustive small-formula comparisons (545 SAT,243 UNSAT,9625 satisfying model occurrences): 276 local Boolean relation types, all 128 Fano factor subsets, all 128 coordinate-complement masks of Fano, 128 seeded weighted Fano subinstances,128 seeded mixed formulas. 130 positive counting certificates (127 signed), independently checked with zero observed false refutations. All 128 Fano masks refuted. 1072 numeric bound comparisons against the exact minimum over all assignments (for eligible orientation views); six damaged certificates rejected. This is a counting-only corpus comparison, not a claim of 130 additional refutations over the inherited solver. The adapter test separately confirms a checked counting UNSAT becomes the constant contradiction factor and a satisfiable Fano-minus-line retains the exact original residual.

| fixture | variables | original factors | selected triples | threshold | deficit | lower bound | predecessor processing |
|---|---:|---:|---:|---:|---:|---:|---|
| STS21 |21|70|70|1|0|100|yes|
| incomplete STS21 |21|56|56|1|42|58|yes|
| nonuniform weighted STS21 |21|135|135|2|30|170|raw|
| STS21 with attached chain |41|80|70|1|0|100|raw|
| complemented STS21 |21|70|70|1|0|100|yes|
| STS93 |93|1426|1426|1|0|2116|yes|
| STS303 |303|15251|15251|1|0|22801|raw|

All seven rows independently checked. Four marked predecessor rows retain all coordinates and zero affine equations. The tail fixture recovers the core after ten peels. Weighted fixture counts multiplicities of distinct original factor indices; threshold two is necessary for this whole-set bound because t=1 gives at most 100<135. The incomplete fixture deletes fourteen triples (42 missing pair incidences) and still yields 58>56. The largest test directly verifies the raw counting input, not an integrated preprocessing/physical run. The previous 21-coordinate D7K structural fixed-point limitation is refuted by a one-candidate count, without invoking adaptive inference.

## New compositional limitation and proposed next step

Take the Fano plane with line {0,1,2} removed. The remaining six triples cover 18 of the 21 pairs. They have ten satisfying assignments (exhaustive oracle), and every model forces the three missing-line coordinates equal: the six triples contribute exactly six same-color pairs, the complete seven-point coloring has at least nine, and only three pairs are missing. Thus all three missing pairs must be same-color. Combine two copies sharing coordinate 0, with missing lines {0,1,2} and {0,7,8}; add NAE {1,2,7}. The copied equality implications contradict that last triple. All 8192 complete assignments were checked; none satisfy. The 13-factor system is linear and has 13 coordinates. Its iterative D7K closure derives zero consequences (1451 charged units,183 probes). For every nonempty subset of the 13 factors (8191 checked), all pair weights are 0 or 1, and the best positive threshold is one. The gap L(1)-m=2m-floor(v^2/4) has maximum zero over those subsets. Thus even exhaustive factor-subset search cannot obtain a strict uniform-deficit contradiction of this type. Signs do not help for these exact NAE factors, since any compatible orientation is constant on each selected connected component. This is a limitation of this inequality family, not of all weighted bounds or SAT algorithms. Independently checked inherited width-four resolution refutes it (3111 proof records,1194369 charged work,12379 pairs). Separate tree verification also succeeds (135 nodes,2534 units,18 leaves,17 splits,100 units nodes). It is NOT an unresolved full-pipeline barrier.

Next: use saturation at equality, rather than only strict contradiction, to derive parity consequences. When L(t)=m, every nonnegative slack term must vanish; w_ij<t forces y_i=y_j, w_ij>t forces y_i!=y_j, and the overall coloring is balanced. Investigate certified composition of these equalities with affine/relational closure and bounded discovery of overlapping tight subsystems. These consequences are mathematically implied but the extraction/composition algorithm is not implemented in D7L. General SAT and direct physical normalization remain open.

## Execution scope

The producer, independent checker, oracle, larger rows, structural limitation and separate adapter tests ran in the connector JavaScript runtime. A physical replay attempt disconnected without returning results; no new physical timings, clock comparisons, or descriptor changes are claimed. Main and PR #248 are untouched. Remote Proctor completion unconfirmed.
