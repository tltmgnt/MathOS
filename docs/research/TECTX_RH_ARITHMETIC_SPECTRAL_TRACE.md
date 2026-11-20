# ResearchOS / TECT-X: arithmetic operator with Riemann zero-counting density

**Status:** research construction and falsification, not a proof of the Riemann hypothesis.  
**Claim:** a precise, self-adjoint arithmetic diagonal operator can reproduce the entire *known Riemann–von Mangoldt counting asymptotic including its O(log T) error scale*, yet fail even the first spectral-zero comparison. An exact prime-power **toy heat-trace formula** follows but is not the Riemann explicit formula. No novelty, full zero correspondence or external independent review is claimed.

## 1. Independent specification

Let `F(T) = (T/(2π))(log(T/(2π))-1)` for `T>2πe`. Since `F'(T)=(1/(2π))log(T/(2π))>0`, it maps `(2πe,∞)` bijectively onto `(0,∞)`. For every integer `n>=1`, define `a_n=F^{-1}(n)` independently of any zero list, equivalently `a_n=2π n/W_0(n/e)`, with `W_0` the positive principal Lambert-W branch.

Let `Λ(n)=log p` when `n=p^k`, `k>=1`, and zero otherwise. Let `δ_n = Λ(n)/(1+log(n+1))`, so `0<=δ_n<1`.

For each `0<=ε<=1`, define `H_ε` on `ℓ²(N>=1)` by

```
(H_ε x)_n = λ_n(ε) x_n,
λ_n(ε) = a_n + ε δ_n,
D(H_ε) = {x ∈ ℓ² : Σ λ_n(ε)^2 |x_n|² < ∞}.
```

This multiplication operator is self-adjoint: its diagonal entries are real and its domain is maximal. As `a_n → ∞`, the resolvent is compact; the spectrum comprises positive eigenvalues of finite multiplicity, counted with repetition. This is an artificial *engineered* arithmetic operator, not a naturally derived quantization of the primes or zeta zeros.

## 2. Proposition: correct Riemann–von Mangoldt density is not sufficient

For `T>=a_1`, `N_0(T)=floor(F(T))`, by monotonicity and `F(a_n)=n`. Because `0<=εδ_n<1`, termwise comparison gives

```
N_0(T-1) <= N_ε(T) <= N_0(T).
```

For large `T`, the mean-value theorem yields

```
F(T)-F(T-1) = O(log T)
```

since `F'(T)=log(T/(2π))/(2π)`. Therefore

```
N_ε(T)=F(T)+O(log T).
```

The independently established Riemann–von Mangoldt theorem says that the number of nontrivial Riemann zeta zeros with ordinates `0<Im ρ<=T`, counted with multiplicity and without assuming RH, is

```
N_ζ(T)=F(T)+O(log T).
```

Consequently `N_ε(T)-N_ζ(T)=O(log T)` for every `ε ∈ [0,1]`. This matches **the known error order**, not the point spectrum or the exact counting function.

**Immediate obstruction:** `a_1>2πe≈17.079` but the first nontrivial zeta-zero ordinate is `γ_1≈14.134725`. Since `δ_1=Λ(1)=0` and `δ_n>=0`, **none of these operators has an eigenvalue at γ_1**. Thus `σ_p(H_ε)` cannot equal the multiset of positive zeta-zero ordinates. The external first-zero tabulation is an input, not computed by this package.

## 3. A genuinely arithmetic but insufficient trace identity

For `t>0` the heat operator `e^{-tH_ε}` is trace class. Indeed `a_n` grows as `2πn/log n` and in particular at least on the order of `sqrt n`; thus `Σ exp(-t a_n)<∞`.

The following identity follows *directly from the definitions*, not from the zeta function:

```
Tr(e^{-tH_ε}) - Tr(e^{-tH_0})
  = Σ_{p prime} Σ_{k>=1} e^{-t a_(p^k)}
      [exp(-t ε log p/(1+log(p^k+1))) - 1].
```

