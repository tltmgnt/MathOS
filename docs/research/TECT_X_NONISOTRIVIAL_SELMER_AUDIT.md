# ResearchOS | TECT-X — nonisotrivial Selmer-3 infinitude audit

**Scope:** The family in the user's supplied mathematical expression, not the separate quadratic-twist construction.

## Exact desired assertion (OPEN)

For integers `n = 5 + 759m` (`m >= 0`), define

- `a_n = (n^2+27)/(27-n^2)`, `b_n = 6n/(27-n^2)`, and
- `E_n: y^2 = x^3 - a_n^2*x + b_n^2`.

Its `j`-invariant is nonconstant (the family is nonisotrivial), and the existing three independent sections give `rank E_n(Q) >= 3`.  To complete the requested assertion one must independently prove that infinitely many such `n` have `dim_{F_2} Sel_2(E_n/Q)=3`, equivalently that the classes of the three sections exhaust the Selmer group.

**There is no established proof of this infinitude statement in the supplied notes.** A quadratic-twist family with constant `j` where the 2-Selmer dimension equals three is not a proof for `E_n`.

## New exact obstruction at the first parameter: n=5

Here `a_5=26`, `b_5=15` and

`E_5: y^2 = x^3 - 676*x + 225`.

Four rational points are

`P=(0,15), Q=(26,15), R=(-1,30), T=(-18,81)`.

All four are on the curve by direct substitution.  We show that they are independent in `E_5(Q)/2E_5(Q)`.

- `E_5` has discriminant `19748739664`, which is not divisible by any of `3,5,11,23`. It therefore has good reduction at these primes.
- Modulo `11`, the 2-division cubic `x^3-676x+225 ≡ x^3+6x+5` has no root. Therefore `E_5(Q)[2]=0`.
- Modulo `3`, the finite group is `(Z/2)^2`.  `P,T` both reduce to `(0,0)` and `Q,R` both reduce to `(2,0)`. Thus the **only** potentially doubled nonempty binary sums of the four points are `Q+R`, `P+T`, and `P+Q+R+T`.
- Modulo `5`, the curve is `y^2=x^3-x`, with `2E(F_5) = {O,(0,0)}`. `P=(0,0)`, `Q=(1,0)`, `R=(4,0)`, `T=(2,1)`, and `Q+R=(0,0)`. Therefore `P+T=(2,4)` and `P+Q+R+T=(2,1)` are **not** doubled, leaving only `Q+R` as a possible doubled global sum.
- Modulo `23`, the cubic factors as `(x-4)(x^2+4x+7)`, the point `Q+R` reduces to `(2,10)`, and `x(Q+R)-4=-2` is a nonsquare in `F_23`.  Under the 2-isogeny descent criterion associated with the rational 2-torsion point `(4,0)`, a doubled point must have square `x-4`. Hence `Q+R` is **not** doubled either. Alternatively, enumerate the 20 points of `E(F_23)` and directly check that `(2,10)` is absent from `2E(F_23)`; the attached verifier uses this direct enumeration.

All 15 nontrivial binary combinations fail to be twice another rational point. Therefore

`dim_{F_2} E_5(Q)/2E_5(Q) >= 4`.

Since `E_5(Q)[2]=0`, the Mordell–Weil theorem gives

**`rank E_5(Q) >= 4`**, and the Kummer exact sequence gives **`dim_{F_2} Sel_2(E_5/Q) >= 4`**.

Thus `n=5` is a **certified exception** to any claim that every term of the progression has 2-Selmer dimension three. This does not contradict the possibility of an infinite *other* subset of parameters with 2-Selmer dimension three.

## Remaining research obligation

For `K_n=Q[U]/(U^3-(n^2+27)^2 U+36 n^2(n^2-27))`, let `V_n` denote the admissibly ramified norm-one squareclass space. The Kummer images of the three points define a 3-dimensional subspace `W_n`. Let `lambda_n` impose the local Kummer conditions, so that `Sel_2(E_n/Q)=ker(lambda_n)` under the cubic-field realization. Prove an explicit infinite parameter set `I` on which `ker(lambda_n)=W_n` or `rank(lambda_n)=dim(V_n)-3`.

A finite computation for sampled parameters, or local splitting conditions from the Chinese remainder theorem, is not sufficient for this infinitude statement without a global class-group and local-condition argument.

**Status:** Infinite-family rank >=3: established. First fiber `n=5` rank >=4: established in this note. Infinitely many 2-Selmer-dimension-3 fibers: open for this family.

## References

- D. Zywina, *An elliptic surface with infinitely many fibers for which the rank does not jump* (2025), https://arxiv.org/abs/2502.01026 . Explains the nonisotrivial nonjump difficulty and uses highly specialized 2-descent for a rank-0 family.
- Sage documentation, `selmer_rank` and `simon_two_descent`, https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_rational_field.html .

## Preliminary manuscript and publication gate (November 2026)

- [LaTeX preliminary research note](papers/TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex) gives complete finite-field rank lower-bound arguments, the rank-at-least-four first fiber, and the **conditional** mean-16-to-density implication. It does **not** claim a new statistical estimate or Selmer-3 infinitude.
- [Publication readiness and independent review checklist](papers/TECT_X_PUBLICATION_READINESS.md) enumerates explicit mathematical and editorial blockers.
- Targeted GitHub Actions compile the LaTeX draft for review and execute the existing exact-arithmetic regressions. A successful build is a typesetting check, **not** mathematical certification.
