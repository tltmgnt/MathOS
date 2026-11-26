# F038 / negative route — MRA-X: affine selector rigidity and exact semantic cover complexity

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not Lean.
Verified parent 56d99b5a376fb6e227bd90371c9768cda282ca98: https://github.com/tltmgnt/MathOS/actions/runs/45730723629 (success). The parent Proctor replay passed; at inspection TOPO-406 was still running. This does not claim every parent workflow finished.

## Backward gap analysis

The previous physical DAG charge theorem is limited by indirect storage access. Replace syntactic ancestor counts by semantic affine restrictions of the SAT selector function. Determine whether allowing arbitrary parity constraints rather than coordinate pins can compress the entire satisfiable region. Test the resulting affine cover lower bound against actual general-circuit elimination costs. The arguments use elementary binary linear algebra, monotone certificates and inclusion-exclusion; no claim of literature novelty. The seven MRA-X roles are authored local records, not independently running agents.

## Constructive track: exact affine cover of the satisfiable selector region

Let U_n be the full normalized nonempty width-at-most-three clause pool on n>=1 Boolean variables, as in prior F038 cycles. Write N=|U_n| and M=sum_{j=1}^min(3,n) binom(n,j). Every assignment x falsifies exactly M clauses, one per support; let X_x be the N-bit vector selecting all clauses true at x. Write q=N-M. The satisfiable selector region S is the downward closure of the 2^n vectors X_x, equivalently the union of coordinate subcubes C_x={p:p<=X_x} of dimension q. Each X_x has weight q and the X_x are distinct by the units. These are precisely the inclusion-maximal elements of S and precisely its weight-q points.

For any affine subspace H contained in S, let d be its dimension. Choose d independent coordinate projections (an information set), and set all these coordinates to one. The resulting point of H has weight at least d, hence d<=q. This upper bound is attained by every C_x.

For n>=2 the dimension-q flats are exactly the C_x. Indeed, in an information set P of size q, the all-ones point is some X_x and all its outside coordinates are zero. Decreasing exactly one coordinate of P to zero can increase at most one outside bit, since weight cannot exceed q. If an outside bit becomes one, the result is another weight-q point at Hamming distance two from X_x. But for distinct x,y, with source Hamming distance e>=1, half the selector Hamming distance is

    D(x,y)=sum_{j=1}^min(3,n) (binom(n,j)-binom(n-e,j)),

using binomial zero outside its range. A support contributes exactly one swap when it intersects the source difference set. Its minimum is delta=1+(n-1)+binom(n-1,2), with delta>=2 for n>=2. Thus distance two is impossible. Every one-coordinate decrement leaves the outside coordinates zero; the affine parametrization then makes them identically zero. Hence H=C_x. For n=1 the additional line joining the two maximal vectors is allowed; rigidity is not asserted there.

### Two maximal points in an affine flat: exact deficit

Any affine flat contained in S contains at most two distinct X_x. For three distinct x,y,z, their differences y+x and z+x are linearly independent over GF(2); choose two source coordinates on which their restrictions are independent. The XOR X_x+X_y+X_z selects one unit sign per source variable, forcing the assignment w=x+y+z. On the chosen two coordinates, the three projected assignments are distinct, and w projects to the fourth value. Each of the three maximal vectors selects the binary clause falsified by that fourth value, so their XOR selects it too. Thus the XOR of the three maximal vectors is unsatisfiable. A flat containing the three would contain their XOR, a contradiction. This uses only the units and all signed binary clauses; for n=1 no triple exists.

Suppose H contains X_x and X_y with x!=y. Translate the flat by X_x. Project its direction space onto the q coordinates in support(X_x). The projection is injective: a nonzero direction zero there would increase weight above q. Hence the direction space is the graph of a linear map L:U -> GF(2)^(N-q), where U is a d-dimensional subspace of GF(2)^q. For every u in U, weight(L(u))<=weight(u), since toggling the selected coordinates loses weight(u), while toggling the unselected ones gains weight(L(u)). The direction X_y+X_x corresponds to u0 with weight(u0)=weight(L(u0))=D(x,y). Let U0 be the intersection of U with the coordinate space supported on supp(u0). Its dimension is at least d+D(x,y)-q. For u in U0, apply the weight inequality to u and u+u0. Their weights sum to D(x,y), while the weights of L(u) and L(u)+L(u0) sum to at least D(x,y). Both inequalities must be equalities. Thus every such u yields a weight-q point of H. Since H has at most two such points, dim(U0)<=1. Consequently

    dim(H)<=q-D(x,y)+1.

