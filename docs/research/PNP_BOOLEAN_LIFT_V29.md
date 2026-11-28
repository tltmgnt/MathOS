# MathOS v29 — bounded nonlinear Boolean lifting

This release builds on v28's symbolic GF(2) compatibility engine.
It reproduces a bounded polynomial-calculus/linearization technique,
not a general SAT-to-linear-system equivalence.

## Exact polynomial representation, inexact linear relaxation

For a clause C, let p_C be the product of its literal falsification
indicators: (1+x_i) for a positive literal and x_i for a negative
literal over GF(2). On Boolean assignments C holds iff p_C=0.
Reduce monomials by x_i^2=x_i; addition is XOR. Thus the conjunction
of all polynomial equations is exactly the CNF on Boolean inputs.

Introduce one column y_S per nonconstant square-free monomial in
these equations (include every singleton). A genuine assignment
induces y_S=product_{i in S} x_i. Replacing these products by
independent columns gives a necessary linear system. Inconsistency
of that system proves UNSAT of the original CNF. Consistency alone
does not prove SAT: products may not agree with their factors.
Project singleton columns back to a Boolean assignment and check
every original normalized clause; only then credit SAT. Otherwise
return UNKNOWN, retaining the linear assignment and inconsistent
products as diagnostic evidence. No false SAT from relaxed models.

## One-wave refinement

For each original polynomial p_C and each active variable x_i,
include x_i p_C=0 if its reduced degree is within the configured
bound. Retain the original equations and deduplicate identical
polynomials. These are necessary consequences, not extra assumptions.
No recursive multiplication or multiplication by arbitrary monomials
is implemented. The verifier reconstructs coefficients independently
from local Boolean truth tables by a GF(2) Möbius transform,
checks source clause and multiplier indices, and replays the v28
linear dependency contradiction or linear model. SAT projection
is independently checked. Input fingerprint and normalization map
bind the result to the declared original formula.

The control

    (not x or y) AND (x or not y) AND (x or y)
    AND (not x or z) AND (not y or not z)

is UNSAT: the first three clauses force x=y=1, and the final two
force z and not z. Its original monomial relaxation is consistent
but has no satisfying projected model. Adding the one-wave
multiplications produces a linear contradiction. This is a concrete
strict improvement on the base relaxation, not a proof that one
wave always suffices.

## Cost and evaluation scope

For fixed degree D, at most sum_{d=1}^D binom(n,d) nonconstant
monomial columns exist, and the one-wave candidate row count is at
most m(n+1). For fixed clause width and degree, expansion, coefficient
replay and Gaussian elimination have polynomial bit complexity.
The transformation is only a relaxation, not a universally complete
SAT decision procedure. Exact nonlinear consistency would reintroduce
product constraints; this release does not solve those in general.
The practical limits are 12 active variables, degree at most four,
128 distinct lifted rows and 256 columns. Caps yield unknown or
explicit resource exhaustion rather than a logical conclusion.

The experiment compares base degree three and one-wave degree four
on five controls and 24 seeded small binary/ternary CNFs, using
exhaustive reference decisions. These arms differ in degree and
row set and are not an equal-total-work comparison. Record both
directions of coverage difference and construction work, row and
column counts; do not equate cooperative work steps with bit
complexity or runtime. Failed searches and exhaustion metadata are
not proof-certified. Tests cover all 81 signed/absent patterns on
four variables with all 16 assignments, 100 random small CNFs under
both modes, a strict refinement control, tampering and upstream
audit. Lean targets local Boolean identities and abstract relaxation
soundness only, not the full Python compiler or polynomial-calculus
theorem. No universal obligation is closed.

## Run

    python -m mathos.research.pnp_boolean_lift_frontier --simulation artifacts/v24.json --barriers artifacts/v25.json --hypotheses artifacts/v26.json --refinement artifacts/v27.json --symbolic artifacts/v28.json --checkpoint artifacts/v29.json

Use the same upstream inputs with --audit artifacts/v29.json.
Regenerate upstream reports according to the v28 specification.
