# TECT-X — Verified positive *prime-active* 2×2 Weil arithmetic Gram

**Status:** a rigorous, narrowly enclosed **actual Weil quadratic-form Gram** on exactly two explicit compactly supported smooth test functions. The certified bound is

```text
lambda_min(H) > 137/5000 = 0.0274.
```

The result includes pole, prime-2 and *complete regularized archimedean distributional* terms, evaluated with rational-endpoint interval box integration. It uses no zeta-zero table and makes no RH assumption. This is a **finite 2D** statement, not global Weil positivity or an unconditionally completed Weil Hilbert space. Mathematical validity depends on the documented classical identities and the implementation of directed interval arithmetic; it is not Lean/Arb-verified or independently peer reviewed.

## 1. Actual arithmetic Weil formula and compact tests

Use the additive logarithmic normalization of Suzuki's Weil distribution:

```text
W(h) = integral_R h(x)(e^(x/2)+e^(-x/2))dx
    - sum_(n>=2) Lambda(n)/sqrt(n) [h(log n)+h(-log n)]
    - [log(4*pi)+EulerGamma] h(0)
    - integral_0^infinity [h(x)+h(-x)-2e^(-x/2)h(0)]
                          e^(x/2)/(e^x-e^(-x)) dx.
```

Take `phi(u)=exp(1-1/(1-u²))` for `|u|<1`, zero elsewhere, and

```text
f0(x)=phi(8x), f1(x)=phi(8(x-3/4)).
H_ij=W(f_i * tilde(f_j)), tilde(f)(x)=f(-x).
```

The diagonals are identical **exactly** because translating both factors of an autocorrelation does not change the convolution: `H_00=H_11=d`. The off-diagonals are real and equal by reflection symmetry: `H_01=H_10=c`.

The diagonal convolution supports are `[-1/4,1/4]`, with no prime powers. The off-diagonal convolution supports are `[-1,-1/2]` and `[1/2,1]`, so only `n=2` can contribute, as proved with exact rational log bounds in PR #86. **The cross prime-2 term is nonzero and negative**; neither the archimedean nor pole term is omitted.

## 2. Rigorous intervals from exact rational boxes

The new implementation uses pinned `mpmath.iv 1.3.0` interval arithmetic and partitions finite integration domains into boxes with endpoints represented by exact Python `Fraction` values. The interval endpoints used in exponentials, logarithms and Fourier kernels are rounded outward by the backend. No unproved convergence order, ordinary Simpson quadrature or floating-point eigenvalue calculation enters the certificate.

The bump function is monotone decreasing in `|u|` on `[0,1]`. On each interval box, its minimum and maximum are therefore bounded by evaluating the analytic expression at the corresponding extreme absolute values. Outside support it is identically zero.

The archimedean kernel

```text
K(x)=e^(x/2)/(e^x-e^(-x)), x>0,
```

is strictly positive and decreasing, since `K'(x)/K(x)=1/2-coth(x)<0`. Thus on `[a,b]` with `0<a<=b`, its interval is `[K(b),K(a)]` with outward endpoint evaluation.

This elementary monotonicity significantly reduces interval overestimation.

### Off-diagonal: direct two-dimensional box enclosure

For the support `h_10(x)=f_1*tilde(f_0)`, set `x=3/4+s-t` to obtain exactly

```text
arch_cross =
    - integral_[-1/8,1/8]^2
          phi(8s)*phi(8t)*K(3/4+s-t) ds dt.
```

Because `3/4+s-t∈[1/2,1]`, there is **no singularity**. The code encloses the double integral by subdividing each axis into `N=256` rational boxes and summing the full interval range multiplied by the exact box area.

The prime contribution is independently enclosed using a rational interval for `log2` (24 terms of an exact atanh series, plus a proved tail):

```text
prime_cross =
    -log2/sqrt2 * integral_[-1/8,1/8]
                    phi(8t)*phi(8(t+3/4-log2)) dt.
```

The pole contribution factors into ordinary moments `m=integral phi(8t)e^(t/2)dt`, evaluated by box integration:

```text
pole_diag=2*m²,
pole_cross=2*cosh(3/8)*m².
```

### Diagonal: exact cancellation before interval evaluation

The diagonal archimedean kernel in its original formula has an apparently singular expression of the form `0/0` at `x=0`. Instead of separately interval-evaluating terms which diverge, use the exact autocorrelation identity (valid for real compactly supported `f`)

