# ResearchOS / TECT-X — Interval-enclosed archimedean Weil scalar

**Scope:** a rigorously bounded **one-dimensional** Weil quadratic-form entry for the Gaussian test function `h(t)=exp(-t²/50)`. This is a genuine finite-test positivity inequality, not a proof of the RH-equivalent Weil positivity theorem over all admissible functions. No three-dimensional Gram eigenvalues or new global Hilbert-space completion are certified.

## 1. Classical arithmetic-side formula (no zero inputs)

Let the Fourier convention be `hhat(u)=integral_R h(t)e^{-iut}dt`. The even-test Weil explicit formula gives the scalar

```text
W(h)=h(i/2)+h(-i/2)
     -log(pi)/(2*pi)*hhat(0)
     +1/(2*pi)*integral_R h(t) Re digamma(1/4+i*t/2)dt
     -1/pi*sum_(n>=2) Lambda(n)/sqrt(n)*hhat(log n).
```

For `h(t)=exp(-a*t²)`, `a=1/50`,

```text
hhat(u) = sqrt(pi/a)*exp(-u²/(4a)),
pole     = 2 exp(a/4),
arch     = (1/pi)*integral_0^infinity exp(-a*t²)
                             Re digamma(1/4+i*t/2)dt.
```

The code computes `n<=256` prime powers with integer primality/power detection and interval `log, exp, sqrt, pi`. The exact omitted all-prime-power tail bound `delta` comes from PR #75.

## 2. Certified digamma enclosure for EVERY real t>=0

The Binet integral representation, for `Re(w)>0`, is

```text
psi(w) = log(w)-1/(2w)
       -2*integral_0^infinity u/((w²+u²)*(exp(2*pi*u)-1))du.
```

Since `|w²+u²|=|w+i*u|*|w-i*u| >= (Re w)²`, and

```text
2*integral_0^infinity u/(exp(2*pi*u)-1)du = 1/12,
```

the Binet remainder is bounded by `1/[12(Re w)²]` in absolute value. Put `z=1/4+i*t/2` and `w=z+64`, and apply the exact digamma recurrence:

```text
psi(z)=psi(w)-sum_(k=0)^63 1/(z+k).
```

For `y=t²/4` and `r_k=k+1/4`, this gives the entirely **real** interval expression

```text
Re psi(z) lies in
  (1/2)*log((64+1/4)²+y)
  -(64+1/4)/(2*((64+1/4)²+y))
  -sum_(k=0)^63 r_k/(r_k²+y)
  +[-R,R],

where R=1/(12*(64+1/4)²).
```

All denominators are bounded away from zero. The formula is independent of RH and valid for every t, including every t in the integration interval.

## 3. Enclose the whole archimedean integral without a Simpson assumption

Divide `[0,45]` into exactly 4096 subintervals with **dyadic rational endpoints** and interval-evaluate the Gaussian times the certified digamma interval over each entire subinterval. Each cell's true integral lies in its interval range multiplied by its exact width. Adding the outward intervals bounds the complete integral on `[0,45]`. This method needs **no** unproved 4th-derivative error estimate.

For the infinite tail `t>=45`, write `M=64` and use

```text
|Re psi(1/4+i*t/2)| <= C + t/(2M),

C=log(M+1)+4+log(4M)+1/(2M)+1/(12M²).
```

The estimate follows from the shifted Binet remainder, `log|w| <= log(M+1)+t/(2M)`, and the elementary harmonic-sum bound. Then

```text
|arch_45_to_infinity|
 <= exp(-a*45²)/pi *
    [C/(2*a*45) + 1/(4*a*M)].
```

This bound covers the entire omitted archimedean integral and is evaluated with outward interval arithmetic.

## 4. Control omitted prime powers and the scalar eigenvalue

From the exact rational argument in PR #75, for the chosen Gaussian and every `n>256`,

```text
|prime_full-prime_256| <= delta,

delta = 10*(5/(199/2)+1/(199/2)²)
         /(1+(39601/200)/16)^16
      < 10^(-17).
```

