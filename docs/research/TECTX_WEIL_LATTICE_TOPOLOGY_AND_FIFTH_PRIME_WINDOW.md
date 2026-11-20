# TECT-X — Topological obstruction to extending the four-dimensional Weil certificate

**This PR solves two narrower mathematical questions, not RH.** The compact translates used in the fixed four-dimensional positive Weil Gram in PR #89 are **not dense in the Weil test topology**, even if extended to an infinite lattice; nevertheless, their ordinary \(L^2\) reference Gram is **exactly diagonal and perfectly conditioned** for every dimension. A separate fifth-direction arithmetic audit identifies precisely which new prime powers appear and proves an actual nonzero negative prime-19 contribution. It does **not** enclose the complete fifth Weil Gram or certify its positivity.

## 1. The precise density obstruction

Define the smooth bump \(\phi(u)=\exp(1-1/(1-u^2))\) on \(|u|<1\), zero otherwise, and the infinite sequence

\[
f_j(x)=\phi(8(x-3j/4)),\quad j=0,1,2,\ldots.
\]

The support of \(f_j\) is \([3j/4-1/8,3j/4+1/8]\). Consecutive supports are separated by open gaps of length **1/2**. In particular, **every function** in the linear span of the entire infinite lattice vanishes on the nonempty open interval \((1/8,5/8)\).

Choose any nonzero \(g\in C_c^\infty((1/8,5/8))\). Then \(g\) is orthogonal to every \(f_j\) in ordinary \(L^2(\mathbb R)\). Therefore the infinite span is **not dense in \(L^2\)**. More strongly, evaluation at any point in the gap is continuous in the canonical test-function topology on \(\mathcal D(\mathbb R)=C_c^\infty(\mathbb R)\), so no net or sequence of these translates can converge to a test function that is nonzero there. Hence the span is **not dense in the Weil-admissible LF test space**.

This non-density is a **formal obstruction** to promoting arbitrarily many lattice Gram certificates to global Weil positivity; it is **not** a counterexample to RH and does not negate a finite Gram positivity certificate.

## 2. Exact dimension-independent \(L^2\) reference Gram

Since each pair of distinct \(f_i,f_j\) has disjoint supports, the ordinary \(L^2\) Gram satisfies for *every* finite dimension

\[
L_{ij}=\langle f_i,f_j\rangle_{L^2}=\alpha\,\delta_{ij},
\quad
\alpha=\int_{-1/8}^{1/8}\phi(8x)^2\,dx.
\]

For \(|x|<1/16\), \(|8x|<1/2\), and so \(\phi(8x)>e^{-1/3}>2/3\). Therefore

\[
\boxed{\frac1{18}<\alpha<\frac14,\qquad \kappa_2(L_m)=1\quad\text{for every }m.}
\]

**Conclusion:** the coefficient-to-\(L^2\) conditioning is ideal on this family, and any eventual weakening of Weil quadratic-form eigenvalues **cannot** be blamed on coefficient ill-conditioning. However, good reference conditioning does not make a subspace dense or prove Weil positivity.

## 3. The genuine fifth arithmetic prime-support window

Add \(f_4(x)=\phi(8(x-3))\). The new off-diagonal convolution with \(f_0\) has exact support

\[
\operatorname{supp}(f_4*\tilde f_0)\subseteq
\left[\frac{11}{4},\frac{13}{4}\right].
\]

Use the fully rational identity for any positive integer \(n\), writing \(n=2^k y\) with \(1\le y<2\),

\[
\log n=k\log2+2\sum_{j=0}^{N-1}
\frac{t^{2j+1}}{2j+1}+R_N,
\qquad t=\frac{y-1}{y+1}\le\frac13
\]

with the **exact rational** remainder bound

\[
0\le R_N\le
\frac{2t^{2N+1}}{(2N+1)(1-t^2)}.
\]

Apply the same series to \(\log2\). At \(N=16\), rational comparisons verify

\[
\log15<\frac{11}{4}<\log16
\quad\text{and}\quad
\log25<\frac{13}{4}<\log26.
\]

The integers in the support window are thus precisely \(16,17,\ldots,25\). Their nonzero von Mangoldt terms occur exactly at

\[
\boxed{16=2^4,\quad17,\quad19,\quad23,\quad25=5^2.}
\]

The composite integers \(18,20,21,22,24\) are **not** prime powers, so their von Mangoldt coefficients are exactly zero. This extends the previous certified arithmetic support inventory without using any zeta-zero ordinates.

## 4. Strictly nonzero arithmetic prime-19 cross contribution

The Weil cross convolution at separation 3 obeys

\[
h_3(x)=\int_{-1/8}^{1/8}
\phi(8t)\phi(8(t+3-x))\,dt.
\]

Our exact rational logarithm enclosure gives

\[
\frac{147}{50}<\log19<\frac{59}{20},
\qquad \frac1{20}<3-\log19<\frac3{50}.
\]

For \(t\in[-1/32,0]\), both bump arguments have absolute value below \(1/2\), so each bump is strictly greater than \(2/3\). Integrating over this rational interval proves

\[
h_3(\log19)>\frac1{32}\cdot\frac49=\frac1{72}.
\]

Since \(\log19>147/50\) and \(\sqrt{19}<5\), its actual prime contribution to the logarithmic Weil formula is strictly negative:

\[
\boxed{
-\frac{\log19}{\sqrt{19}}h_3(\log19)
< -\frac{49}{6000}<0.
}
\]

This is a **partial arithmetic term bound**, not an interval enclosure of the entire cross entry. In particular, the pole, other prime powers and archimedean contributions may have either net effect. No fifth eigenvalue or Schur complement is claimed.

## 5. Why this matters for solving the theorem

The following two facts must be kept separate:

1. The translated-bump lattice has excellent, dimension-independent \(L^2\) conditioning and can support arbitrarily many rigorously studied finite matrices.
2. The lattice is **not** a dense core for the Weil criterion, so even positivity at *every* lattice dimension would not by itself prove RH.

An RH-relevant program must instead use an LF-dense compact test family (as in the distinct rational-bump construction of PR #83), prove continuity in the precise normalization, and establish positivity for **every** finite member of that dense core. All-index vanishing-negative-error bounds on a consistent nested Gram are already RH-equivalent (PR #84). No such global theorem is established here.

## 6. Reproduce

```bash
python -m unittest discover -s tests -p 'test_riemann_weil_lattice_topology_audit.py' -v
python -m mathos.research.riemann_weil_lattice_topology_audit \
  --output artifacts/riemann/tectx_weil_lattice_topology_audit.json
```

CI checks the exact rational logarithm expansion, complete fifth prime-power inventory, disjoint lattice supports, dimension-independent \(L^2\) condition number, a rigorous nonzero prime-19 bound, and explicit negative assurance flags for fifth PSD and global positivity.

**Review boundary:** The proofs are written and checked with exact rational arithmetic in Python, not independently verified in Lean or by mathematical referees. The legacy positive four-dimensional PR #89 remains a fixed-space certificate contingent on its classical formula and interval backend. RH, an all-index positive Weil criterion, and a complete positive Weil Hilbert space remain unproved.
