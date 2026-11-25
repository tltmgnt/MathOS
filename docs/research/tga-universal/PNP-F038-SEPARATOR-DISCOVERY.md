# F038 — Exact affine separator discovery and all-tree rank obstruction

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not a Lean declaration.
Verified base 146a2ff95fc45805dfb49633ba847cd317d243a6: https://github.com/tltmgnt/MathOS/actions/runs/45710646307 (success).

## Exact minimum-width recurrence

Use the direction spaces W_i of the residual clause occurrences after the preceding provenance-checked affine extraction. For a set X of clause occurrences let W(X) be their span. Let E be the full occurrence set and define the symmetric cut function

lambda(X) = dim(W(X) intersect W(E-X))
          = rank(W(X)) + rank(W(E-X)) - rank(W(E)).

For a rooted full binary tree whose leaves are the clause occurrences, its width is max lambda(X_v), with X_v the descendant occurrence set of a node. The complement is always taken relative to E, not relative to the current recursive subproblem. Let D(X) be the least possible maximum of these *global* cut ranks in a binary subtree on X. Then D(empty)=0 for the empty instance, D({i})=lambda({i}), and for |X|>=2,

D(X) = max(lambda(X), min_{empty != Y proper subset X}
                            max(D(Y),D(X-Y))).

Proof: every subtree has a first binary split and two child subtrees. Its width is at least the displayed value; conversely choose a minimizing split and optimal child trees, whose existence follows by induction. Thus D(E) is the exact optimum over all binary clause trees. Store a minimizing split for reconstruction. Compute the ranks for every subset by extending the span of a smaller subset. Then compute the recurrence in increasing subset order, considering only splits containing the least element on one side. There are O(3^m) total split trials for m=|E| and O(2^m) states. Each rank and bookkeeping operation costs polynomial time in the explicit input length L. Hence time O(3^m poly(L)), space O(2^m poly(L)). No polynomial-time general optimum discovery is asserted. A certificate of exact optimum can consist of the DP table and reconstructed tree: check every rank and recurrence and compute the tree width. This verifier has the same exponential parameter, not an unconditional polynomial certificate bound. A supplied low-width tree alone is efficiently checkable without computing the optimum.

The cut rank is unchanged by invertible linear coordinate changes. If some occurrences are deleted, the minimum width cannot increase (prune those leaves and suppress unary nodes, and each remaining cut has two spans contained in the corresponding original spans). This gives a valid lower-bound method via subcollections. It is not a claim that arbitrary equivalent rewrites or quotient maps preserve width.

## Polynomial constructive discovery on a connected family

For the preceding affine cycle with m>=3, equalities a_i=b_i and residual triples requiring the group bit a_i to be opposite a_(i+1), there are two residual occurrences per cycle edge. Their identical direction spaces are rank two, spanned by the independent adjacent group-bit directions. Consider the deliberately bad occurrence order listing all positive triples first, then all negative triples. The balanced bisection's root children each span all m directions, so the separator width is exactly m. This is a family of a single direct-sum component and linear global rank; the bad order defeats the previous default tree even though the constraints are easy.

Construct a tree without knowing the generating variable labels: compute canonical bases of clause direction spaces, group equal rank-two spaces in pairs, and connect distinct groups whose spaces intersect nontrivially. On this family that graph is the cycle of edges, including the triangle case. Traverse it, pair the two occurrences of each group as sibling leaves, and recursively bisect the list of these paired subtrees. Each cut at an internal group boundary has at most the two endpoint directions; each singleton occurrence has boundary dimension exactly two because its paired occurrence is outside. Hence the output width is exactly two, the global optimum. Grouping, pairwise intersections, traversal and checking the returned tree width all take polynomial time. The procedure refuses unsupported shapes; even when the intersection graph is a cycle outside this family, the returned width is checked explicitly, since pairwise intersections alone need not capture intersections of larger sums. The algorithm is a special-family discovery theorem, not an approximation guarantee on arbitrary subspaces.

Combining the verified width-two tree with the previous message algorithm gives polynomial total cost for this family. The new executable module implements tree discovery and width verification, not a rewrite of the previous message solver to accept arbitrary trees. The gluing theorem applies directly to any verified tree.

## Explicit obstruction valid for every clause tree

Consider the satisfiable monotone width-two CNF F_n = AND_{i<j}(x_i OR x_j), n>=3. No width-two parity group is complete, so the specified extraction leaves all clauses residual, with the coordinate directions e_i independent. Its m=binom(n,2) occurrences are edges of the complete graph. For any cut of the edges into X and E-X, lambda(X) equals the number b of vertices incident to edges on both sides.

Every binary leaf tree with m>=2 has a node with between m/3 and 2m/3 descendant leaves: starting at the root descend a child with more than 2m/3 leaves while possible; the stopping node still has more than 2m/3 leaves, and one of its children has at least m/3 and at most 2m/3. At this balanced cut let S be the shared vertices, A the vertices exclusive to X, B the vertices exclusive to E-X. Both A and B cannot be nonempty: the edge joining a vertex of A to one of B must be on one side, contradicting exclusivity. Thus one of the two sides uses only S, and contains at least ceil(m/3) edges. Therefore

binom(b,2) >= ceil(m/3).

In particular every clause tree has width Omega(n), despite the trivial all-one satisfying assignment. The explicit bit length is O(n^2 log n) under conventional dense indexed encoding. The lower bound rules out a universal logarithmic-width guarantee for this particular extraction and decomposition of original clause occurrences, even with optimal discovery. It does not establish a SAT lower bound or a lower bound on all equivalent representations, and does not assert that an implementation must populate every possible boundary row. The family is intentionally easy to solve, distinguishing decomposition width from intrinsic computational difficulty.

## Finite regression

Use eight fixed small direction-space generators [1], [2], [3], [4], [5,6], [1,2], [2,4], [1,4] in GF(2)^3. Exhaust all subsets with at most five occurrences, compare exact DP with enumeration of every unordered rooted binary leaf tree, and independently check each cut rank by intersection. Expected: 219 cases, 3489 states/cuts, 7154 split trials, 7135 enumerated trees, optimum-width distribution 26,42,146,5 for widths 0..3, and 51 cases in which default balanced order is suboptimal. Check reconstructed optimum and table corruption rejection. For complete graphs n=3,4,5 exact optima 2,3,4 satisfy the balanced-cut bound (states 8,64,1024; splits 6,301,28501). For cycles m=3,4,7,8,15,16,31,32 compare bad-order widths m to recovered optimum two; verify actual affine extraction, direction groups and trees. Independent finite validation checks these quantities, not asymptotic claims by enumeration.

Next: improve the exact separator join computation or add certified logical simplifications that remove high-width but easy constraints, with full resource accounting. The unconditional obstruction excludes universal small width under the current fixed representation. No new Lean declaration or P versus NP resolution.
