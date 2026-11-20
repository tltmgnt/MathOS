# TECT-X — Prime-active compact Weil 3×3 Gram with prime powers 2, 4, 5

**Proof scope:** one actual three-dimensional compactly supported Weil test space. This does not establish RH, positivity of an LF-dense family, or the full Weil Hilbert-space completion. Directed interval arithmetic and analytic formula normalization remain trusted computing/mathematical assumptions.

## Three actual compact tests

Let phi(u)=exp(1-1/(1-u²)) for |u|<1 and zero otherwise. Define

- f0(x)=phi(8x), center 0;
- f1(x)=phi(8(x-3/4)), center 3/4;
- f2(x)=phi(8(x-3/2)), center 3/2.

For the classical additive-logarithmic Weil functional W of Suzuki, define G_ij=W(f_i*tilde(f_j)). This is the **actual** arithmetic Weil form, incorporating pole terms, all contributing von Mangoldt prime powers, and the regularized archimedean distribution; no zeta-zero locations are input.

Translation invariance of autocorrelation and the reality of the Weil distribution give the exact Toeplitz form

\[
G=\begin{pmatrix}d&c&e\\c&d&c\\e&c&d\end{pmatrix}.
\]

The old diagonal d and short-range cross term c come from the certified prime-2 compact calculation in PR #87. The new long-range entry e is evaluated independently from the classical arithmetic formula.

## Exact finite prime support

A pair of translated test bumps separated by s has convolution support inside [s-1/4,s+1/4]. The short crosses at s=3/4 have support [1/2,1] and therefore encounter only the prime 2. The long cross at s=3/2 has support [5/4,7/4].

Exact rational enclosures of interval logarithms verify

\[
\log 3<\frac54<\log4<\log5<\frac74<\log6.
\]

Thus the long cross contains **exactly the potential prime powers 4 and 5**, with Λ(4)=log2 and Λ(5)=log5. The program computes both actual convolution values at log4 and log5 using rational-box interval integration and verifies their contributions are strictly negative.

The positive pole term is 2cosh(3/4)m², where m is the previous rigorously enclosed Gaussian-bump exponential moment. The long archimedean term is the actual nonsingular integral

\[
-\int_{-1/8}^{1/8}\!\int_{-1/8}^{1/8}
  \phi(8s)\phi(8t)
  \frac{e^{(3/2+s-t)/2}}{e^{3/2+s-t}-e^{-(3/2+s-t)}}\,dt\,ds.
\]

All terms are enclosed with interval ranges over **exact rational subintervals**, preserving the infinite-dimensional gamma tail from the inherited diagonal certificate.

## Strict rational eigenvalue and interval LDL

Let d_low be a rigorous rational lower endpoint for d, and C,E the rigorous rational upper bounds on |c| and |e|. The code checks

\[
d_{\mathrm{low}}-\max(C+E,2C)>\frac1{200}.
\]

Gershgorin then proves the fixed Gram has minimum eigenvalue **strictly above 1/200**. A separate interval LDL factorization of the full 3×3 Gram must yield three strictly positive pivot intervals. Either failure aborts the certification.

The certificate serializes the entire real symmetric matrix entry intervals, prime-power inventory and individual new arithmetic term intervals, the Gershgorin rational margin and all interval pivots.

## Reproduction

    python -m pip install mpmath==1.3.0
    python -m unittest discover -s tests -p 'test_riemann_weil_prime_four_five_gram3.py' -v
    python -m mathos.research.riemann_weil_prime_four_five_gram3 --panels 256 --output artifacts/riemann/weil_prime_four_five_gram3.json

Tests cover the actual 4 and 5 prime contributions, interval matrix symmetry, strict positivity inequalities, invalid inputs and refusal to claim RH.

## Precise limits

This is a **fixed** 3D compact-support result, not an all-index theorem. No inference is made to arbitrary support windows or an LF-dense test core. The RH-equivalent global positivity theorem would require proof for every admissible compact test; a finite certified Gram, regardless of its margin, is not sufficient.

Source: Suzuki, *On the Hilbert space derived from the Weil distribution*, and previous MathOS prime-active Weil PRs #86–#87. No independent formal proof-assistant or mathematical peer review has been performed.
