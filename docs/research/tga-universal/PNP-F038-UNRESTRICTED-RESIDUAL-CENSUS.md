# F038 / direct unrestricted route — witness-preserving residual census amplification

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Parent 8c18a1b861c7ad1c5997c0518d650e8a6d5f6de0 passed exact-head Proctor replay: https://github.com/tltmgnt/MathOS/actions/runs/45736972330 . Six parent workflows passed at inspection; TOPO-406 was still running.

## Direct target

Keep exactly the existing U, explicit selector encoding, program syntax, verifier and stage clocks. The preceding symbolic compiler gives the exact residual languages B_k. We now investigate a possible polynomial success cutoff by charging a bounded-frontier search that uses only actual stage-k calls, and prove a quantitative necessary condition for failure at larger polynomial exponents. No extra assumption about the algorithms inside U. This is a classical self-reducibility/sparse-hardness style argument specialized to the same residual family, not a novelty claim. The proof is self-contained; seven MRA-X roles are locally authored records.

## 1. One-variable exact disjunction of prefix restrictions

For each n>=1 let C=U_n be the normalized width-at-most-three clause pool. Let F_p be the conjunction selected by p, and L(n)=n+1+|U_n|. Let a,b be distinct length-i prefixes on the first i source variables, 1<=i<=n. Add one fresh variable z=x_(n+1). Define

    Q(p,i,a,b) = F_p AND
      AND_(j<=i) [(z OR literal(a_j,x_j)) AND
                  (not z OR literal(b_j,x_j))].

All added clauses are non-tautological normalized binary clauses. For any x,z, Q is satisfied iff x satisfies F_p and its first i bits are a if z=0, or b if z=1. Consequently any verified output for Q yields an original witness simply by dropping z. Conversely any original model extending either prefix gives a model of Q. This adds only one variable regardless of the number of original clauses. The complete universal selector encoding at n+1, not just a compact clause list, is used in every stage call.

The encoding (p,i,a,b) -> selector Q is injective for fixed n. Clauses not containing z recover exactly p. The guarded clauses have one per sign of z for every j<=i, and no others; they recover i and the ordered pair of prefixes. No original clause mentions z. This avoids any assumption that arbitrary OR reductions are injective or preserve the original size. L(n+1)=Theta(L(n)); construction and decoding take polynomial bit time in the explicit input length.

## 2. Bounded frontier witness algorithm A_(k,d)

Fix positive integer k and nonnegative integer d. Set b=L(n)^d (any integer cap b>=1 is permitted in the bounded prototype). Maintain a list of at most b distinct prefixes, starting with the empty prefix. At each depth i=1..n, extend every retained prefix by both possible bits of x_i. While there are more than b prefixes, take the first prefix a and the next b distinct prefixes a_1,...,a_b. For each j in order, construct Q(p,i,a,a_j) and run exactly the existing stage s=k ceil(log2 L(n+1)) of U. If a verified witness is returned, project it to x, verify it on the original p and return. If all b calls fail to find a verified witness, delete a. At the final depth, check the remaining at most b full assignments directly, returning a verified model or FAIL.

This is a deterministic total search procedure, not an unconditional SAT decider. It never produces a false witness. FAIL on an arbitrary input is not an UNSAT certificate. No exact SAT test of a pivot occurs in the search; it makes a deliberately lossy deletion if the stage calls all fail. All choices and ordering are fixed. The audit may inspect true witnesses to analyze deletions, but that is separate from the production algorithm.

At each depth at most 2b prefixes are present, at most b deletions occur, and each deletion or successful early exit costs at most b stage calls. The entire algorithm uses at most n b^2 stage calls (including a successful call group), polynomial prefix bookkeeping, and at most b final verifications. Since k,d are fixed, and the previous stage runtime is bounded by a fixed polynomial in L(n+1)+2^s, the total bit runtime is polynomial in L(n), including explicit pool construction, selector materialization, actual program simulation, arithmetic, memory, witness checking and projection. It is not claimed polynomial uniformly in binary k,d. Storing all deletion records for this theorem also costs polynomial for fixed parameters; the search itself need not retain all logs.

## 3. Exact failure-star theorem

Suppose F_p is satisfiable and the algorithm returns FAIL. Fix ANY satisfying assignment x. Until a deletion removes its prefix, the expansion step preserves that prefix. If no such deletion ever occurs, x must appear at the final depth and be accepted. Therefore some deletion removes a prefix a of x. At this deletion, all b actual stage calls on Q(p,i,a,a_j) failed, yet every query has model (x,z=0). By injectivity the queries are pairwise distinct. For the exact exponent-k call they all lie in B_k(n+1), where B_k(n) is the set of residual selectors at source size n.

This gives a local common-witness star of b distinct residual failures, all sharing the same original formula and the same satisfying pivot restriction. The theorem is stronger than just a count of unsuccessful stage calls: each of these b failures is on a satisfiable instance. The star can be recovered in polynomial time from the deletion trace and ANY supplied model x; it does not discover x. If p is known to be a bad satisfiable input but no model is supplied, the existence proof alone does not supply an efficient witness finder.

