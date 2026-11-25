# F038 — Random-access nonmonotone decision branching program barrier

PNP_RESOLUTION_STATUS = OPEN. Scoped mathematical transfer, not a Lean declaration.
Verified base: 12ec40efcc2d9b0711e7decc022aea662e9720c0, exact-head dedicated replay https://github.com/tltmgnt/MathOS/actions/runs/45698503883 (success).

## Direct total-promise circuit encoding

For n>=1, define x in {0,1}^n and y in {0,1}^{2n-1}. With zero-based indices, put
G_n(x,y) = XOR_{0<=j<i<n} (x_i AND x_j AND y_{i+j}).
This is the strict-lower-triangular Hankel quadratic form from Beame, Saks, Sun and Vee, Time-Space Trade-Off Lower Bounds for Randomized Computation of Decision Problems, JACM 50 (2003), 154–195, Section 6.1, Corollary 6.7, https://homes.cs.washington.edu/~beame/papers/randomts.pdf (printed p.184). With one-based indices the Hankel entry is y_{i+j-1}.

Take a fixed circuit for G_n: start accumulator at zero and for each pair use two binary AND gates and one binary XOR gate. Encode each gate by its full truth-table equivalence in 3-CNF (AND uses three clauses, XOR four). Pin each input variable with exactly one unit clause of the required sign. Equate the final accumulator with z via two binary clauses. If r=n(n-1)/2, this gives 3n+1+3r variables and 3n+2+10r clauses. Every assignment of source input bits has a unique satisfying extension by induction in topological gate order. In particular:
SAT(F|z=0) iff G_n(x,y)=0;
SAT(F|z=1) iff G_n(x,y)=1.
Every formula is satisfiable; the choice output is forced, without using counting or off-promise correctness.

## Local projection and arbitrary random access

Use a public fixed template: each input pin has two possible unit-clause presence coordinates, (v) and (not v), occupied according to the input bit and its complement; gate and output constraints are constants. A query to any coordinate is either constant or reads exactly one source bit (possibly negated). This is the chosen input representation, not an arbitrary compact or preprocessed serialization.

Take any randomized acyclic Boolean decision branching program for safe choice on these formulas, with maximum path length T and at most 2^S nodes in each deterministic program (the log-size convention of the cited paper). Randomness is independent of input. Replace each input-coordinate test by the corresponding source-bit test with swapped outgoing edges when needed; contract constant tests. This preserves the size and depth upper bounds, retains the random distribution over programs, and computes G_n with the same error. No read order, monotonicity or read-once restriction is needed.

By Corollary 6.7, for fixed worst-case error epsilon<1/2 and e.g. 1<=S<=n^{1-delta} for fixed 0<delta<1, one obtains
T = Omega(n sqrt(log(n/S)) / (log log(n/S))^{3/2}).
Consequently T/n grows without bound in this space regime. For exact deterministic selectors the same bound follows as a special case. Log-size is not necessarily width or machine working memory; a layered length-T width-2^s program has log-size at most s+log2(T+1)+O(1), giving a corresponding bound by substitution, in particular ruling out T=O(n) and s<=n^{1-delta} simultaneously. Do not equate these measures without charging the layer/address overhead.

## Scope and significance

This is a superlinear bound in the number of independent source bits (3n-1), and applies to arbitrary adaptive random-access Boolean branching programs in the public template representation. The explicit CNF has Theta(n^2) clauses; thus it is NOT a superlinear lower bound in explicit formula length. A program can read all independent bits in linear queries with exponential size by a decision tree. A small-space algorithm can compute the form by rereading source bits for all pairs in O(n^2) queries, with O(log n) counters and accumulator (or corresponding polynomial-size layered program). Neither upper bound contradicts the trade-off. Preprocessing, general circuits, and polynomial-time selectors are not ruled out. No unrestricted P vs NP result follows.

The finite regression enumerates all source assignments for n=1..4, checks both branch restrictions with the existing exact SAT oracle, and checks coordinate locality by all single-bit flips. Expected: 2340 instances, 4680 branches, 1568 zero, 772 one, 31 max variables, 74 max clauses; 2*(2*4+5*32+8*256+11*2048)=49488 changed-coordinate observations. The audit checks the reduction, not the imported asymptotic theorem.

Next: find a near-linear-size local encoding of a function with a known arbitrary-access time-space trade-off, or prove an obstruction to such encoding. Do not claim a near-linear formula-length barrier from the present quadratic template.
