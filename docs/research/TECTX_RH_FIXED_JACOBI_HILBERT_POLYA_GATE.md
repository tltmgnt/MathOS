# ResearchOS / TECT-X — fixed arithmetic Jacobi operator and Hilbert–Pólya gap

**Status:** a genuinely fixed, non-diagonal self-adjoint arithmetic operator with compact resolvent and correct leading Riemann–von Mangoldt zero-counting law, but a **rigorous mismatch with the first Riemann zero**. **Not a Hilbert–Pólya realization or proof of RH.** No new mathematical theorem or independent expert review is claimed.

## 1. The candidate, specified without zero data

Define the known main-term function

```text
F(T)=T/(2π)*(log(T/(2π))-1),  T>2πe.
```

It is strictly increasing from zero to infinity. Let `a_n=F^{-1}(n)`, for positive integers `n`. Let `Λ(m)` be the von Mangoldt prime-power function, `Λ(p^k)=log p`, zero otherwise. Fix the off-diagonal weights

```text
b_n = (1/5)*Λ(n+1)/(1+log(n+2)),   n>=1;  b_0=0.
```

Since `0<=Λ(n+1)<=log(n+1)<1+log(n+2)`, we have `0<=b_n<1/5`.

On `ℓ²(N>=1)` define a *fixed* Jacobi operator, independent of the spectral variable:

```text
(H x)_n = a_n x_n + b_(n-1) x_(n-1) + b_n x_(n+1),
D(H) = { x in ℓ² : Σ_n a_n² |x_n|² < ∞ }.
```

The coupling is genuinely off-diagonal and arithmetically indexed by prime powers. The diagonal is deliberately engineered using the **already known** Riemann–von Mangoldt main term; this is a limitation, not an unexplained discovery.

## 2. Rigorous operator properties

The maximal real diagonal operator `H0=diag(a_n)` is self-adjoint. Since `a_n→∞`, its resolvent is compact.

Let `B=H-H0`, with weights `b_n`. As a sum of a weighted right shift and its adjoint, `B` is bounded and self-adjoint. Each shift has norm at most `sup_n |b_n|<1/5`; therefore `||B||<=2/5`. The bounded perturbation theorem makes `H=H0+B` self-adjoint on the explicit domain `D(H0)`. Bounded perturbations preserve compact resolvent by the resolvent identity.

Thus `H` has real, discrete eigenvalues of finite multiplicity accumulating only at positive infinity. If `μ_n` denotes its eigenvalues in nondecreasing order, min–max gives

```text
a_n - 2/5 <= μ_n <= a_n + 2/5.
```

## 3. Weyl law: correct count is only a necessary condition

Writing `N_H(T)` for the number of eigenvalues less than `T`, with multiplicities, min–max yields

```text
N_0(T-2/5) <= N_H(T) <= N_0(T+2/5).
```

For `T` sufficiently large, `N_0(T)=floor(F(T))` (up to endpoint conventions), because `F(a_n)=n`. Since `F'(T)=log(T/(2π))/(2π)`, a bounded argument shift changes `F(T)` by `O(log T)`. Hence

```text
N_H(T)=F(T)+O(log T)
     = T/(2π)*log(T/(2π)) - T/(2π) + O(log T).
```

This agrees with the **known Riemann–von Mangoldt zero-counting asymptotic**, without proving any correspondence of zeros. It is not sufficient evidence for a Hilbert–Pólya construction.

## 4. An explicit, unconditional spectral failure

The first eigenvalue obeys the rigorous bound

```text
μ_1 >= a_1 - 2/5 > 2πe-2/5 ≈ 16.679.
```

The first positive nontrivial zeta-zero ordinate is independently known to be approximately `14.134725`. Thus the spectrum of `H` omits that ordinate entirely, and cannot equal the positive imaginary parts of the zeta zeros, with multiplicities. The first-zero fact is a **standard external result**; this MathOS module does not re-prove it.

This is an explicit counterexample to the unsupported claim

```text
fixed self-adjoint + nontrivial prime-power couplings + RH Weyl law
   ==> all-zero spectral identity.
```

It does not rule out another, less engineered arithmetic operator satisfying the identity.

## 5. Determinant and trace requirements remain open

A fixed self-adjoint operator is now available, but no noncircular identity with the completed xi function has been derived. Its spectrum is demonstrably wrong.

For a real spectral parameter `z` outside the spectrum, the resolvent exists. One may construct regularized spectral determinants using compact-resolvent and eigenvalue estimates, but **any** determinant with zeros at this operator's eigenvalues necessarily fails to match the completed xi zero set, already at the first ordinate. Analytic prefactors that are nowhere zero cannot fix that.

A genuine Hilbert–Pólya program needs an operator *independently determined by arithmetic* plus a complete identity for **every** nontrivial zeta zero, including possible off-line zeros and multiplicities. Since a fixed self-adjoint operator has real spectrum, a properly established mapping `ρ ↦ Im ρ` must also prove that `Re ρ=1/2`; matching imaginary parts alone is not enough, since off-line zeros can share an ordinate.

The global theta rank-one determinant construction in PR #70, by contrast, represents the entire zero divisor but its operator depends on `s`. Neither construction closes the full missing bridge.

## 6. Reproduce

```bash
python -m unittest discover -s tests -p 'test_riemann_fixed_jacobi.py' -v
python -m mathos.research.riemann_fixed_jacobi \
  --count 256 --output artifacts/riemann/fixed_jacobi.json
```

The executable builds finite Jacobi blocks and obtains finite-matrix eigenvalue counts through floating-point Sturm LDL recursion. A bounded-perturbation bracket is checked against the diagonal model. This is **numerical regression**, not a formally certified eigenvalue enclosure; the self-adjointness, compact resolvent, min–max inequalities and mismatch are independent analytic arguments recorded above.

The operator's first eigenvalue bound does not rely on numerical Sturm iterations.

## 7. TGA and ResearchOS / TECT-X obligations

| Registered obligation | Status | Evidence |
|---|---|---|
| `RH.operator` | OPEN | Fixed self-adjoint arithmetic *candidate*, but provably wrong spectrum |
| `RH.zero_identity` | OPEN | No valid xi/trace identity; first eigenvalue mismatch |
| `BRIDGE.RH.spectral` | OPEN | No proof that all nontrivial zeros lie on the critical line |
| Fixed candidate's self-adjointness | Analytically established | Bounded perturbation theorem |
| Fixed candidate's counting asymptotic | Analytically established | Min–max and known `F` |
| Independent review, novelty or Clay acceptance | NOT ESTABLISHED | Requires separate qualified external work |

## References

- [Clay Mathematics Institute: Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/)
- [Riemann–von Mangoldt zero counting](https://openmaths.org/courses/AG-LTF/support/NT-ZETA--NT-ZETA-10.html)
- [First zero ordinate (classical source)](https://assets.cambridge.org/97811070/28838/excerpt/9781107028838_excerpt.pdf)
- [Earlier MathOS arithmetic diagonal negative control](TECTX_RH_ARITHMETIC_SPECTRAL_TRACE.md)
- [Global theta rank-one xi determinant, PR #70](https://github.com/tltmgnt/MathOS/pull/70)

**Scientific integrity:** this candidate is deliberately a *negative control*. Neither CI nor graph entailment can promote it to a new RH solution. The intended achievement is to demonstrate, with a genuine fixed non-diagonal self-adjoint arithmetic operator, that numerical density matching and arithmetic coefficients still do not supply the missing zero-correspondence theorem.
