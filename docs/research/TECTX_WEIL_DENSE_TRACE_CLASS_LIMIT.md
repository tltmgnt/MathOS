# ResearchOS / TECT-X — Unbounded dense Weil test family and trace-class convergence

**Status:** an unconditional, explicit infinite-dimensional **signed** self-adjoint trace-class operator carrying the arithmetic Weil quadratic form on a weighted coefficient Hilbert space; a countable Gaussian–cosine test family with span dense in **even L²**, and a **geometric, dimension-independent finite-section trace-norm estimate**. This does **NOT** prove the operator positive, does **NOT** establish density in the RH-relevant Weil-admissible topology, and does **NOT** prove RH.

## 1. A genuinely infinite family, explicitly enumerated

For every rational frequency `c∈[0,1/2]`, define

```text
q_c(t)=exp(-t²/100)*cos(c*t).
```

Enumerate a sequence of **distinct** frequencies `(c_j)_(j>=0)`: begin at `0,1/5,1/2` (the previously certified 3D Weil basis); then enumerate all *positive odd dyadic fractions* `k/2^(n+1)` with `n>=1`, `k=1,3,...,2^n-1`, omitting duplicates. The resulting set is dense in `[0,1/2]`.

This is **not** the same family as the separately certified fourth-direction span in PR #81, whose new center `21/5` lies outside the compact frequency interval. No 4D positivity certificate is imported into the present increasing dense family.

### Exact even-L² density theorem

The span of these functions is dense in even `L²(R)`:

Suppose `f∈L²_even(R)` is orthogonal to each `q_(c_j)`. Set `g(t)=f(t)exp(-t²/100)`. By Cauchy–Schwarz, `g∈L¹(R)` and `g(t)exp(a|t|)∈L¹(R)` for every finite `a`. Therefore

```text
F(z)=integral_R g(t)*cos(z*t)dt
```

is an **entire function** of `z`. It vanishes at every `c_j`, whose set has an accumulation point in the interior of `[0,1/2]`. The complex identity theorem gives `F≡0`. Since `g` is even, this is its Fourier transform; uniqueness of the Fourier transform on `L¹` implies `g=0`, hence `f=0`. Thus the orthogonal complement is trivial and the span is dense. □

**Essential caveat:** Density in the ordinary `L²` norm does NOT imply density in the much stronger admissible topology relevant to Weil's criterion. The Weil distribution includes evaluation at complex arguments, not an a priori bounded functional on L². Inferring RH from this L² density would be invalid.

## 2. Uniform entry bound for the COMPLETE arithmetic Weil form

Define

```text
G_ij=W(q_(c_i)*q_(c_j)).
```

This is the classical arithmetic-side explicit formula with **all** pole, `log(pi)`, archimedean real digamma, and von Mangoldt prime-power terms, without a zero table. For `h_ij(t)=exp(-t²/50)cos(c_i t)cos(c_j t)`, its Fourier transform is positive and bounded by `sqrt(50*pi)<13`, uniformly in `c_i,c_j∈[0,1/2]` and real `u`.

The following elementary bounds apply **uniformly to every matrix entry and hence every dimension**:

| Weil component | Absolute bound | Justification |
|---|---:|---|
| Polar term `h(i/2)+h(-i/2)` | 5 | `2exp(1/200)cosh(1/4)² <5` |
| `-log(pi)*hhat(0)/(2pi)` | 5 | `log pi<2`, `pi>3`, `hhat<13` |
| Entire archimedean digamma integral | 35 | `|Re psi(1/4+it/2)|<16+t/128`, `int_0^infty e^(-t²/50)dt<13/2`, `int_0^infty t e^(-t²/50)dt=25`, `pi>3` |
| Prime powers `2<=n<=256` | 6,630 | `Lambda(n)<=log n<6`, `n^(-1/2)<=1`, at most 255 terms, `hhat<13`, `pi>3` |
| **All omitted prime powers** `n>256` | 1 | Previous **exact rational** Gaussian-tail estimate from PR #75 |

The real-digamma inequality comes from the 64-step recurrence and elementary Binet-remainder bound: with `r=64+1/4` and `t>=0`, the log, remainder and harmonic terms give

```text
|Re psi(1/4+i*t/2)|
 <= C + t/128
 C=log(65)+4+log(256)+1/128+1/(12*64²)<16.
```

Consequently, for all `i,j` and without RH,

```text
|G_ij| < 5+5+35+6630+1 = 6676 < M := 10000.
```

This bound controls **every term of the entire Weil form**, not merely the prime-power tail, across the **unbounded** family of finite dimensions, with the Fourier frequencies confined to `[0,1/2]`. The constants are intentionally conservative. The implementation performs only exact rational checks of the resulting inequalities and inherits the separately documented classical analytic identities.

## 3. Fixed self-adjoint, trace-class *signed* Weil operator

Set `w_j=2^(j+1)`. On the **coefficient Hilbert space** `H_c=ell²(N_0)`, define the real symmetric matrix

```text
T_ij = G_ij/(w_i*w_j).
```

The matrix is defined by arithmetic, not by any zeta-zero table. Since `|G_ij|<M`,

```text
sum_(i,j>=0) |T_ij|
 <= M*(sum_(j>=0)2^(-j-1))²
 = M.
```

