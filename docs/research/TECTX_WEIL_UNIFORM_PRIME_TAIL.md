# ResearchOS / TECT-X — Uniform Weil prime-power tail estimate

**Status:** an explicit, reproducible, **exact rational bound** on one infinite arithmetic component of the actual Weil form for a *restricted but arbitrary finite-dimensional Gaussian test family*. This is **NOT** a global Weil positivity theorem and does **NOT** prove RH. No new mathematical novelty is claimed.

## Mathematical setting

Use the classical explicit formula with Fourier convention `hhat(u)=integral_R h(t)e^(-iut)dt`, and the test functions

```
h_jk(t)=exp(-a*t²)*cos(c_j*t)*cos(c_k*t), a=1/50,
0 <= c_j <= 1/2.
```

The prime-power part of the Weil quadratic form is

```
P(h) = -(1/pi)*sum_(n>=2) Lambda(n)/sqrt(n) * hhat(log n).
```

Every term is included, not just primes; `Lambda(p^k)=log(p)`. Let `P_N(h)` denote the sum truncated at `n<=N`. The familiar Fourier transform is

```
hhat_jk(u)=sqrt(pi/a)/4 * sum_(epsilon,eta in {+1,-1})
   exp(-(u-epsilon*c_j-eta*c_k)^2/(4*a)).
```

For `u>=5` and `c_j+c_k<=1`, each shifted exponent is bounded from above by `-(u-1)^2/(4a)`. Therefore

```
0 <= hhat_jk(u) <= sqrt(pi/a)*exp(-(u-1)^2/(4a)).
```

Since `Lambda(n)<=log(n)`, and `N>=256>e^5`, it follows that

```
|P(h_jk)-P_N(h_jk)|
 <= 1/sqrt(pi*a) * sum_(n>N) log(n)/sqrt(n)
                      *exp(-(log(n)-1)^2/(4*a)).
```

## Rigorous decreasing-tail integral and exact rational bound

The scalar summand `f(x)=log(x)/sqrt(x)*exp(-(log(x)-1)^2/(4*a))` is decreasing for `x>=e^5`: writing `u=log x`,

```
d[log f(x)]/du = 1/u-1/2-(u-1)/(2*a) < 0, u>=5.
```

Thus

```
sum_(n>N) f(n) <= integral_N^infinity f(x)dx
                 <= integral_(e^5)^infinity f(x)dx
                 = integral_5^infinity u*exp(u/2-(u-1)^2/(4*a))du.
```

Complete the square with `m=1+a`, `beta=(5-m)/(2*a)`, `X=(5-m)^2/(4*a)`:

```
u/2-(u-1)^2/(4*a)
   =1/2+a/4-(u-m)^2/(4*a).
```

For `u>=5`, the inequality

```
(u-m)^2 >= (5-m)^2+2*(5-m)*(u-5)
```

gives

```
integral_5^infinity u*exp(-(u-m)^2/(4*a))du
    <= exp(-X)*(5/beta+1/beta^2).
```

Use the elementary inequalities `pi>3`, `log 2>2/3`, and `e^x >= (1+x/16)^16` for `x>=0`. At `a=1/50` these imply

```
1/sqrt(pi*a)<5,
exp(1/2+a/4)<2,
exp(-X)<=(1+X/16)^(-16).
```

The exact parameters are

```
beta = 199/2,   X = 39601/200.
```

Consequently, for **every** pair of centers in `[0,1/2]` and **every** integer prime-power cutoff `N>=256`,

```
|P(h_jk)-P_N(h_jk)| <= delta

delta = 10*(5/(199/2)+1/(199/2)^2)
        /(1+(39601/200)/16)^16,
```

a positive exact rational number approximately `4.80 × 10^(-19)`.

The repo computes this **exact fraction** with Python `Fraction`, no floating-point comparisons or zeta-zero tables. The inequality itself is a transparent elementary proof; the decimal approximation is for readability only.

## Uniform extension to any finite span (dimension explicit)

For arbitrary real coefficients `v=(v_1,...,v_m)` and any centers `c_j∈[0,1/2]`, let `G` denote the exact full Weil Gram and `G_N` the form with only the prime-power sum truncated. **Both include the same infinite archimedean and pole terms**. The entry-wise estimate above, followed by Cauchy–Schwarz, yields

```
|vᵀ(G-G_N)v| <= delta*(sum_j |v_j|)^2
              <= m*delta*||v||_2^2.
```

This is a uniform error estimate for the *prime-tail difference*, valid for **all coefficient vectors** within each span, not merely eigenvectors or sampled matrices. The bound increases explicitly with the dimension `m`; it is not a dimension-independent coercivity or positivity theorem.

A conditional finite-dimensional positivity statement is available:

```
IF   λ_min(G_N) >= m*delta
THEN G is positive semidefinite on that span.
```

But `G_N` here is the **exact** operator with complete pole/archimedean terms, not the previous floating-point truncated quadrature. The current software does **not** provide certified bounds on those terms or a verified lower bound on `λ_min(G_N)`. Thus it does **not** satisfy the antecedent and cannot promote a numerical finite Gram to a proved positive Gram.

This restricted uniform arithmetic error estimate does not establish positivity over all Weil-admissible tests or construct the complete Weil Hilbert space. It does not imply RH.

## Suzuki's screw function and limit warning

Suzuki's work develops forms and kernels representing the Weil distribution through the screw function and discusses Hilbert completions *under conditions closely tied to RH*. A general Hilbert-space construction cannot be obtained by presuming positivity of the Weil quadratic form.

Recent compact-window work investigates rigorously small positivity margins as test-function windows grow. This makes dimension- and window-independent positive lower bounds a substantive open research objective, not a routine consequence of finite calculations. See [Suzuki's journal paper](https://londmathsoc.onlinelibrary.wiley.com/doi/full/10.1112/jlms.12785), [Suzuki's Hilbert-space work](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6), and [compact-window certified-bound preprint](https://arxiv.org/abs/2608.24827).

## Reproduction

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_gram.py' -v
python -m unittest discover -s tests -p 'test_riemann_weil_prime_tail.py' -v

python -m mathos.research.riemann_weil_prime_tail \
  --centers 0,1/5,1/2 --prime-cutoff 256 \
  --output artifacts/riemann/weil_prime_tail.json
```

Inspect the exact rational `per_gram_entry_upper_rational` and `quadratic_form_norm_upper_rational`. The CLI rejects centers outside the proved interval, invalid dimensions and cutoffs too small for the uniform proof.

## Remaining proof obligations

| Obligation | Result |
|---|---|
| Exact analytic bound on prime-power tail | **Established for a=1/50 and centers in [0,1/2]** |
| Bound uniform over finite coefficients | **Established with dimension factor m** |
| Rigorous archimedean/gamma quadrature remainder | OPEN |
| Certified finite Gram entry and eigenvalue enclosures | OPEN |
| Uniform positivity as dimension/windows expand | OPEN |
| Hilbert completion of full Weil form | OPEN |
| Fixed self-adjoint all-zero spectral mapping | OPEN |
| Riemann hypothesis | NOT PROVED |

**No independent review or proof of novel mathematical results is claimed.** This contribution resolves a narrow arithmetic error-control step and intentionally leaves the RH-equivalent global positivity barrier explicit.
