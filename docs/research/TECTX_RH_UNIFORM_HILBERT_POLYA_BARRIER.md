# ResearchOS / TECT-X — Uniform bounded perturbation barrier for Hilbert–Pólya

**Outcome:** a mathematically specified *family-wide exclusion criterion*, rather than another attempt to claim RH. For a particular fixed diagonal model engineered from the Riemann–von Mangoldt main term, **every bounded self-adjoint perturbation with operator norm at most 14/5** fails an essential all-zero correspondence. This result is conditional only on standard spectral theory and the externally established first nontrivial zeta-zero ordinate. No new proof of RH or independent publication novelty is claimed.

## Why a new route is necessary

A valid Hilbert–Pólya argument needs much more than any single true statement about operator self-adjointness, prime couplings, density, or a parameter-dependent Fredholm determinant:

1. Define a *fixed* arithmetic self-adjoint operator independently from the Riemann zeros.
2. Independently derive a global trace/distribution or determinant formula whose zero divisor is the complete multiset of nontrivial zeros, *not merely* their imaginary parts and not only zeros on the critical line.
3. Specify the spectral variable so self-adjointness constrains the real parts of those zeros, including a proof that possible off-critical-line zeros are not discarded.
4. Prove equality of analytic multiplicities, gamma/archimedean factors, pole subtraction, trivial-zero cancellation, and normalization without asserting the global correspondence as an assumption.
5. Confirm the operator is not a post hoc inverse spectral construction from a known zeta-zero table or completed xi function.

As of this investigation, those conditions have **not** been derived for MathOS operators; mathematical research still considers such a construction open. Formal claims of an RH solution in preprints must not be treated as accepted mathematical theorems without verification. For example, recent work on Weil-form finite matrices states the spectral convergence and positivity research questions without closing the entire Hilbert–Pólya program.

## A uniform spectral exclusion theorem

Put

```
F(T)=(T/(2π))(log(T/(2π))-1), T>2πe.
```

For each integer `n>=1`, let `a_n` be the unique root `F(a_n)=n` with `a_n>2πe`. Let `H0=diag(a_1,a_2,...)` on `ℓ²(N>=1)` with maximal diagonal domain. Its eigenvalues tend to infinity, so `H0` is self-adjoint with compact resolvent.

Let `B` be **any** bounded self-adjoint operator with `||B||<=14/5`. The perturbation can be nonlocal, finite-rank, infinite-rank, prime-weighted, or otherwise arithmetic, provided the operator norm bound holds. Define

```
H=H0+B, D(H)=D(H0).
```

By the bounded self-adjoint perturbation theorem, `H` is self-adjoint and has compact resolvent. The quadratic-form bound `B>=-||B|| I` yields

```
inf sigma(H)>=a_1-||B||>2πe-14/5.
```

Use the rigorous elementary inequalities

```
π > 157/50 = 3.14,
e > 271/100 = 2.71.
```

Then

```
2πe-14/5 > 2*(157/50)*(271/100)-14/5
            = 14.2188...
            > 707/50 = 14.14.
```

The first positive nontrivial Riemann zeta-zero ordinate `γ_1` is externally established to satisfy `γ_1<14.14`. Consequently,

```
**inf sigma(H) > 14.14 > γ_1.**
```

In particular the point `γ_1` is not in the spectrum of any operator in this entire class. No operator from this family can realize the full positive zeta-zero ordinates with multiplicities. The result is unconditional with respect to RH itself: the first *on-line* zero is known regardless of other hypothetical off-line zeros.

The same min–max estimate gives `|μ_n-a_n|<=14/5`, and hence the asymptotic counting law

```
N_H(T) = F(T)+O(log T).
```

Thus even **self-adjoint + compact resolvent + arbitrary bounded arithmetic perturbation + correct known Riemann zero-counting asymptotic** cannot establish the demanded correspondence within this model family.

### Spectral determinant consequence

Every `H` in the family is strictly positive, and its eigenvalues grow as `2πn/log n`. Therefore `H^(-2)` is trace class, so

```
D_H(z)=det(I-z² H^(-2))
```

is an even entire function with zeros at `±μ_n`, with multiplicities. Because `D_H(γ_1) != 0` and `ξ(1/2+iγ_1)=0`, there is **no entire, zero-free** `E(z)` for which

```
ξ(1/2+iz)=E(z) D_H(z)
```

for every complex `z`.

This conclusion covers arbitrary bounded perturbations under the same budget, not merely the prime-weighted Jacobi candidate in PR #71.

## Numerical and proof boundary

The Python program reports the exact rational inequality using `fractions.Fraction`, not floating-point guesses. It invokes a helper from the existing MathOS finite arithmetic spectral model only to produce **finite numerical regression diagnostics**. The mathematical bound holds for the whole infinite operator class and follows from the separately stated min–max argument. The first zeta ordinate bound `γ_1<14.14` is a preexisting mathematical fact cited from the literature; the program does not independently certify its existence.

Reproduce:

```bash
python -m unittest discover -s tests -p 'test_riemann_uniform_hp_barrier.py' -v
python -m mathos.research.riemann_uniform_hp_barrier \
  --budget-numerator 14 --budget-denominator 5 --sample-size 128 \
  --output artifacts/riemann/uniform_hp_barrier.json
```

## What this does NOT exclude

The result does not rule out Hilbert–Pólya generally. The operator `H0` is artificial and designed from an existing zero-counting law. The exclusion applies **only** to `H0+B` with the specified bound. It says nothing about more distant bounded perturbations, unbounded arithmetic perturbations, different Hamiltonians, de Branges/canonical-system models, Weil positivity constructions, or nonlocal constructions with genuinely different domains.

A successful global correspondence theorem would effectively prove RH; merely naming such a theorem as a dependency, or checking finitely many matrices, cannot substitute for its proof.

## ResearchOS / TECT-X recommendation

Rather than continuing to fit this excluded spectral family, pursue the independent **Weil positivity / arithmetic trace** approach with a prespecified test-function space and exact archimedean/prime-power distribution. A positive Hilbert-space construction must be proved for the **entire admissible class**, with a no-circularity argument and strong spectral convergence/absence of pollution, before claiming a global zeta-zero interpretation. Finite prime-built Gram matrices, even if positive for hundreds of samples, cannot certify all-index positivity or RH.

The present implementation acts as an *automated rejection gate* for a broad false lead, while keeping canonical RH claims in `NOT_CERTIFIED` state.

## References

- [Clay Mathematics Institute: Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/)
- [NIST Digital Library of Mathematical Functions: zeta zeros](https://dlmf.nist.gov/25.10)
- [LMFDB nontrivial zeta-zero reference](https://www.lmfdb.org/zeros/zeta/)
- [Construction of Finite Hilbert–Pólya Matrices from Weil's Explicit Formula (2026 preprint)](https://arxiv.org/abs/2609.04908)
- [Weil's quadratic form via the screw function (2026)](https://arxiv.org/abs/2606.09096)
- [MathOS fixed Jacobi candidate PR #71](https://github.com/tltmgnt/MathOS/pull/71)
- [MathOS global trace identity gate PR #72](https://github.com/tltmgnt/MathOS/pull/72)

**Status:** no RH proof, no genuinely new zero-correspondence theorem, no independent external mathematical review. The precise family-wide exclusion is a testable negative result with explicit assumptions and proof.
