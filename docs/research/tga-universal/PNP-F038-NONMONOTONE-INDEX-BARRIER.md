# F038 — Nonmonotone index barrier for reusable branch-choice summaries

Status: scoped mathematical argument; executable regression, not a verified Lean declaration. PNP_RESOLUTION_STATUS = OPEN.
Base: 2c8f6491e0dda5cc11fe4f99c9c932f438d88619 (F038 monotone choice replay passed).

## Model
Use the existing fixed oriented clause-template representation: each edge bit is copied into its associated coordinates (presence of color constraints, absence of clique constraints); fixed clauses are constant. Consider a one-way summary of a fixed data block before a disjoint query block is revealed. The encoder can be arbitrary nonmonotone, nonlinear, computationally unbounded. A decoder receives only the summary and query, not the original data or access to its source. It must choose a satisfiable branch whenever one exists. The same summary must work for every completion. Memory is measured in bits (at most 2^s possible states for s bits).

## Reduction
For a,b >= 1, k >= 4, let A,B be disjoint sets of sizes a,b and C a set of k-2 vertices. Put an arbitrary bipartite graph between A and B, encoded by x in {0,1}^{ab}. Make C a clique. For query (i,j), join every vertex of C to exactly the two vertices u=A_i and v=B_j in A union B; add no other edges. Write G(x,i,j) for the graph, N=a+b+k-2 and m=ab.

If x_ij=1, C union {u,v} forms a k-clique and the graph is not (k-1)-colorable. If x_ij=0, assign distinct colors 1,...,k-2 to C, color both u and v with color k-1, all remaining A vertices with color 1, and all remaining B vertices with color 2. This is proper: the selected pair is nonadjacent, C has no neighbors other than the pair outside C, and all other data edges go between the two parts. Thus the graph is (k-1)-colorable and has no k-clique. This proof works because k>=4. The existing F038 guarded 3-CNF F_G therefore has exactly one satisfiable branch, whose index is x_ij.

Data-edge coordinates depend only on x; all remaining coordinates depend only on the query or are fixed. The lower bound applies to the specified block split, not arbitrary permutations or representations.

## Deterministic lower bound
If distinct x and y shared a summary, choose a coordinate where they differ. That same query forces opposite outputs on two satisfiable formulas, contradicting correctness. Hence there must be 2^m distinct summary states, so s >= m. Balanced a,b give s >= floor((N-k+2)^2/4) for N>=k; fixed k=4 gives Omega(N^2) bits. This is tight for this data/query family: store the entire m-bit data matrix and answer a query by indexing.

For any exact finite-field affine sketch into F_q^d, the total sketch splits as a data-only vector plus a query-only vector and a constant. Even with unrestricted nonlinear decoding, injectivity implies q^d >= 2^m, or d log2(q) >= m. For GF(2) this forces full column rank on the m independent data bits after composing the sketch with the clause-coordinate repetition map. No dimension bound over exact unbounded-precision reals follows.

## Randomized extension
For public randomness R independent of uniform X in {0,1}^m and an s-bit message M, suppose every input and query is answered with error <= epsilon < 1/2. Absorb independent private randomness into R if needed. For each coordinate t, the decoder predicts X_t from (M,R,t). Its binary error indicator gives H(X_t|M,R) <= h2(epsilon). By conditional entropy subadditivity,
m-s <= H(X|M,R) <= sum_t H(X_t|M,R) <= m h2(epsilon).
Consequently s >= m(1-h2(epsilon)). This is the standard one-way INDEX information bound, here transferred to existential branch selection. See https://www.cs.cmu.edu/afs/cs/user/dwoodruf/www/teaching/15851-spring25/lec20.pdf.

## Scope and validation
The regression exhausts four small (a,b,k) triples, checks graph properties and both SAT branches with the existing exact finite DPLL oracle, and checks that all query-answer signatures are distinct within each triple. It also verifies that oriented clause inputs factor across the designated split. Expected: 514 graph/query instances, 1028 SAT branch checks, 257 each branch, 98 distinct signatures summed across the four families.

This is not a general nonmonotone circuit lower bound or a superpolynomial memory lower bound. It blocks lossless subquadratic-bit reusable summaries on this family, even with an unbounded nonmonotone decoder; it does not block a query-aware encoder, rereading the data, interactive protocols, polynomial-space algorithms, or unrestricted SAT selectors. The finite replay does not prove the asymptotic theorem. No Lean count increment or P versus NP resolution is claimed.
