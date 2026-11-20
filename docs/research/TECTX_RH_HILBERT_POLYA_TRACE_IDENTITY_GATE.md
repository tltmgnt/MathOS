# ResearchOS / TECT-X: global Hilbert–Pólya determinant/trace identity gate

**Scope:** a mathematically defined determinant and exact necessary trace identity for a **fixed** self-adjoint arithmetic Jacobi operator, with a definitive obstruction to global zeta-zero correspondence for this candidate. This is **not** a proof of RH, not a new Weil explicit formula, and not an independently verified new mathematical theorem.

## 1. Use the fixed, independently specified operator

The dependency `mathos.research.riemann_fixed_jacobi` defines the real, self-adjoint Jacobi operator `H` on `ℓ²(N>=1)` with

```
a_n=F^(-1)(n), F(T)=T/(2π)*(log(T/(2π))-1), T>2πe
b_n=(1/5)*Lambda(n+1)/(1+log(n+2))
(Hx)_n=a_n*x_n+b_(n-1)*x_(n-1)+b_n*x_(n+1)
```

on the maximal weighted diagonal domain. The Jacobi perturbation is bounded, symmetric and has norm at most 2/5. Standard bounded-perturbation theory and min–max imply a positive, compact-resolvent operator with ordered eigenvalues `μ_n` satisfying

```
a_n-2/5 <= μ_n <= a_n+2/5.
```

It is a genuinely fixed operator but its main diagonal has been **engineered from the already-known Riemann–von Mangoldt counting main term**. The prime-power coupling does not prove a trace/zero relation.

## 2. An entire spectral determinant that is actually defined

The asymptotic `a_n ~ 2πn/log(n)` implies `μ_n ~ 2πn/log(n)` and

```
sum_n 1/μ_n^2 < infinity.
```

Thus `H^(-2)` is trace class. Define the standard trace-class Fredholm determinant

```
D_H(z)=det(I-z^2 H^(-2))=product_(n>=1)(1-z^2/μ_n^2).
```

This is an even entire function. Its zeros are **exactly** `+μ_n` and `-μ_n`, including spectral multiplicities. As `H` is self-adjoint, all these zeros are real. The identity is valid for the explicitly defined operator, with no use of the Riemann hypothesis.

For `z` off the zeros, the trace-class resolvent identity is

```
D_H'(z)/D_H(z)=-2z*Tr((H^2-z^2 I)^(-1)).
```

This formula is global and meromorphic in `z`, with poles at the candidate's **own** spectral eigenvalues. It is not the Riemann explicit formula.

## 3. The exact prime-power and archimedean matching obligation

Write `s=1/2+i z`. On the Euler half-plane `Re(s)>1` (equivalently `Im(z)<-1/2`), logarithmic differentiation of

```
xi(s)=1/2*s(s-1)*pi^(-s/2)*Gamma(s/2)*zeta(s)
```

gives the classical identity

```
xi'(s)/xi(s)
  =1/s+1/(s-1)-(log pi)/2+(1/2)*digamma(s/2)
     -sum_(n>=1)Lambda(n)n^(-s).
```

This combines the pole factors, gamma/archimedean term, and *all* prime powers via the von Mangoldt function. It requires `Re(s)>1` for absolute convergence of the prime-power series. Its meromorphic continuation in `s` is known from classical analytic number theory; the prime series itself does not converge in the critical strip.

**Conditional zero-free factor criterion:** A fixed self-adjoint Hilbert–Pólya realization would require, for an independently specified entire nowhere-zero function `E(z)`,

```
xi(1/2+i z)=E(z) D_H(z),             every z in C.
```

Logarithmic differentiation in the Euler half-plane yields the **necessary** prime/archimedean trace equation

```
i[1/s+1/(s-1)-(log pi)/2+(1/2)digamma(s/2)
     -sum_(n>=1)Lambda(n)n^(-s)]
    = E'(z)/E(z) -2z Tr((H^2-z^2 I)^(-1)).
```

