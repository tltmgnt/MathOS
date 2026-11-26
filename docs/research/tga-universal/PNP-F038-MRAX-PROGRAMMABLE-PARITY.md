# F038 / negative route — MRA-X: programmable directional parity and restricted-oracle lower bound

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent f246bd8ddab58720d3a8d177ff3311a0beaab274: https://github.com/tltmgnt/MathOS/actions/runs/45731742826 (success). TOPO-406 and Millennium bounded probes were still running at inspection.

## Backward gap analysis

The previous derivative-batch result requires exponentially many output wires. Replace that batch by a single programmable output, keeping all parameters explicit. Study the cost of its computation and distinguish it from ordinary SAT. Alternative: prove an adaptive oracle-query lower bound even for compactly represented restrictions of the universal selector. No novelty claim for parity counting or query adversaries. MRA-X roles are locally authored records, not independent live agents.

## Constructive track: programmable directional finite differences

Let U_n be the full normalized nonempty non-tautological width-at-most-three clause pool on n>=1 Boolean source variables, with N=|U_n|. Let F_n(p) indicate SAT of the selector vector p. Work over GF(2) in selector space. For a base selector p and an explicit N by k binary matrix A with columns a_i, define the single Boolean output

    Q(n,p,A) = XOR_{z in {0,1}^k} F_n(p+A z).

This is the iterated directional finite difference along the columns of A (translations commute, and each difference is identity plus translation). For k=0 it is F_n(p). Ordinary coordinate derivatives are the special case of distinct standard basis columns. The main reduction below uses paired directions, NOT ordinary coordinate derivatives; it does not assert hardness of their special case.

If rank(A)<k, every image point occurs an even number 2^(k-rank(A)) of times, so Q=0. Otherwise Q is exactly parity of satisfiable selector vectors in the affine image. Rank checking is polynomial in explicit dimensions; when rank is full the direct algorithm uses 2^k calls to F_n, each on N bits. No free parity aggregation is assumed.

Define the class ParityExistsP here to avoid oracle-notation ambiguity: languages of inputs v for which an odd number of strings z of a fixed polynomial length in |v| satisfy exists w of polynomial length R(v,z,w), with R a deterministic polynomial-time predicate. Count projected z values, not pairs (z,w). This is the parity-of-NP-predicate class often written parity-dot-NP. It is not defined here as arbitrary adaptive NP oracle computation. Polynomial-length strings may be padded by forced zeros; padding with unconstrained bits would change parity.

The explicitly encoded Q language (n unary, p and A explicit, malformed inputs rejected) belongs to ParityExistsP: z selects the affine point and w is a satisfying source assignment. For a fixed polynomial witness length in input encoding size rather than the variable k, force unused z bits to zero. A single deterministic predicate computes the point and checks the selected clauses in polynomial time.

### Exact projected parity reduction with disjoint pair directions

Given any width-three CNF G(x,w), x consisting of h projected bits and w existential auxiliaries, introduce h fresh source variables u_i and fixed equality clauses (not x_i OR u_i),(x_i OR not u_i). Normalize G, handle empty clauses by a fixed contradictory pair on an extra variable if needed, and rename to the universal pool on all variables. If there are zero variables, add an unused source variable. Fix outside selectors to exactly G and the equality clauses. Select exactly the negative unit on each u_i at the base p. For each i take the direction with ones precisely at the selectors for the positive and negative units on u_i. These directions are disjoint and independent. Neither unit selector occurs in the fixed G/equality part because the u_i are fresh.

At p+A z exactly one unit sign is selected per u_i, pinning u=z. Thus

    F_n(p+A z) = 1 iff exists w G(z,w).

Consequently Q equals the parity of the number of distinct satisfying projections onto x. This is a polynomial-time many-one reduction even though there can be exponentially many such projections. For an arbitrary predicate R in the class definition, use the standard uniform polynomial-size Boolean circuit simulation of R, followed by width-three gate-equivalence clauses and a forced accepting output. Retain the projected z bits; existentially quantify original witnesses and all gate variables. For each z this preserves existence exactly, irrespective of the number of original witnesses. Therefore Q is ParityExistsP-complete under polynomial-time many-one reductions even for these disjoint pair directions (with the zero-direction case allowed). No general machine-to-CNF compiler is implemented in the finite prototype.

This gives an exact conditional complexity boundary. Q in P implies P=NP by k=0, and P=parity-P (ordinary parity of deterministic polynomial-time predicates, usually denoted parity-P or XOR-P) by the projected reduction without existential witnesses. Conversely if P=NP and P=parity-P, the inner existential predicate is polynomial-time decidable and the outer parity computation is in P. Thus Q in P iff both equalities hold. No independence between the two equalities is asserted; no claim that P=NP implies or does not imply P=parity-P. Likewise any uniform polynomial-time compiler from ordinary SAT circuits of polynomial size to Q circuits of polynomial size, for this input encoding, under P=NP would imply P=parity-P. A single-output evaluation problem can be strictly different in its quantified structure from the original decision problem; lower bounds for it do not automatically transfer back to F_n. The result is a completeness/conditional barrier, not an unconditional separation.

