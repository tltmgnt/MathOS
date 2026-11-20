# ResearchOS / TECT-X — Growing Weil spans, a dimension-free tail and a coercivity obstruction

**Result classification:** two elementary, rigorously justified structural statements about the **actual arithmetic Weil form** restricted to Gaussian–cosine tests. These are useful negative and positive *boundaries*, but neither supplies the requested RH-equivalent global positivity theorem. No full Weil Hilbert space, unconditional self-adjoint zeta operator, or RH proof is claimed.

## 1. Why increasing Gram dimensions does not establish a uniform spectral gap

Let `q_c(t)=exp(-t²/100)cos(ct)`, with `c∈[0,1/2]`. The Weil-form Gram on a finite tuple of centers `c_1,...,c_m` is

```text
G_jk = W(q_(c_j) q_(c_k)),
Q(v) = v^T G v = W((sum_j v_j q_(c_j))²),   v real.
```

The classical Weil distribution acts continuously on this Gaussian test family: each term of the explicit formula is continuous in the centers, the digamma integral has a common Gaussian majorant, and the Gaussian Fourier transform provides a uniform super-exponentially decaying prime-power majorant. This does **not** assume RH or require zero ordinates as input.

**Proposition (no positive uniform coefficient-space gap).** There is no `kappa>0` satisfying

```text
G_m >= kappa I_m
```

for *all* finite center tuples of *all* dimensions, even restricting to **pairwise distinct centers**.

*Proof.* Duplicate centers give `q_c-q_c=0`, so the Gram for centers `(c,c)` has zero quadratic value on the vector `(1,-1)`. For a nonduplicate example, take distinct centers

```text
c_j=1/(j+2), j=0,1,2,...
c_j-c_(j+1)=1/((j+2)(j+3)) -> 0.
```

For each adjacent pair choose the Euclidean-unit coefficient vector `v=(1,-1)/sqrt(2)`. Then

```text
v^T G_2 v = (1/2)*W((q_(c_j)-q_(c_(j+1)))²) -> 0
```

as `j->infinity`, by continuity of the Weil functional on this Gaussian family. Thus any fixed positive `kappa` is violated for large enough `j`. This proof does **not** assert that the Rayleigh quotient is positive; it only shows it tends to zero and cannot have a positive uniform lower bound. □

**Crucial norm distinction:** This obstructs **Euclidean-coefficient-norm coercivity** for unrestricted center choices, *not* an L²-, Sobolev-, distribution- or function-norm-normalized Weil bound. A nearly duplicate coefficient representation also has a small function norm. Therefore this observation does **not** disprove RH, Weil positivity, or meaningful other-norm estimates.

## 2. A genuinely dimension-independent inequality — in the coefficient L¹ norm

The proved uniform Gaussian prime-tail estimate in PR #75 gives

```text
|P(q_(c_j) q_(c_k)) - P_256(q_(c_j) q_(c_k))| <= delta
```

for **every** `c_j,c_k∈[0,1/2]`, where `delta` is an explicit positive exact rational number independent of the center tuple.

For any number `m>=1` of test functions and any real coefficients `v`, bilinearity and the triangle inequality give

```text
|P((sum_j v_j q_(c_j))²)-P_256((sum_j v_j q_(c_j))²)|
 <= sum_jk |v_j| |v_k| delta
 = delta * (sum_j |v_j|)².
```

Thus

```text
         |prime-power tail Q(v)| <= delta ||v||_1²
```

holds at **all finite dimensions with the same delta**. This is a valid dimension-independent constant in the ***coefficient L¹ norm***. The familiar coefficient L² estimate `m*delta||v||₂²` follows from Cauchy–Schwarz but is **dimension-dependent**. Neither estimate controls all the archimedean and pole contributions, nor establishes nonnegativity of the full Weil form.

The program evaluates the bound in exact Python `Fraction` arithmetic and rejects centers outside the proved parameter window.

## 3. A basis-invariant *relative* inequality, but only on the previously certified 3D span

PR #78 established (subject to the specified interval-arithmetic proof assumptions) for the exact centers `(0,1/5,1/2)`:

```text
v^T G v > (1/1,000,000)||v||₂²,  for all nonzero real v∈R³.
```

Let `L` be the **ordinary positive Gaussian L² comparison Gram**,

```text
L_jk = integral_R exp(-t²/50)cos(c_j t)cos(c_k t)dt.
```

Since `L` is positive semidefinite, and each diagonal entry satisfies

```text
L_jj <=sqrt(50*pi) < sqrt(200) <15,
```

