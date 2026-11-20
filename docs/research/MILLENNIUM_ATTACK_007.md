# Millennium research attempt 007 — BSD local Euler-factor blind spot

**Date:** November 18, 2026  
**Track:** **Birch and Swinnerton-Dyer conjecture (BSD)**, following the P vs NP, Riemann, and Hodge investigations.  
**Research status:** BOUNDED_RESEARCH / NOT_CERTIFIED / NO_BSD_SOLUTION / NO_CLAIM_OF_NOVELTY.

This attack tests a tempting but inadequate route: **could one infer the rational rank of an elliptic curve from infinitely many matching local point counts on a specified congruence class of primes?** No. For a simple pair of curves with *different known ranks*, those local point counts agree at **every prime** congruent to 3 modulo 4. The result demonstrates a limitation of a partial local-Euler-factor strategy, not of the actual Birch and Swinnerton-Dyer conjecture, which involves the *complete* L-function.

### The official target

The [Clay Mathematics Institute's BSD problem](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/) concerns **every elliptic curve over the rational numbers**. The rank form asks for

\[
\operatorname{ord}_{s=1}L(E,s)=\operatorname{rank}E(\mathbb Q).
\]

The refined version additionally involves the leading term, periods, regulator, local Tamagawa factors, rational torsion and the Tate–Shafarevich group. Proving statements for a chosen example, or an infinite *subset* of the Euler factors, cannot establish the all-curves assertion.

## Theorem — matching infinitely many good Euler factors despite different known ranks

Consider the elliptic curves over the rationals

\[
E_1:\ y^2=x^3-x,\qquad
E_5:\ y^2=x^3-25x.
\]

**Claim 1 (elementary, proved below):** For every prime \(p\equiv3\pmod4\),

\[
\#E_1(\mathbb F_p)=\#E_5(\mathbb F_p)=p+1,\qquad
a_p(E_1)=a_p(E_5)=0.
\]

Both reductions are smooth at these primes: for \(E_d:y^2=x^3-d^2x\), the discriminant is \(64d^6\), so only primes dividing \(2d\) are bad. Every prime \(p\equiv3\bmod4\) is odd and is not \(5\).

**Claim 2 (known external arithmetic, not proved by MathOS):** The Mordell–Weil ranks differ: \(E_1(\mathbb Q)\) has rank \(0\), while \(E_5(\mathbb Q)\) has rank \(1\). These specific values are independently recorded in [LMFDB 32.a3](https://www.lmfdb.org/EllipticCurve/Q/32/a/3) and Alice Silverberg's [ECC2001 BSD lectures](https://cacr.uwaterloo.ca/conferences/2001/ecc/silverberg.pdf), which explicitly discuss **both equations**, their rational groups and analytic ranks. We do **not** infer either exact rank from the finite-field counts.

There are infinitely many primes \(p\equiv3\pmod4\) (proof below). Thus this pair is a rigorous, standard counterexample to the inference that **matching the good Euler factors on this infinite congruence class alone** forces equal rational rank. It is not a BSD counterexample: the L-functions differ at other primes, including \(p=13\), where the exact counts are \(8\) and \(20\).

### Proof of Claim 1 — quadratic-character cancellation

More generally fix any nonzero integer \(d\) and any prime \(p\equiv3\pmod4\) with \(p\nmid d\). Write

\[
f_d(x)=x^3-d^2x,\qquad
\chi_p(t)=\begin{cases}
0 &t=0,\\
1 &t \text{ is a nonzero square modulo }p,\\
-1 &t \text{ is a nonsquare modulo }p.
\end{cases}
\]

For any \(t\in\mathbb F_p\), the number of \(y\in\mathbb F_p\) with \(y^2=t\) is \(1+\chi_p(t)\), including \(t=0\). Adding the unique point at infinity gives

\[
\#E_d(\mathbb F_p)
=1+\sum_{x\in\mathbb F_p}(1+\chi_p(f_d(x)))
=p+1+\sum_{x\in\mathbb F_p}\chi_p(f_d(x)).
\]

Since \(p\equiv3\pmod4\), Euler's criterion gives \(\chi_p(-1)=(-1)^{(p-1)/2}=-1\). Multiplicativity of the quadratic character therefore implies

\[
\chi_p(-t)=-\chi_p(t)\quad\text{for every }t,
\]

including \(t=0\). Also \(f_d(-x)=-f_d(x)\), so for every \(x\ne0\) the pair \(x,-x\) contributes

\[
\chi_p(f_d(x))+\chi_p(f_d(-x))
=\chi_p(f_d(x))+\chi_p(-f_d(x))=0.
\]

The involution \(x\mapsto-x\) has only the fixed point \(0\) for an odd prime; its contribution is \(\chi_p(f_d(0))=0\). The entire sum vanishes, yielding

\[
\boxed{\#E_d(\mathbb F_p)=p+1}
\]

for **every** eligible \(d,p\). Taking \(d=1,5\) proves Claim 1 for all primes \(p\equiv3\bmod4\). \(\square\)

### Infinitely many such primes

Suppose there were only finitely many primes \(p_1,\ldots,p_k\equiv3\bmod4\) and let \(P=p_1\cdots p_k\), with \(P=1\) if the list is empty. Then \(N=4P-1>1\) is an odd integer congruent to 3 modulo 4 and not divisible by any \(p_i\). Its prime factorization must include some prime \(q\equiv3\bmod4\), because a product of primes all congruent to 1 modulo 4 is 1 modulo 4. This \(q\) is not among the \(p_i\), a contradiction. Thus infinitely many good matching Euler factors exist. \(\square\)

## Independent rational-point witness and how rank enters

An exact rational point on \(E_5\) is

\[
Q=(25/4,75/8),\qquad
(75/8)^2=(25/4)^3-25(25/4)=5625/64.
\]

The integral short Weierstrass model has nonzero discriminant, and \(Q\) has a nonintegral x-coordinate. By the **external Nagell–Lutz theorem** (rational torsion points on this integral short Weierstrass equation have integer coordinates), \(Q\) is **not torsion**. Thus \(E_5(\mathbb Q)\) has **positive rank**. This establishes a rank-lower-bound argument using one standard nontrivial theorem as external input; MathOS formalizes the coordinate identity, **not Nagell–Lutz**. The exact rank \(1\) and \(E_1\)'s exact rank \(0\) are **cited external results** from Silverberg's lecture notes.

Both curves have three obvious rational points with \(y=0\): \((-d,0)\), \((0,0)\), \((d,0)\). Together with the point at infinity they give full rational 2-torsion of order four, which does **not** determine free rank. Known congruent-number examples, including \(d=5\), illustrate why rank requires global arguments.

The point \(Q\) is also recorded in Keith Conrad's [*The Congruent Number Problem*](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/congnumber.pdf) along with the right triangle with sides \(3/2,20/3,41/6\) and area \(5\).

## What the formal checker actually proves

[BSDInertPrimeBlindspot.lean](../../formal/BSDInertPrimeBlindspot.lean) uses **Lean 4.14.0 Init only** and proves:

1. The integer cubic \(f_d(x)=x(x^2-d^2)\) is odd for **all** integers \(d,x\).
2. For **any** abstract function \(\chi:\mathbb Z\to\mathbb Z\) satisfying the explicitly stated hypothesis \(\chi(-t)=-\chi(t)\), contributions at \(x,-x\) cancel. The required Legendre-character property and passage to finite-field sums are **paper mathematics**, not formalized in Lean.
3. The exact rational coordinates \(Q=(25/4,75/8)\) satisfy \(y^2=x^3-25x\).
4. \(25\bmod4=1\), documenting the nonintegral x-coordinate without formalizing Nagell–Lutz.

**Lean does not establish finite-field primality, Euler's criterion, the all-prime point-count theorem, elliptic-curve group law, rational rank, analytic rank, an L-function or the BSD conjecture.** There is no hidden axiom asserting BSD.

The independent standard-library [Python checker](../../mathos/research/bsd_inert_007.py) uses two genuinely different point-count algorithms at each checked good prime: exhaustive y-square enumeration and an Euler-criterion Legendre-symbol character sum. It verifies pairwise character cancellation for every checked \(p\equiv3\bmod4\), records the local traces of both curves, rejects bad reduction and invalid inputs, and checks \(Q\) with exact [fractions.Fraction](https://docs.python.org/3/library/fractions.html) arithmetic.

### Reproducible finite validation

~~~sh
lean formal/BSDInertPrimeBlindspot.lean
python -m unittest discover -s tests -p 'test_bsd_inert_007.py' -v
python -m mathos.research.bsd_inert_007 \
  --prime-limit 101 --output artifacts/millennium007/bsd_inert_007.json
~~~

The companion [GitHub Actions workflow](../../.github/workflows/bsd-inert-007.yml) uses pinned Lean and Python 3.11 and retains the generated exact-arithmetic JSON report for 30 days. The tests are **finite consistency checks only**. The universal p≡3 argument is the elementary character-pairing proof above, not the finite enumeration.

## What remains for a genuine BSD solution

The two curves have different **full** L-functions; matching infinitely many Euler factors on the selected 3 mod 4 class is compatible with the true BSD predictions for both curves. Finite computations cannot establish the equality of analytic and algebraic ranks for arbitrary elliptic curves, still less the refined leading-term identity. MathOS's three BSD obligations remain OPEN:

- **BSD.analytic_selmer:** all-curves analytic rank versus algebraic rank, with complete hypotheses.
- **BSD.sha_finiteness:** Tate–Shafarevich finiteness needed for a claimed full refined version.
- **BSD.leading_term:** fully normalized leading-coefficient formula with periods, regulators and local factors.

**Research conclusion:** Any proposed BSD proof using only the Euler factors at primes \(p\equiv3\bmod4\) is missing information, since these two familiar curves agree at every such prime but have distinct established ranks. This is **a classical special-family diagnostic, not new research novelty or an obstruction to the actual conjecture**. The next meaningful theorem would need a noncircular bridge from sufficiently rich global L-function/ Selmer information to rational rank for genuinely new families, subject to external mathematical review.


## TECT-X follow-up: nonisotrivial rank lower bounds (not Selmer-3 infinitude)

An independent exact-arithmetic follow-up studies the nonisotrivial family `E_n: y^2=x^3-a_n^2 x+b_n^2`, `n=5+759m`. The three rational sections are independent modulo doubling for every parameter, so `rank E_n(Q) >= 3`. At `n=5`, four explicit points are independent modulo doubling (reductions at `3,5,23`), proving `rank E_5(Q) >= 4` and `dim_F2 Sel_2(E_5/Q) >= 4`. This **does not** establish rank exactly three or 2-Selmer dimension three on infinitely many nonisotrivial fibers; elimination of additional Selmer classes remains open.

- [TECT-X proof scope and exact arithmetic audit](TECT_X_NONISOTRIVIAL_SELMER_AUDIT.md)
- `python -m mathos.research.tect_x_rank3_family_certificate`
- `python -m mathos.research.tect_x_rank4_fiber_certificate`
- `python -m unittest discover -s tests -p 'test_tect_x_noni_selmer.py' -v`
