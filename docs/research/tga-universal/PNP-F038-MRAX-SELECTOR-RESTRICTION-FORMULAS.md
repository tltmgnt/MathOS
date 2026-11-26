# F038 / negative route — MRA-X: restriction-sensitive formula lower bound and sharing cost

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite regression, not Lean.
Verified parent e1f572b6615e833c9e2c4b947bc9c31422ca976c: https://github.com/tltmgnt/MathOS/actions/runs/45728906720 (success). All seven exact-head workflows succeeded.

## Backward gap analysis

Previous degree symmetry gives a linear general binary-circuit bound. Seek a genuinely superlinear bound on the same fixed universal 3CNF selector function using many disjoint restrictions, and isolate exactly the overhead required to transfer that result to shared circuits. This is an explicit application of the classical Nechiporuk subfunction method (see Savage, Models of Computation, section 9.4, https://cs.brown.edu/people/jsavage/book/pdfs/ModelsOfComputation_Chapter9.pdf ; Buss course notes, https://mathweb.ucsd.edu/~sbuss/CourseWeb/Math262A_2013F/Scribe04.pdf). No claim of novelty or best known lower bound. MRA-X seven stages are authored local records, not independent live agents.

## Constructive theorem: many disjoint blocks with arbitrary residual truth tables

Let F_n be satisfiability of the selected nonempty non-tautological clauses of width <=3 on n variables, with N=2n+4 binom(n,2)+8 binom(n,3)=Theta(n^3) selector inputs as before. For n>=6 put r=floor(n/3), partition the source variables into an address region A of r variables, a guard region B of r variables, and an auxiliary region D of n-2r variables. Put h=floor(log2(r+1)), m=2^h. Partition A into floor(r/h) disjoint h-variable groups (ignore leftovers). For each group I and unordered pair u,v in B, take a selector block consisting of the 2h clauses (x_i OR u OR v) and (not x_i OR u OR v) for i in I. These blocks are pairwise disjoint, since each clause identifies its address coordinate, guard pair, and sign. Their number is t=floor(r/h) binom(r,2). The block fixes no ordinary assignment itself; it specifies a subset of signed pins after we restrict outside inputs.

For each of the 2^m arbitrary subsets T of {0,1}^h, construct an outside-block restriction as follows. Select the units not u, not v. Encode membership in T by a full binary decision tree of depth h on the address bits, with leaf constants equal to its truth table. Introduce one auxiliary source variable y for each internal node, using m-1<=r available variables in D. For address bit x, child values a,b, enforce y=(if x then b else a) by the four width-three clauses

    (x OR not a OR y), (x OR a OR not y),
    (not x OR not b OR y), (not x OR b OR not y).

Simplify Boolean constants at leaves by removing true clauses and false literals. Select a unit forcing the root to one. Normalize any duplicate clauses. All these clauses belong to the universal pool, involve only I and D (except the two guard units), and lie outside the target block. For each address assignment, the auxiliary values are uniquely forced by the mux constraints; the root condition is satisfiable iff that address belongs to T. Set every other outside-block selector to zero. Inside the target block, the positive and negative pin selectors can force any complete address assignment w by selecting exactly one sign per coordinate. The residual function evaluated on that pin pattern equals 1 iff w in T. In fact for every block input the residual is 1 iff T contains an address compatible with all its selected pins. Contradictory pin patterns are rejected.

Thus each block has at least 2^m distinct subfunctions under outside restrictions. This is a statement about the original fixed F_n, not a different circuit for each selected formula. Each outside restriction can be constructed in polynomial time in n given the explicit m-bit T (and can be represented sparsely or as the full selector vector). Enumerating all T is not required in the lower-bound proof. No extra clauses outside the pool and no exponential number of auxiliary source variables are used.

## TECT-X: formula restriction lemma and superlinear lower bound

Consider a rooted Boolean formula (a tree of arbitrary binary Boolean gates, constants and variable leaves) computing a function f. Let a block of its inputs have ell variable-leaf occurrences. If ell=0, outside restrictions yield at most two constants. If ell>=1, retain paths from the root to these leaf occurrences and suppress nodes with exactly one retained child. The resulting fixed full binary skeleton has ell leaves and ell-1 branch vertices. Branch gates and leaf labels are fixed by the original formula. After setting outside variables, every removed subtree evaluates to a constant, and each suppressed path becomes a unary Boolean transformation on the retained child's result. There are at most four possible unary maps (including constants). There are 2ell-2 skeleton edges plus a root path, hence at most 4^(2ell-1) distinct subfunctions. This count allows a retained subtree to become constant and does not require the residual to depend on every retained leaf.

For the constructed blocks m>=2. Since the 2^m subfunctions include nonconstant ones (choose a singleton T), ell>=1. Therefore 2^m<=4^(2ell-1) implies ell>=ceil((m+2)/4). Sum across disjoint blocks to obtain the unconditional leaf-size lower bound

    L_formula(F_n) >= floor(r/h) binom(r,2) ceil((m+2)/4)
                  = Omega(n^4/log n)
                  = Omega(N^(4/3)/log N).

The asymptotic statement uses n tending to infinity; small-n values of this specific lower bound can be below the trivial essential-input bound. A binary formula has total leaf count equal to its internal gate count plus one, so the same asymptotic lower bound holds for formula gates. This exceeds the previous linear degree ceiling in this explicitly restricted computation model. It is not a superpolynomial formula bound and not an unrestricted circuit-size lower bound. All gate functions are allowed; no monotonicity premise.

## Alternative track: valid transfer to general circuits with explicit sharing charges

For any single-output fan-in-two circuit DAG C, unfold it backwards to a formula, duplicating a shared predecessor once per incoming use (count repeated wire references as distinct). The number of unfolded copies of a node is the number of directed paths from that node to the output, counting multiplicity; prove by reverse topological propagation from the output with count one. Let R be the maximum such count among internal gates and S the number of gates. Then the unfolded tree has at most SR internal nodes and at most SR+1 total leaves. Consequently

    SR+1 >= L_formula(F_n).

If D is maximum gate depth, the unfolded binary tree has at most 2^D leaves, regardless of sharing. Hence a general binary circuit for F_n has depth at least log2 of the explicit formula bound, asymptotically 4 log2 n - log2 log2 n - O(1). This improves the earlier degree-derived logarithmic coefficient for sufficiently large n (previous depth bound was log2 N=3 log2 n+O(1)); it remains logarithmic, compatible with polynomial circuits. Also some selector input must have at least L_variable/N unfolded paths, giving Omega(n/log n) multiplicity for at least one selector when L_variable is bounded below by the block sum. This is a necessary amount of reuse in a small circuit, not a bound on distinct physical fan-out. The S*R tradeoff is a lower bound for circuits with a separately justified bound on unfolded gate reuse.

Adversarial counterexample: start with y_0=x_0 and at each stage compute y_i=(y_(i-1) AND x_i) XOR (y_(i-1) OR x_i). This is exactly parity of x_0 through x_i, with three binary gates per stage. The unfolded tree has L_0=1, L_i=2L_(i-1)+2, hence L_i=3*2^i-2 leaves, and 2^i paths from x_0. The actual circuit has only 3i gates, and parity even has a simpler linear-size formula. So a bound on the size of every unfolded formula does not control physical circuit size without controlling reuse, and an explicit unfolding can be highly inefficient even on simple functions. No free polynomial bound on R is assumed.

## Evidence, resource ledger and scope

Independent JavaScript constructed mux CNFs and exhaustively tested all tables for h=1,2,3, all complete pins and all auxiliary assignments, then all partial pin patterns. Rows [h,source variables including guards and auxiliaries,tables,complete pin tests,auxiliary assignment tests,accepted pin tests,unique accepted extensions,partial pin tests]:
[1,4,4,8,16,4,4,16], [2,7,16,64,512,32,32,256], [3,12,256,2048,262144,1024,1024,16384].
Python also builds the actual outside-block units and clauses, verifies membership in the prior universal pool and disjointness from the target block, compares residuals for every partial selector pattern and asserts uniqueness. Independent JS checked all 4096 three-gate formulas over the 16 binary functions on the fixed leaf pattern x0,x1,x0,x2 and all seven nonempty input blocks: [formulas,formula/block pairs,outside restrictions,sum of distinct subfunction counts,max distinct count]=[4096,28672,77824,46320,4]. It enumerated block partitions [n,r,h,m,blocks,distinct block selectors,explicit lower bound]:
[6,2,1,2,2,4,2], [12,4,2,4,12,48,24], [24,8,3,8,56,336,168], [48,16,4,16,480,3840,2400], [96,32,5,32,2976,29760,26784].
The sharing example was checked on all inputs at k=1,2,4,8, rows [stages,gates,unfolded leaves,paths from x0,input checks]:
[1,3,4,2,4], [2,6,10,4,8], [4,12,46,16,32], [8,24,766,256,512].
Python independently evaluates formula skeleton subfunction counts and actual DAG path multiplicities; JS did not execute the submitted Python. All finite enumerations are regression only, not polynomial solvers for arbitrary SAT. General proof uses the block construction and restriction argument, not extrapolation. No universal gate eliminator is implemented. CI required.

Topology: disjoint selector regions admit independently chosen outside restrictions that distinguish arbitrary address tables; the formula skeleton budgets leaf occurrences across regions. Shared computational DAG paths can reuse those occurrences, so the precise cost of unfolding is a necessary transfer condition, not an unrestricted topological invariant of SAT.

Forward TGA: BARRIER_IDENTIFIED. Superlinear formula lower bound and a stronger logarithmic depth bound for general binary circuits; no universal obligation closes. Next investigate direct gate-DAG restriction charging or a justified reuse-sensitive measure that avoids unfolding, with explicit counterexamples to uncharged reuse. Do not claim a superpolynomial general circuit bound. Independent mathematical review and Lean formalization outstanding.
