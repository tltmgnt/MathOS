# F038 / MRA-X: decision-preserving affine selector elimination by syndrome DP

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent 008500fa576b015dd510d7035a6ed2ad95b18eb2: https://github.com/tltmgnt/MathOS/actions/runs/45732063063 (success). TOPO-406 was still running at inspection.

## Backward gap analysis

The previous programmable directional derivative changed SAT decision into projected parity. Return to the ordinary existential decision task on a fixed universal normalized nonempty width-three clause pool. Ask whether an affine selector reparametrization admits exact elimination of its selector variables without enumerating its affine dimension. Charge the entire explicit encoding, linear algebra, dynamic program and witness reconstruction. No literature novelty claim; the methods are elementary linear algebra and finite-state dynamic programming. Seven MRA-X stages are authored local records, not independent agents.

## Constructive track: exact syndrome elimination

Let C_1,...,C_N be an explicit list of clauses on n Boolean source variables (in particular, the universal pool). Let p in GF(2)^N select a subset, and let F(p) be its satisfiability indicator. Consider

    E(B,b) = exists p [ Bp=b AND F(p)=1 ],

where B is an explicitly represented binary matrix with N columns and b is a binary right-hand side. An affine parametrization p=p0+Az can be converted by Gaussian elimination to such a system: choose a basis of the annihilator of the column space of A as rows of B and set b=Bp0. The rank r of B is the affine codimension, NOT the number of free selector parameters. For a general system first row-reduce, reject inconsistency, and keep r independent equations. All these steps are polynomial in the explicit encoding. The trivial case r=0 has p=0 as a solution (the empty selection is satisfiable). The dimension n is explicit and charged in complexity; unused source variables may be removed.

For a source assignment x, let J(x) consist of indices of clauses true at x. SAT of a selector with witness x is precisely support(p) subset J(x). Hence E(B,b) iff some x has b in the linear span of columns B_j with j in J(x). This is exact, not a relaxation in which individually feasible selectors need not be jointly satisfiable.

For each variable i and value v in {0,1}, let L_i^v be the list of indices of clauses containing a literal on variable i that is true at value v. Let V_i^v be the span of their columns. For every x,

    span{B_j : j in J(x)} = V_1^(x_1) + ... + V_n^(x_n).

This equality holds because a nonempty clause is true iff at least one of its literals is true; duplicate appearances of a column do not change its span. An empty clause is never contributed; a tautological clause can contribute under either truth value. The theorem does not require all clauses to have width three.

Let D_0={0}, and update the reachable syndrome sets by

    D_i = (D_(i-1) + V_i^0) union (D_(i-1) + V_i^1),

where plus is the set of all pairwise XOR sums. By induction D_i is exactly the union of the spans available from assignments to the first i variables. Each step chooses only one value for the next variable; it never allows both signs to contribute on the same branch. Thus E(B,b) iff b in D_n. Note that the union of the two subspaces need not be a subspace; replacing this union by its span would be unsound.

For each value v compute a linear basis of V_i^v, tracking each basis vector as the XOR of a subset of original column indices. Starting from D_(i-1), close under XOR shifts by successive basis vectors, using old-set snapshots or equivalent Boolean table updates. The closure is exactly D_(i-1)+V_i^v, takes at most r shifts of a 2^r-state table, and the two resulting sets are unioned. Record for each reachable syndrome a predecessor syndrome, the chosen value of x_i and a subset of contributed columns. Reverse traversal reconstructs x and p (XOR the contributed selector masks). Every selected column is from a clause true under the reconstructed assignment, even if a column was used more than once and canceled. The original linear system is satisfied by row-equivalence. This gives a deterministic algorithm with time and space 2^r poly(L), with L the complete explicit input length including the variable count, matrix, clauses and indices. More precisely, the state-update cost is O(n(r+1)2^r) syndrome-table operations after basis computation; storing N-bit selector provenance and n layers of backpointers is charged polynomially per state. A decision-only version needs just two layers. The algorithm can compute all attainable syndromes for a fixed B at once. The prototype implements augmented row reduction, column-basis provenance, exact set updates and witness replay; no arbitrary SAT oracle or free witness discovery is used.

Consequently affine-selector feasibility is fixed-parameter tractable in codimension r, and polynomial when r=O(log L). For a full-row-rank system with an affine space with exponentially many points (dimension N-r) this bound can still be polynomial. This is a new route for the explicit affine-selector subproblem, not a claim that general SAT has a small-codimension representation.

### Exact dual source CNF

For any fixed x, b belongs to the span of satisfied columns iff every dual vector lambda with lambda dot b=1 has some satisfied column B_j with lambda dot B_j=1. This is the finite-dimensional annihilator criterion, valid also for b=0 with the empty collection of tests. Equivalently the source assignment must satisfy the CNF

    AND_{lambda: lambda dot b=1} ( OR_{j: lambda dot B_j=1} C_j(x) ).

