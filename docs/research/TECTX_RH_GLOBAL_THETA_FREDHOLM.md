# ResearchOS / TECT-X — Global theta-derived Fredholm determinant for the completed xi function

**Status:** an explicit, entire, rank-one trace-class operator family with a **global** determinant identity capturing the *divisor* of all nontrivial Riemann zeta zeros. The construction is a reformulation of the **classical theta integral**, not a novel Hilbert–Pólya operator, a proof of the Riemann hypothesis, or a new explanation for the zeros' location.

## 1. Explicit construction without feeding in zero locations

For real `x>=1`, let

```
psi(x) = sum_{n>=1} exp(-pi*n^2*x).
I(s)   = integral_1^infinity psi(x) [x^(s/2-1)+x^(-(s+1)/2)] dx.
b(s)   = s(s-1)/2.
```

The theta-series `psi(x)` converges rapidly and exponentially. For every compact subset of complex `s`, the integrand and all its derivatives in `s` are bounded by an integrable polynomial factor times `exp(-pi*x)`. Therefore `I(s)` is **entire** and satisfies `I(1-s)=I(s)`.

Let `H=L²([1,infinity),dx)` and define a fixed vector and a holomorphic vector:

```
v(x)   = exp(-(x-1)),
u_s(x) = exp(-(x-1)) - b(s) exp(x-1) psi(x)
            * [x^(s/2-1) + x^(-(s+1)/2)].
```

Both are in `H`, since `exp(x-1)psi(x)` decays as `exp(-(pi-1)x)`. As `s` varies over a compact complex set, `u_s` depends holomorphically in the Hilbert norm. Define an explicitly **parameter-dependent** rank-one operator

```
(K_s f)(x) = u_s(x) * integral_1^infinity v(y)f(y) dy.
```

This linear map is bounded and trace class for **every** `s in C`, not just the right half-plane. It has rank at most one and trace `Tr K_s = integral v(x)u_s(x)dx`. It does not use the zeta zeros as input.

## 2. Full Fredholm determinant, with derivation

The constant term in the trace is

```
integral_1^infinity exp(-2(x-1)) dx = 1/2.
```

Hence

```
Tr(K_s) = 1/2 - b(s)I(s)
det(I-K_s) = 1-Tr(K_s)
           = 1/2 + (s(s-1)/2)I(s).            (A)
```

Riemann's classical theta argument, starting from the Mellin representation for `Re(s)>1` and Jacobi's theta modular identity, gives

```
pi^(-s/2) Gamma(s/2) zeta(s)
   = 1/[s(s-1)] + I(s),                      (B)
```

where equality is meromorphically continued by the explicit entire `I(s)`. Multiplying (B) by `s(s-1)/2` yields exactly

```
xi(s) := 1/2*s(s-1)*pi^(-s/2)*Gamma(s/2)*zeta(s)
       = 1/2 + (s(s-1)/2)I(s).
```

Together with (A) this proves the **global operator identity**

```
                 det(I-K_s) = xi(s),       EVERY s in C.
```

This is not obtained by asserting that the old Euler-product operator continues; it constructs a **different rank-one operator** directly from the theta series. Nevertheless, it is only a Fredholm *repackaging of an already known analytic identity*. It does **not** independently derive new information about zero locations.

## 3. Gamma factor, poles, trivial zeros and all nontrivial zeros

The normalization includes the `pi^(-s/2)Gamma(s/2)` archimedean factor and `s(s-1)/2` factor. The modular-theta derivation explicitly isolates the `1/[s(s-1)]` polar term; multiplication by `s(s-1)` removes the apparent poles at `s=0,1`. In particular

```
det(I-K_0)=det(I-K_1)=xi(0)=xi(1)=1/2.
```

At negative even integers, the classical zeta trivial zeros cancel the corresponding gamma poles in the completed product, and the theta expression is finite. No additional spurious trivial zeros are introduced by this determinant. It is an entire function with exactly the nontrivial zeta zero divisor.

The equality is between entire functions, so **every** nontrivial zero is represented, whether on or off `Re(s)=1/2`, and with exactly its analytic order of vanishing. More precisely, at a zero `s_0`, `1` is an eigenvalue of the *parameter-dependent* operator `K_(s_0)`; the order of the determinant's zero at `s_0` equals the zero multiplicity of `xi`. It must **not** be confused with the geometric multiplicity of that rank-one eigenvalue, which is at most one.

