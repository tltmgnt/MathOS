# F038 — Low-degree support certification and dense-circuit obstruction

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not a Lean declaration.
Verified base 24a972fe85ed1f7c3f283053fae2ec5b334f5f05: https://github.com/tltmgnt/MathOS/actions/runs/45707998190 (success).

## Exact support criterion

Given an explicit Boolean circuit C on R input bits and a fixed nonnegative integer d (capped by R), let S be its one-set. Define D=sum_{j=0}^d binom(R,j) and v_d(x) in GF(2)^D to be the vector of all squarefree monomial values of degree <=d, including the constant. A coefficient vector p defines the Boolean polynomial P(x)=p dot v_d(x).

There exists a nonzero degree-<=d polynomial supported inside S iff the linear span Z of {v_d(x):C(x)=0} is proper in GF(2)^D. Indeed P vanishes on all zero inputs precisely when p belongs to Z^perp. Distinct coefficient vectors give distinct functions by the earlier Mobius argument. There are exactly 2^(D-rank Z)-1 nonzero supported polynomials. The conclusion applies even if S itself has high algebraic degree.

Failure has a short, directly verifiable certificate: D zero inputs with linearly independent evaluation vectors. Verify C(x)=0 for each and compute rank over GF(2). For fixed d the certificate length O(RD) and verification time are polynomial. Thus deciding existence of such a support polynomial is in coNP. This is not a claim that verifying a proposed support polynomial is easy; checking that it vanishes on every zero input can itself require a universal quantifier.

A polynomial-time algorithm with an NP oracle can compute Z and recover a polynomial or certify failure. Start with an empty span. Pick any nonzero p orthogonal to the current span; ask whether C(x)=0 AND p dot v_d(x)=1 is satisfiable. If not, return p; otherwise recover such x by self-reduction and add its evaluation row. Rank increases at each successful query, so at most D such iterations and polynomially many NP decision queries including self-reduction suffice. At full rank return the collected certificate. All circuits and linear-algebra costs are polynomial for fixed d. This algorithm does not provide unconditional uniform polynomial-time recognition.

## Hardness persists even for dense circuits

For each fixed d>=0 reduce Boolean circuit tautology to the existence problem. Given C(x), choose g=ceil(log2(4(d+1))) fresh guard bits and define G(x,b)=C(x) OR OR_j b_j. Its zero fraction is at most 2^(-g). On d+1 mutually disjoint blocks form

S(u_1,...,u_(d+1)) = AND_i G(u_i).

The size is polynomial in |C| for fixed d. Uniform input bits give one-density at least 1-(d+1)2^(-g)>=3/4 by the union bound. If C is a tautology then S is identically one and the constant-one polynomial is supported. If C is not a tautology, choose a falsifying x0 and let u0=(x0,0^g). Any supported polynomial must vanish whenever any one of its blocks is fixed to u0, regardless of other blocks. Translate each block by u0 (XOR constants), which preserves the degree upper bound and nonzeroness. In the translated ANF, fixing one block to zero kills exactly the monomials touching that block; vanishing then forces every coefficient of a monomial not touching it to be zero, by ANF uniqueness. Apply this to all d+1 blocks: each surviving monomial must have degree at least d+1. There is therefore no nonzero polynomial of degree <=d supported in S.

Thus the existence problem is coNP-complete for every fixed d, even on circuits promised to have density at least 3/4. One can avoid promise-problem terminology by noting that unrestricted recognition is in coNP and the reduction always produces dense instances. This is a direct reduction from circuit tautology (coNP-complete by complementing circuits for SAT); no external proof-complexity conjecture is used.

This also strengthens the earlier density obstruction: an explicit efficient predicate can have high mass without containing ANY nonzero bounded-degree polynomial one-set. For example take C identically zero. Then the support condition requires at least one bit from each of d+1 disjoint guard blocks in every ANF monomial. Its minimum possible support degree is exactly d+1, since the product of one selected bit from each block is supported. Choosing d as a growing parameter gives a uniform family of polynomial-size predicates with density >=3/4 and growing minimum support degree (e.g. d growing linearly in the raw input parameter, tape length O(d log(d+1))). A genuine randomized witness algorithm on the easy complete unit-CNF domain can gate its output by such a predicate, returning the correct pinned assignment on successful tapes and abstaining otherwise. This is not a claim about the specific universal witness machine, which may have additional successful programs.

## Implications for F038

For the fixed-clock sweep of the preceding notes, actual success is decidable by running the sweep on its tape, with polynomial cost for fixed parameters. A circuit for that success predicate is therefore constructible by bounded simulation in polynomial time in the input length. For fixed d, the criterion above characterizes whether it contains a bounded-degree support polynomial, and a full-rank certificate disproves that condition for a particular input and deadline. It does not show that actual universal-clock success predicates realize the hardness family, nor that finding a success tape is hard on the constructed easy unit formulas. If every sufficiently large satisfiable input satisfies the support condition, the earlier sparse hitting list decides SAT in polynomial time without needing to recognize the condition or construct coefficients.

Hence a generic polynomial-time recognition algorithm for arbitrary dense success circuits would imply P=NP, but recognition is unnecessary for the conditional hitting algorithm. What remains unresolved is a structural theorem guaranteeing success of that list, a direct polynomial-time SAT algorithm, or an unrestricted lower bound. No asymptotic progress toward either resolution is asserted solely from these equivalent or restricted conditions.

## Finite regression

Exhaust all Boolean functions on R=1..3 bits and d=0..min(2,R); enumerate every nonzero candidate ANF, compare supported-polynomial counts with rank nullity, and check explicit full-rank certificates or returned coefficients. Expected: 276 functions, 824 degree cases, 294368 polynomial-point checks, 438 full-rank cases, 386 support-existence cases, 3348 nonzero supported polynomials counted, 3176 zero rows summed.

Separately exhaust all 16 two-bit truth tables for each d=0,1,2 using the full guarded-block construction with g=ceil(log2(4(d+1))). Expected: 48 dense circuits, 4210944 tape evaluations, 45 full-rank cases, minimum mass 3/4. Repository audit tests independent basis rows and the exact density bound. The finite tests validate the rank and reduction logic, not the general complexity claims by enumeration.

Next: consider explicit uniform algorithms beyond structural tape promises; a finite list, recognizer or certificate criterion does not settle the universal polynomial-clock obligation. No new Lean declaration or P versus NP resolution.
