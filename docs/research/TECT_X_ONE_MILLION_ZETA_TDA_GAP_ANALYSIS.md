# ResearchOS / TECT-X — One Million Zeta Variants and TDA Gap Analysis

**Date:** 2026-11-19  
**Status:** `BOUNDED_NUMERICAL_TOPOLOGICAL_AUDIT_NOT_CERTIFIED`  
**Arithmetic breakthrough claimed:** **No**  
**Input:** Four explicit families, 250,000 mathematically distinct functions each.

## Motivating video: AI, brute force, and mathematical insight

The user-provided screenshot identifies Superintelligence's 21 March 2026 YouTube short, [*AI & Math: Solving Riemann Hypothesis by Brute Force? #shorts*](https://www.youtube.com/watch?v=M7eQUHH-oWI). Its visible description asks whether computation alone can resolve the Riemann hypothesis or whether insight is necessary. This is **motivation**, not an evidentiary claim about actual zeta zeros or the video's spoken arguments. We did not review a full transcript.

This experiment provides one bounded test of that distinction: one million **function descriptions and feature measurements** do not constitute one million zero proofs; selected numerical TDA clusters need invariant descriptors before they can support analytic conclusions. The [video-reference and proof-gap protocol](TECT_X_VIDEO_REFERENCE_AI_RH_BRUTE_FORCE.md) records the source, method, counterchecks, and strict no-certification policy.

## Executive finding

A deterministic computation of **1,000,000 distinct zeta functions** across four mathematically specified families was run successfully. It establishes three useful but **largely known** connections, plus a serious topological-identifiability warning:

1. For unweighted cycles `C_n`, the Laplacian spectral zeta special values and the Ihara graph zeta both determine `n`. This is an exact connection between two genuinely different zeta constructions on the *same underlying graph*.
2. The rescaled cycle spectral zeta values converge to the Riemann zeta values `2ζ(2)` and `2ζ(4)` with **closed-form finite-n errors**. The Riemann zeta is itself the Hurwitz zeta anchor `ζ(s,1)`.
3. On `C_n`, the Ihara graph zeta coincides with the Artin–Mazur dynamical zeta of the nonbacktracking edge shift consisting of two oriented `n`-cycles.
4. Deliberately choosing *parameter-dependent probes* `u_n=exp(-τ/n)` makes all 250,000 distinct cycle Ihara functions return **exactly the same two observed values**. An apparent TDA cluster can thus be a measurement alias, not an intrinsic identity.

The sampled Vietoris–Rips feature clouds have no degree-one homology at the seven declared thresholds. A same-sized circle control exhibits a degree-one cycle, while a line control does not. **Only 128 feature points per family** underwent this degree-one TDA computation; the full 1,000,000 variants were evaluated for scalar features, with full-cloud 0D connectivity scales calculated from an O(N) monotone-chain formula. This work does not evaluate *any* nontrivial zero of the Riemann zeta function or prove any Riemann-hypothesis or BSD claim.

## Experimental registry — exactly 1,000,000 distinct functions

For each of the four families below, `i=0,...,249999`. The compressed CSV contains every variant identifier, exact parameter where applicable, and the two declared numeric features. Unlike random polynomial perturbations, these are genuine named zeta-function constructions.

| Family | Count | Mathematical definition | Measured feature pair | Why all functions are distinct |
|---|---:|---|---|---|
| Hurwitz | 250,000 | `ζ(s,a_i)`, `a_i=1+(i+1/2)/250000` | `ζ(2,a_i)`, `ζ(3,a_i)` | `ζ(2,a)` strictly decreases with `a>0` |
| Finite spectral zeta | 250,000 | `Z_{Δ,C_n}(s)=Σ_{j=1}^{n-1}(4sin²(πj/n))^{-s}`, `n=i+3` | `log Z(1)`, `log Z(2)` | `Z(1)=(n²−1)/12` strictly increases |
| Ihara graph zeta | 250,000 | `Z_{C_n}(u)=(1-u^n)^{-2}`, `n=i+3` | `log Z(e^{-1/n})`, `log Z(e^{-2/n})` | First positive-degree term of `Z−1` occurs at degree `n` |
| Artin–Mazur full shift | 250,000 | `ζ_k(u)=(1-ku)^{-1}`, `k=i+2` symbols | `log(k)`, `log(k²)` from period-1, period-2 counts | Different poles at `u=1/k` |

