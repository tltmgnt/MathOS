# TECT-X — Primary LF-dense compact Weil core workflow

**Status:** The RH-relevant test-function strategy is now represented by executable research workflow code. The fixed-width translated lattice remains a **comparison** and is not promoted to a domain-dense core. This PR computes exact rational convolution supports and exhaustive arithmetic prime-power inventories for a nested sequence of finite prefixes of a countable compact-bump core. **It does not compute all full Weil entries, certify a new positive Gram, or prove RH.**

## 1. Replace the non-dense lattice with the admissible core

The disjoint translates `phi(8(x-3j/4))` from PR #89 have an exact diagonal ordinary-L² Gram for all dimensions, but the permanent gap `(1/8,5/8)` prevents their span from being dense even in ordinary L², much less the LF topology of `D(R)=C_c^infinity(R)`. See PR #91.

The correct primary research core, introduced analytically in PR #83, consists of all normalized smooth compact bumps

```text
b_(n,r)(x) = 2^n phi(2^n(x-r)),
  n>=1, r=p/q in Q, gcd(|p|,q)=1, q>=1,
phi(x)=C^-1 exp(-1/(1-x²)) if |x|<1, else 0.
```

Enumerate by increasing integer height `n+|p|+q`, with stable tie breaking by `n,q,p`. This lists an explicit **countably infinite** set whose span has an analytic proof of density in the *canonical LF topology* of smooth compactly supported tests, using mollification, rational-grid Riemann sums, and common-compact derivative convergence.

**Important logical distinction:** each finite prefix is a finite-dimensional vector space, hence not LF-dense. A fixed test function need not lie in *any* finite prefix; LF density means finite linear combinations can approximate it in the test topology. No code asserts otherwise. The density theorem is a separately documented mathematical argument, not established by enumerating finitely many bumps.

## 2. Exact upper-triangle support and prime-power inventory

For any first-prefix functions `b_i,b_j`, write their exact rational support endpoints as `[a_i,b_i]` and `[a_j,b_j]`. The convolution in the *actual* Weil criterion

```text
h_ij=b_i * tilde(b_j),
tilde(b_j)(x)=conjugate(b_j(-x))
```

is supported in

```text
[a_i-b_j, b_i-a_j].
```

The additive-log arithmetic Weil formula samples `h_ij` at `±log(p^k)`. For a support bound `B=max(|left|,|right|)`, the *rigorous* finite cap

```text
p^k <= exp(B) <= 3^ceil(B)
```

follows from `e<3`. The code enumerates all integers up to that cap, identifies exactly those which are powers of a single prime, and decides whether `±log(p^k)` lies inside the rational support. It uses the exact convergent rational atanh series, with explicitly bounded geometric remainder:

```text
log n = k log 2 + 2 sum_(j>=0) t^(2j+1)/(2j+1),
n=2^k y, 1<=y<2, t=(y-1)/(y+1)<=1/3.
```

An entry is rejected as **inconclusive** if 64 rational terms cannot decide whether a prime logarithm crosses an endpoint. This avoids fragile floating-point inclusion/exclusion decisions. To bound runtime, the module rejects support ranges requiring a cap above 10,000; that is an audit resource limit, **not a mathematical restriction of the underlying family**.

The returned JSON contains **every pair** in the first `m`-prefix upper triangle, its exact rational convolution support and its complete set of potential nonzero von Mangoldt prime-power terms. The lists are nested: the first `k×k` entries are unchanged when the prefix expands.

**The inventory is not the Weil matrix.** The pole moments, prime-convolution sample values and full regularized archimedean terms have not yet been evaluated for this family. The code explicitly reports `actual_Weil_entry_enclosed=false` and `full_Gram_PSD_certified=false`.

## 3. Proof-decision topology and assurance

The executable report invokes the proof-decision engine from PR #90 with two separate evidence claims:

- The LF-density and continuity *analytic arguments* from PR #83, with the exact canonical test domain and a countable dense core.
- An **interval-verification-stage finite arithmetic support inventory** for a specified prefix, with no complete Weil matrix entries and no positivity theorem.

It is a false promotion to infer global positivity from either property alone. The global Weil criterion requires positive semidefiniteness of **every** finite Gram for the dense core, with the correct distributional normalization and continuity bridge. That universal theorem remains RH-equivalent and open.

The previous fixed lattice is retained as a **comparison** with `span_LF_dense=false`, despite its perfectly conditioned ordinary L² Gram. Its finite positive certificates remain valid only for the specified spans, not transferred to the new core.

## 4. Workflow and reproducibility

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_lf_dense_core_workflow.py' -v

python -m mathos.research.riemann_weil_lf_dense_core_workflow \
  --prefix 8 \
  --output artifacts/riemann/tectx_weil_lf_dense_core_workflow.json
```

The module supports up to 24 requested functions, but safely **rejects** finite prefixes whose exhaustive prime-support inventory would exceed the configured cap. The default is 10.

Adversarial tests validate exact support reflection, nesting, upper-triangle completeness, known prime powers for `[-1,1]` and `[-2,2]`, fail-closed invalid ranges, deliberate nonpromotion of LF density from finite lists, and correct separation from the lattice that PR #91 proved non-dense.

## 5. Next substantive mathematical requirement

Build directed interval enclosures for the actual Weil entries

```text
G_ij = W(b_i * tilde(b_j))
```

on the newly selected LF-dense core, including all finite prime-power values, pole moments, regularized infinite archimedean integrals and their exact analytic tails. Then certify a finite Schur complement or rigorous lower bound for successive prefixes. **Even an arbitrarily large list of passing finite tests is not an all-index theorem.** A uniform argument covering all finite prefixes, in the correct domain, remains the RH-equivalent missing result.

This is an implementation of a **domain-correct research control workflow**, not a claim of full Weil positivity, positive Weil Hilbert completion, or a solution to RH.

## Related MathOS results

- [PR #83 — Countable canonical Weil test-domain dense core](https://github.com/tltmgnt/MathOS/pull/83)
- [PR #90 — Proof-decision topology and nonpromotion control](https://github.com/tltmgnt/MathOS/pull/90)
- [PR #91 — Lattice non-density and fifth arithmetic window](https://github.com/tltmgnt/MathOS/pull/91)
- [PR #89 — Fixed four-dimensional arithmetic Weil Gram](https://github.com/tltmgnt/MathOS/pull/89)
