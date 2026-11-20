# TECT-X — Beyond the prime-free window: certified prime-2 Weil arithmetic cross entry

**Status:** a complete, mathematically rigorous **conservative rational enclosure** of the actual compactly supported arithmetic Weil cross entry involving a nonzero prime-2 contribution and a nonzero archimedean term, with no zeta-zero inputs. **Not** a certified PSD matrix, not a dense-domain positivity theorem, and not an RH proof. The bounds are analytic rather than narrow numerical quadrature.

## 1. Exactly specified C_c^∞ test functions

Let

```
phi(u)=exp(1-1/(1-u²))  if |u|<1, and 0 otherwise.
h=1/8,
f_0(x)=phi(x/h),       support [-1/8,1/8],
f_1(x)=phi((x-3/4)/h), support [5/8,7/8].
```

Both functions are real nonnegative and infinitely differentiable with compact support. The Weil Hermitian Gram is

```
H_ij = W(f_i * tilde(f_j)),   tilde(f)(x)=f(-x).
```

The exact convolution supports are:

```
supp h_00, h_11 subset [-1/4,1/4],
supp h_10 subset [1/2,1],
supp h_01 subset [-1,-1/2].
```

The logarithmic Weil explicit formula in Suzuki's normalization is

```
W(h) =
  integral_R h(x)*(exp(x/2)+exp(-x/2)) dx
  -sum_(n>=2) Lambda(n)/sqrt(n)*(h(log n)+h(-log n))
  -(log(4*pi)+gamma_E)*h(0)
  -integral_0^infinity [h(x)+h(-x)-2*exp(-x/2)h(0)]
     *exp(x/2)/(exp(x)-exp(-x)) dx.
```

This defines the complete arithmetic side without consulting the nontrivial zero locations. The diagonal supports exclude all primes. In the off-diagonal, **only n=2** can contribute, since log(2) lies strictly between 1/2 and 1, and log(3)>1. The archimedean term does not vanish for the off-diagonal.

## 2. Exact rational log(2) and prime support

Use the convergent series

```
log(2) = 2*sum_(k>=0) 3^(-2k-1)/(2k+1).
```

Truncating after N terms gives an exact rational lower bound, and the omitted tail is less than

```
2*3^(-2N-1) / [(2N+1)*(1-1/9)].
```

Already N=4 proves, with exact rational comparisons,

```
69/100 < log(2) < 70/100.
```

Likewise `log(3)=2*atanh(1/2)>13/12>1`. All arithmetic support exclusions therefore have explicit rational proofs. There is **no** approximate floating-point test for whether a prime is included.

## 3. A strict rational lower bound for the prime-2 contribution

Write

```
h_10(x)=integral_R f_1(t)*f_0(t-x)dt.
```

For **every** x in [69/100,70/100] and every t in [72/100,74/100], the scaled bump arguments obey

```
|8*(t-3/4)|<1/2, |8*(t-x)|<1/2.
```

Since `phi(u)>=exp(-1/3)>2/3` for `|u|<=1/2`, the integrand exceeds 4/9 across an integration interval of length 1/50. Hence

```
h_10(x)>2/225,
h_10(log 2)>2/225.
```

The cross prime contribution is precisely

```
P_10 = -(log 2)/sqrt(2)*h_10(log 2)
```

because h_10(-log 2)=0. With log 2>69/100 and sqrt 2<3/2,

```
-1/4 < P_10 < -23/5625 <0.
```

The lower -1/4 follows from h_10<=1/4 and (log2)/sqrt2<1.

This is a **provably nonzero negative arithmetic prime term** within the actual Weil form, not a guessed or fitted coefficient.

## 4. Independently prove the archimedean cross term is negative

Since the cross convolution h_10 is supported in [1/2,1], h_10(0)=0, and the archimedean distribution has no subtraction tail for this entry:

```
A_10 = -integral_(1/2)^1
  h_10(x)*exp(x/2)/(exp(x)-exp(-x)) dx.
```

The integrand is positive on the interior. More quantitatively, on [69/100,70/100], the kernel is greater than 1/3, because its numerator exceeds 1 and its denominator is less than e^1<3. Using the same convolution lower bound,

```
A_10 < -(1/100)*(2/225)*(1/3)
     = -1/33750.
```

For an independent absolute enclosure, the kernel is at most 1/x on 0<x<=1, h_10<=1/4 and the interval [1/2,1] has length 1/2, yielding

```
-1/4 < A_10 < -1/33750.
```

The archimedean integral has thus been *rigorously bounded and shown nonzero*, but has **not** been numerically evaluated to a tight interval.

## 5. Complete arithmetic Weil cross entry enclosure

The pole term is positive and bounded above by 1/2, because h_10<=1/4, its support length is 1/2, and exp(x/2)+exp(-x/2)<4 on [1/2,1]. The completed cross entry therefore satisfies

```
-1/2 < H_10 <
    1/2 - 23/5625 - 1/33750.
```

The Gram is real symmetric: H_01=H_10. The two diagonals are arithmetically prime-free; using the regularized archimedean distribution, rational bump-derivative bounds and compact support produces the conservative enclosures

```
-177/16 < H_00, H_11 < 177/16.
```

These are deliberately broad **complete arithmetic entry enclosures**, not PSD certificates. No positive eigenvalue is inferred from them. Their purpose is to provide the first rigorous normalization-checked calculation that actually **crosses a prime-power support threshold**.

## 6. Exact limitations

- The previous Yoshida/Bombieri prime-free small-support positivity theorem **does not apply** to the union of the two bump supports here.
- The form can have nonzero pole, prime and gamma/archimedean contributions; all three are accounted for.
- The intervals are too wide to decide whether the resulting 2×2 Hermitian matrix is PSD, and no statement about its eigenvalues is asserted.
- The two directions do not span an LF-dense core of C_c^infinity(R), and this calculation does not prove Weil positivity on all windows.
- The asymptotic all-test-function positivity assertion remains RH-equivalent and unproved.
- Python unit tests check exact rational inequalities and report flags; the analytic identity and support derivation are mathematical arguments for expert review, not independently formalized proof-assistant theorems.

## 7. Reproduce

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_prime_two_window.py' -v
python -m mathos.research.riemann_weil_prime_two_window \
  --output artifacts/riemann/weil_prime_two_window.json
```

The JSON stores the exact rational log2 bracket, all exact convolution supports, strictly negative prime and archimedean intervals, full arithmetic cross and diagonal outer intervals, and explicit false global PSD/RH fields.

## Sources

- Suzuki, *On the Hilbert space derived from the Weil distribution*, equation (3.3): https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6
- *The explicit formula with general test functions*, finite prime-support discussion: https://openmaths.org/courses/NT-EXPF/NT-EXPF-01.html
- Previous compact prime-free archimedean calculation: [MathOS PR #85](https://github.com/tltmgnt/MathOS/pull/85)
- Global Weil compact-bump RH-equivalent criterion: [MathOS PR #84](https://github.com/tltmgnt/MathOS/pull/84)

**No RH proof, global positivity, full Weil Hilbert space or new unconditional all-index positive theorem is claimed.**