The complete scalar is enclosed by outward interval arithmetic combining the pole, `log(pi)`, the finite-interval archimedean range, **both** analytic tails, and the finite prime-power sum.

At 4096 panels the resulting interval has a strictly positive lower endpoint, approximately **0.026**, and upper endpoint below **0.049**. The exact portable result is recorded as outward-rounded rational endpoints in the generated JSON file. The original unrounded interval endpoints remain more accurate internally.

This yields a valid **one-dimensional** positivity statement for the exact Weil Gram on the span of `q(t)=exp(-t²/100)`, since `h=q²`. Indeed for any real coefficient `v`,

```text
W((v*q)²) = v² W(q²) > 0.
```

The `1×1` Gram eigenvalue is exactly `W(q²)` and is enclosed by the reported rational interval. The same result **does not** establish positivity for an arbitrary finite span or the full Weil test-function class.

## 5. Assumptions, computation trust and independent review

The implementation uses `mpmath.iv==1.3.0` with 45 decimal digits of directed interval arithmetic. The JSON serializes endpoints as exact rational numbers rounded **outward** to six decimal places, making positivity easy to independently check with `fractions.Fraction`.

- The analytic Binet, Gaussian-tail, prime-tail and Weil-form equations are mathematical arguments. The interval library computes enclosures of their arithmetic operations.
- This is **not a fully formal proof**: the correctness of `mpmath.iv`'s directed rounding, code, and integration implementation is a trusted computing assumption. Independent Arb/FLINT or Lean checking would strengthen confidence.
- Prior floating-point Simpson and digamma truncation results from PR #74 remain *uncertified*. The new certificate uses a separate enclosure algorithm and does not retroactively certify those floating-point matrices.
- The script computes only the **single center c=0** and the cutoff `n<=256`. Its positive lower bound does not imply uniform coercivity for increasing dimension or Fourier-support windows.
- All nontrivial zeta zeros, including possible off-line zeros, are already covered by the classical explicit formula, but no positive Hilbert-space completion of the full Weil form or fixed self-adjoint zero operator follows here.

## 6. Run and examine the certificate

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_prime_tail.py' -v
python -m unittest discover -s tests -p 'test_riemann_weil_certified_scalar.py' -v

python -m mathos.research.riemann_weil_certified_scalar \
  --panels 4096 \
  --output artifacts/riemann/weil_certified_scalar.json
```

Inspect `components_outward_rationals.full_G_eigenvalue` and convert the strings with Python `Fraction`. The CI explicitly requires a positive exact rational lower bound, nonzero analytic tail bounds, and no global proof promotion.

## 7. Next mathematical milestone

To certify the actual previous `3×3` Weil matrix from PR #74, one needs sharper interval integration (e.g. derivative-bound midpoint quadrature or validated adaptive quadrature) and eigenvalue inclusion with interval `LDL^T` or Gershgorin/verified Cholesky. Its smallest approximate eigenvalue is only around `10^-4`, so the conservative interval **range** integration used here, though sufficient for the scalar certificate, cannot certify that matrix at 4096 cells.

Thereafter the major barrier remains **all-functions positivity**, with constants and dense-domain controls independent of finite dimension and truncations, before any Hilbert completion or RH implication.

## References

- [NIST DLMF gamma/digamma integral formulas](https://dlmf.nist.gov/5.9)
- [NIST DLMF zeta/explicit formula context](https://dlmf.nist.gov/25.10)
- [Weil quadratic form research and Hilbert space: Suzuki](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6)
- [mpmath 1.3.0 interval arithmetic](https://mpmath.org/doc/current/contexts.html#interval-arithmetic-iv)
- [MathOS underlying Weil form: PR #74](https://github.com/tltmgnt/MathOS/pull/74)
- [MathOS exact prime tail: PR #75](https://github.com/tltmgnt/MathOS/pull/75)

**Result:** genuine **bounded one-dimensional** Weil positivity certificate, conditional on the stated interval arithmetic implementation and classical formula. **Not** a global theorem or RH proof.
