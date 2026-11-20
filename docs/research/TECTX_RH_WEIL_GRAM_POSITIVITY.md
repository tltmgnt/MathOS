# ResearchOS / TECT-X — Weil explicit-formula Gram experiment

**Scientific status:** FINITE, UNCERTIFIED RESEARCH DIAGNOSTIC. No new RH proof, no certified global Weil positivity, no completed Weil Hilbert space, and no fixed self-adjoint zeta operator. This contribution puts the **correct arithmetic-side pole, gamma/archimedean, and all prime-power terms** in a consistent finite numerical calculation, then demonstrates the exact difference between a finite positive matrix and the global theorem.

## 1. Weil's positivity criterion is an RH-equivalent obligation

The classical Weil criterion recasts the Riemann hypothesis as positivity of a distributional quadratic form on an appropriate *full* test-function space, when functions are combined through convolution with reflection/conjugation. In an additive log-coordinate spectral normalization, for sufficiently admissible even entire tests `h` with adequate decay in horizontal strips, the classical explicit formula reads

```text
sum_(rho nontrivial, multiplicities) h((rho-1/2)/i)
  = h(i/2)+h(-i/2)
    -log(pi)/(2*pi)*hhat(0)
    +1/(2*pi)*integral_R h(t)*Re digamma(1/4+i*t/2) dt
    -1/pi*sum_(n>=2) Lambda(n)/sqrt(n)*hhat(log n).
```

Here `hhat(u)=integral_R h(t)*exp(-i*u*t)dt`. The *full infinite* prime-power sum and archimedean term are part of the classical equality. The zeros of zeta are **not** inputs to the computation. Every zero contributes to the left side with its multiplicity, on or off the critical line. The formula itself is classical and does not imply RH.

For our basis, let `a>0`, choose centers `c_j>=0`, and set

```text
h_jk(t)=exp(-a*t²)*cos(c_j*t)*cos(c_k*t).
```

It is the product of the real-axis Gaussian spectral functions `q_j(t)=exp(-a*t²/2)*cos(c_j*t)`. These are even entire functions with Gaussian decay on horizontal strips. The matrix `G_jk=W(h_jk)` is the **Weil-form Gram matrix restricted to this finite span**. The exact Fourier transform is

```text
hhat_jk(u)=(sqrt(pi/a)/4) *
  sum_(eps=±1,eta=±1) exp(-(u-eps*c_j-eta*c_k)²/(4a)).
```

In particular the full *arithmetic* matrix can be computed from poles, gamma terms and prime powers, without a zeta-zero table or an RH assumption.

## 2. Numerical components and rigorous boundary

The implementation:
- evaluates pole terms `2*exp(a/4)*cosh(c_j/2)*cosh(c_k/2)` explicitly;
- evaluates `-log(pi)*hhat_jk(0)/(2*pi)` analytically;
- approximates `integral_R h_jk(t)*Re digamma(1/4+i*t/2)dt/(2*pi)` by symmetric Simpson quadrature on a finite interval, using the digamma recurrence and finite Bernoulli expansion;
- evaluates the finite prime-power sum `-sum_(2<=n<=N) Lambda(n)*hhat_jk(log n)/(pi*sqrt(n))` by explicit integer factorization;
- diagonalizes the small real symmetric matrix by floating-point Jacobi rotations.

For default `a=0.02`, centers `(0,0.2,0.5)`, `max_t=45`, and `N=512`, the resulting finite matrix has **numerically positive eigenvalues**, but none has a certified, outward-rounded enclosure. The script does **not** rigorously bound every quadrature, digamma-truncation, prime-tail, or roundoff error. In particular an eigenvalue reported as positive is *not* an independently proved positivity result for the exact Weil form.

The test family is narrow, three dimensional by default. Its numerical positivity cannot establish the Weil criterion, because the criterion quantifies over an **infinite-dimensional admissible class**, with arbitrary Fourier support. Finite-volume limits, cutoff limits, density and absence of spectral pollution remain open.

## 3. Positive Hilbert space: an essential distinction

The implementation separately computes

```text
L_jk = integral_R exp(-a*t²)*cos(c_j*t)*cos(c_k*t) dt
     = (sqrt(pi/a)/2) *
       [exp(-(c_j-c_k)²/(4a))+exp(-(c_j+c_k)²/(4a))].
```

This is an **unconditionally positive-semidefinite** Gram kernel because for real coefficients `v_j`,