## Alternative track: exponential oracle lower bound with compact one-hole instances

Consider an unknown relation T subset {0,1}^h. An oracle takes a partial assignment (each coordinate free, zero, or one) and returns whether some member of T extends it. This models exact SAT queries on a fixed hidden outside-selector restriction plus arbitrary choices of the signed unit selectors on h address bits. Contradictory pin selections always return zero and provide no information. The task is to compute parity |T| mod 2, not just existence.

For T_full={0,1}^h and T_a=T_full minus {a}, h>=1, the two oracle answer functions differ exactly on the singleton query pinning every coordinate to a. Every non-singleton nonempty subcube contains at least two points and still intersects T_a. Their parities are opposite. A deterministic exact algorithm on T_full must query every singleton: otherwise the same adaptive transcript would occur on an unqueried-hole oracle with opposite answer. Thus at least 2^h queries are necessary, matching the algorithm asking every singleton.

For a randomized algorithm correct with probability >=1-epsilon on each oracle, epsilon<1/2, couple executions on T_full and T_a with the same internal random tape. Until the singleton a is queried, transcripts and output are identical. The probabilities of output one on the two instances differ by at least 1-2epsilon, so the probability on T_full of querying a is at least 1-2epsilon. Sum over a to obtain an expected number of DISTINCT singleton queries of at least (1-2epsilon)*2^h on T_full. This allows adaptive queries, unbounded computation between queries and arbitrary internal randomness; it is not a general runtime lower bound with explicit formula access.

Both types of oracle arise from compact width-three CNFs on a common pool of 2h source variables. The full relation uses no outside clauses. To remove just a, introduce h auxiliary variables y_i for prefix ORs of the mismatch literals l_i (x_i if a_i=0, not x_i if a_i=1). Enforce y_1=l_1 by two binary clauses, and y_i=y_(i-1) OR l_i for i>1 by three clauses of width at most three. Force y_h=1 by a unit. The auxiliary extension is unique exactly on the addresses unequal to a; no address unit occurs in this outside formula, even for h=1. Thus the restricted SAT oracles above are representable by O(h) selected clauses and a fixed polynomial-size universal pool. The exponential query lower bound is not an artifact of encoding an exponential arbitrary truth table. However the oracle hides the outside selector vector; with explicit access the one-hole instance is readily recognized and its parity computed. The theorem rules out generic black-box parity extraction with only such SAT pin queries, not algorithms examining the formula, more general SAT queries, or arbitrary circuits.

Topology: a full affine selector cube of paired unit choices parametrizes projected source assignments. Each partial pin oracle query asks if its subcube intersects the projected witness set. One deleted point is invisible to every non-singleton subcube. This is a precise semantic query distinction, not an unrestricted topological invariant of SAT.

## Evidence and cost

Independent JS enumerated all 256 selected subformulas of the two-variable full clause pool and every projected subset of the two variables, constructed equality-copy CNFs and tested all full pin patterns and all enlarged source assignments. Metrics [formulas,projection cases,distinct projections summed,pin evaluations,assignment checks,odd projections,nonempty projections,fixed CNF clauses summed]:
[256,1024,447,2304,25600,323,380,6144].
Independent JS built the actual one-hole prefix-OR CNFs, checked all source/auxiliary assignments and all ternary partial pin patterns, for h=1..5. Rows [h,addresses,partial patterns,oracle pairs,address checks,differing answers,positive hole answers,full CNF assignment checks,accepted unique extensions]:
[1,2,3,6,12,2,4,8,2],
[2,4,9,36,144,4,32,64,12],
[3,8,27,216,1728,8,208,512,56],
[4,16,81,1296,20736,16,1280,4096,240],
[5,32,243,7776,248832,32,7744,32768,992].
Python constructs actual universal selector bitsets and paired directions, compares parity with projected model sets, checks rank-deficient cancellation, replays actual one-hole CNFs and oracle answers. The JS did not execute Python. Enumeration is bounded regression only; rank checking and reduction encoding are polynomial in explicit size, parity enumeration exponential in k. No general efficient parity or SAT solver, quantified oracle compiler or unrestricted lower-bound transfer is implemented. Exact-head CI required.

Forward TGA: BARRIER_IDENTIFIED. A single-output programmable directional derivative has a precise parity-of-existential complexity classification; a compact SAT restriction family forces exponentially many pin-oracle queries. Neither closes the unrestricted decision lower bound because the former changes computational task and the latter restricts access. Next investigate single-output reductions that preserve ordinary SAT decision rather than parity, e.g. circuit evaluation under monotone/affine selector reparametrization, with a justified structural lower bound or explicit counterexample to the proposed transfer. Do not continue derivative amplification without a decision-preserving theorem. Independent mathematical review and Lean formalization outstanding.
