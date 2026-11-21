# TECT-X — The first genuine 2×2 Weil Gram on the LF-dense compact core

**Status:** a reproducible, fail-closed candidate finite arithmetic certificate for the actual first TWO test functions of the rational-center/dyadic-scale LF-dense core. The exact arithmetic source evaluates both diagonals and the previously missing off-diagonal, with prime powers **2, 3, 4, 5, 7** and the full pole and archimedean distributional contributions. Only a passing interval-margin gate authorizes the claim of a strict fixed-space 2×2 eigenvalue floor.

**Scientific boundary:** even a positive first 2×2 Gram on an analytically LF-dense infinite family does not establish all-index Gram positivity or RH. The full Weil-positive Hilbert-space completion remains conditional. These calculations are trusted analytic derivations and pinned interval computation, not proof-assistant formalized or independently peer-reviewed theorems.

## 1. The exact enumeration matters

The PR #83/#92 LF-dense canonical bump family is

\[
b_{n,r}(x)=2^n C^{-1}\exp\left(-\frac1{1-(2^n(x-r))^2}\right),
\qquad |2^n(x-r)|<1
\]

and zero otherwise. The first two **actual** entries of the immutable height enumeration are \((n,r)=(1,0)\) and \((1,-1)\), not a cherry-picked convenient scale or an unrelated finite lattice.

Write \(f(x)=\exp(1-1/(1-4x^2))\) on \(|x|<1/2\), zero otherwise, and \(m_0=\int f(x)dx\). Then the two normalized functions are **exactly**

\[
b_0(x)=f(x)/m_0,\qquad
b_1(x)=f(x+1)/m_0.
\]

Their supports are respectively \([-1/2,1/2]\) and \([-3/2,-1/2]\). Because the two tests are real translates, the actual Weil Gram is

\[
G_2=\frac1{m_0^2}\begin{pmatrix}d&c\\c&d\end{pmatrix}
\]

where \(d=W(f*\widetilde f)\) is the rigorously positive arithmetic scalar from PR #94, and \(c=W(f*\widetilde{f(\cdot+1)})\) is newly enclosed.

## 2. Full arithmetic off-diagonal formula and exact primes

The positive-support orientation of the off-diagonal convolution is

\[
h_{01}(x)=(f*\widetilde{f(\cdot+1)})(x)
=h_0(x-1),\quad h_0(v)=(f*\widetilde f)(v).
\]

Its support is **[0,2]**, and \(h_{01}(0)=0\) exactly because the bump is flat at its compact boundary. The additive-log Weil distribution of Suzuki has the pole + prime + archimedean decomposition

\[
\boxed{\begin{aligned}
c={}&2\cosh(1/2)m_1^2\\
&-\sum_{n\in\{2,3,4,5,7\}}
\frac{\Lambda(n)}{\sqrt n}\,h_0(|\log n-1|)\\
&-\int_0^2
\frac{e^{x/2}}{e^x-e^{-x}}\,h_0(|x-1|)\,dx,
\end{aligned}}
\]

with \(m_1=\int f(x)e^{x/2}dx\). No subtraction tail remains in the off-diagonal gamma term because \(h_{01}(0)=0\), although its endpoint at \(x=0\) must be treated analytically. All five prime-power evaluations use exact rational logarithm brackets and certified autocorrelation samples. Every \(n\) outside the list has vanishing von Mangoldt contribution or lies outside support. No nontrivial zeta zeros are used.

The pole moment is enclosed with the same smooth trapezoid-error argument as PR #94, at increased resolution.

## 3. Remove the apparent endpoint gamma singularity without dropping terms

Put \(K(x)=e^{x/2}/(e^x-e^{-x})\) and \(g(x)=K(x)h_0(|x-1|)\) for \(0<x<2\). The gamma contribution is \(-\int_0^2g(x)dx\). Although \(K(x)\sim1/(2x)\) near zero, the *actual product* \(g\) extends to a smooth function with \(g(0)=g(2)=0\), because the two bumps vanish to every order at their support edges.

