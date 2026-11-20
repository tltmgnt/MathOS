# TECT-X — Fourth compact Weil test direction with prime powers 8, 9, 11

**Scope:** the exact arithmetic Weil form on one fixed four-dimensional span, not positivity over the entire admissible Weil test space. Every claimed lower spectral bound is contingent on passing the actual outward interval certification, including strict rational Gershgorin and shifted interval LDL. No RH proof or unconditional global Weil Hilbert-space construction is claimed.

## Fixed real compact test family

Let φ(u)=exp(1−1/(1−u²)) on |u|<1, and zero outside. Define f_j(x)=φ(8(x−3j/4)) for j=0,1,2,3. Their centers are 0, 3/4, 3/2 and 9/4; all are C_c^∞. Let G_ij=W(f_i*tilde(f_j)) be the classical additive-log arithmetic Weil form in Suzuki's normalization, incorporating the pole moments, every contributing prime power and the regularized archimedean integral.

Translation invariance makes the Gram exactly real symmetric Toeplitz:

```text
G = [ d c e g ]
    [ c d c e ]
    [ e c d c ]
    [ g e c d ].
```

The previously certified three-dimensional arithmetic block (PR #88) supplies d,c,e. The genuinely new long-range arithmetic entry g uses separation s=9/4.

## Exact new prime-power inventory

The convolution at separation s has support in [s−1/4,s+1/4]. At s=9/4 this is [2,5/2]. Directed-rounding interval logarithms with exact outward rational endpoints check log7<2<log8<log9<log10<log11<log12<5/2<log13. Of the integers 8,9,10,11,12 only 8=2³, 9=3² and 11 are prime powers. Thus the *exact* new von Mangoldt contribution is

[
P_g=-rac{log2}{sqrt8}h_g(log8)
    -rac{log3}{3}h_g(log9)
    -rac{log11}{sqrt{11}}h_g(log11).
]

These terms are independently computed using outward boxes for the *actual compact convolutions*, never synthetic matrix data or zeta-zero coordinates. The prime term for the composite integers 10,12 vanishes exactly.

## Validated non-prime terms

The new pole term is 2cosh(9/8)m², where m=∫φ(8t)e^(t/2)dt has an interval enclosure from the original finite rational-box method. The full new archimedean term is the nonsingular double integral

[
A_g=-int_{-1/8}^{1/8}int_{-1/8}^{1/8}
phi(8s)phi(8t)
rac{e^{(9/4+s-t)/2}}{e^{9/4+s-t}-e^{-(9/4+s-t)}},dt,ds.
]

The analytic archimedean kernel is positive and decreasing for positive arguments, and φ is monotone decreasing in |u|. Exact rational boxes and pinned outward interval evaluation enclose the integral, including the true pole term and all arithmetic primes. The diagonal inherits the fully regularized archimedean interval from PR #87; no divergent kernel is evaluated at zero.

## Two independent finite-dimensional positivity gates

Let d_low be the certified lower bound of the diagonal, and C,E,J the certified upper bounds on the absolute values of the three successive cross entries c,e,g. Gershgorin yields

[
lambda_{min}(G)ge
d_{mathrm{low}}-max{C+E+J,,2C+E}.
]

The implementation requires the *exact rational* lower bound to be strictly greater than 1/10000. Independently, it checks all four interval LDL pivots of G−(1/10000)I are strictly positive, rejecting every ambiguous or nonpositive pivot. Only a complete passing CI run justifies the fixed-space conclusion λ_min(G)>1/10000.

## Reproduction

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_prime_eight_nine_eleven_gram4.py' -v
python -m mathos.research.riemann_weil_prime_eight_nine_eleven_gram4 --panels 256 --output artifacts/riemann/weil_prime_8_9_11_gram4.json
```

The JSON contains outward rational endpoints for every matrix entry, the full new pole/archimedean/prime-power components, exact rational support tests, the Gershgorin lower margin, all shifted LDL pivots and explicit rejection of any global PSD/RH claim.

## Fundamental limit

Certification of the actual fourth test does not establish positivity for arbitrary additions, nor does it establish a uniform all-index estimate on the LF-dense Weil core. Global Weil positivity remains RH-equivalent; this fixed four-dimensional result is not a proof of the Riemann hypothesis or a full Weil-positive Hilbert space.

Prerequisites: [MathOS PR #87](https://github.com/tltmgnt/MathOS/pull/87), [PR #88](https://github.com/tltmgnt/MathOS/pull/88). The classical Weil distribution normalization is discussed in Suzuki's *On the Hilbert space derived from the Weil distribution*. The trusted implementation uses mpmath.iv==1.3.0 and has not been independently checked in a formal proof assistant or by expert referees.