```text
D(x) := integral_R [f(t)-f(t-x)]²dt
      =2[h(0)-h(x)] >=0,
h=f*tilde(f).
```

Let `R=1/4`, `C=log(4*pi)+EulerGamma`, `h0=h(0)`,
`J=int_0^R K(x)D(x)dx`, and

```text
I1 = integral_0^R [e^(x/2)-1]/[e^x-e^(-x)] dx.
Tail = -log(tanh(R/2)).
```

The complete diagonal archimedean contribution equals

```text
arch_diag = -C*h0 + J -2*h0*I1 + h0*Tail.
```

This follows by substituting `h(x)=h0-D(x)/2` on `[0,R]` and evaluating the remaining subtraction term analytically on `(R,infinity)`:

```text
2 integral_R^infinity e^(-x/2) K(x)dx
    = integral_R^infinity dx/sinh(x)
    = -log(tanh(R/2)).
```

The integral `J` is nonnegative and fully enclosed on `[1/2048,R]` by a rational-box double Riemann sum. For `0<x<1/2048`, the elementary derivative inequality `|f'|<=64`, union-support measure `<1/2`, and `K(x)<1/x` yield the rigorous missing range bound

```text
0 <= J_(0,1/2048) <= 1024*(1/2048)^2.
```

The bounded regularizer `I1` is enclosed on `[R/512,R]` by ordinary interval boxes. On the first box `[0,delta]`, the analytically valid estimates

```text
e^(-delta/2)*(1/4-delta/16)
 <= [e^(x/2)-1]/[e^x-e^(-x)]
 <= e^(delta/2)/4
```

avoid division by an interval containing zero. The pole moment `m` and `h0` are separately evaluated on rational boxes. Therefore **all** diagonal and off-diagonal Weil contributions are enclosed with proved infinite tails and no unchecked quadrature remainder.

## 3. Portable strict positive matrix certificate

For 256 boxes per long axis, the machine generates **outward-rounded exact rational endpoints** whose indicative decimal values are:

```text
pole_diag:     [0.04524158, 0.04585379]
prime_cross:   [-0.04547806,-0.04524058]
arch_cross:    [-0.02055585,-0.01998493]
arch_diag:     [-0.00025310,0.02059117]

d=H_00=H_11:  [0.04498849,0.06644495]
c=H_01=H_10:  [-0.01757381,-0.01610968]
```

The closed form of the symmetric 2×2 matrix is

```text
H=[d c]
  [c d].
```

For every matrix consistent with the full rational entry enclosures,

```text
lambda_min(H) = d-|c|
  > 0.04498849-0.01757381
  = 0.02741468 > 137/5000 =0.0274.
```

Additionally, the implementation performs an independent interval `LDL^T` check:

```text
pivot_1=d>0,
pivot_2=d-c²/d>0.
```

The JSON contains strictly positive outward rational endpoints for both pivots and an exact binary rational diagonal-dominance margin. Both checks **fail closed** if their respective lower endpoints are not provably positive.

## 4. Reproduction and limitations

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_prime_two_interval.py' -v
python -m mathos.research.riemann_weil_prime_two_interval \
  --panels 256 \
  --output artifacts/riemann/weil_prime_two_interval_psd.json
```

The standalone CI independently checks rational matrix bounds, their strict eigenvalue floor, both interval LDL pivots, the **nonzero prime-2 and archimedean terms**, and the explicit false global/RH flags.

The certificate applies to **only two specified compactly supported test functions** and does not prove positivity for even one arbitrary new direction. It is not an unrestricted small-support theorem, a uniformly positive Weil kernel on all support windows, a full Weil Hilbert space, or a proof of RH.

For broader research, the next defensible task is to validate **new off-diagonal arithmetic blocks** as other test functions and prime powers enter, and investigate whether any global operator inequality can hold for an LF-dense compact-support family without assuming the Weil positivity criterion.

## Sources

- Suzuki, *On the Hilbert space derived from the Weil distribution*, full additive-log explicit formula: https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6
- Yoshida/Bombieri restricted small-support positivity and quantitative modern exposition: https://openmaths.org/courses/NT-EXPF/NT-EXPF-05.html
- MathOS PR #86: https://github.com/tltmgnt/MathOS/pull/86

**No independent formal verification, claim of originality of classical identities, global Weil positivity, or Millennium-prize solution is made.**
