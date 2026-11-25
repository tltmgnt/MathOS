# F038 — Unrestricted-read deterministic branching-program size barrier

PNP_RESOLUTION_STATUS = OPEN. Scoped mathematical derivation and finite regression, not a Lean declaration.
Verified base ce56f9138118c71061c72abe489c312c1769f311: https://github.com/tltmgnt/MathOS/actions/runs/45700192272 (success).

## Indirect storage access and linear local encoding

For integer k>=1 let D=2^k, r=k-ceil(log2 k), B=2^r. Input consists of an r-bit address a, B disjoint k-bit pointer blocks P_i, and a D-bit data table d. Define f(a,P,d)=d[P_a]. The independent input length n=r+kB+D is Theta(D), since D/(2k)<B<=D/k (with equality allowed in the upper bound).

A binary multiplexer mux(s,u,v)=(not s AND u) OR (s AND v) uses three binary gates with signed input literals. Use k multiplexer trees of B leaves to select the k bits of P_a, then one D-leaf tree to select the addressed data bit. This uses exactly g=3(k(B-1)+D-1)=O(n) gates. Encode each AND/OR by its full three-clause equivalence, pin each source input with one signed unit clause, and equate output with selector z via two binary clauses. There are n+g+1 variables and n+3g+2 clauses. Each input has a unique satisfying extension and SAT(F|z=b) iff b=f(a,P,d).

In a public fixed presence template there are M=2n+3g+2=Theta(n) coordinates. Each signed pin presence coordinate is a single source bit or its negation, and all other coordinates are constants. Project any deterministic acyclic selector branching program to a source-bit program by swapping successors on negative pin queries and contracting constants; this cannot increase the number of query nodes. No semantic or syntactic restriction on repetitions, order, width or depth is imposed. All source inputs are promised. The size measure is nodes, not path length.

## Self-contained Nechiporuk counting argument

For each pointer block P_i, fix the primary address to i, fix all other pointer blocks, and vary the data table. This realizes all 2^D distinct Boolean functions on the k bits of P_i. If t_i is the number of nodes of a source branching program labelled by variables in P_i, fixing the other variables and contracting their tests leaves a program with at most t_i query nodes. For counting, pad with unreachable nodes, label the nodes 1,...,t_i, and use two labelled terminals. Such a program has at most (t_i+2)[k(t_i+2)^2]^{t_i} descriptions: choose the start, and for each node its queried bit and two successors. Including invalid or cyclic descriptions only enlarges the bound. t_i>=1 since nonconstant restrictions occur.

If t_i<=D then log2(t_i+2)<=k+1 and log2 k<=k. Taking logs of the description bound gives D <= (k+1)+t_i(3k+2) <= 7kt_i. If t_i>D the same lower bound on t_i is automatic. Therefore t_i>=D/(7k). The pointer blocks are disjoint, so total query nodes >= BD/(7k) >= D^2/(14k^2). With M=Theta(D) this yields Omega(M^2/log^2 M). This is the classical indirect-storage-access application of Nechiporuk's method, here transferred to promised existential branch choice with linear-size clause encoding. Background: Beame et al., Nondeterminism and an abstract formulation of Nechiporuk's lower bound method, https://arxiv.org/abs/1608.01932.

An explicit upper bound is a primary address decision tree, a separate pointer tree for each block, and D shared data-query nodes. It has O(BD+D)=O(M^2/log M) nodes and depth r+k+1=O(log M). Thus this is not a time lower bound, and the hard family itself has a linear ordinary circuit and a polynomial-size branching program. If a layered length-T program has at most W query nodes per layer, then TW=Omega(M^2/log^2 M); this is only a size tradeoff, not a superpolynomial time-space lower bound.

## Regression

Exhaust all source assignments at k=1,2,3 (33312), checking both restricted formulas with the existing exact finite SAT oracle (66624 checks). Enumerate all truth tables induced on each pointer block by fixing other inputs; 552 distinct signatures summed across blocks and parameters. Expected zero/one counts 16656 each, max 46 variables and 107 clauses. Check the fixed template and paired signed pin locality; finite controls validate the reduction, not the asymptotic counting proof.

## Resolution boundary

The preceding stretched-exponential syntactic-read bound and the present unrestricted-read polynomial bound apply to different families; do not combine their strengths. The new lower bound imposes no repetition restriction but does not prove superpolynomial size, randomized branching-program hardness, or a lower bound on unrestricted circuits. M is clause-presence length (and comparable to clause count), not DIMACS bit length. The counting here counts program descriptions and subfunctions, not satisfying assignments. No Lean increment or P vs NP resolution is claimed. Next: evaluate the precise uniform/nonuniform gap for universal selectors or seek a genuinely stronger general branching-program bound; further transfers alone do not imply P != NP.