Absolute convergence follows by comparison with `Σ exp(-t a_n)`. Each summand is nonpositive for `ε>0`, and the `p=2,k=1` contribution is strictly negative; hence the trace difference is strictly negative for all `t>0, ε>0`.

**This is a prime-power heat-trace identity, but not the classical Riemann explicit formula.** Its weights, frequencies, and test-function dependence are induced by our artificial definition of `H_ε`. Rewriting a perturbation as a sum over prime powers cannot establish any equality to a trace constructed from zeta zeros.

For comparison, for any `ε` one can form an even entire product

```
D_ε(z)=∏_{n>=1} (1-z²/λ_n(ε)²),
```

whose local uniform convergence follows from `λ_n ~ 2π n/log n` and `Σ λ_n^{-2}<∞`. This determinant-like product has zeros **by construction** at the real points `±λ_n(ε)`, not at zeta ordinates. In particular the first-ordinate mismatch prevents any identity

```
ξ(1/2+iz)=E(z) D_ε(z)
```

with `E` entire and zero-free. The left side is zero at `z=γ_1`, and the right side is not. Even allowing non-zero-free correction factors would require fully specifying and proving the new factors; an unverified correction is precisely the missing theorem.

## 4. Falsification and TGA outcome

This investigation produces a **specific counterexample to the inference**:

```
self-adjoint + arithmetic prime-power structure + correct T log T counting
⇒ nontrivial zeta zero spectral correspondence.
```

The antecedents hold for `H_1`; the consequent fails for the first ordinate. Thus no argument using only those three premises can yield RH. A valid Hilbert–Pólya route requires substantially stronger, independently derived arithmetic spectral data and a noncircular global identity accounting for all zeros and multiplicities.

| Existing MathOS obligation | Result |
|---|---|
| `RH.operator` | Remains OPEN; explicit self-adjoint *toy* operators constructed, but none realizes the required spectrum |
| `RH.zero_identity` | Remains OPEN; this candidate has a refuted zero correspondence |
| `BRIDGE.RH.spectral` | Remains OPEN; no global RH implication |
| Density-matching subexperiment | Analytic derivation documented; finite regression tests only |
| Prime heat-trace identity | Elementary exact derivation for toy operator; not a Riemann explicit formula |
| Independent mathematical review | Not performed |

## 5. Reproduction

From the MathOS checkout:

```bash
python -m unittest discover -s tests -p 'test_riemann_arithmetic_spectral.py' -v
python -m mathos.research.riemann_arithmetic_spectral \
  --max-index 2048 --epsilon 1 \
  --output artifacts/riemann/arithmetic_spectral.json
```

The script computes the inverse main term by deterministic floating-point bisection, prime-power weights by integer factorization, bounded spectral counts, and a truncated prime-power heat-trace comparison. The mathematical statements above rely on explicit analytic arguments **and known external theorems**; the generated float64 report is not a computer-assisted proof or independently certified zeta-zero list.

## 6. Next genuinely open research problem

Construct an operator with a domain and arithmetic dynamics determined *without* target zeta-zero data such that a trace, resolvent, transfer operator or determinant reproduces the **correct explicit formula, including prime-power weights and archimedean terms**, in an admissible test-function space. Prove normalizations, analytic continuation, error/tail control and all zero multiplicities. Only after that derive a noncircular full zero correspondence and subject it to independent mathematical review.

This work is a **negative control** useful for eliminating density-based false proofs, not a claim of mathematical novelty or a solution of the Riemann hypothesis.

### References

- [Clay Mathematics Institute RH problem](https://www.claymath.org/millennium/riemann-hypothesis/)
- [Riemann–von Mangoldt zero-counting formula](https://mathworld.wolfram.com/Riemann-vonMangoldtFormula.html)
- [LMFDB tabulated nontrivial zeta zeros](https://www.lmfdb.org/zeros/zeta/)
- [Berry–Keating operator discussions](https://link.springer.com/article/10.1007/s11785-026-01990-w)

No original claim of having established the classical zero-counting theorem, analytic continuation of zeta, or the Riemann explicit formula is made.
