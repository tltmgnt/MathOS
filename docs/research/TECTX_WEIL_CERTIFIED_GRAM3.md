# ResearchOS / TECT-X — Verified (3\times3) Weil arithmetic Gram

**Certification level:** Strict positivity of a single, fixed, three-dimensional Gaussian-cosine Weil Gram is established by explicitly justified analytic remainder bounds and outward interval arithmetic. The conclusion is **conditional on the correctness of the pinned interval-arithmetic library and implementation**; it is not an independently formalized theorem. **This is not global Weil positivity, a Hilbert–Pólya operator, or a Riemann hypothesis proof.**

## 1. Precisely which matrix?

Let (a=1/50), let (c=(0,1/5,1/2)), and define

```text
q_j(t) = exp(-t²/100) cos(c_j t)
h_jk(t) = q_j(t) q_k(t) = exp(-t²/50) cos(c_j t) cos(c_k t).
```

The **actual** Weil-form Gram matrix is (G_{jk}=W(h_{jk})), computed from the classical explicit formula under the Fourier convention `hhat(u)=integral_R h(t)e^(-iut)dt`:

```text
W(h) =
  h(i/2)+h(-i/2)
  -[log(pi)/(2*pi)] hhat(0)
  +[1/(2*pi)] integral_R h(t) Re psi(1/4+i*t/2)dt
  -[1/pi] sum_(n>=2) Lambda(n) n^(-1/2) hhat(log n).
```

All test functions are admissible even entire Gaussian-Schwartz functions; the RHS is meaningful without supplying or assuming the location of any zeta zeros, and the zeta zero sum on the other side of the explicit formula incorporates multiplicities and hypothetical off-critical-line zeros.

Unlike the independent positive `L²` Gram in PR #74, **this calculation is for the real Weil form itself**.

## 2. Digamma enclosure through Binet's integral

Put `z=1/4+it/2`, `r=64+1/4`, and `w=r+it/2`. The recurrence

```text
psi(z)=psi(w)-sum_(k=0)^63 1/(z+k)
```

is exact. Binet's integral gives, for `Re w>0`,

```text
psi(w)=log w-1/(2w)-1/(12w²)+1/(120w⁴)+R(w),
|R(w)| <=1/(252 |w|⁴ (Re w)²) <=1/(252 r⁶).
```

For clarity, the last bound follows by expanding
`1/(w²+u²) = 1/w²-u²/w⁴+u⁴/[w⁴(w²+u²)]`
inside Binet's integral and using
`2 integral_0^infinity u⁵/(e^(2*pi*u)-1)du=1/252` and
`|w²+u²|>=r²`.

Therefore the real digamma function can be bounded by **real interval arithmetic** at each integration node:

```text
Re psi(1/4+it/2) =
  (1/2)log(r²+q) - r/[2(r²+q)]
  - (r²-q)/[12(r²+q)²]
  + (r⁴-6r²q+q²)/[120(r²+q)⁴]
  - sum_(k=0)^63 (k+1/4)/[(k+1/4)²+q]
  + [-R,R],
q=t²/4, R=1/(252r⁶).
```

The implementation evaluates the displayed center expression outward and separately adds the worst-case integrated remainder `45R/pi`. No digamma value from unverified floating-point special-function routines is used to certify positivity.

## 3. High-accuracy validated Simpson error with a *proved* fourth derivative

For each entry define `f_jk(t)=e^(-t²/50)cos(c_j t)cos(c_k t) Re psi(1/4+it/2)`. Composite Simpson on `[0,45]` with `n=8192` **even** panels satisfies

```text
| integral_0^45 f_jk(t)dt - Simpson_n(f_jk) |
   <= 45/180 * (45/n)^4 * sup_[0,45] |f_jk''''(t)|.
```

A uniform elementary rational bound is available **for all centers in [0,1/2]**. For the digamma real part `g(t)`, the recurrence and the classical polygamma series give

```text
|g^(k)(t)| <= [16,10,36,208,1632][k]  for k=0,...,4.
```

For `k>=1`, bound the absolutely convergent series by

```text
|g^(k)| <= (k!/2^k)*sum_(n>=0)(n+1/4)^(-k-1)
         <= (k!/2^k)*(4^(k+1)+4^k/k).
```

For `g` itself, the shifted Binet expression on `[0,45]` and a harmonic-sum bound give `|g|<16`.

For the Gaussian `E(t)=e^(-a t²)`, let `v=2a*45=9/5`. Since `|E|<=1`, the first four derivatives are bounded by

```text
[1, v, v²+2a, v³+6av, v⁴+12av²+12a²].
```

The `k`th derivative of `cos(c_jt)cos(c_kt)` has absolute value at most `(c_j+c_k)^k<=1`, and Leibniz's rule bounds the derivatives of the product. Together these estimates yield the **exact rational envelope**

