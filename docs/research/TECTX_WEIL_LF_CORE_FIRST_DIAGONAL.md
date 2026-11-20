# TECT-X — First actual LF-dense-core Weil arithmetic diagonal, certified strictly positive

**Scope:** a complete outward interval enclosure for the *actual normalized first diagonal* of the canonical compact-bump core of PR #83/#92, including **nonzero prime 2**, pole contributions, and the regularized infinite archimedean distribution. The code requires

\[
\boxed{W(b_{1,0}*\widetilde b_{1,0})>1/1000.}
\]

The positivity certificate uses interval arithmetic and explicit analytic remainder bounds, not zeta-zero ordinates or RH. It is **one fixed scalar test**, not positivity of every finite Gram, an all-index theorem, a complete Weil Hilbert space, or RH. The implementation has not been independently formalized or peer reviewed.

## 1. Match the first LF-dense core function exactly

PR #83 enumerates the normalized compact tests

\[
b_{n,r}(x)=2^n C^{-1}\exp\!\left(-\frac1{1-(2^n(x-r))^2}\right),
\quad |2^n(x-r)|<1,
\]

and zero elsewhere, where \(C=\int_{-1}^1e^{-1/(1-u^2)}du\), \(n\ge1\), \(r\in\mathbb Q\). The very first enumeration entry is \((n,r)=(1,0)\), supported on \([-1/2,1/2]\).

For numerical stability define an **unnormalized** bump

\[
f(x)=\begin{cases}
\exp(1-1/(1-4x^2)), & |x|<1/2,\\
0,& |x|\ge1/2,
\end{cases}
\qquad m_0=\int_{\mathbb R}f(x)dx.
\]

Since \(m_0=eC/2\), the original unit-mass first core test is **exactly** \(b_{1,0}=f/m_0\). Therefore

\[
W(b_{1,0}*\widetilde b_{1,0})
=\frac{W(f*\widetilde f)}{m_0^2},
\qquad m_0>0.
\]

The code encloses \(m_0\) with an analytic integration-error bound. This is not a new or substituted positive comparison kernel.

## 2. Correct full arithmetic Weil formula

Use Suzuki's additive-logarithmic normalization of the Weil distribution, with \(h=f*\widetilde f\):

\[
\begin{aligned}
W(h)={}&\int_{\mathbb R}h(x)(e^{x/2}+e^{-x/2})dx\\
&-\sum_{n\ge2}\frac{\Lambda(n)}{\sqrt n}
      [h(\log n)+h(-\log n)]\\
&-(\log(4\pi)+\gamma)h(0)\\
&-\int_0^\infty
 \frac{h(x)+h(-x)-2e^{-x/2}h(0)}
      {\vphantom{\int}e^x-e^{-x}}e^{x/2}\,dx.
\end{aligned}
\]

Because the first bump is real and even, its autocorrelation \(h\) is also real and even. It is supported in \([-1,1]\). Exact rational logarithm bounds verify \(\log2<1<\log3\), so the **only** nonzero von Mangoldt input is 2.

Write

\[
m_1=\int_{\mathbb R}f(t)e^{t/2}dt,\quad
K(x)=\frac{e^{x/2}}{e^x-e^{-x}}.
\]

The pole term is precisely \(P=2m_1^2\); the finite prime term is

\[
P_2=-\sqrt2\log2\,h(\log2).
\]

The first genuine arithmetic LF-core diagonal therefore has a nonzero *negative* prime contribution, unlike the earlier narrow support lattice.

## 3. Remove the gamma singularity exactly

Let \(h_0=h(0)\). For real compactly supported \(f\), the autocorrelation identity gives

\[
D(x)=\int_{\mathbb R}|f(t)-f(t-x)|^2dt
=2[h_0-h(x)]\ge0.
\]

With \(R=1\), the full regularized archimedean contribution becomes

\[
A=J+h_0[-\log(4\pi)-\gamma-2I_1+T],
\]

where

\[
J=\int_0^1 K(x)D(x)dx,
\qquad
I_1=\int_0^1
\frac{e^{x/2}-1}{e^x-e^{-x}}dx,
\qquad
T=\int_1^\infty\frac{dx}{\sinh x}.
\]

The *infinite tail* and apparently singular regularizer have **closed forms**:

\[
T=\log\frac{e+1}{e-1},
\]

\[
I_1=\arctan z
 +\frac12\log\frac{e+1}{2}
 -\log\frac{e^{1/2}+1}{2},
\quad
z=\frac{e^{1/2}-1}{e^{1/2}+1}.
\]

Since \(0<z<1/4\), the alternating Taylor series for \(\arctan z\), truncated after 20 terms, has an explicitly bounded remainder at most \(z^{41}/41\). This is evaluated with outward interval arithmetic. **No numerical quadrature at a singular point or unjustified omission of the infinite tail.**

## 4. Rigorous error budget for all remaining integrals

Put \(y=(1-u^2)^{-1}\) and \(\phi(u)=e^{1-y}\). Direct differentiation yields

\[
\phi''(u)=\phi(u)y^2(4y^2-12y+6).
\]