If, for a particular p, every satisfiable-pivot star has fewer than b distinct stage-k failures at the same depth and with that same pivot, the algorithm cannot fail on a satisfiable p. In particular a global census condition |B_k(n+1)|<b suffices. This is a sufficient criterion, not necessary. Many large residual sets may still be easy for a particular alternative algorithm. A failed call on an unsatisfiable query is not evidence of membership in B_k.

## 4. Quantified transfer between exponents of the SAME U

For every fixed k,d, A_(k,d) has a fixed finite program description in the existing universal machine family and a polynomial simulation bound (ordinary multitape/one-tape polynomial simulation is sufficient). Its verified success, whenever it occurs, is covered by the original length-weighted stage clock at some integer K>=k, uniform over all input sizes and inputs. To see this, if its general tape implementation has length ell and runtime <=c L^e on successful inputs, its stage is <=ell+ceil(log2(c L^e)); increase K to absorb ell,c and rounding for L>=2. No assumption of polynomial success on every SAT input is used. Only the total runtime of the bounded procedure is needed. K depends on k,d and the fixed implementation; no explicit numerical K or efficient generic compiler from source code to U descriptions is supplied here.

If p belongs to B_K(n), this algorithm must fail on p, or its verified model would be available to U at stage K, contradicting membership. Thus for every p in B_K(n) and every model x of p there is a star of L(n)^d distinct members of B_k(n+1), with a common witness extending x. Moreover stars for different p at the same n are disjoint because removing all z-containing clauses recovers p. Summing disjoint stars yields the exact census inequality

    |B_k(n+1)| >= L(n)^d |B_K(n)|    for every n>=1.

This is an unconditional quantified transfer theorem: for each k,d there exists one K>=k such that the inequality holds at every size. The direction is important: the many weaker-stage failures follow from a stronger-stage failure. This cannot be inverted to infer a stronger-stage failure from numerous weaker-stage failures. The known exponent-two counterexamples do not imply existence at the K required here.

Two consequences directly concern the unrestricted problem.

* If for some k there exist constants C,e with |B_k(n)|<=C L(n)^e at every size, choose integer d>e and handle finitely many small n separately. Since L(n+1)=Theta(L(n)), the census inequality forces B_K(n) empty at sufficiently large n. Equivalently the bounded-frontier algorithm finds a verified witness for all sufficiently large SAT instances, and direct exhaustive treatment of the finitely many remaining lengths gives a total polynomial SAT decider. Thus P=NP. The same result holds under the weaker local star bound of polynomial size on every p. Neither bound is assumed or established here.
* If P!=NP, every B_K has unbounded source sizes by the prior exact equivalence. For each fixed k,d, the transfer then forces, at infinitely many n, a common-witness star of L(n)^d distinct residual queries at size n+1. In particular B_k is not sparse: it exceeds every fixed polynomial census bound at arbitrarily large lengths. This follows here from an explicit self-reduction and not by assuming a separate sparse-hardness theorem. The conditional conclusion must not be reported as an unconditional superpolynomial lower bound.

For k=3 this creates a concrete positive route (prove a global or local polynomial residual census, then obtain a polynomial cutoff) and a necessary condition for a negative route (under P!=NP all larger-stage failures enforce arbitrarily large polynomial-sized clusters at the cubic stage). Neither direction currently proves the antecedent needed to resolve the original problem. Proving actual B_3 nonemptiness at arbitrarily large sizes remains open. Even proving superpolynomial density of one B_k would not exclude a polynomial success cutoff at a larger exponent.

## 5. Validation and evidence

Independent JavaScript enumerated all 256 two-variable original selectors, constructed the ordered prefix-pair clauses at both depths, and evaluated all eight enlarged assignments. Metrics [encoded pairs,assignment checks,accepted assignments,selected clauses summed,distinct selectors]=[3584,28672,1024,27648,3584]. It then ran the bounded frontier with the exact parent built-in semantics at stages 0..6 (no general tape descriptions are short enough to appear) and caps 1..4, without using SAT tests in the deletion procedure. Afterward it classified stars by brute source truth. Rows are [stage,cap,inputs,SAT inputs,verified successes,failed SAT inputs,stage calls,successful query calls,deletions,satisfiable-pivot deletions,star count on failed SAT inputs]. Exact independent rows are in the plan JSON. Python additionally constructs the actual normalized selector masks, calls the parent stage implementation, replays all emitted models, and recovers the common-witness star for every original model of every failed SAT fixture. Controls distinguish unsafe deletion from verified rejection, check caps and ordered injectivity, and show that an exhaustive fallback at a small stage cannot fail on satisfiable queries. These are finite tests, not proof of the asymptotic census transfer. The finite test caps and stages are chosen to expose loss; they are not claimed to be the actual fixed-k,d asymptotic parameters. Independent JS did not execute Python.

Forward TGA: BARRIER_IDENTIFIED, with a direct quantitative unrestricted transfer and constructive positive criterion. Next investigate the cubic-stage local census or a resource-preserving adversarial construction that establishes bad instances at the stronger exponent directly. Do not substitute unrelated restricted-model lower bounds, or infer higher-stage hardness from lower-stage stars. No universal obligation closes. Independent mathematical review, Lean formalization and exact-head CI required.
