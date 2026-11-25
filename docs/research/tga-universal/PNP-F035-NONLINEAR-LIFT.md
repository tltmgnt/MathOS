# F035 — Nonlinear lifting and the completeness gap

PNP_RESOLUTION_STATUS = OPEN.

Expand clause products over GF(2) as sums of monomials. Under an
actual Boolean assignment this agrees exactly with the factored
polynomial. Relaxing independent monomial values to linear unknowns
preserves every real model but not conversely. The formula
(not x1), (not x2), (not x3), (x1 or x2 or x3) is unsatisfiable.
Its expanded linear equations accept the pseudo-moments
m_empty=m_123=1 and all other moments zero. No Boolean assignment
realizes these moments. The Lean candidate also proves that multiplying
a vanishing clause polynomial by a variable preserves vanishing.

An independent Python experiment uses square-free Boolean monomials
and static monomial multiples of the original clause polynomials.
For pigeonhole 4 into 3 (12 variables, 22 clauses), exhaustive
assignment checking proves UNSAT. The exact coefficient span does
not contain 1 at degree caps 2,3,4,5; it does at cap 6.
The 5-degree system therefore has a feasible normalized linear
moment assignment despite the absence of Boolean models. This is a
finite counterexample to completeness at that cap, not a lower
bound for iterative polynomial calculus, arbitrary multipliers,
all algebraic algorithms or asymptotic SAT complexity. Row counts
at the refuting degree stop when a contradiction is discovered.

A degree-d square-free monomial representation has
sum_{j=0}^d binomial(n,j) coordinates. A constant degree cap admits
a polynomial-size explicit lift, but universal completeness of such
a cap is not proved and this experiment already falsifies cap 5
for this exact static construction. An increasing degree may require
superpolynomial resources. A compact nonlinear encoding is not a
decision procedure.

Nine new Lean candidates, 97 Lean controls, 4096 truth-table controls
and five degree-span checks. Strict replay includes all fifteen
upstream affine candidates; do not count upstream declarations twice.
