# ResearchOS / TECT-X — Certified fourth Weil direction and real arithmetic Schur block

**Result sought:** extend the exact Weil arithmetic quadratic form from its previously certified three-dimensional Gaussian-cosine span to a **genuinely new fourth direction**, with all cross terms, gamma and prime-power corrections, and a verified L²-relative Schur complement.

**Certification scope:** the fixed four-dimensional subspace only. The computation relies on mathematically derived remainder bounds and pinned `mpmath.iv` outward arithmetic. It is not an independent formal proof, a dimension-independent positivity estimate, the full Weil Hilbert space or an RH proof.

## 1. Actual, independently specified fourth test function

Use the **fixed** Gaussian test functions

```
q_c(t)=exp(-t²/100)*cos(c*t),
c in (0,1/5,1/2,21/5).
```

The new direction `q_(21/5)` is a genuine fourth test function, not a synthetic positive block or a function interpolated from zeta-zero data. The actual Weil arithmetic Gram is

```
G_ij = W(q_(c_i)*q_(c_j)),
```

with the classical explicit-formula prescription

```
W(h) = h(i/2)+h(-i/2)
       -log(pi)*hhat(0)/(2*pi)
       +integral_R h(t)*Re digamma(1/4+i*t/2)dt/(2*pi)
       -sum_(n>=2) Lambda(n)*n^(-1/2)*hhat(log n)/pi.
```

All nontrivial zeros, including off-line possibilities, occur on the **other side** of the classical formula; none are supplied to the computation.

The old 3×3 block is imported unchanged from the previous certified calculation, and the four genuinely new entries `G_(0,3),G_(1,3),G_(2,3),G_(3,3)` are computed independently from the arithmetic formula.

## 2. Expanded, rigorous prime-power tail for larger Fourier shifts

The Fourier transform of `h_ij(t)=exp(-a*t²)cos(c_i*t)cos(c_j*t)` with `a=1/50` is

```
hhat_ij(u)=sqrt(pi/a)/4 * sum_(epsilon,eta=±1)
             exp(-(u-epsilon*c_i-eta*c_j)²/(4a)).
```

Since the centers lie in `[0,21/5]`, every Fourier shift has magnitude at most

```
C=42/5 = 8.4.
```

The code explicitly includes **every prime power up to 65536** by enumerating primes and their powers. The remaining tail is bounded without any unproved prime-number estimates.

Because `e<3`, the cutoff satisfies `65536>3^10>e^10`. Hence `u=log n>=10` for every omitted index. Applying `Lambda(n)<=log n` and the Gaussian Fourier envelope gives

```
|P(h_ij)-P_65536(h_ij)|
 <= (1/sqrt(pi*a)) *
    integral_10^infinity u*exp(u/2-(u-C)²/(4a))du.
```

With `m=C+a`, `beta=(10-m)/(2a)=79/2`, `X=(10-m)²/(4a)=6241/200`, completion of the square and a tangent bound yield

```
delta4 =
  1280*(10/beta+1/beta²)/(1+X/128)^128.
```

The bounds `1/sqrt(pi*a)<5` and
`exp(C/2+a/4)<exp(5)<3^5<256`
give the rational prefactor 1280. The inequality
`exp(-X)<=(1+X/128)^(-128)`
holds for every positive `X`. The code evaluates this in exact `Fraction` arithmetic; the conservative `delta4` is about `2.43×10^-10`. It bounds **all** omitted prime powers, not merely omitted primes, for every entry of the enlarged matrix.

## 3. Verified archimedean integral for the new center

The digamma term uses the classical Binet expansion and shifted recurrence at `64+1/4+it/2`. The center expression and analytic remainder satisfy

```
|R| <= 1/(252*(64+1/4)^6).
```

The integral on `[0,45]` is approximated by composite Simpson quadrature with a mathematically bounded fourth derivative. For each entry, put `D=c_i+c_j`. For the Gaussian factor `E=e^(-at²)` and `0<=t<=45`, the `k<=4` derivatives have the rational majorants

```
gamma=(1, v, v²+2a, v³+6av, v⁴+12av²+12a²),
v=2a*45.
```

The cosine-product `k`th derivative is bounded by `D^k`. The real digamma derivatives admit the previously proved uniform bounds

```
g=(16,10,36,208,1632).
```

Leibniz's rule provides the explicit center-dependent rational majorant

```
H_k(D)=sum_(j=0)^k binom(k,j)*gamma_j*D^(k-j),
M4(D)=sum_(j=0)^4 binom(4,j)*H_j(D)*g_(4-j).
```

The implementation uses the exact rational `M4(D)` for **each new entry**, rather than applying a small-center derivative bound outside its domain. The archimedean Simpson error is then enclosed by

```
(45/180)*(45/N)^4*M4(D)/pi, N=65536.
```

