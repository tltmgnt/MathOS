# F038 — Exponential Horn-cover obstruction and exact backdoor threshold

PNP_RESOLUTION_STATUS = OPEN. Structural derivation and finite regression, not a Lean declaration.
Verified base 1d10e5af6bcd94bc1b6f2874f7eb54be20aef4e9: https://github.com/tltmgnt/MathOS/actions/runs/45702060990 (success).

## Linear-size satisfiable family with linear renamable-Horn backdoor

For t>=1, use t disjoint triples of variables and the two clauses per triple
(a_i OR b_i OR c_i) AND (not a_i OR not b_i OR not c_i).
The model relation S_t is the t-fold product of the six nonconstant words on three bits. It has 3t variables, 2t clauses and an elementary linear-time model constructor.

In any sign orientation, the two clauses on an untouched triple are complementary literal lists. Their positive literal counts sum to three; both cannot be Horn. Therefore any set B whose deletion yields a renamable-Horn formula must hit every triple, so |B|>=t. This also bounds strong backdoors into renamable Horn: if a triple is untouched by B, both of its clauses survive every restriction and prevent renamability. Conversely choose one variable per triple, delete it and orient the two survivors oppositely. The remaining clauses are Horn under one common orientation, and every assignment to B leaves a Horn residual in that orientation. The minimum size for both definitions is exactly t.

Designate the first variable of each triple as a universal parameter and the other two as existential. The same bound holds even when B is restricted to existential variables: choose the second variable in each triple. The projection onto parameters is nevertheless total, since setting the other two bits to 1 and 0 always works. Thus there is no universal constant or logarithmic existential-backdoor bound for this structural class, even among total, trivially constructible relations. This is not a complexity lower bound for SAT.

## Exact common-orientation cover number of the full model relation

Consider a cover of S_t by projections of arbitrary Horn formulas, with any number of private existential auxiliaries, all using the same sign orientation s of the 3t visible variables. Require exact equality of the union with S_t, so every projected component is a subset of S_t. The transformed components are meet-closed, because existential projection of a meet-closed model relation preserves coordinatewise AND. In each oriented triple the two forbidden words are s_i and its bitwise complement. Choose the one u of weight at most one. Pick two distinct zero positions of u, and let p,q be obtained by setting one of these positions each. Both p,q are allowed: they differ by one bit from u, not by all three. Their meet equals forbidden u.

Take all 2^t products of these local pairs. These are allowed full words, but the coordinatewise meet of any two distinct products is forbidden in at least one triple. No meet-closed subset of the oriented relation can contain two such words. Hence at least 2^t alternatives are necessary for EVERY common orientation, regardless of auxiliary-variable count or formula length.

For an upper bound choose a common orientation complementing the second variable of each triple, and split by the first variable in every triple. After pinning the first variables, at most one complementary clause remains per triple, and its two literals have opposite signs. Each of the 2^t pieces is represented by a Horn CNF in that common orientation (with the pins included). Thus the minimum over common orientations is exactly 2^t.

## Independent orientations still require exponentially many components

For a single oriented triple, the six allowed words cannot all be meet-closed, by the local p,q construction. Thus any meet-closed subset has at most five words. Project any one component of a cover of S_t onto each triple, after orienting that component's visible coordinates; each projection is meet-closed and contained in the local allowed relation. Its size is at most five, so the full component contains at most 5^t words, even with dependencies between triples or auxiliary variables. Counting the 6^t distinct visible words gives
K >= ceil((6/5)^t).
This counts visible relation elements, not the satisfying assignments of auxiliary formulas.

The exponential base is optimal up to a factor O(t). For orientation s_i=001 (least-significant coordinate first), delete the additional allowed oriented word 011. The resulting five words are exactly the models of (not y_0 OR y_2) AND (y_0 OR not y_1 OR not y_2), a Horn formula. In the original orientation the omitted allowed word is 010. Permuting coordinates and complementing all three original bits preserves NAE and acts transitively on its six allowed words. Therefore for each of the six choices of an omitted word there is a renamable-Horn representation of the other five. Independently choose one omitted word uniformly per triple; the product is a renamable-Horn component, and any fixed model is covered with probability (5/6)^t. For K independent components the probability any word remains uncovered is at most 6^t exp(-K(5/6)^t). Choosing K=floor(t ln(6)(6/5)^t)+1 makes this less than one. Thus a cover exists with that many components. This is a probabilistic existence proof, not an efficient construction of an explicit list.

Together the bounds show that allowing each component its own signs changes the exponential base but cannot make an exact explicit Horn-cover representation polynomial. Private auxiliary variables cannot bypass the lower bounds. The result concerns the entire visible model relation, not just one satisfiable branch, equisatisfiability, or the projection onto the universal parameters in the preceding total example. In particular a factored circuit, implicit cover, or direct witness constructor can be small.

## Validation

Exhaust all eight sign orientations and all 64 subsets of their six allowed local words, checking closure and maximum cardinality (3 for forbidden 000/111, 5 otherwise). For t=1,2,3 exhaust all common orientations, verify the 2^t-model pairwise incompatibility certificates, and test every deletion set using the preceding 2-SAT orientation algorithm. Independently verify the analytic hit-every-triple criterion, the direct totality witness and the common-orientation upper cover. Expected: 512 local subsets, 260 closed, 8 local caps, 584 orientations, 4368 incompatible-set model checks, 14728 meet checks, 584 deletion sets, 399 successful, 14 total-projection witness checks and 258 upper-cover model checks.

Next: implicit/factored covers with certified interface compatibility and explicit representation-size accounting, not further attempts to make an explicit cover universally small. No new Lean declaration or P vs NP resolution.