For \(j\ge1\), \(y^je^{1-y}\le j^je^{1-j}\), and \(e>5/2\). Consequently

\[
|\phi'|<4,\quad
|\phi''|<
4\frac{2048}{125}+12\frac{108}{25}+6\frac85
<127.
\]

After the spatial scaling \(f(x)=\phi(2x)\), we have \(|f'|<8\) and \(|f''|<508\). The second derivative of \(f(u+x/2)f(u-x/2)\) is bounded by \(2\cdot508+2\cdot8^2=1144\).

For each fixed rational \(x\in[0,1]\),

\[
h(x)=2\int_0^{(1-x)/2}
f(u+x/2)f(u-x/2)du.
\]

The composite trapezoid formula at \(N\) subintervals is enclosed by the explicit smooth second-derivative remainder

\[
|h(x)-h_N(x)|
\le\frac{2\cdot1144}{12N^2}
\left(\frac{1-x}{2}\right)^3.
\]

Every numerical evaluation of \(f\) uses outward `mpmath.iv` interval arithmetic at an **exact rational point**. The same second-derivative reasoning gives moment bounds \(508\) for \(m_0\) and \(690\) for \(m_1\), since \(e^{1/4}<4/3\).

**Validated positive integral \(J\):** The autocorrelation \(h\) is nonincreasing for \(x\ge0\): an even, nonnegative, radially decreasing function admits a layer-cake representation by symmetric intervals, whose convolutions are nonincreasing in the shift. Thus \(D(x)=2(h_0-h(x))\) is nondecreasing; meanwhile \(K(x)\) is positive and decreasing.

Partition \([1/512,1]\) into nine consecutive dyadic bands, each with 256 exact rational cells. For any \([a,b]\), use

\[
K(b)D(a)\le K(x)D(x)\le K(a)D(b),
\]

where both \(D\) endpoints are themselves rigorously enclosed by the pointwise trapezoid certificates. Multiply by the exact rational cell width and sum.

For \(0<x<1/512\), use

\[
D(x)\le x^2\|f'\|_2^2\le64x^2,
\qquad K(x)\le1/x.
\]

Therefore

\[
0\le J_{[0,1/512]}\le32/512^2=1/8192.
\]

No delicate extrapolation near zero is used.

## 5. Full arithmetic and normalized interval certification

Compute the complete unnormalized Weil entry

\[
W(f*\widetilde f)=2m_1^2
-\sqrt2\log2\,h(\log2)
+J+h_0[-\log(4\pi)-\gamma-2I_1+T].
\]

The prime argument \(\log2\) is bracketed with an **all-rational atanh series**, and monotonicity of \(h\) bounds its convolution value at the unknown exact logarithm.

The program encloses each term and divides the full interval by the positive interval for \(m_0^2\). It accepts the proof ONLY if the **lower exact rational endpoint** of the normalized value is greater than \(1/1000\). A low-resolution run whose interval includes zero must fail closed. The serialization rounds *outward* to reproducible rational decimal endpoints; CI checks the serialized positivity again, without floating-point eigenvalues.

The initial local validated calculation at \(N=256\) half-interval trapezoid panels and 256 segments per dyadic band gave indicative **outward** ranges (these are not fixed evidence; regenerate with CI):

```text
raw pole          approximately [ 0.7349998,  0.7360640]
raw prime 2       approximately [-0.0195993, -0.0195786]
raw archimedean   approximately [-0.7147100, -0.7022229]
raw complete Weil approximately [ 0.0006907,  0.0142624]
normalized Weil   approximately [ 0.0018958,  0.0391868]
```

These broad but strictly positive intervals are *complete arithmetic enclosures* of one **actual, normalized LF-dense-core diagonal**. The numerical backend and all derived analytic bounds are trusted components pending independent review.

## 6. Reproduction

```bash
python -m pip install mpmath==1.3.0
python -m unittest discover -s tests -p 'test_riemann_weil_lf_core_first_diagonal.py' -v
python -m mathos.research.riemann_weil_lf_core_first_diagonal \
  --half-panels 256 --dyadic-panels 256 \
  --output artifacts/riemann/weil_lf_core_first_diagonal.json
```

Tests include a deliberately insufficient-resolution case that fails rather than pretending positivity, exact bump matching, analytic derivative majorants, rational dyadic support, closed gamma regularization, the nonzero prime-2 term, normalization, and a portable strict positive scalar certificate.

## 7. Remaining RH-equivalent work

This verifies **only the first diagonal** of the new LF-dense compact core. It does not compute even its first genuine off-diagonal Weil entry, nor any higher-dimensional PSD Schur condition. An all-index theorem for every finite prefix remains precisely the Weil positivity obstruction equivalent to RH. The fact that the infinite core is analytically LF-dense does **not** permit extrapolation from finitely many certified matrices.

**Source:** Masatoshi Suzuki, *On the Hilbert space derived from the Weil distribution*, equation (3.3), https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6 . Relevant MathOS groundwork: PR #83 (dense core), #91 (lattice obstruction) and #92 (prime-power support workflow).

**No RH proof, universal Weil PSD theorem, complete Weil Hilbert-space construction or independent formal mathematical verification is asserted.**