Therefore the series `T=sum_(i,j) T_ij |e_i><e_j|` converges absolutely in **trace norm**. It defines a **fixed, real self-adjoint trace-class operator**, even if the Weil form takes negative values. Trace-classness, self-adjointness, and compactness are unconditional; **positive semidefiniteness is NOT established**.

Define a weighted synthesis map

```text
Q(a)(t)=sum_(j>=0) a_j 2^(-j-1)q_(c_j)(t).
```

Cauchy–Schwarz gives `sum_j |a_j|/w_j <=||a||_2/sqrt(3)`; and since `||q_c||²_L2<=sqrt(50*pi)<13`,

```text
||Q(a)||²_L2 <= (13/3)||a||²_ell2.
```

Thus `Q` is bounded. Its range is dense in even `L²`, by §1. It is also injective: if `Q(a)=0`, remove the positive Gaussian factor to obtain a uniformly convergent cosine series with absolutely summable coefficients; uniqueness of the Fourier transform of its finite discrete frequency measure forces all coefficients to be zero. Nevertheless `Q` does **not** have a bounded inverse onto its dense range; its coefficient norm is artificially weighted and cannot be substituted for the ordinary L²/Weil test-function norm.

The form `<a,Ta>_ell2` extends the arithmetic Weil quadratic form of the weighted Gaussian series. The double sum converges absolutely by the uniform entry bound and the Cauchy–Schwarz coefficient estimate.

## 4. Exact dimension-independent truncation theorem

Let `P_m` project onto the first `m` coefficient coordinates. Set `T_m=P_mTP_m` extended by zero outside that finite block.

The trace-norm difference has an explicit, exact **global bound**, valid for EVERY integer `m>=0`:

```text
||T-T_m||_1
 <= sum_(i>=m or j>=m) |T_ij|
 <= M*[(sum_(j>=0)1/w_j)² - (sum_(j<m)1/w_j)²]
 = 10000*(2^(1-m)-2^(-2*m)) =: eps_m.
```

This bound is rational and is computed exactly with `fractions.Fraction`. In particular `eps_m->0` geometrically. Because operator norm is at most trace norm,

```text
||T-T_m|| <= eps_m.
```

A **uniform lower spectral bound** therefore follows without presuming positivity: whenever the exact finite compression obeys `T_m>=b_m I_m`,

```text
T >= [min(0,b_m)-eps_m] I  on the entire ell² space.
```

In particular, **if** a rigorously certified finite compression is positive semidefinite, then `T>=-eps_m I`. This bounds the possible infinite-dimensional negative spectrum to a vanishing error *as m grows*, but **does not prove it vanishes**, because no all-`m` finite-section positivity theorem has been proved.

A logically sufficient future theorem would supply a proven sequence `b_m` for **every integer m** with `min(0,b_m)-eps_m->0`. That would establish `T>=0` on this *specific weighted coefficient space*. It would **not by itself prove RH**, absent density in the correct Weil-admissible topology and the required continuity/density bridge.

## 5. Why strict uniform coercivity is impossible in this coefficient space

The operator is trace class and hence compact. More directly,

```text
|<e_j,T e_j>|=|G_jj|/w_j² <10000/4^(j+1)->0.
```

Thus `T>=kappa I` for a fixed `kappa>0` is impossible for all `j`, regardless of the unresolved question of `T>=0`. Asking for strictly positive **uniform eigenvalue margins** in this particular infinite-dimensional coefficient Hilbert space is therefore the wrong target; nonnegative positivity is the best possible global goal.

This failure is not evidence against RH. It is a consequence of trace-class weighting.

## 6. Reproducible research gate

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_dense_limit.py' -v
python -m mathos.research.riemann_weil_dense_limit \
  --dimension 32 \
  --output artifacts/riemann/weil_dense_limit.json
```

The report contains exact rational `eps_m`, the first `m` distinct rational frequencies, the all-component uniform Weil entry majorant, the infinite operator construction, and explicit **false** values for global Weil positivity, unconditional Weil Hilbert completion and RH.

**What the software tests do not do:** prove every analytic theorem merely by running a few unit tests, compute or diagonalize an infinite matrix, or prove finite-section positivity for all `m`. The analytic density, trace-class and truncation arguments are supplied here for independent review.

## 7. Relation to the Hilbert–Pólya and Suzuki programs

Suzuki's Hilbert spaces derived from the Weil distribution are built in a setting that explicitly considers the Riemann hypothesis. The weighted `ell²` space here is **unconditionally well-defined and not the same object**. It can carry a bounded, possibly indefinite arithmetic Weil form, but it is not the sought completed Weil-positive Hilbert space. <https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6>

The correct next bridge is a **Weil-admissible density and continuity theorem**, plus a **global finite-section sign theorem** (or direct positive-kernel theorem), not further uncontrolled numerical extrapolation. The previous PR #81 establishes positivity of a different fixed four-dimensional Gaussian family with center `21/5`; it **does not** certify the next term `1/4` in this dense sequence.

**Final classification:** a mathematically substantive infinite-dimensional **convergence and negative-spectrum control theorem** for an explicit signed Weil operator, but **not** a global positivity theorem, a zero-spectrum identity, or an RH proof.