This is a specification of what would have to be *proved* and checked, not an established trace equality for this operator. Defining `E=xi/D_H` merely as a quotient in a zero-free region is not an independent proof that it extends to an entire zero-free function. Nor does imposing a trace equation on a test region solve the global divisor problem without analytic and normalization arguments.

If the factorization were established globally with `E` nowhere zero, `xi` and `D_H` would have the same zeros with analytic multiplicities. Since `D_H` has only real `z`-zeros, this would force every nontrivial zeta zero onto the critical line. **That would prove RH, so it cannot be assumed.**

## 4. Rigorous falsification for the actual fixed Jacobi candidate

The lowest possible spectral point of `H` satisfies

```
inf spectrum(H) >= a_1 - 2/5 > 2πe - 2/5 > 16.67.
```

The first tabulated positive ordinate `γ1≈14.1347251417` of a nontrivial zero of `ζ` is a **classical external mathematical fact**. Since `γ1 < inf spectrum(H)`, the entire spectral determinant obeys

```
D_H(γ1) > 0.
```

But `xi(1/2+iγ1)=0`. It follows that **no entire nowhere-zero factor `E` can satisfy `xi(1/2+i z)=E(z)D_H(z)` for all `z`.** This is a precise failed requirement, rather than an inconclusive numeric fit.

Even if an operator happened to share the positive ordinates of the zeros, an argument must also rule out off-critical-line zeros. Matching ordinates alone is insufficient; the factorization criterion genuinely includes both real and hypothetical nonreal `z` with their analytic multiplicities.

## 5. Reproducible tests (numeric diagnostics only)

```bash
python -m unittest discover -s tests -p 'test_riemann_fixed_jacobi.py' -v
python -m unittest discover -s tests -p 'test_riemann_trace_identity_gate.py' -v
python -m mathos.research.riemann_trace_identity_gate \
  --size 256 --output artifacts/riemann/trace_identity_gate.json
```

The program uses positive-definite finite-section LDL factorizations to report

```
D_N(z)=det(H_N-zI)*det(H_N+zI)/det(H_N)^2
```

at several real `z` values strictly below the certified infinite spectral floor. This is the **exact algebraic definition of the finite-section determinant**, numerically approximated in floating point. It does not provide a certified infinite determinant value or a zero-finding theorem. The min–max spectral floor is an analytic statement independent of the finite computation.

A finite Dirichlet prefix `sum_(n<=4096) Lambda(n)n^(-2)` is computed only as a reproducible arithmetic check. It is **not** promoted to the full prime trace, and the gamma/digamma identity is a mathematical obligation rather than a numerically fitted match.

## 6. What remains open

- Construct an arithmetic, **fixed self-adjoint** operator whose spectrum is actually related to the Riemann zeros, rather than reverse engineering its mean density.
- Derive a normalized prime/archimedean trace formula **from the operator**, not by defining the correction as `xi/D_H` or importing the target zero set.
- Control test functions, gamma terms, poles, analytic continuation, convergence, and multiplicities across the entire critical strip.
- Establish and independently review a global zero-free entire factorization or another theorem that proves **every** nontrivial zero corresponds to a real spectral parameter.
- Keep `RH.operator`, `RH.zero_identity`, and `BRIDGE.RH.spectral` open until those are actually established.

## Sources

- [NIST DLMF zeta zeros and xi-function material](https://dlmf.nist.gov/25.10)
- [Riemann–von Mangoldt counting law](https://mathworld.wolfram.com/Riemann-vonMangoldtFormula.html)
- [LMFDB zero table](https://www.lmfdb.org/zeros/zeta/)
- [Regularized Fredholm determinants background](https://doi.org/10.1098/rspa.2014.0597)
- [Fixed arithmetic Jacobi candidate PR #71](https://github.com/tltmgnt/MathOS/pull/71)

**No research breakthrough or independent external validation is claimed.** The value of this integration is a precise, global determinant-and-trace criterion plus a mathematically decisive failed-instance report.
