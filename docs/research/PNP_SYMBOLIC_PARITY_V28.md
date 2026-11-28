# MathOS v28 — symbolic conjecture synthesis for linear parity systems

v28 replaces finite descriptor search with a symbolic refinement
mechanism on explicit binary linear systems. This generalizes the
component parity criterion beyond graph incidence matrices. It
reproduces standard linear algebra, not a new theorem about SAT.

## Exact criterion and completeness

Let A be an m by n binary matrix and b an m-bit charge vector.
Apply invertible row operations to obtain echelon matrix E=T A.
The first r rows have strictly increasing pivot positions and
the remaining m-r rows are zero. Consequently rank(A)=r.
Let H consist of the last m-r rows of T. Then

    A x = b is solvable iff H b = 0.

Necessity: the zero rows of E require zero transformed charges.
Sufficiency: the first r equations can always be solved by
back substitution, setting nonpivot variables to zero.
The rows of H are independent because T is invertible, and
H A = 0, so H is a basis for the left nullspace of A.

This is one criterion valid for ALL possible b for the given A,
not an extrapolation from a finite holdout. The number of
independent checks is exactly m-r. Any conjunction of k homogeneous
linear charge checks that characterizes the same image must
have rank m-r by rank-nullity, so k >= m-r. This minimality
is restricted to the number of linear scalar checks, not
arbitrary formulas or proof size.

## Symbolic counterexample refinement

Initially accept every charge vector. For each missing check j
in the derived basis, compute b_j=T^-1 e_(r+j) by reversing
the recorded elementary row operations. Its transformed zero
rows have exactly one nonzero entry. Thus b_j passes every
other basis check but fails check j, and is unsatisfiable.
Add that check to the criterion. Each step is justified by
a concrete symbolic witness that defeats the previous rule.
The verifier checks these dot products directly, as well as the
entire row operation trace, pivot order, rank and zero rows.
This is a fixed linear hypothesis class and a constructive
basis-generation algorithm; it is not unconstrained conjecture
discovery. Unlike the v27 search, no enumeration of RHS vectors
is needed. Independent per-charge proofs are an explicit
solution x or a dependency h with hA=0 and hb=1.

For graph incidence systems this recovers the component
criterion (possibly in another basis). The release also tests
arbitrary overlaps, duplicate and zero rows, and dense generated
matrices. It starts from explicit equations, not an arbitrary
CNF recognizer or universal SAT-to-linear transformation.
The existing v26 recognizer remains scoped to graph parity CNFs.

## Resource and formal scope

Bounded implementation: 128 rows, 256 columns. Gaussian elimination
uses polynomially many row operations, with bit vectors of length
at most max(m,n); inverse replay for all isolated witnesses is
also polynomial. No asymptotic improvement over standard Gaussian
elimination is claimed. The full proof is documented above, not
fully formalized in Lean. Two abstract Lean targets verify XOR
involution and the omitted-check counterexample principle.
The verifier checks algebraic premises on each matrix; the
general rank-nullity and back-substitution arguments are mathematical
background, not machine-checked universal theorems in this release.

Sixteen systems, 128 seeded RHS controls, and exhaustive reference
testing of all 512 binary 3x3 matrices across all eight RHS vectors.
The largest row count represents 2^128 possible charges; only
symbolic basis verification and the specified RHS controls are run,
not enumeration of that many charges. The audit replays exact
upstream v24-v27 reports, basis certificates, decision witnesses
and governance. All universal obligations and barrier assessments
remain open.

## Run

    python -m mathos.research.pnp_symbolic_frontier --simulation artifacts/v24.json --barriers artifacts/v25.json --hypotheses artifacts/v26.json --refinement artifacts/v27.json --checkpoint artifacts/v28.json

Use the same upstream inputs with --audit artifacts/v28.json.
Regenerate upstream reports according to the v27 specification.
