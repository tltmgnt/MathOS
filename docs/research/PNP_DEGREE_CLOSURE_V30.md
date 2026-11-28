# MathOS v30 — adaptive degree closure and algebraic proof complexity

v29 evidence/formal CI passed (46155235136): base 22/29 decisions,
one-wave 29/29, with observed construction work 9,309 versus 112,896.
On fresh cases the counts were 18/24 and 24/24; both refuted the
same eleven UNSAT cases. This is a coverage improvement, not a
work-normalized speedup. v26 and v27 also passed, v28 evidence
passed with 166 independent checks and 128 RHS controls.

## Exact inference model

Work in the Boolean quotient GF(2)[x]/(x_i^2-x_i). A proof starts
with the clause falsification polynomials from v29, uses XOR of
two previously derived polynomials and multiplication by one
variable, and refutes by deriving the constant polynomial 1=0.
Every record must have square-free degree at most D AFTER reduction.
This is a specified Boolean polynomial-calculus variant, not a
claim about all conventions of polynomial calculus or all proof
systems. Degree below initial clause width is outside the model.

The vector space V_D has dimension M=sum_{i=0}^D binom(n,i).
Maintain an independent echelon basis B of derived polynomials.
At a fixed point all original axioms are in its span. For each
variable, let L be multiplication by that variable and let Q
project onto monomials of degree > D. Eligible multiplications of
elements of span(B) are exactly those with Q L(p)=0.

Merely trying eligible products of individual basis vectors is
insufficient: high-degree terms can cancel in linear combinations.
Instead eliminate the high parts of L(B), tracking the combinations
of basis records. The zero high-part columns in this elimination
give a basis of the kernel (one independent combination per
nonpivot input). Multiply those valid combinations and add any
new independent low-degree result. Repeat until 1 is derived or
no dimension increases in a complete sweep. At most M dimension
increases are possible.

## Independent closure and refutation certificates

Every recorded inference is independently reconstructed, with
axiom coefficients obtained from the v29 truth-table transform.
For a closed-space certificate the verifier checks independence,
containment of every axiom, and absence of 1. It independently
eliminates high parts of full products and checks that every
resulting low-degree product belongs to the space. The kernel
basis argument proves closure under ALL eligible products, not
only the sampled or selected ones.

By induction on any valid degree-D derivation, every line belongs
to this space. Consequently 1 outside the space is a certificate
that no degree-D refutation exists in the specified model. This
is stronger than a search timeout. Conversely a checked constant
root certifies UNSAT. A closed space at a lower degree alone
does not certify SAT. Resource exhaustion never establishes
either refutation or obstruction. The algorithm starts at the
maximum normalized clause width and increases D until refutation,
full degree or exhaustion. A refutation preceded by verified
closed spaces at all lower admissible degrees certifies exact
minimum degree in this model.

## Completeness and costs

At degree n every UNSAT CNF is refutable in this quotient model:
for each Boolean assignment a choose a falsified clause C.
Multiply its falsification indicator by the corresponding
indicators for all variables outside C. Multiplication by 1+x
can be implemented as p + xp. This derives the full assignment
indicator delta_a, of degree <= n. Summing all assignment
indicators gives 1. This is an exponential-size existence
argument, not a polynomial-time general SAT algorithm.

For fixed D the abstract monomial dimension is polynomial in n,
and elimination and closure require polynomially many arithmetic
operations in that dimension and n. However this implementation
uses integer bit positions indexed by monomial masks, so the
representation may occupy 2^n bits regardless of D; it is not
an implementation of a general polynomial bit-complexity bound
at fixed degree. Limits: eight normalized variables, 20,000
records, cooperative work/time/cell limits, and independent
replay. No asymptotically growing degree lower bound is claimed.
The closure tests can certify instance-specific degree
obstructions if an independently UNSAT case fails at low degree;
the suite is not guaranteed to contain a strict degree separation.

Six controls plus 24 seeded small CNFs compare one-wave refutations
against adaptive closure, with exhaustive reference decisions.
The comparison is not equal-budget or a representative SAT
benchmark; SAT references are used only for cross-checks, not
credited as algebraic refutations. Tests exhaust all 512 normalized
clause subsets on two variables and 80 seeded small formulas.
Lean checks local inference identities and an abstract soundness
lemma, not the full kernel argument, completeness theorem or Python
code. All universal obligations and barrier statuses remain open.

## Run

    python -m mathos.research.pnp_degree_frontier --simulation artifacts/v24.json --barriers artifacts/v25.json --hypotheses artifacts/v26.json --refinement artifacts/v27.json --symbolic artifacts/v28.json --lifting artifacts/v29.json --checkpoint artifacts/v30.json

Use the same upstream inputs with --audit artifacts/v30.json.