```text
M4 := sup |f_jk''''| <= 946104/125 < 8000.
```

The implemented Simpson error includes the factor `1/pi`. The conservative per-entry Simpson contribution at 8192 panels is smaller than `5.5*10^-7`.

## 4. Infinite archimedean and prime-power tails

For `t>=45`, shifted Binet + harmonic estimates give

```text
|Re psi(1/4+it/2)| <= C+t/(2*64),
C=log(65)+4+log(256)+1/128+1/(12*64²).
```

Because `|cos(c_j t) cos(c_k t)|<=1`, the Gaussian archimedean integral tail is bounded by

```text
(e^(-a*45²)/pi) * [ C/(2a*45) +1/(4a*64) ].
```

The exact rational prime-power error from **PR #75** bounds the omitted full sum `n>256` by `delta<10^-17` for every center pair in this family. Both tails are added as outward symmetric error intervals. The finite prime-power sum uses **integer prime-power recognition**, interval logarithms, and the exact analytic Gaussian Fourier transform.

Thus **every** matrix entry is enclosed, including pole terms, `log(pi)`, archimedean integral, and all prime powers. Approximate entries are around

```text
G ≈
[  0.03708258346, -0.03511814137,  0.02591496600 ]
[ -0.03511814137,  0.03333113683, -0.02469637709 ]
[  0.02591496600, -0.02469637709,  0.01850777088 ].
```

These decimals are **illustrative only**. The JSON file contains outward exact rational bounds on every entry and is the verification evidence.

## 5. Interval LDL and an explicit, *true eigenvalue* lower bound

For a real symmetric matrix `G`, the `LDL^T` pivot recursion is

```text
d_i = G_ii - sum_(k<i) L_ik² d_k,
L_ji = [G_ji-sum_(k<i)L_jk d_k L_ik]/d_i.
```

The implementation performs these operations **with intervals**. When every computed pivot interval has a strictly positive rational lower bound, every real symmetric matrix inside the stated entry enclosures is positive definite.

For the actual Weil Gram, all three pivot intervals are strictly positive. More strongly, repeating this check for

```text
G - (1/1000000) I
```

also yields three strictly positive pivots. Therefore for every real coefficient vector `v in R³`,

```text
vᵀ G v > (1/1000000) ||v||².
```

Equivalently, the exact smallest eigenvalue of this specific Weil matrix satisfies

```text
lambda_min(G) > 10^-6.
```

The previously floated numerical estimate is around `8.38*10^-6`. The proof only claims the safer `10^-6` bound.

**This is a fixed three-dimensional statement, not a uniform lower bound in dimension or Fourier support.** The Weil form on the entire admissible function space remains an RH-equivalent open problem.

## 6. Reproduce and inspect

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_certified_gram3.py' -v
python -m mathos.research.riemann_weil_certified_gram3 \
  --panels 8192 --output artifacts/riemann/weil_certified_gram3.json
```

The JSON reports all 3×3 matrix-entry interval endpoints, each Simpson/digamma/archimedean/prime bound, unshifted and shifted interval LDL pivots, and no-RH-promotion flags. These are exact rational strings **rounded outward** to 12 decimals for matrix entries and pivots, and to 18 decimals for analytical component errors. The underlying calculations retain greater interval precision.

The analytic argument relies on the classical Weil explicit formula, Binet/polygamma identities, Simpson error theorem, and finite-dimensional Sylvester criterion. The computation trusts pinned `mpmath.iv` directed rounding and source-code correctness, not independently verified Lean or Arb formalization.

## 7. Scientific scope and next research obstacle

| Obligation | Outcome |
|---|---|
| Digamma evaluation for all quadrature nodes | Rigorous analytic Binet remainder with interval nodes |
| Archimedean integral `[0,45]` | Outward Simpson plus proved fourth derivative bound |
| Infinite archimedean/prime-power tails | Explicit analytical enclosures |
| Exact fixed `3×3` Weil Gram | All entries enclosed |
| Fixed `3×3` positive definiteness | Certified conditional on interval implementation |
| Fixed `3×3` least eigenvalue | Strictly above `10^-6` |
| Global Weil positivity / Hilbert completion | **Open** |
| Riemann hypothesis | **Not proved** |

The next serious challenge is an inequality **uniform over growing families and support**, or a sound infinite-dimensional positive operator construction à la Suzuki's screw function. Such a theorem cannot be inferred from any finite Gram matrix, however carefully certified.

Related research: [NIST DLMF §5.9](https://dlmf.nist.gov/5.9), [Suzuki's Weil Hilbert-space research](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6), and the parent [PR #74](https://github.com/tltmgnt/MathOS/pull/74), [PR #75](https://github.com/tltmgnt/MathOS/pull/75), [PR #76](https://github.com/tltmgnt/MathOS/pull/76).

**No new Millennium solution, global Hilbert space, global spectrum, or formal proof is claimed.**
