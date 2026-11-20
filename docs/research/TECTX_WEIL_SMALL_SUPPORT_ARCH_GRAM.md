# TECT-X — Actual compact-bump Weil arithmetic Gram: rational enclosures and an all-index small-window theorem

**Research status:** a restricted, genuinely infinite-dimensional **positive Weil subspace** follows from the established Yoshida/Bombieri small-support theorem. For explicitly constructed smooth compact bumps, the entire **actual** Weil arithmetic Gram entries are enclosed by conservative exact rational intervals: both pole and prime-power contributions vanish *identically*, while the full archimedean distributional integral is bounded, including its removable singularity and infinite tail. **The archimedean entries are not individually evaluated to narrow numerical intervals.** We do **not** establish the global Weil positivity criterion or RH.

## 1. Correct classical normalization (Suzuki)

In additive logarithmic coordinates, the Weil explicit formula, for `h∈C_c^infinity(R)`, is

```text
W(h) = integral_R h(x)(exp(x/2)+exp(-x/2)) dx
       - sum_(n>=2) Lambda(n)/sqrt(n) [h(log n)+h(-log n)]
       - (log(4*pi)+EulerGamma)*h(0)
       - integral_0^infinity
             [h(x)+h(-x)-2*exp(-x/2)*h(0)]
             *exp(x/2)/(exp(x)-exp(-x)) dx.
```

The convolution-Hermitian Gram is `H_ij=W(f_i*tilde(f_j))`, with `tilde(f)(x)=conjugate(f(-x))`. This is the arithmetic-side formula (no numerical zeta zeros). The apparently singular archimedean integrand is regularized by the exact subtraction term; dropping or modifying its normalization changes the answer.

Source: Suzuki, *On the Hilbert space derived from the Weil distribution*, formula (3.3); see https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6 .

## 2. An explicitly enumerable genuine Cc-infinity family

Take the smooth unnormalized real bump

```text
phi(x)= exp(1-1/(1-x²)),   |x|<1,
        0,                 |x|>=1.
```

For dyadic widths `h=2^-n`, integers `n>=3`, and rational centers `r=p/q` with `|r|+h<1/4`, define

```text
phi_(h,r)(x)=phi((x-r)/h),
f_(h,r)(x)=[D²-1/4]phi_(h,r)(x).
```

These are real smooth compactly supported functions **strictly inside** `(-1/4,1/4)`. The program enumerates all admissible rational pairs by height `n+|p|+q`, and any finite prefix is the start of a genuine unbounded test sequence.

The exponential pole moments vanish **exactly**, by two integrations by parts:

```text
integral_R exp(±x/2) f_(h,r)(x) dx
 = ((±1/2)²-1/4) integral_R exp(±x/2)phi_(h,r)(x) dx = 0.
```

For `h_ij=f_i*tilde(f_j)`, the exponential moments factor, so both pole terms are **zero** for every pair. Every convolution support is contained in `(-1/2,1/2)`; because `log 2>1/2`, no `±log(n)` for any integer `n>=2` occurs. Thus **all prime-power contributions are exactly zero**, not merely numerically tiny.

The full arithmetic Weil Gram here is therefore **exactly its archimedean distributional form**. This only applies within this small support window.

## 3. Rigorous rational outer enclosures for every archimedean entry

The program does not trust an unchecked point-quadrature of a near-zero singular kernel. Instead, it bounds the **entire** remaining archimedean integral by explicit derivative and support inequalities.

Put `y=(1-x²)^(-1)` inside `|x|<1`. The identities

```text
phi^(k)(x) = phi(x) P_k(x,y), P_0=1,
P_(k+1)=partial_x P_k + 2*x*y²*(partial_y P_k-P_k)
```

generate exact integer-coefficient derivative polynomials for k=0,1,2,3. Since `y>=1`,

```text
0<exp(1-y)*y^j <= max(1,j^j),
```

and `|x|<=1`, the sums of weighted absolute polynomial coefficients give exact **integer derivative sup bounds** C_k for the bump. For `f=(D²-1/4)phi_(h,r)` this yields explicit rational bounds

```text
F0 = C2/h²+1/4 >= ||f||_infinity,
F1 = C3/h³+C1/(4h) >= ||f'||_infinity.
```

For `h_ij=f_i*tilde(f_j)`, the convolution is supported in `[-R,R]`, `R<1/2`, and one has the rational bounds

```text
H0=2*min(h_i,h_j)*F0_i*F0_j >= ||h_ij||_infinity,
H1=2*min(h_i,h_j)*F1_i*F0_j >= ||h_ij'||_infinity.
```

Near the apparent archimedean singularity, for x>=0,

```text
|h(x)+h(-x)-2 exp(-x/2) h(0)|
  <= x*(2*H1+H0).
```