**Notes on classification:** The four families do **not** have a shared zero locus, functional equation, Euler product, topological domain, or standardized filtration. The sampled features have different mathematical meanings; an arbitrary cross-family Euclidean metric would not be invariant under a change of normalization. The number `1,000,000` is a registry count, not a statistical sample of one million independent conjectures.

## Exact analytic bridges, not inferred from clustering

### Spectral zeta ↔ Riemann/Hurwitz zeta

For the unweighted cycle graph `C_n`, the Laplacian has eigenvalues `λ_j=4sin²(πj/n)`, `1≤j<n`. The standard finite trigonometric identities give

\[
Z_{\Delta,C_n}(1)=\frac{n^2-1}{12},\qquad
Z_{\Delta,C_n}(2)=\frac{n^4+10n^2-11}{720}.
\]

Therefore, using the classical `ζ(2)=π²/6` and `ζ(4)=π⁴/90`, one gets **exactly**

\[
\left(\frac{2\pi}{n}\right)^2 Z_{\Delta,C_n}(1)
=2\zeta(2)\left(1-\frac1{n^2}\right),
\]

\[
\left(\frac{2\pi}{n}\right)^4 Z_{\Delta,C_n}(2)
=2\zeta(4)\left(1+\frac{10}{n^2}-\frac{11}{n^4}\right).
\]

As `n→∞`, the left sides tend to `2ζ(2)` and `2ζ(4)`. The Riemann zeta is also `ζ(s,1)` in the Hurwitz family. This is an **established special-value relationship**, not a discovery from the experiment, and involves **positive integer spectral exponents, not critical-strip zeros**.

### Graph zeta ↔ dynamical periodic-orbit zeta

For an undirected simple cycle `C_n`, reduced nonbacktracking edge trajectories form two oriented primitive cycles of length `n`. The dynamical Artin–Mazur zeta of this finite edge shift equals

\[
\zeta_{\rm NB,C_n}(u)=(1-u^n)^{-2}=Z_{C_n}(u),
\]

which is the Ihara zeta of the cycle. This is a **different dynamical model** from the `k`-symbol full shifts included in the numerical registry.

### Graph topology ↔ zeta descriptors

The graph-theoretic first Betti number `β₁(C_n)=|E|-|V|+1=1` for every `n≥3`. In contrast, the descriptor point cloud formed by the 250,000 *different cycle spectral zeta functions* is an arc-like monotone curve; its sampled Vietoris–Rips Betti-1 is zero at the declared radii. These are **not the same topological spaces**. A persistent cycle in graph data is not automatically a persistent cycle in the space of graph-zeta descriptors, and the converse is false without a theorem.

## Executed topological data analysis

- CSV features: **1,000,000** variants, 2 scalar features per variant, double precision.
- Full-cloud H0: connectivity death scales from consecutive-neighbor MST on *coordinatewise-monotone* curves (250,000 each for Hurwitz, spectral, full shift). Ihara probes collapse to 1 unique location.
- H0/H1: explicit F₂ 2-skeleton boundary-rank computations for **128 subsampled points per family**, at radii `0.03, 0.06, 0.12, 0.18, 0.25, 0.40, 0.55` after independent min–max scaling *within each family*.
- Calibrations: 128 evenly spaced points on a Euclidean circle (positive H1 control), and a 128-point straight line (negative H1 control).

| Point cloud | Distinct sample coordinates | β₀ at radius 0.12 | β₁ at radius 0.12 | β₁ detected at any tested radius |
|---|---:|---:|---:|---|
| Hurwitz | 128 | 1 | 0 | No |
| Cycle spectral | 128 | 2 | 0 | No |
| Cycle Ihara, adapted probes | **1** | 1 | 0 | No |
| Full-shift dynamical | 128 | 2 | 0 | No |
| Circle control | 128 | 1 | **1** | **Yes** |
| Line control | 128 | 1 | 0 | No |

All values above are read from the generated report, not asserted as general mathematical theorems about arbitrary zeta families. Lack of a detected H1 on an embedding does **not** imply that the corresponding analytic function has no nontrivial zeros. The cycle Ihara row is a deliberate stress test of *non-identifying observables*.

**Permutation sensitivity check:** At fixed radius `0.12` and 128 points, 12 deterministic random permutations of the *second feature coordinate* (breaking the mathematical correspondence between coordinates) produced spurious Betti-1 cycles in **12/12 Hurwitz** permutations, **2/12 cycle spectral** permutations and **2/12 full-shift** permutations. The original, correctly paired data had Betti-1 equal to zero at that radius. This is a diagnostic warning against treating loops caused by feature misalignment, scaling, sampling, or numerical pipelines as intrinsic number-theoretic topology. It is not a statistical hypothesis test over independently sampled zeta functions.