The bound is exact: let the coordinates shared by X_x and X_y vary freely, and let one extra binary parameter choose all differing coordinates as in X_x or as in X_y; other coordinates are zero. This is an affine flat of dimension |supp(X_x) intersect supp(X_y)|+1=q-D(x,y)+1, contained in C_x union C_y. The argument gives the exact maximum dimension of a satisfiable flat containing a specified pair of maximal selectors.

### Exact minimum number of affine pieces

The minimum number of arbitrary binary affine flats contained in S whose union is S is exactly 2^n. The witness cubes attain it. For n>=4, every flat has at most 2^q points, while the first two inclusion-exclusion terms give

    |S| >= 2^n * 2^q - sum_{x<y} 2^(q-D(x,y))
         > (2^n-1)*2^q.

The strict inequality follows from binom(2^n,2)<2^delta when delta>=2n-1, true for n>=4. For n=3, the pair counts by distance e=1,2,3 are 12,12,4 and D=4,6,7; normalized pair overlap is 12/16+12/64+4/128=31/32<1, so the same proof works. For n=2, N=8,q=5 and the exact union size is 4*32-40+8-1=95 (pair overlaps 40; each of four triple intersections contains two points; fourfold intersection one point). If three flats covered S and even one had dimension <=4, the combined cardinality would be at most 32+32+16=80. All three would thus have dimension five and be witness cubes by rigidity, but three witness cubes cannot cover the four distinct maximal selectors. For n=1, S has three points and each flat has at most two; two suffice.

A stronger rigidity conclusion holds for optimal covers when n>=4. For n=4 the normalized pair overlap is 32/128+48/2048+32/8192+8/16384<1/2. For n>=5 delta>=2n+1, so the crude pair sum is <1/4. Therefore |S|>(2^n-1/2)*2^q. In a cover of exactly 2^n flats, even one smaller-dimensional piece would make the combined volume at most (2^n-1/2)*2^q. Every piece must have dimension q and hence be a witness cube. Thus for n>=4 the optimal cover is the witness-cube family itself, up to permutation. No assertion of this stronger uniqueness at n=3 is needed.

## Alternative track: exact local affine certificates for all monotone Boolean functions

For an increasing Boolean function f on N bits, let c(x) be the smallest number of coordinates whose values at x force f(x). Let a(x) be the smallest codimension of an affine flat through x on which f is constant. Every coordinate certificate is such a flat, so a(x)<=c(x). Conversely, suppose f(x)=1 and a d-dimensional constant flat H contains x. Intersect it with the coordinate constraints fixing all zeros of x to zero; this nonempty intersection has dimension at least d-number_of_zeros(x), and lies in the remaining one-coordinates. Choose an information set for that intersection and set those coordinates to zero. It produces y<=x with weight(y)<=N-d (if the dimension lower bound is negative, the same bound is already trivial using y=x). Since f(y)=1 and f is increasing, pinning the ones of y to one is a certificate for x of size <=N-d. For f(x)=0 apply the same argument to the increasing function g(z)=1-f(1-z) at z=1-x. Decreasing functions follow by output complementation. Hence a(x)=c(x) for every input of every monotone Boolean function. This is about exact monochromatic affine flats, not arbitrary affine approximations or probabilistic tests.

For the downward monotone universal SAT selector, each satisfiable p has coordinate certificate size exactly M: one may pin all clauses falsified by a satisfying assignment to zero; conversely any coordinate certificate can discard its pinned ones by downward monotonicity, and the largest selected set consistent with its zero pins must itself be satisfiable, hence has at most q selected clauses. On UNSAT inputs the minimum certificate is the size of a smallest unsatisfiable subformula selected at that input (discard pinned zeros by downward monotonicity). Arbitrary parity constraints therefore do not reduce the optimal local exact certificate codimension for either output. This equality is semantic, not a claim that finding a smallest certificate is cheap.

