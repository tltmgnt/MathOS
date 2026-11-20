# ResearchOS / TECT-X — Riemann spectral route: fixed dilation obstruction

**Research status:** known mathematical obstruction, independently reproducible *toy-model* counting computations, **NOT_CERTIFIED**, **NO_RH_PROOF**, no claim of new mathematical discovery. The mathematical argument below is elementary/standard and invokes the known Riemann–von Mangoldt formula. Its scope is the *unmodified dilation generator* and its *fixed logarithmic compactification*, not every Hilbert–Pólya program.

## Registered target and routing

The official Riemann hypothesis asserts that every nontrivial zero `rho` of the analytically continued Riemann zeta function satisfies `Re(rho)=1/2`. A spectral approach must specify the actual Hilbert space, an operator with a justified self-adjoint domain, and an identity that relates **every zero, including all multiplicities and possible off-line zeros**, to its real spectrum without assuming RH.

The MathOS proof-route registry `docs/research/CLAY_PROOF_ROUTES.v1.json` records `RH.spectral` with obligations `RH.operator`, `RH.zero_identity` and `BRIDGE.RH.spectral`. None is closed by this investigation. The TGA machinery locates these modeled gaps; it does not prove the authored route sufficient. TECT-X supplies a falsifiable spectral-model check; the million zeta/TDA variant experiment does **not** supply a zero-operator identity.

## Proposition A — the free dilation operator has no point spectrum

On `L²((0,∞), dx)` define the symmetric differential expression

```text
H = -i (x d/dx + 1/2).
```

Set `y=log x` and `(Uf)(y)=e^{y/2}f(e^y)`. The substitution `dx=e^y dy` gives

```text
∫_R |Uf(y)|² dy = ∫_0^∞ |f(x)|² dx.
```

Thus `U` extends to a unitary map onto `L²(R,dy)`. A direct differentiation calculation on test functions yields

```text
U H U⁻¹ = -i d/dy.
```

The self-adjoint momentum realization with domain `H¹(R)` has spectrum all real numbers, purely absolutely continuous, and **empty point spectrum** (Fourier transformation is a standard justification). In particular, no nonzero square-integrable eigenfunction exists for any real eigenvalue. A supposed eigenfunction `g(y)=C exp(i λ y)` has constant modulus and fails to be in `L²(R)` unless `C=0`.

**Conclusion:** the bare dilation generator on the full positive half-line is not an operator whose point spectrum consists of Riemann-zero ordinates. This does not rule out generalized eigenstates, resonance constructions, arithmetic perturbations or alternative Hilbert spaces.

## Proposition B — fixed logarithmic compactification has the wrong density

Restrict the transformed momentum operator to a **fixed** interval `[0,L]`, `L>0`, with domain

```text
{g in H¹([0,L]) : g(L)=exp(2πi α)g(0)},   0 ≤ α < 1.
```

These quasiperiodic boundary conditions give a standard self-adjoint realization. Solving the eigenvalue equation exactly produces

```text
λ_n = (2π/L)(n+α),   n ∈ Z.
```

There is exactly one eigenvalue per normalized interval of width 1. Counting positive eigenvalues `0 < λ ≤ T`, with fixed `L, α`, gives

```text
N_H(T) = (L/(2π))T + O(1).
```

By the established Riemann–von Mangoldt theorem, the number of nontrivial zeta zeros with positive imaginary parts at most `T`, **counting multiplicity**, satisfies

```text
N_ζ(T) = (T/(2π)) log(T/(2π)) - T/(2π) + O(log T).
```

Dividing by `T log T` and taking `T → ∞` produces

```text
lim N_H(T)/(T log T) = 0,
lim N_ζ(T)/(T log T) = 1/(2π).
```

Consequently the positive point spectrum of **this fixed compactification** cannot coincide, counting multiplicities, with the full multiset of positive nontrivial zeta-zero ordinates. This conclusion is unconditional with respect to RH because the zero-counting formula is known independently of RH.

**Not covered:** variable-length boundaries, energy-dependent truncations, infinite graph constructions, arithmetic operators, scattering poles, spectral determinants with justified corrections, or any more general Hilbert–Pólya proposal. A matching leading count would in any case be necessary but far from sufficient for a zero correspondence.

## Executable, exact arithmetic

```bash
python -m unittest discover -s tests -p 'test_riemann_spectral_obstruction.py' -v
python -m mathos.research.riemann_spectral_obstruction \
  --max-radius 12 --phase-numerator 1 --phase-denominator 2 \
  --output artifacts/riemann/spectral_obstruction.json
```

The checker counts `0 < n+α ≤ R` using Python `Fraction` and exact integer division, where `R=TL/(2π)`. The code does **not** approximate π or the Riemann zeta function. It verifies only fixed-period spectral counts at specified rational normalized thresholds. It reports the spectral/asymptotic comparison as a **mathematical argument relying on external theorems**, not as a computation-derived proof. Every output retains `riemann_hypothesis_proved=false` and `spectral_route_closed=false`.

## TGA gap outcome

| Registered obligation | Status after this investigation | Reason |
|---|---|---|
| `RH.operator` | OPEN | A precise self-adjoint *toy* operator is studied, but the bare/compactified examples lack the requisite spectrum |
| `RH.zero_identity` | OPEN | No arithmetic spectral determinant or exact bijection to all zeta zeros is obtained |
| `BRIDGE.RH.spectral` | OPEN | No theorem derives the official RH target from a correctly justified global correspondence |
| Adversarial model audit | BOUNDED PASS if CI passes | Exact finite unit-interval counts and known analytic density mismatch |

The strongest next candidate test is **not** fitting the first million zeros: it is specifying a noncircular, arithmetic operator and deriving its full counting law, self-adjoint domain, trace/explicit formula, and zero correspondence. For any operator with a discrete spectrum, prevent spectral pollution and ensure all nontrivial zeros (including possible off-line zeros) are accounted for. Keep the zero-correspondence claim separate from the density claim.

## Sources

- [Clay: Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/)
- [Riemann–von Mangoldt zero counting](https://mathworld.wolfram.com/Riemann-vonMangoldtFormula.html)
- [Analytic number theory lecture notes (zero-counting theorem)](https://www2.math.uu.se/~ast10761/analtalt23/lecture_notes.pdf)
- [On the Berry–Keating operator (2026)](https://link.springer.com/article/10.1007/s11785-026-01990-w)
- [Berry–Keating operator on the positive half-line and quantum graphs](https://cris.technion.ac.il/en/publications/the-berry-keating-operator-on-lsup2suprsubgtsub-dx-and-on-compact/)

**Review boundary:** The exact arithmetic tests and the analytic derivation are different evidence classes. A specialist should review the operator domains, spectral counting convention, theorem citations and translation to official RH scope before using this packet in a research manuscript. No independent external review has been performed by committing this file.