For `0<x<=R<1/2`, its kernel `exp(x/2)/(exp(x)-exp(-x))<=1/x`. Hence the absolute integral over `[0,R]` is at most `R*(2H1+H0)`.

Beyond R, the compactly supported h vanishes; the remaining subtraction tail is exactly controlled by

```text
int_R^infinity dx/sinh(x) <= 1/R+2.
```

With `log(4*pi)+EulerGamma<4`, the **full** Weil entry satisfies the simple rational enclosure

```text
|H_ij| <= (6+R+1/R)*H0 + 2*R*H1 =: B_ij.
```

All support and derivative quantities are exact rationals; the report records `[-B_ij,+B_ij]` for each actual matrix entry. These intervals are broad by design and do **not** alone certify the matrix PSD, nor do they constitute tight validated quadrature. The bound covers the *complete* infinite archimedean integral, not just its initial segment.

## 4. Positivity for ALL finite prefixes — restricted small-window theorem

The classical results of Yoshida, reproved or discussed by Bombieri and Connes–Consani, establish nonnegative Weil quadratic form for compactly supported tests in the short logarithmic interval `[-log(2)/2, log(2)/2]`, subject to the relevant pole-moment conditions. The course *Explicit formulas and positivity*, Lesson 5 Theorem 5.1, presents the quantitative bound

```text
W(f*tilde(f)) >= (1/250)*||f||²_L2(R)
```

for tests supported in that window with at least one pole Mellin moment zero. **We use this existing theorem rather than claiming a new proof.** Our family lies strictly within `[-1/4,1/4]`, and *both* moments vanish. Therefore every complex finite linear combination `f_v=sum_j v_j f_j` also meets the theorem, so

```text
sum_(i,j<m) conjugate(v_i)*H_ij*v_j
  = W(f_v*tilde(f_v))
  >= (1/250)*||f_v||²_L2 >= 0
```

for **EVERY integer m>=1**. This is an honest infinite-dimensional all-prefix PSD result on a **proper restricted small-support and moment-zero test subspace**. It does not extend to the full canonical Weil test space and cannot imply RH.

An explicit strict rational diagonal lower bound follows for each test `f_(h,r)`: at its center, `f(r)=-2/h²-1/4`. The derivative sup bound F1 gives `|f| >= |f(r)|/2` on a radius `delta=min(h,|f(r)|/(2 F1))`, so

```text
||f||²_L2 >= delta*|f(r)|²/2,
W(f*tilde(f)) >= delta*|f(r)|²/500 > 0.
```

The program records that exact rational lower bound and the independent archimedean upper enclosure. These are bounds on real *arithmetically specified* entries, **not** evaluations from a table of zeta zeros.

## 5. What is NOT solved

The restricted functions are supported inside `(-1/4,1/4)` and both pole moments vanish. Their span is therefore **not dense** in all `C_c^infinity(R)` in its LF topology. The small-support positivity theorem is unconditional because its function class excludes the regions and directions where RH-equivalent obstructions arise.

Even an unbounded sequence of verified restricted Gram matrices cannot prove RH. There is no new positive Hilbert–Pólya operator, no global all-index Weil PSD theorem, no full Weil-positive Hilbert completion, and no proof of the Riemann hypothesis.

**New priority:** compute **tight** validated archimedean integrals for individual test pairs; then enlarge the support window across `log(2)`, where actual prime-power terms appear, and seek uniform bounds on larger spaces. This requires a new theorem to reach all of `C_c^infinity`.

## 6. Reproduce

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_small_support_gram.py' -v
python -m mathos.research.riemann_weil_small_support_gram \
  --count 3 --output artifacts/riemann/weil_small_support_gram.json
```

The serialized report contains exact rational full-entry intervals, exact zeros for pole and prime terms, strictly positive rational lower bounds on diagonal entries derived from the classical theorem, and explicit false flags for RH/global positivity. The unit tests audit the **implementation of the bounds**; they do not independently establish the cited published small-support positivity theorem.

## References

- Enrico Bombieri, *Remarks on Weil's quadratic functional in the theory of prime numbers, I*, 2000, Sections 1 and 12, https://www.bdim.eu/item?id=RLIN_2000_9_11_3_183_0 .
- *Explicit formulas and positivity*, Lesson 5, Theorem 5.1 (quantitative post-Yoshida small-support theorem), https://openmaths.org/courses/NT-EXPF/NT-EXPF-05.html .
- Masatoshi Suzuki, *On the Hilbert space derived from the Weil distribution*, formula (3.3), https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6 .
- MathOS canonical compact-bump LF core: PR #83. RH-equivalence and finite-prime support gate: PR #84.

**No independent formal/peer review of this implementation, new RH theorem or original small-support theorem claimed.**
