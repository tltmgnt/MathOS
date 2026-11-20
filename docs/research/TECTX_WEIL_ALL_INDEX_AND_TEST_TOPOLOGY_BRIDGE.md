# TECT-X — All-index signed Weil bounds and the canonical test topology

**Scientific status:** This PR proves an unconditional *negative* lower bound for every compression of the signed Weil operator in PR #82, and establishes a rigorous domain/density/continuity bridge for a different countable compact-bump family inside the canonical Weil test space. **It does not prove global positivity or RH.**

## 1. All-index lower bounds for the prior signed coefficient operator

For the Gaussian tests in PR #82, let G_ij be their full arithmetic Weil-form entries, with the previously established uniform bound |G_ij| < M=10000. Let w_j=2^(j+1) and T_ij=G_ij/(w_i w_j), with zero-indexed coordinates. For every integer m>=1 and real x in R^m,

**|x^T T_m x| <= M (sum_(j<m) |x_j|/w_j)^2 <= (M/3)(1-4^(-m))||x||_2^2.**

Thus the unconditional all-index spectral estimate is

**T_m >= -(10000/3)(1-4^(-m)) I_m, for every m>=1.**

It is negative and does not tend to zero as m increases.

### Sharper all-index estimate using a certified three-dimensional head

The already certified positive 3D Weil Gram from PR #78 makes the weighted first three coordinates nonnegative. Separate a coefficient vector into old coordinates and tail coordinates. Their squared reciprocal-weight sums have exact values

- S_head = sum_(j<3) 1/w_j^2 = 21/64.
- S_tail = sum_(j>=3) 1/w_j^2 = 1/192.

Because sqrt(S_head*S_tail) <= 1/24, 2ab <= a²+b², and all absolute Weil entries are bounded by M, we obtain

**T_m >= -(3M/64) I_m = -(1875/4) I_m for every m>=3, conditional on the already certified positive first 3D block.**

This bound remains negative regardless of m and is not a positive limit theorem.

More generally, if T_k>=0 has *independently* been proved for a chosen prefix k, the same argument gives **T_m >= -(M/3)(2^(-k)+4^(-k)) I_m for every m>=k**. These conditional lower floors tend to zero as k increases. That convergence only establishes T>=0 if positive prefixes are actually proved for an unbounded sequence of indices. The present PR does not assert that.

## 2. Why the old Gaussian L2 basis is not a canonical Weil test-family core

The earlier spectral Gaussian functions q_c(t)=exp(-t²/100)cos(ct) have inverse Fourier transforms equal to combinations of translated Gaussians. These are not compactly supported in logarithmic coordinates. Consequently, the Gaussian basis does not lie in the standard Weil test domain D(R)=C_c^infinity(R). Ordinary L2-density of those functions cannot be used as a test-space density/continuity bridge.

The standard Weil positivity formulation uses the convolution quadratic form W(f * tilde(f)) for f in compactly supported smooth functions, where tilde(f)(x)=conjugate(f(-x)). This is the domain used in Suzuki's Hilbert-space work, and its full positivity is equivalent to RH.

## 3. Explicit countable family dense in the correct LF topology

Let phi(x)=C^(-1)exp(-1/(1-x²)) for |x|<1 and zero elsewhere, where C is its positive integral. For integers n>=1 and rational centers r=p/q, q>=1, define the smooth compactly supported normalized bumps

**b_(n,r)(x)=2^n phi(2^n(x-r)).**

Their supports lie inside [r-2^(-n),r+2^(-n)]. The parameter set is countable, with an explicit enumeration by height n+|p|+q, taking p/q in lowest terms.

**Density proof.** For every f in D(R), convolution f*phi_(2^-n) tends to f together with all derivatives. Their supports stay in one fixed slightly enlarged compact set. For each fixed scale, Riemann sums of appropriately fine rational-center translates converge to that convolution in arbitrarily many derivative seminorms. Diagonalizing these approximations over shrinking scales and increasing derivative order gives convergence in the LF topology of D(R). Therefore the linear span of the countable bump family is dense in the true Weil test-function topology.

This is a topology-correct density theorem, not merely L2-density.

## 4. Continuity and the RH-equivalent all-index Gram criterion

The classical Weil distribution W is a distribution on D(R): it is continuous in the LF topology. On each compact-support Fréchet space D_K, its continuity gives a finite-derivative-seminorm bound on functions supported in K-K. Convolution and reflection jointly map D_K × D_K continuously into D_(K-K). Hence the Hermitian quadratic form Q(f,g)=W(f*tilde(g)) is jointly continuous on fixed-support test spaces.

Let H_m denote the *actual Weil Hermitian Gram matrix* of the first m compact bumps. Then:

**RH is equivalent to H_m being positive semidefinite for every integer m>=1.**

The forward direction is the classical Weil criterion. For the converse, positivity of all finite matrices proves positivity of finite bump combinations; LF-density and continuity extend this to all compactly supported smooth tests, and the classical criterion gives RH. This is a rigorous **equivalence reduction to a countable core**, not proof of the required all-m inequalities.

The code intentionally does not compute H_m, falsely assert its positivity, or substitute the 3D/4D Gaussian certificates from the earlier PRs.

## 5. Proof-obligation register

| Item | Result |
|---|---|
| Unconditional all-index lower bound for signed T_m | Established, negative |
| Sharper all-index bound using certified 3D prefix | Established conditionally, negative |
| Prefix-k-to-all-m rational lower-bound implication | Established, conditional |
| Countable dense family in compactly supported Weil test LF topology | Established |
| Continuity of Weil convolution form in canonical test topology | Standard distribution-theoretic theorem applied |
| RH equivalence to PSD of every compact-bump Gram H_m | Established as a reduction using the classical criterion |
| PSD of every H_m | **Not proved; RH-equivalent** |
| Unconditional positive Weil Hilbert completion | **Not proved** |
| Riemann hypothesis | **Not proved** |

## 6. Reproduce

Run:

    python -m unittest discover -s tests -p 'test_riemann_weil_all_index_bridge.py' -v
    python -m mathos.research.riemann_weil_all_index_bridge --dimension 32 --bump-count 24 --output artifacts/riemann/weil_all_index_bridge.json

The tests validate exact rational bounds and concrete bump enumeration and fail closed on unsupported positivity claims. They do **not** formally verify the analytic topology and distribution theory, which are documented for mathematical review.

## References

- [Suzuki, On the Hilbert space derived from the Weil distribution](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6)
- [Suzuki, Aspects of the screw function corresponding to the Riemann zeta-function](https://onlinelibrary.wiley.com/doi/10.1112/jlms.12785)
- [Weil positivity and compactly supported tests](https://openmaths.org/courses/NT-EXPF/NT-EXPF-04.html)
- [Prior trace-class signed operator PR #82](https://github.com/tltmgnt/MathOS/pull/82)

**No peer-reviewed proof of RH, global Weil positivity, positive Hilbert completion, or global Hilbert–Pólya operator is claimed.**