This is combined with the digamma remainder, an analytic Gaussian tail beyond 45, and `delta4`, with all finite arithmetic performed in directed interval mode. The existing 3×3 entries retain their tighter independent enclosures from the predecessor.

## 4. Intrinsic generalized eigenvalue and actual new-direction Schur test

Let `L` be the separately evaluated ordinary Gaussian `L²` Gram for **all four** functions,

```
L_ij=sqrt(pi/a)/2 * [exp(-(c_i-c_j)²/(4a))
                    +exp(-(c_i+c_j)²/(4a))].
```

The previously certified three-dimensional generalized lower bound does not survive the fourth direction. For the four-dimensional positivity test use the smaller candidate bound

```
kappa=1/1,000,000,000.
```

The target is positive definiteness of the full **actual** matrix

```
M=G-kappa*L.
```

Partition `M=[A B;B^T C]` with old `A` the certified three-dimensional subspace and new scalar `C` its arithmetic fourth direction. Calculate the **actual** interval Schur complement

```
S=C-B^T A^(-1)B.
```

The program verifies the old block `A\succ0` by interval `LDL^T`, but **does not form an unstable interval inverse**. Instead, it uses a rational witness `x\in\mathbb Q^3` and the exact residual identity

```text
r = b-A*x,
S = C - 2*b^T*x + x^T*A*x - r^T*A^(-1)*r.
```

If `A\succeq\alpha I` with `\alpha>0`, then, with rigorous outward interval evaluation of `C-2b^Tx+x^TAx` and each component of `r`,

```text
lower(core) - upper(||r||_2²)/alpha
    <= S <= upper(core).
```

The old 3×3 certified bound `G_3\succ10^-6I` (PR #78), the independent positive `L_3`, and the Gaussian estimate `trace(L_3)<45` establish `A\succ(10^-6-45*kappa)I`. The program **rechecks** the old `G_3-10^-6 I` interval LDL pivots and `L_3` diagonal upper bounds rather than assuming the spectral floor numerically.

The rational approximate solution is only a candidate witness; the final conclusion uses the verified residual and analytic old-block lower bound. This avoids interval dependency blow-up when the old matrix is ill-conditioned. Certification is accepted **only if every old and new pivot has a strictly positive lower bound**. Independently checking all four pivots of `M` and of `L` helps detect implementation inconsistencies. The same interval arithmetic also computes the **new-direction Schur complement at the old three-dimensional constant `1/50,000,000`** and requires its entire enclosure to lie **strictly below zero**. Thus the old constant provably fails for this enlarged span, while the reduced four-dimensional constant is separately accepted only if the new Schur pivot is positive.

If this succeeds, the exact finite-dimensional conclusion is

```
W(q_v²) > (1/1,000,000,000) * ||q_v||_(L²(R))²
```

for every nonzero real vector in this particular four-dimensional span. This strictly weaker four-dimensional bound is **not** claimed to be uniform across arbitrary future directions. The drop from the three-dimensional bound is part of the research result, not an implementation regression.

## 5. Reproduce

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_certified_fourth.py' -v
python -m mathos.research.riemann_weil_certified_fourth \
  --panels 65536 --output artifacts/riemann/weil_certified_fourth.json
```

The certificate contains interval entries of the full 4×4 Weil and reference L² matrices, all new entry error components, the exact rational new prime tail, and positive LDL and Schur pivots for the reduced lower bound, plus a **negative** Schur interval for the previous three-dimensional constant. It retains explicit false flags for dimension five and above, global positivity, the Weil Hilbert completion and RH.

**Warning:** A successful local numerical or CI run is not an independent formal verification of the analytic estimates. Those estimates are part of the mathematical proof obligation and must be reviewed separately.

## 6. Limits and the genuine infinite-dimensional research task

This is an *actual fourth arithmetic direction*, unlike synthetic Schur examples. Yet certification of a fixed fourth direction, even with a meaningful L² reference norm, does not imply that **every** future direction passes the Schur test.

The next step would require a theorem, not mere enumeration of successful instances: an all-directions lower bound or nonnegative form estimate on a specified dense test domain, a topology allowing continuity or closability, and a justified passage to the whole Weil form. Global positivity remains RH-equivalent, and an unconditional Weil-positive Hilbert-space completion remains unavailable.

Related code: [3D verified Gram (PR #78)](https://github.com/tltmgnt/MathOS/pull/78), [L² generalized Schur (PR #80)](https://github.com/tltmgnt/MathOS/pull/80), [prime-tail error (PR #75)](https://github.com/tltmgnt/MathOS/pull/75), and the [Weil Hilbert-space work of Suzuki](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6).

**Assurance:** no proof of RH, no dimension-independent global Weil coercivity, no mathematical novelty claim, and no independent expert review.