we have `lambda_max(L) <=trace(L) <45`. Combining this with the certified result yields

```text
v^T G v > (1/50,000,000) v^T L v,
```

for every nonzero coefficient vector in **that fixed three-dimensional span**. The exact rational remaining margin is

```text
1/1,000,000 -45/50,000,000 = 1/10,000,000 >0.
```

This is invariant under a change of coordinates **within that same span** because it compares the actual Weil and L² quadratic forms on functions. It is NOT a universal coercivity estimate as dimensions or Fourier-support windows expand.

## 4. The correct conditional Hilbert-space construction

Let `V` be a specified admissible **complex** test-function vector space on which the Weil form is a well-defined Hermitian sesquilinear form `W(f,g)`. **Suppose**, without claiming a proof, that

```text
W(f,f)>=0 for EVERY f∈V.
```

Then Cauchy–Schwarz follows for the PSD form, and the null subspace `N={f∈V:W(f,f)=0}` is orthogonal to every `g∈V`. The quotient `V/N` carries the inner product `<[f],[g]>=W(f,g)`. Its completion is an honest Hilbert space.

This algebraic construction is standard and fully rigorous **conditional on global positivity**. It does not establish that hypothesis. It is a mistake to claim the Hilbert completion unconditionally merely because each member of a finite test sequence appears positive; a global PSD result must cover all finite linear combinations in the specified whole test space.

**No uniform positive spectral gap is logically required for the abstract quotient-and-completion itself.** Global semidefinite positivity is the requirement. If one wants quantitative embeddings or a fixed densely defined self-adjoint arithmetic generator, further closability, boundedness, invariance and domain theorems will be needed.

The *unconditional* L² comparison Gram does yield ordinary positive Hilbert spaces, but this is not the Weil completion and says nothing about RH.

## 5. Machine-readable verification and failure gates

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_span_stability.py' -v

python -m mathos.research.riemann_weil_span_stability \
  --centers 0,1/5,1/2 --coefficients 1,-2,3 \
  --output artifacts/riemann/weil_span_stability.json
```

The report records the exact rational L¹ prime-tail inequality, the explicit clustering sequence and gap `1/[(j+2)(j+3)]`, the conditional quotient theorem and the inherited fixed-three-span L²-relative estimate. It retains **false** for every full-Weil-positivity, global-Hilbert-space and RH certification field.

The continuity proof is an analytic dominated-convergence argument; the finite unit tests check its rational parameter sequence and the logic gates, but do **not** independently formalize or certify the Weil distribution in Lean or Arb. These are elementary deductions from the explicit formula, not new general number-theory advances.

## 6. Growing dimensions: next valid strategy

A productive next objective is an operator estimate **relative to a specified function-space norm**, rather than raw basis coefficients, with all tail, integration and conditioning constants explicit. Concrete criteria to test:

- Define nested function spaces or compact support windows and state which topology makes their union dense in the admissible Weil test space.
- Re-orthonormalize a basis in a **verified L² Gram**, then compute *generalized* Weil eigenvalues, carefully controlling change-of-basis conditioning; do not infer stability from coefficient-space eigenvalues.
- Use a block-Schur complement to control new directions and old–new couplings and maintain rigorous positivity on each enlarged subspace, with quantifiers over *all* such subspaces.
- Prove positivity across the entire dense union (not finite numerical samples), and justify continuity/closability needed to extend the quadratic form to its intended domain.
- Only after global PSD: define the Weil null quotient, Hilbert completion and a candidate arithmetic operator with a noncircular full-zero correspondence.

The literature takes precisely this distinction seriously: Suzuki's screw-function/Hilbert-space constructions and spectral-convergence studies do not simply assume unconditional global positivity for the Riemann zeta case.

## Sources

- [Suzuki, *On the Hilbert space derived from the Weil distribution*](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6)
- [Suzuki, *Weil's quadratic form via the screw function*](https://arxiv.org/abs/2606.09096)
- [Suzuki, *Spectral convergence associated with Weil's quadratic form*](https://arxiv.org/abs/2610.32704)
- [Weil positivity in compact windows: certified two-sided bounds](https://arxiv.org/abs/2608.24827)
- [MathOS certified fixed three-dimensional Gram, PR #78](https://github.com/tltmgnt/MathOS/pull/78)
- [MathOS exact prime-power tail, PR #75](https://github.com/tltmgnt/MathOS/pull/75)

**Assurance boundary:** no unconditional complete Weil Hilbert space, no dimension-independent natural-function-norm coercivity theorem, and no RH proof has been produced.
