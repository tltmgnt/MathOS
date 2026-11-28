# MathOS v32 — compressed algebraic degree coordinates

v31 evidence CI passed (46157972316), with 15 dynamic dual
certificates, 48 functionals, eight refutations, four resolution
simulations and one cross-model separation. Its 16 search cases
contained four UNSAT formulas but no genuine degree obstruction.

## Representation

The former coordinate for square-free monomial x_S was the
integer bit position sum_{i in S} 2^i. Even degree two could
therefore allocate exponentially many bits in n. Enumerate
only subsets of size <= D and give them consecutive indices.
The vector dimension is M=sum_{k=0}^D binom(n,k); at fixed D
this is polynomial in n. Subset labels have n bits and polynomial
vectors have M bits. Generation uses combinations, not range(2^n).
The implementation is compressed dense bit-vector linear algebra,
not a general sparse matrix solver. It retains caps of 64 active
variables, degree four, 4096 coordinates and 50,000 records;
not every combination of the caps is admissible.

For multiplication by x_v, map each monomial S to S union {v}.
An output of degree D+1 can only come from S of degree D with
v absent. It has exactly one such preimage. Therefore a polynomial
in the low-degree space has an eligible product iff all its
coefficients on those blocked coordinates vanish. Cancellation
across linear combinations is still possible and must be accounted
for. Eliminate blocked coefficients of the current basis, tracking
combinations, then multiply the resulting kernel basis and insert
new independent vectors. Repeat until 1 or a fixed point. This is
the v30 model, without exponential coordinate gaps.

## Independent certificates

Refutations replay XOR and variable multiplications in the compressed
coordinates. Original clause polynomials are independently rebuilt
by local truth tables and subset Möbius inversion. Closed spaces
use v31's dual approach: H annihilates every axiom, some h(1)=1,
and each pullback h L_v restricted to eligible coordinates lies in
the span of the similarly restricted H rows. The high-part
constraints are singleton blocked coordinates, so this projected
row-span test is equivalent to the full v31 test. No primal
derivation history is needed for the dual certificate.

For a supplied satisfying assignment, the evaluation functional
h(S)=product_{i in S} x_i is itself a valid dual certificate at
every admissible degree: evaluation commutes with addition and
multiplication. These supplied-model controls verify obstructions
on SAT formulas; they do not demonstrate discovery of an unknown
model or a degree lower bound on UNSAT.

At fixed D, the abstract algorithm makes polynomially many
arithmetic operations in n and M (at most M rank increases,
elimination per variable and sweep, polynomial-size vectors).
Compressed indexing removes the exponential bit-position overhead.
This is not a polynomial-time general SAT algorithm because the
required degree may grow, and full degree has M=2^n. Work and
cell caps are cooperative estimates, not hard memory or bit-operation
measurements. A failed or exhausted search proves nothing.

## Evaluation

26 cases: ten prism parity twins (9 through 27 variables),
three pigeonhole CNFs (6 through 12 variables), a 64-variable
satisfiable implication chain, and twelve seeded random ternary
CNFs on 9, 10 or 12 variables. Parity references use the independent
component certificate, the chain has a supplied zero model,
and remaining references use exhaustive decisions. For even
prisms and the chain the zero-model dual is supplied; odd prisms
use derivation. Other cases use bounded closure and can exhaust.
An UNSAT reference with a valid closed-space dual is a true
instance-specific degree obstruction. A zero count is a legitimate
negative search result. No growing degree lower bound is asserted.
512 exhaustive small CNF subsets and 60 random small formulas
at two degrees cross-check old and new closure classifications.

The 64-variable degree-two case has 2081 coordinates instead
of a potential 2^64 bits in the former coordinate layout.
This is a representation-size comparison, not measured speedup.
The full algebraic proof and Python implementation are not
formalized in Lean; no new Lean targets in this release.

## Run

    python -m mathos.research.pnp_sparse_degree_frontier --checkpoint artifacts/v32.json
    python -m mathos.research.pnp_sparse_degree_frontier --audit artifacts/v32.json

The standalone report audits every credited certificate and case
reference, not the truth of failed-search work counters. All
universal obligations and published barrier assessments remain open.