### Gate elimination scope and explicit counterexample

For an arbitrary GF(2) XOR-AND circuit with k AND gates (affine operations free), one can adaptively query one affine operand at each AND gate, conditioned on earlier answers, so every gate becomes affine on each resulting affine cell. In topological order the two AND operands are affine on the current cell; after querying one, their product is zero or the other affine operand. Query the final affine output if necessary. Each accepting cell is contained in S, so an exact affine decision tree for SAT needs at least 2^n accepting leaves by the cover theorem, and this simulation gives at most 2^(k+1) total leaves. Thus k>=n-1, weaker than the prior full-degree bound N-1. The simulation counts queries and leaf branching, not a polynomial circuit compiler. The cover lower bound is exponential in n, not a physical-circuit lower bound.

In fact the unit-only signed pool (no binary/ternary selectors) has S={p: for every i, not(p_i^+ AND p_i^-)}. Its affine dimension is at most n by the same information-set argument; its cardinality is 3^n, so an affine cover needs at least ceil((3/2)^n) pieces. Yet the Boolean circuit with n conflict ANDs, n-1 binary ORs (and one final negation if not folded into a gate) is linear size. This explicit counterexample rules out a universal implication from exponential affine cover size to exponential gate size. Do not claim exact 2^n cover or two-maximal-point rigidity for the unit-only pool. Arbitrary nonlinear gate reuse and compressed descriptions of many affine cells remain uncharged by the cover count.

Topology: the satisfiable selector complex is a downward union of assignment cubes. Its maximal selectors form a rigid finite code; affine flats can bridge two maximal points only by losing a quantitatively specified dimension. This is a semantic cover/linear algebra theorem, not a homology invariant of arbitrary SAT encodings.

## Evidence and cost

Independent JS enumerated every affine flat contained in the full satisfiable selector region for n=1,2, via coset extension. Rows [n,N,q,|S|,total flats,counts by dimension,counts containing exactly two maximal points by dimension,flats containing >=3 maximal points,dimension-q witness cubes]:
[1,2,1,3,6,[3,3],[0,1],0,2],
[2,8,5,95,23024,[95,4465,13941,4235,284,4],[0,6,78,38,4,0],0,4].
Independently computed pair distances, triple XOR checks, exact union volume by inclusion-exclusion for n=1..4. Rows [n,N,q,delta,pairs,triples,|S| as decimal string,sum pair overlap as decimal string,ceil(|S|/2^q)]:
[1,2,1,1,1,0,"3","1",2],
[2,8,5,2,6,4,"95","40",3],
[3,26,19,4,28,56,"3741839","507904",8],
[4,64,50,7,120,560,"17708796636724409","312811058102272",16].
The local certificate equality was checked on all 20 increasing Boolean functions on three variables, all eight inputs and all 51 affine flats, with [n,flats,functions,input cases,coordinate subset tests,affine flat tests,sum certificate sizes]=[3,51,20,160,1280,8160,192].
Python constructs actual signed clauses via the previous pool implementation, independently enumerates affine cosets, checks pair-containing flat dimension maxima and the explicit attaining construction, computes exact union cardinalities, verifies local certificates and unit-only controls. Independent JS did not execute Python. Full affine enumeration and inclusion-exclusion are exponential finite tests only. The mathematical proofs do not rely on finite extrapolation. No general circuit minimizer or unrestricted affine-cell compiler is implemented. Exact-head CI required.

Forward TGA: BARRIER_IDENTIFIED. Exact affine cover complexity and rigidity survive arbitrary parity constraints, and local exact affine certificates cannot beat coordinate certificates for monotone functions. However even exponential affine cover complexity can coexist with linear circuits. Next investigate a genuinely gate-sensitive measure, for example a restriction recurrence using a resource-charged multi-output affine-AND normal form or a structural lower bound on reuse across semantic regions. Do not pursue further cover counts as if they bounded physical size without a valid transfer. No universal obligation closes. Independent mathematical review and Lean formalization outstanding.