The code uses the following explicit second-derivative majorant, which is an analytic proof ingredient, not a fitted numerical value.

For the base \(f\), PR #94 established \(0\le f\le1\), \(|f'|<8\), and total support length 1. When \(0<x\le1/2\), the two factors in \(h_0(1-x)\) overlap on an interval of length \(x\). Each factor vanishes at the respective support edge, so

\[
h_0(1-x)\le\frac{32}3x^3,\qquad
|\partial_xh_0(1-x)|\le32x^2,\qquad
|\partial_x^2h_0(1-x)|\le64x.
\]

For \(1/2\le x\le2\), the global bounds \(0\le h_0\le1\), \(|h_0'|\le8\), and \(|h_0''|\le64\) suffice.

On \(0<x\le2\), the decreasing kernel satisfies

\[
K(x)\le\frac1x,\quad
|K'(x)|\le\frac2{x^2},\quad
|K''(x)|\le\frac5{x^3}.
\]

The product rule therefore gives \(|g''|<246\) on \((0,1/2]\) and \(|g''|\le296\) on \([1/2,2]\). In particular,

\[
\boxed{\|g''\|_{L^\infty[0,2]}<300.}
\]

With \(N\) equal trapezoid panels on \([0,2]\), the **global signed quadrature error** is bounded by

\[
\boxed{\left|\int_0^2g(x)dx-T_N(g)\right|
\le\frac{2^3\cdot300}{12N^2}
=\frac{200}{N^2}.}
\]

At the default \(N=2048\), this is a small *exact rational* error. Furthermore, every trapezoid node uses a separately interval-enclosed value of the actual autocorrelation \(h_0\), with its own certified analytic second-derivative integration remainder inherited from PR #94. The code pairs symmetrical nodes to halve the expensive convolution calculations.

This procedure does **not** extrapolate from unchecked floating-point endpoint values.

## 4. Exact-rational Schur and eigenvalue gates

The first diagonal \(d\) and raw normalizing mass \(m_0\) are taken from the complete PR #94 interval certificate, generated again in the same audit. The second diagonal equals \(d\) *exactly* by translation invariance.

Let \(d_-\) be the lower outward rational endpoint of \(d\), \([c_-,c_+]\) the new off-diagonal interval, and \(M_+\) the upper mass endpoint. Define

\[
C=\max(|c_-|,|c_+|),\qquad
\delta=\frac{d_--C}{M_+^2}.
\]

The code rejects the run unless \(\delta>10^{-4}\). For the actual normalized symmetric Gram, the exact eigenvalue formula \(\lambda_\min=(d-|c|)/m_0^2\) then proves

\[
\lambda_{\min}(G_2)>10^{-4}.
\]

An independent exact-rational Schur check requires \(d_--C^2/d_->0\). This is a *finite* positive-definiteness certificate, not an infinite-dimensional positivity theorem.

## 5. Reproduction and fail-closed scope

\`\`\`bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_lf_core_first_2x2.py' -v
python -m mathos.research.riemann_weil_lf_core_first_2x2 \\
  --gamma-panels 2048 --covariance-panels 512 \\
  --prime-panels 1024 --pole-panels 1024 \\
  --output artifacts/riemann/weil_lf_core_first_2x2.json
\`\`\`

The dedicated workflow regenerates both entries, then *independently recombines* the outward rational pole, prime and archimedean bounds; checks the complete five-prime inventory, raw diagonal dominance, the normalized eigenvalue floor and Schur pivot; and explicitly rejects all claims of positivity for every LF-core prefix, a full Weil-positive Hilbert completion, or RH.

### What remains

The next core member is another genuine distinct rational/scale direction. Its new arithmetic cross terms and a verified 3×3 Schur complement remain unproved until evaluated. No finite number of verified matrices solves the RH-equivalent all-index positivity criterion.

Primary arithmetic reference: Suzuki, *On the Hilbert space derived from the Weil distribution*, equation (3.3), https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6 .

Related MathOS: PR #83 (domain), #92 (LF-dense-core workflow), #94 (first full diagonal), #91 (non-dense lattice obstruction).
