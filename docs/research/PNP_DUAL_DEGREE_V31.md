# MathOS v31 — dual algebraic degree certificates

v30 passed evidence and formal CI (46157313501). It refuted all 16
UNSAT instances in its 30-case suite, exactly matching one-wave
refutations; 31 closed spaces and no UNSAT degree obstruction were
observed. v31 separates proof verification from generation by using
dual constraints, and tests the relationship with resolution.

## Dual closure criterion

For degree D let V be the vector space of square-free polynomials
of degree <= D over GF(2), as in v30. A functional h is a coefficient
dot product. H is a family of such rows, W=ker H. A certificate
requires every original clause polynomial in W and some h(1)=1.
For each variable v, let L be multiplication by x_v followed by
Boolean reduction, Q project onto degrees > D. For every h in H
verify that the pullback of h along L belongs to the row span
of H together with the rows of QL (h is extended by zero at
high coordinates). This implies H p=0 and Q L p=0 entail H L p=0.
Thus W contains the axioms, is closed under XOR and every eligible
multiplication, and excludes 1. Induction rules out every degree-D
refutation, regardless of search budget.

The converse follows by taking H a basis of the annihilator of
the exact v30 closure W whenever 1 is outside W. Every h L
annihilates ker(H) intersect ker(QL); the annihilator of this
intersection is the row span of H and QL. This is ordinary finite
linear algebra. The producer uses verified v30 closure, but the
dual verifier needs only input CNF, degree and H. It independently
reconstructs axiom coefficients and row span tests. No proof-search
completeness or primal history is trusted. The implementation
checks independent H rows, although completeness of the annihilator
basis is not necessary for soundness of a valid dual certificate.

A static dual for the span of just the original axioms has weaker
scope. The v29 strict control admits this static certificate but
has a degree-two dynamic refutation. Relabeling that certificate
as dynamic is rejected by the closure tests. Static and dynamic
obstructions are not interchangeable.

## Resolution simulation

For a clause A write p_A for its Boolean falsification polynomial.
A non-tautological resolution inference from A or x and B or not x
has polynomial premises p_A(1+x) and p_B x. Multiply the first by
p_B and the second by p_A and XOR them. The result is p_A p_B, the
falsification polynomial of the resolvent (repeated variables reduce
by x_i^2=x_i). Multiplication by a positive literal's falsification
factor 1+x_i is realized by one variable multiplication and one XOR.

For ordinary resolution proof width W including its axioms, every
intermediate polynomial has degree <= W+1 (and <= n after Boolean
reduction): its support is within the resolvent variables plus pivot.
A proof of t derived resolution records translates to at most
(4W+1)t polynomial inference records. Both source and translated
refutation replay independently. In particular a valid degree-D
dual obstruction excludes resolution width <= D-1 in this model;
if D<n and the input width permits that comparison. The converse
does not follow. This is a documented simulation argument, not
a formally verified compiler or a new proof-complexity theorem.

The K4 graph-parity control has six edge variables and four
ternary parity blocks (odd charge at one vertex). Distinct scopes
share one variable, so v21's first-step obstruction excludes
resolution derived width three. XORing the four clause polynomials
within each block recovers its parity equation, and summing all
four parity equations derives 1=0 in degree three. Both the
structural premises and the algebraic refutation are replayed.
The zero-charge twin has the same scope graph but is satisfiable.
This is a strict finite cross-model separation, not a growing
lower bound in algebraic degree.

## Search and limits

Seven controls and sixteen seeded binary-quotient 3-CNF search
cases on six to eight declared variables use the minimum admissible
degree (maximum normalized clause width). A reference exhaustive
decision distinguishes a closed space on a SAT case from a true
degree obstruction on an UNSAT case. A zero count of UNSAT
obstructions is a valid negative result. Resource exhaustion is
never credited with a lower bound. The search is not guaranteed
to discover a growing-degree family. It retains v30's eight-variable
cap, exponential bit-mask coordinates, and cooperative budgets.
There is no general SAT solver complexity claim, and the dual
verification and simulation arguments are not fully formalized
in Lean. This release adds no new Lean theorem. All universal
obligations and barrier assessments remain unresolved.

## Reproduce

    python -m mathos.research.pnp_dual_degree_frontier --checkpoint artifacts/v31.json
    python -m mathos.research.pnp_dual_degree_frontier --audit artifacts/v31.json

This standalone report uses the prior verified implementations
but does not embed or regenerate the entire v24-v30 evidence chain.
