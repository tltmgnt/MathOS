# Millennium research attack 005 — why a finite Li-positive prefix is insufficient under zero symmetries

**Date:** 2026-11-18.
**Track:** **Riemann Hypothesis** (a different Millennium problem from the prior P-versus-NP attacks).
**Status:** \`BOUNDED_RESEARCH\` / \`NOT_CERTIFIED\` / \`NO_RH_PROOF_OR_COUNTEREXAMPLE\`.
**Scope:** A rigorous, **synthetic** finite-zero-multiset construction demonstrating an obstacle to inferring an all-index Li inequality from a finite prefix. This does **not** construct or assert any new zero of the actual Riemann zeta function. No claim of mathematical novelty.

The [Clay Mathematics Institute's RH problem](https://www.claymath.org/millennium/Riemann-Hypothesis/) requires **every** nontrivial zero of analytically continued zeta to satisfy real part 1/2 (or a genuine counterexample). [Li's established criterion](https://mathworld.wolfram.com/LisCriterion.html), with details in [Lagarias, *Li coefficients for automorphic L-functions*](https://www.numdam.org/articles/10.5802/aif.2311/), is that **all** genuine Li coefficients indexed by every positive integer must be nonnegative. The sum over actual zeta zeros requires specific convergence and pairing.

MathOS previously evaluated a first Li coefficient. This attack asks: does positive Li-style data over a finite prefix, even with the standard zero reflection/conjugation symmetries, force every point onto the critical line? **No, for artificial finite zero sets.** This does not answer the same question for actual zeta zero sets with their additional analytic constraints.

## Theorem — arbitrarily long positive prefixes with off-line synthetic zeros

For every fixed integer N ≥ 1, there is a finite multiset Z_N of six complex numbers inside the strip 0 < Re(ρ) < 1 such that (i) Z_N is closed under conjugation and reflection ρ ↦ 1−ρ; (ii) four of its members lie off Re(ρ) = 1/2; yet (iii) all its first N **synthetic Li-style** sums

\[
L_n(Z_N)=\sum_{\rho\in Z_N}\left[1-\left(1-\frac1\rho\right)^n\right]
\]

are real and strictly positive, for n = 1,...,N.

**Crucial distinction:** The artificial Z_N is *not* asserted to be the zero set of the Riemann xi-function, and L_n(Z_N) is *not* an actual Riemann Li coefficient. The result establishes a limitation of **zero symmetry plus finitely many positivity tests alone**, not of all possible special properties of zeta.

### Proof part 1 — a positive baseline critical-line pair

Choose ρ₀ = 1/2+i and its conjugate 1/2−i. Let q(ρ)=1−1/ρ. Then

\[
q_0=q(\rho_0)=\frac{3+4i}{5},\qquad |q_0|=1.
\]

The pair contributes B_n = 2 − 2 Re(q₀ⁿ) ≥ 0. In fact **B_n > 0 for every n ≥ 1**. Put u_n+iv_n=(3+4i)^n with integer coordinates. Since

\[
(3+4i)^2=-7+24i\equiv3+4i\pmod5,
\]

and multiplication by 3+4i preserves that residue modulo 5, induction gives

\[
v_n\equiv4\pmod5\quad\text{for every }n\ge1.
\]

Thus Im(q₀ⁿ)=v_n/5ⁿ is nonzero, so q₀ⁿ ≠ 1. Because |q₀ⁿ|=1, its real part is strictly below 1. Hence B_n>0 for every n≥1.

The all-n Gaussian-numerator congruence and nonzero imaginary-coordinate lemma are **formally proved in pinned Lean 4.14.0** in [LiPrefixObstruction.lean](../../formal/LiPrefixObstruction.lean). The step to B_n>0 also uses the elementary complex norm |3+4i|=5; the Lean file does **not** formalize the zeta function, Li's criterion or the entire analytic construction.

Fix N and take b_N = min(B₁,...,B_N)>0. This is a positive rational number.

### Proof part 2 — a high off-line quartet

For any integer T≥2 add four off-line points:

\[
\rho=3/4+iT,\quad\bar\rho=3/4-iT,\quad
1-\rho=1/4-iT,\quad1-\bar\rho=1/4+iT.
\]

Each is in the critical strip but not on the critical line; together with the baseline pair the six-point multiset respects conjugation and reflection.

For each of the quartet points w, |w|≥T, and the binomial theorem gives

\[
\left|1-\left(1-\frac1w\right)^n\right|
\le \sum_{k=1}^n \binom nk |w|^{-k}
=\left(1+\frac1{|w|}\right)^n-1
\le\left(1+\frac1T\right)^n-1.
\]

Thus the quartet's total contribution D_n(T) has

\[
|D_n(T)|\le 4\left[\left(1+\frac1T\right)^n-1\right]
\le 4\left[\left(1+\frac1T\right)^N-1\right]
\quad\text{for }1\le n\le N.
\]

This bound tends to zero as T grows while b_N remains strictly positive. Choose an integer T such that

\[
4\left[\left(1+\frac1T\right)^N-1\right] < b_N.
\]

Then for all 1≤n≤N,

\[
L_n(Z_N)=B_n+D_n(T)\ge b_N-|D_n(T)|>0.
\]

Conjugate pairing makes every sum real. All three properties are established. **This proves the theorem for every fixed finite N.** ∎

## Independent exact arithmetic and a finite demonstration

The standard-library-only [riemann_li_prefix_005.py](../../mathos/research/riemann_li_prefix_005.py) computes rational-pair complex powers using Python's Fraction type, with no floating-point sign testing. It checks exact base coefficients, the quartet's actual contribution, the strict rational perturbation bound and full symmetry, then emits a **synthetic-only** status.

\`\`\`sh
lean formal/LiPrefixObstruction.lean
python -m unittest discover -s tests -p 'test_riemann_li_prefix_005.py' -v
python -m mathos.research.riemann_li_prefix_005 \
  --prefix 8 --output artifacts/millennium005/finite_li_prefix.json
\`\`\`

For N=8, exact rational arithmetic gives

\[
b_8=3364/78125\approx0.0430592,
\]

and the first power-of-two T meeting the strict bound is **T=1024**, with

\[
4\big[(1+1/1024)^8-1\big]<b_8.
\]

The six synthetic points therefore include four explicit off-critical-line members while the first eight synthetic Li-style coefficients are strictly positive. The executable checker supports prefixes 1 through 12 as a computational bound; the **mathematical construction** above covers every finite N.

The [GitHub Actions workflow](../../.github/workflows/riemann-li-prefix-005.yml) replays the Lean congruence and rational checks. Green CI is not independent mathematical review or proof about the actual Riemann zeta zero set.

## Full Clay obstruction still open

A solution to the **actual** RH requires all actual nontrivial zeros on the line, or a genuine counterexample. Alternatively, a valid all-index proof of positivity of the genuine xi-function's Li coefficients—with fully justified analytic continuation, zero sums and convergence—would suffice. This attack supplies **neither**. No self-adjoint operator with the required zero-spectrum correspondence has been constructed, so MathOS's \`RH.operator\` and \`RH.zero_identity\` obligations remain open.

No novelty, discovery of actual zeta zeros, mathematical validation of RH, public research publication or external prize eligibility is claimed. **Never promote this synthetic theorem into an RH proof or counterexample.**