```text
sum_jk v_j L_jk v_k
  = integral_R exp(-a*t²)*(sum_j v_j cos(c_j*t))² dt >= 0.
```

It therefore defines a finite positive Hilbert-space inner product after quotienting by the null space. **But it is not the Weil quadratic form**, and its positivity does not imply RH. The two matrices have different definitions and are returned in separate result fields.

If the full Weil form could independently be proved positive semidefinite on its entire admissible domain, one could form a positive pre-Hilbert quotient and Hilbert completion. Such a positivity theorem would essentially be the RH-equivalent hard step; the proposed completion is only conditional. There is currently **no proved global Weil-positive Hilbert space** in this implementation and no fixed self-adjoint zeta Hamiltonian.

## 4. TGA proof-obligation register

| Mathematical obligation | Current result | Status |
|---|---|---|
| Arithmetic prime-power + archimedean Weil matrix | Explicit formula implemented numerically for Gaussian basis | BOUNDED DIAGNOSTIC |
| Finite Gram positivity | Positive approximations for tested centers, **not certified** | UNVERIFIED AS EXACT INEQUALITY |
| Always-positive alternative Hilbert Gram | L² comparison kernel, elementary proof | ESTABLISHED, NOT WEIL |
| Uniform Weil positivity on all admissible tests | No global inequalities or operator estimate | OPEN |
| Weil-form Hilbert completion | Conditional on unavailable global positivity | OPEN |
| Complete zero correspondence and multiplicities | Classical explicit formula is used, not an independently derived self-adjoint realization | OPEN |
| RH proof | None | NOT ESTABLISHED |

The use of the explicit formula is **noncircular**: its classical validity does not assume RH, and its zero-side incorporates any hypothetical off-critical-line zeros. What remains unresolved is *global positivity*. It would be circular to declare the Weil form positive merely because a Hilbert-space completion is desired.

## 5. Reproduce and stress-test

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_gram.py' -v
python -m mathos.research.riemann_weil_gram \
  --a 0.02 --centers 0,0.2,0.5 \
  --max-t 45 --panels 4096 --prime-bound 512 \
  --output artifacts/riemann/weil_gram.json
```

Inspect the `finite_Weil_Gram.entry_components` array for each pair, `approx_eigenvalues` for numerical behavior, and `independent_positive_L2_comparison` for the **different** analytically positive kernel. Negative numerical eigenvalues, unstable refinement, or unexpected normalizations are grounds for rejecting a numerical claim; no finite success promotes `RH.operator`, `RH.zero_identity`, or `BRIDGE.RH.spectral`.

## 6. Research direction with falsifiable milestones

1. Add independently reviewed interval/ball arithmetic enclosing all four Weil terms and every cutoff error; publish precise verified finite-basis inequalities, including failed windows.
2. Expand basis dimension and support; prespecify windows and holdout tests; compare with published screw-function and finite Weil-positivity experiments.
3. Seek a **uniform coercivity/positivity estimate** with constants independent of dimension, window and truncation. Explicitly analyze escape directions and loss of lower bounds.
4. Only after a genuine global positivity theorem: construct and study the resulting positive Hilbert-space completion, densely defined operator, and a noncircular spectrum/zero map with all multiplicities and off-line possibilities.
5. Require outside mathematical review and reproducibility before advancing any Clay or RH certification claim.

## Related research

- [Weil’s positivity criterion, accessible exposition](https://openmaths.org/courses/NT-EXPF/NT-EXPF-04.html)
- [J. C. Lagarias: Riemann hypothesis, arithmetic and geometric approaches](https://www.math.lsa.umich.edu/~lagarias/doc/mt-holyoke-rev.pdf)
- [M. Suzuki, Weil’s quadratic form via the screw function (2026 preprint)](https://arxiv.org/abs/2606.09096)
- [Y. Shi, Construction of Finite Hilbert–Pólya Matrices from Weil's Explicit Formula (2026 preprint)](https://arxiv.org/abs/2609.04908)
- [Compact-window finite Weil positivity work (2026 preprint)](https://arxiv.org/abs/2608.24827)
- [Previous MathOS Hilbert–Pólya spectral exclusion](TECTX_RH_UNIFORM_HILBERT_POLYA_BARRIER.md)

**Scientific classification:** an arithmetic explicit-formula implementation with finite unverified PSD experiments and an independently proven positive *comparison* Hilbert Gram. It does not establish an RH-equivalent global positivity theorem.