The symmetry `I(1-s)=I(s)`, `b(1-s)=b(s)` gives the stronger family identity `K_(1-s)=K_s` and consequently `xi(1-s)=xi(s)`. Complex conjugation also yields the usual reality symmetry.

## 4. Why this is not Hilbert–Pólya and does NOT prove RH

The crucial difference from a Hilbert–Pólya spectral solution is:

**K_s is a family depending analytically on the complex number s. It is not a fixed self-adjoint operator whose real eigenvalues are the ordinates of the nontrivial zeros.**

The condition `det(I-K_s)=0` says `1` belongs to the spectrum of `K_s` at that particular parameter. This has no implication that `Re(s)=1/2`.

Indeed, the construction reproduces an off-line zero just as faithfully as an on-line zero. Its success at zero *correspondence* is logically **orthogonal** to the unsolved zero-*location* theorem.

The rank-one approach also generalizes to nearly any prescribed entire scalar function by selecting a suitable parameter-dependent vector. Therefore **the determinant identity alone is not a discriminating arithmetic spectral mechanism**. The nontrivial arithmetic content here is the known modular-theta identity, not a newfound operator-theoretic constraint.

The next truly difficult objective is a **fixed, independently specified self-adjoint operator**, plus an independently justified spectral/trace correspondence, where self-adjointness actually forces the appropriate real spectral parameter. This theta family does not supply that.

## 5. Reproduction and numerical scope

```bash
python -m unittest discover -s tests -p 'test_riemann_theta_fredholm.py' -v
python -m mathos.research.riemann_theta_fredholm \
  --panels 4096 --xmax 12 --theta-terms 8 \
  --output artifacts/riemann/theta_fredholm_xi.json
```

The code approximates the integral via composite Simpson quadrature, with finite `x` and theta-series cutoffs. It tests `xi(0)=xi(1)=1/2`, `xi(2)=pi/6`, the functional equation, generic off-critical-line parameters, and proximity to an externally tabulated first zero. The mathematical identity is analytic and infinite-dimensional; the **finite floating-point quadrature is not a certified computation of any zero or multiplicity**. No machine-verified analytic theorem or independent peer review is claimed merely from CI.

## 6. Research status and proof-obligation map

| Obligation | What this construction provides | Status |
|---|---|---|
| Explicit arithmetic operator | Entire rank-one trace-class family from the integer theta series | Established analytically, **not** fixed self-adjoint |
| Global determinant | `det(I-K_s)=xi(s)` by standard theta-Mellin identity | Established analytically, no claim of novelty |
| Gamma/poles/trivial-zero cancellations | Built into classical xi normalization | Accounted for |
| All nontrivial zeros, multiplicities, hypothetical off-line zeros | Equal analytic zero divisor of determinant and xi | Accounted for **tautologically** by determinant identity |
| Noncircular arithmetic spectral mechanism forcing RH | Not supplied | OPEN |
| Genuine fixed self-adjoint Hilbert–Pólya operator | Not supplied | OPEN |
| Independent review and new theorem | Not supplied | OPEN |

Do **not** mark `RH.operator`, `RH.zero_identity`, or `BRIDGE.RH.spectral` solved merely because the scalar divisor is reproduced. The registered **spectral route** demands an operator whose spectrum imposes the critical-line condition, not an unconstrained holomorphic determinant family. The existing MathOS proof registers remain unchanged.

## References

- [NIST DLMF §25.5 — zeta integral and theta representations](https://dlmf.nist.gov/25.5)
- [University of Toronto lecture notes — Riemann zeta functional equation via theta](https://www.utsc.utoronto.ca/people/kupers/wp-content/uploads/sites/50/2020/12/complex-analysis-2019.pdf)
- [Riemann xi-function definition and analytic continuation](https://mathworld.wolfram.com/Xi-Function.html)
- [MathOS prime Fredholm half-plane research](TECTX_RH_PRIME_FREDHOLM_BOUNDARY.md)

**Novelty and certification:** no new analytic number theory theorem, proof of RH, globally self-adjoint spectral representation, or outside expert certification is claimed. This exercise meets the literal global determinant/divisor requirement by a known, deliberately non-Hilbert–Pólya construction, illustrating why further structural requirements are indispensable.