## Gap analysis (TECT-X)

| Research bridge / claim | Evidence now | Missing step | Priority |
|---|---|---|---|
| Hurwitz ↔ Riemann | Exact `ζ(s,1)=ζ(s)` | None for this identity; no zero-location theorem follows | Baseline |
| Cycle spectral ↔ Riemann | Exact special-value and large-n formulas | A defensible operator/zero-spectrum correspondence if extending to critical-strip zeros | High |
| Ihara ↔ nonbacktracking dynamics | Exact finite cycle identity | Generalize to nontrivial graphs with correct determinants and hypotheses | Medium |
| Cycle graph H1 ↔ zeta-feature H1 | Known graph H1, measured sample feature H1 | Functorial map or stability theorem transferring specified topological invariants | High |
| Million-variant data → mathematical universality | Counted and reproducibly sampled finite registry | External validation, invariant feature definition, sampling invariance, error bounds | High |
| TDA of zeta special values → zeros | **Not established** | Analytic argument relating persistence to zero locations and multiplicities | Critical |
| Zeta/TDA → RH | **Not established** | Genuine all-zero critical-line proof or equivalent all-index certificate | Critical |
| Zeta/TDA → BSD / Selmer | **Not established** | Explicit elliptic-curve L-functions and a valid analytic-to-algebraic rank bridge | Critical |

The earlier MathOS RH synthetic Li-prefix countermodel (`docs/research/MILLENNIUM_ATTACK_005.md`) warns that even a long finite sequence of apparently positive Li-style sums can coexist with artificial off-line zeros. This experiment does not repair that logical gap.

## Reproducible outputs and limitations

Files:
- `mathos/research/tect_x_zeta_tda_1m.py` — deterministic generator, exact family descriptions, H0 closed-form MST, GF(2) Betti checks, JSON/CSV export.
- `tect_x_zeta_tda_1m_report.json` — thresholds, Betti numbers, controls, normalization, source definitions and SHA-256.
- `tect_x_zeta_tda_1m_dataset.csv.gz` — **all one million rows**, feature values only, ~17 MB compressed.

Command:

```bash
python tect_x_zeta_tda_1m.py --per-family 250000 --sample-size 128 \
  --report tect_x_zeta_tda_1m_report.json \
  --dataset tect_x_zeta_tda_1m_dataset.csv.gz
```

**Reproducibility caveats:** The CSV compression header is fixed for reproducibility; floating-point values can differ slightly with SciPy versions. Feature data have not been certified with interval arithmetic, and the sampled TDA is conditional on the chosen numerical threshold graph. There is no million-point H1 persistence diagram, no zero search and no statistical significance test of a population effect. The use of standard named zeta families is for research benchmarking, not a mathematical novelty claim.

## Public context

- NIST DLMF, [Hurwitz zeta](https://dlmf.nist.gov/25.11), [Dirichlet L-functions](https://dlmf.nist.gov/25.15).
- [Special values of spectral zeta functions of graphs and Dirichlet L-functions](https://www.sciencedirect.com/science/article/pii/S0022314X23001993).
- [Ihara–Bass graph-zeta determinant formulas](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FSTTCS.2017.46).
- Cohen-Steiner, Edelsbrunner & Harer, [Stability of persistence diagrams](https://scholars.duke.edu/publication/696545).
- Adamaszek & Adams, [The Vietoris–Rips complexes of a circle](https://msp.org/pjm/2017/290-1/pjm-v290-n1-p01-s.pdf).
- [MathOS synthetic Li-prefix obstruction](https://github.com/tltmgnt/MathOS/blob/main/docs/research/MILLENNIUM_ATTACK_005.md).

**Certification:** `BOUNDED_RESEARCH` / `NOT_CERTIFIED` / `NO_RH_OR_BSD_PROOF`.

## MathOS repository integration

The generator is tracked at `mathos/research/tect_x_zeta_tda_1m.py`, with tests at `tests/test_tect_x_zeta_tda_1m.py`. A GitHub Actions workflow executes a small smoke audit on pull requests; a full million-variant rerun is an **opt-in `workflow_dispatch` job** and stores CSV/JSON as a downloadable CI artifact rather than committing a 17 MB generated dataset into git. The first full-size run was executed outside GitHub Actions and produced the reported SHA-256. CI passage does not certify a new theorem.
