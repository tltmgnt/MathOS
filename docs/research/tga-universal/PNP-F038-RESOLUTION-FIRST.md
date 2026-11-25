# F038 — Resolution-first research protocol and first global invariant test

PNP_RESOLUTION_STATUS = OPEN.

## Implemented research direction

The existing F037 single-path logical framework gives the direct
positive route: a uniform total polynomial-time selector p on encoded
3-CNF satisfying SAT(F) implies SAT(F restricted by v=p(F,v)) for
every input and occurring variable. The logical bridge was verified
at d73b3c53bff889609863da5197aa3453e21b8de8
(run 45689218464, job 139469884359); it does not prove the selector
premise or its resource bound.

The dependency model now exposes selector_algorithm,
selector_preservation and selector_bit_cost as separate OPEN
obligations for the identical candidate. It retains the certificate
route and the alternative unrestricted SAT and lower-bound routes.
No flags are promoted by this bookkeeping. The historical cumulative
verified declaration count is 1603, not a measure of distance to
resolution. The latest prior probe barrier replay passed at
5aba40c1456195885c8add35247f8df5d3544f38
(run 45695414270, job 139491435707).

Resolution-first cycle protocol:
1. State a proposed unrestricted invariant and explicit algorithm;
   identify its exact correctness and cost claims before experiments.
2. Attempt a general proof, and independently look for a falsifying
   input with a checked model. Reject refuted invariant classes rather
   than endlessly enlarging their finite budgets.
3. No universal completeness claim from finite tests, certificates
   for promise subclasses, an UNKNOWN result, or a solver oracle.
4. Formalize substantial surviving claims; charge all bit operations,
   decoding and intermediate data. Record exact-head verification.
5. A full correctness proof and polynomial bit-cost theorem for one
   actual unrestricted algorithm, or a universal computational lower
   bound, is required before claiming a mathematical resolution.
   Independent review remains a separate evidence requirement.

No milestone date, number of iterations, or theorem count is a
prediction of when the open mathematical problem will be solved.

## First genuinely global candidate: violation moments

For a formula G on a fixed common set of m variables, let V_G(x)
be the number of violated clause occurrences at assignment x.
Consider the global signature

    M_j(G) = sum_x binom(V_G(x),j),    j=0,...,r.

For fixed r, compute these exactly without enumerating assignments:
sum over each j-element subset of clause occurrences, count the
assignments simultaneously falsifying those clauses. If their
falsification literals demand inconsistent bits the count is zero;
otherwise it is 2^(m-|support|). The first r moments have polynomial
construction cost for fixed r: O((M+1)^r poly(N)) bit operations for
M clause occurrences and encoded length N, since each summand and
sum has O(m+r log(M+1)) bits. The set of relevant variables is
densely enumerable from the input; no sparse-id blowup is needed.

A concrete candidate computes the two branch signatures on the
same remaining variable set, compares their truncated alternating
sums sum_j (-1)^j M_j and chooses false on ties. The full alternating
sum is the number of satisfying assignments, by the binomial
identity at each x. The conjectured general shortcut is that a
small initial prefix of those global counts can identify a safe
branch without computing the complete count. The following proof
refutes that shortcut, including arbitrary deterministic rules
using only the two signatures and the same size metadata.

## Forced selector with indistinguishable global signatures

Take a connected cubic prism graph with 2p vertices (p>=3).
Subdivide one edge, giving n=2p+1 vertices, m=3p+1 edges and
one degree-two vertex u. Each edge has a Boolean variable.
Add selector variable v at u so every vertex sees three bits.
At each vertex impose that the XOR of its three bits is zero
except at u, where the charge is b in {0,1}. Encode each
three-bit equation by the four width-three clauses excluding
its violating assignments.

Summing every equation in GF(2) cancels each edge variable
twice, leaving v=b. The branch v=b is satisfiable (all edge
bits zero); the opposite branch is UNSAT. After restriction
the degree-two equation has two binary clauses and all other
equations retain their four clauses. For any edge assignment,
each failed equation falsifies exactly one of its clauses,
and each satisfied equation falsifies none. Therefore the
number of violated clauses equals the weight of the syndrome.

The edge-to-vertex incidence map over GF(2) has image the
even-parity subspace: every column has two ones; conversely
for an even syndrome a spanning tree permits solving the leaf
equations bottom-up, with root equation then satisfied.
The dimension is n-1, so each even syndrome has exactly
2^(m-n+1) preimages. Flipping the selector to the wrong bit
translates the image to the odd-parity coset. Hence, with
q=2^(m-n+1), the complete violation histograms are

    h_good(j)=q binom(n,j) if j even, 0 otherwise;
    h_bad(j) =q binom(n,j) if j odd,  0 otherwise.

Their j=0 entries are q and zero respectively. However for
every k<n the difference of their k-th factorial moments is

    q sum_j (-1)^j binom(n,j) binom(j,k)
      = q (-1)^k binom(n,k) (1-1)^(n-k)
      = 0.

At k=n they differ. Thus even an oracle giving all initial
n-1 exact aggregate moments cannot distinguish the viable
branch from the impossible one. Both orientations of b
produce the same ordered pair of moment signatures, equal
variable and clause counts and the same variable identifier.
Any deterministic rule restricted to that information fails
on at least one of the two orientations. This includes the
implemented alternating-score rule; it chooses false on ties
and is refuted by b=true. The bound does not require assuming
that the n-1 moments are efficiently computable on arbitrary CNF.
It also covers a fixed or logarithmic moment prefix on sufficiently
large members of this linear-size graph family.

This is a limitation of a specified aggregate invariant, not
all global algorithms. In particular Gaussian elimination
solves these parity instances immediately, and syntax-aware
algorithms need not use the signature alone. The proof does
not establish an unrestricted complexity lower bound.
The family is a self-contained incidence calculation, not a
claim of novelty in parity systems or moment methods.

## Independent evidence

Independent JavaScript evaluation checked both orientations at
p=3,4,5,6, including 16 branch histograms via exact syndrome
enumeration, eight direct CNF histograms for the smaller cases,
and the order-three signatures via subcube intersections.
All passed. The largest formula has 20 variables, 52 clauses,
and equal moments through order 12 even though only one branch
is viable. Its correct branch has 128 satisfying edge assignments.
The new Python implementation repeats these tests and two boundary
controls. Its exact-head replay is pending.

## Decision

F038 rejects aggregate low-order violation moments as a universal
standalone decision invariant. This is substantive negative
evidence about one explicit candidate, not a solution or progress
percentage. The direct route remains blocked by the three new
open obligations. Do not count fixtures as proofs or promote
restricted solvers. Seek a different global invariant capable
of retaining the essential distinctions lost by this aggregate.
No new Lean theorem credit, no main change, no PR.
