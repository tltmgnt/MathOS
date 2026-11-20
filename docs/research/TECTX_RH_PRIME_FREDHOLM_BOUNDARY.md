# ResearchOS / TECT-X — prime Fredholm determinant and global Riemann spectral boundary

**Research status:** mathematically rigorous operator/determinant identity for **Re(s)>1 only**; NOT an all-zero trace formula, NOT a Hilbert–Pólya operator, NOT a solution of RH, and not claimed as novel. This work records an honest noncircular arithmetic starting point and the exact point at which it fails the requested global scope.

## 1. Construction from primes (no zeta-zero inputs)

Let `P` be the rational primes and define the Hilbert space `H = ℓ²(P)` with orthonormal basis `e_p`. For each `s=σ+it`, `σ>1`, define

```
A_s e_p = p^(-s) e_p.
```

The operator is defined entirely by primes and the argument `s`, not by the zeros of zeta. It is bounded and trace class because

```
||A_s||_1 = ∑_{p∈P} |p^(-s)| = ∑_p p^(-σ)
          ≤ ∑_{n=2}^∞ n^(-σ) < ∞     (σ>1).
```

For real `s>1`, `A_s` is positive and self-adjoint. For nonreal `s`, it is generally normal but **not self-adjoint**. No attempt is made to infer the reality of zeta ordinates from `A_s`.

## 2. Noncircular Fredholm determinant, proved in the Euler half-plane

Since the eigenvalues `p^(-s)` are absolutely summable, the ordinary trace-class Fredholm determinant is well-defined. It is exactly

```
det(I-A_s) = ∏_p (1-p^(-s)) = 1/ζ(s),   Re(s)>1.
```

The first equality is the trace-class diagonal determinant formula. The second is Euler's classical product, valid by absolute convergence in `Re(s)>1`. Both formulas require **no** knowledge of zeta zeros. In particular the determinant is nonzero in this half-plane.

For all `k>=1`,

```
Tr(A_s^k) = ∑_p p^(-ks).
```

Since the prime-power series converges absolutely and locally uniformly in `Re(s)>1`, one may differentiate the logarithm:

```
(d/ds) log det(I-A_s)
    = ∑_p ∑_{k>=1} (log p) p^(-ks)
    = ∑_{n>=1} Λ(n)n^(-s)
    = -ζ'(s)/ζ(s).
```

This is an **exact prime-side arithmetic trace identity**, not the Riemann explicit formula that also involves the complete nontrivial zero set, pole, gamma factors, and admissible test functions.

## 3. Rigorous boundary: why this does not solve the problem

For `0<σ<=1`, the unregularized diagonal operator has

```
∑_p |p^(-s)| = ∑_p p^(-σ) = ∞.
```

For `σ=1`, this is Euler's divergence of the prime harmonic series; for `σ<1`, termwise `p^(-σ)>=p^(-1)`. Therefore the `A_s` family as given is **not trace class anywhere in the nontrivial-zero strip**.

The analytic/meromorphic continuation of the scalar function `1/ζ(s)` is established by the classical theory; it does **not** construct a continuation of this particular operator as a trace-class family, nor justify retaining the ordinary Fredholm determinant formula there. In fact, in the strip the reciprocal zeta function is meromorphic at any nontrivial zeta zero, whereas ordinary analytic Fredholm determinants of trace-class holomorphic operator families are holomorphic. A global formulation requires substantively new operator theory or a carefully justified regularized/meromorphic construction.

Furthermore `1/ζ` has **poles** at nontrivial zeta zeros, not zeros. An ordinary Fredholm determinant `det(I-A_s)` cannot be claimed to have its zero set equal to the zeta zeros merely because it equals `1/ζ(s)` for `Re(s)>1`. Proving a global identity involving completed `ξ(s)` and all multiplicities remains open.

A different trace-class or regularized operator family might still exist. This result rules out only the **naive unregularized prime-diagonal continuation** and false proof promotion from the Euler region.

## 4. Verified finite controls

The accompanying Python module generates the finite prime truncations

```
A_(s,P)=diag(p^(-s) : p<=P, p prime),
D_(s,P)=∏_(p<=P)(1-p^(-s)),
Tr(A_(s,P)^k)=∑_(p<=P)p^(-ks).
```

On the real axis `σ>1`, there is a conservative explicit Euler-product tail bound

```
0 <= log ζ(σ) + log D_(σ,P)
   <= P^(1-σ)/[(σ-1)(1-(P+1)^(-σ))].
```

Proof: `-log(1-p^(-σ))<=p^(-σ)/(1-p^(-σ))`; bound the omitted primes by integers `n>P` and their tail integral. Since `p>=P+1`, the denominator bound follows. This is an analytic inequality; finite tests check representative values, not all parameters.

Reproduce from the repository root:

```bash
python -m unittest discover -s tests -p 'test_riemann_prime_fredholm.py' -v
python -m mathos.research.riemann_prime_fredholm \
  --sigma 2 --height 0 --prime-bound 1000 --depth 5 \
  --output artifacts/riemann/prime_fredholm.json
```

**Caveat:** the script uses float64 complex arithmetic and principal numerical logarithms for the *finite* formulas. The reported bound applies to real `s` only. It does not independently certify an infinite-dimensional operator or provide validated interval arithmetic. The infinite identities above are justified analytically, not by the finite outputs.

## 5. TGA outcome and next-stage requirements

| Registered MathOS obligation | New evidence | Status |
|---|---|---|
| `RH.operator` | Explicit prime-diagonal trace-class family on `Re(s)>1` | OPEN: not a global self-adjoint Hilbert–Pólya operator |
| `RH.zero_identity` | `det(I-A_s)=1/ζ(s)` on `Re(s)>1` | OPEN: no all-zero correspondence; reciprocal has poles at zeros |
| `BRIDGE.RH.spectral` | Explicit trace-class boundary `Re(s)>1` | OPEN: no RH implication |
| Prime-trace identity | All power traces and log derivative proved in Euler half-plane | Scope complete within half-plane |
| Independent external review | Not performed | OPEN |

Any subsequent construction must satisfy **all** of the following:

1. Define an arithmetic operator family without inputting the nontrivial zeros or assuming RH.
2. Define operator domains, functional-analytic topology and a valid trace/regularization across the critical strip.
3. Derive the archimedean gamma factor, pole/trivial-zero handling and the Weil explicit formula with specified test-function classes.
4. Prove a noncircular identity whose divisor includes *every* nontrivial zero with multiplicity and distinguishes off-critical-line cases, not merely leading-order counting or finite ordinates.
5. To infer RH, additionally prove a spectral reality statement from actual self-adjointness (or another sound mechanism) and justify the spectral mapping.
6. Supply independent formal and mathematical review; maintain `NOT_CERTIFIED` until then.

## References

- [Clay Mathematics Institute — Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/)
- [DLMF, NIST — Riemann zeta zeros](https://dlmf.nist.gov/25.10)
- [Riemann zeta, Euler product](https://dlmf.nist.gov/25.2)
- [Riemann xi function](https://mathworld.wolfram.com/Xi-Function.html)
- [MathOS RH proof-route register](../research/CLAY_PROOF_ROUTES.v1.json)
- [Previous arithmetic spectral density negative control](TECTX_RH_ARITHMETIC_SPECTRAL_TRACE.md)

**Research statement:** This is a mathematically specified partial construction with an explicit failure boundary. It neither supplies nor claims the requested global theorem.