Each inner OR is simply a single clause given by the union of the original literal lists; repeated literals can be removed, tautological clauses dropped and an empty OR treated as false. If b!=0 there are exactly 2^(r-1) dual vectors to examine after rank reduction. The construction costs 2^r poly(L) and introduces no existential source variables. Width may exceed three. This dual formula is a useful exact semantic certificate of the elimination, but the resulting CNF must still be solved; the syndrome DP above provides the separate FPT decision and reconstruction algorithm. A direct dual CNF representation is not itself an efficient SAT algorithm.

## Alternative track: NP-completeness even for disjoint narrow parity equations

The codimension premise cannot be discarded. Reduce any normalized nonempty-clause 3CNF G with m clauses on n source variables. Handle an empty clause separately by mapping to a fixed infeasible instance; tautologies and duplicate literals may be normalized first. For each source clause C_j introduce a distinct fresh guard variable g_j. Include one equation fixing the selector of the unit (not g_j) to one. For each literal l of C_j take the selector of (l OR g_j) and impose one parity equation requiring the XOR of these selectors to equal one. All these columns lie in the full universal pool on n+m source variables. Within a block literals are distinct; different guards make blocks disjoint, and no binary selector is a guard unit. All remaining selectors are unrestricted. The 2m rows are independent and have pairwise disjoint nonempty supports of size at most three; every column has at most one nonzero matrix entry. If m=0 the system is vacuous.

Any feasible p must select each guard unit, so all g_j are false in a satisfying assignment. An odd subset of the tagged literals is selected for every clause, in particular at least one true literal in every original clause. Conversely a satisfying source assignment allows selecting each guard unit and exactly one tagged true literal per clause, with every other selector zero. Thus E(B,b) iff G is SAT. Both the universal pool and matrix are polynomial in the original input length. Membership in NP is by the explicit pair (p,x). Hence feasibility is NP-complete even under the stated disjoint-row and width-three matrix restrictions, with all right-hand-side bits equal to one. No actual P!=NP separation follows. Nor is a superpolynomial rank-parameter lower bound proved. In this reduction r grows linearly with the number of source clauses, so the FPT algorithm does not yield a polynomial SAT algorithm.

In particular a uniform polynomial-time preprocessing theorem reducing every such system to an equivalent instance of polynomial size and codimension O(log L) would imply P=NP via the constructive track. A nonuniform existence statement of a small-rank encoding without an efficient transformation does not suffice. This is an explicit remaining decision-preserving transfer obligation. It differs from the previous parity class and does not rely on restricted oracle access.

## Evidence, resource ledger and forward disposition

Independent scalar JS enumerated all selectors for n=1 over every binary matrix with 0..3 rows, and n=2 over 64 deterministic matrices per row count 1..4. The two-variable matrices use the same ordered clause pool as the previous Python module; columns generated by x=seed+1 then x=(1664525*x+1013904223) mod 2^32, column=(x>>16) mod 2^r. For each right-hand side, brute-force feasibility is recorded, including inconsistent linear systems. Rows [source n,input rows,matrices,syndromes tested,selector checks,SAT selector checks,feasible syndromes,infeasible syndromes,globally inconsistent syndromes]:
[1,0,1,1,4,3,1,0,0],
[1,1,4,8,16,12,7,1,1],
[1,2,16,64,64,48,37,27,21],
[1,3,64,512,256,192,169,343,301],
[2,1,64,128,16384,6080,128,0,0],
[2,2,64,256,16384,6080,256,0,0],
[2,3,64,512,16384,6080,504,8,8],
[2,4,64,1024,16384,6080,979,45,40].
Python compares the actual rank-reduced DP and reconstruction against these brute-force syndrome sets and tests the dual criterion for every source assignment and syndrome. It independently checks the reduction on all 256 subsets of the full two-variable width-two pool: [formulas,source assignments,tagged block choices,SAT formulas,satisfying source assignments,total feasible tagged configurations with unmentioned selectors zero,DP replay cases with m<=4,max rows]=[256,1024,12288,95,128,192,163,16]. A configuration is counted separately per source assignment; this is not a count of distinct selectors across assignments. Every guard is pinned false. Tests check actual normalized pool membership, disjoint supports, rank, and reconstruct feasible witnesses for the bounded cases. The JS reference did not execute Python. The brute enumerations and small dual tests are regression only. No claim of Lean proof or external mathematical review.

Topology: selector feasibility is intersection of an affine fiber with the downward union of witness subcubes. Mapping each witness subcube by B gives a syndrome subspace. Taking unions with one choice per source variable yields exact reachability rather than replacing incompatible choices by a common span. This is an explicitly charged algebraic and computational representation, not an unrestricted SAT homology invariant.

Forward TGA: BARRIER_IDENTIFIED (with a constructive FPT subcase). Ordinary SAT decision is preserved, and a precise codimension-controlled compiler with witness reconstruction is obtained, but the NP-complete disjoint parity restriction prevents assuming low rank or disjointness alone is universally sufficient. Next investigate whether a decision-preserving preprocessing using local elimination, rank decomposition or tree-structured syndrome interfaces can reduce effective codimension without making the representation exponentially large; charge its discovery and reconstruction and challenge it on the same disjoint-row reduction. No universal obligation closes. Exact-head CI and independent review required.
