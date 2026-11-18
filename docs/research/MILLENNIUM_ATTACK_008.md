# Millennium research attack 008 — exact 2D Z₂ gauge strip and a continuum scaling pitfall

**Date:** November 18, 2026  
**Track:** Yang–Mills Existence and Mass Gap (after research attacks 003–007 on P-vs-NP, RH, Hodge and BSD).  
**Status:** BOUNDED_RESEARCH / NOT_CERTIFIED / NO_YANG_MILLS_SOLUTION.  
**Novelty:** NONE CLAIMED. This is a classical solvable finite **two-dimensional abelian** lattice gauge model, not 4D non-Abelian Yang–Mills theory.

The [Clay Mathematics Institute's official statement](https://www.claymath.org/millennium/yang-mills-the-maths-gap/) and [Jaffe–Witten problem formulation](https://www.claymath.org/wp-content/uploads/2022/06/yangmills.pdf) demand, for each compact simple gauge group, a nontrivial quantum Yang–Mills theory on four-dimensional Euclidean space, the required axiomatic reconstruction, and a strictly positive **physical spectral** mass gap. A finite Z₂ toy model satisfies none of these requirements.

## The finite gauge model

Consider a 1×n rectangular strip of square plaquettes with **open** boundary conditions, with n top horizontal links, n bottom horizontal links and n+1 vertical links: 3n+1 independent Z₂ link spins.

Write each link spin as \(\sigma_e=(-1)^{b_e}\) with bit \(b_e\in\{0,1\}\). For plaquette \(i\),

\[
W_i=T_i B_i V_i V_{i+1}\in\{+1,-1\}
\]

is the product of its four links. A local gauge transformation at a vertex flips all adjacent links; it flips zero or two edges of each plaquette and therefore leaves its Wilson sign invariant.

The boundary Wilson loop is

\[
W_{\partial}=\prod_{i=1}^{n}W_i,
\]

since every interior vertical edge appears twice and its square is one. For integer coupling weight \(t\ge1\), give each configuration relative positive weight

\[
w(\sigma)=\prod_{i=1}^{n}
\begin{cases}t & W_i=+1,\\1&W_i=-1.\end{cases}
\]

This is the usual exponential single-plaquette weight exp(β W_i) up to normalization, if \(t=e^{2\beta}\). Integer t permits *exact rational* verification without floating-point sign tests.

## Theorem 1 — exact partition and boundary Wilson expectation for every strip length

For **every** integer \(n\ge0\) and \(t\ge1\),

\[
\boxed{Z_n(t)=2^{2n+1}(t+1)^n},
\qquad
\boxed{\sum_{\sigma}w(\sigma)W_{\partial}=2^{2n+1}(t-1)^n},
\]

and therefore

\[
\boxed{\left\langle W_{\partial}\right\rangle_{n,t}
=\left(\frac{t-1}{t+1}\right)^n}.
\]

**Proof.** Fix any desired plaquette-sign word \((W_1,\ldots,W_n)\). Choose the n top and n+1 vertical links arbitrarily. For each plaquette, its required sign uniquely determines the bottom link \(B_i=W_iT_iV_iV_{i+1}\). Thus all \(2^n\) plaquette-sign words occur, and *each* has exactly \(2^{2n+1}\) link preimages. Summing the weights over sign words gives the binomial factor \((t+1)^n\), since one plaquette contributes either t (positive) or 1 (negative). Inserting the boundary Wilson product changes the sign of each negative-plaquette contribution, giving \((t-1)^n\). Multiplying by the common fiber count and dividing establishes the theorem. This also covers n=0. \(\square\)

For \(t>1\), this gives an exact finite 2D Wilson-loop area law \(q^n\), where \(q=(t-1)/(t+1)\) lies strictly between zero and one. **An area-law rate is not a Hamiltonian mass gap.**

## Theorem 2 — a regulator trajectory requiring precise units

This is an artificially specified coupling trajectory, not a proposed 4D running coupling. Let the lattice spacing be \(a_k=1/k\) and let \(t_k=k^2+1\). Then

\[
q_k=\frac{k^2}{k^2+2}\in(0,1).
\]

Each finite lattice has a strictly positive *per-plaquette* exponential decay rate. Yet the effective Wilson-loop exponent per unit **long-side physical length** for this **one-plaquette-wide shrinking strip** is

\[
\gamma_k=-\frac{\log q_k}{a_k}
=k\log(1+2/k^2),\qquad
0<\gamma_k\le\frac2k\longrightarrow0,
\]

using \(\log(1+x)\le x\). For a long side of physical length 1, take \(n=k\) and apply the exact Bernoulli/union inequality:

\[
0\le1-q_k^k\le k(1-q_k)
=\frac{2k}{k^2+2}\le\frac2k\longrightarrow0.
\]

Thus \(q_k^k\to1\) even though q_k is strictly less than one for each finite regulator. **This is a warning against deriving regulator-uniform physical statements from a bare positive lattice-unit exponent.**

**Critical dimension warning:** the strip's physical width also shrinks like \(a_k\). The coefficient above is a Wilson-loop rate **per long-side length**, *not* a particle mass, transfer-matrix spectral gap, or string tension. Indeed the *area-normalized* coefficient for the same model is

\[
\sigma_k=-\frac{\log q_k}{a_k^2}
=k^2\log(1+2/k^2)\longrightarrow2,
\]

so it does **not** vanish. The model cannot demonstrate a vanishing Yang–Mills mass gap. It demonstrates why a proof must identify its observable, physical normalization, continuum scaling and spectral reconstruction separately. \(\square\)

## Formal verification and independent finite regression

The Lean 4.14.0 source [YMZ2Strip.lean](../../formal/YMZ2Strip.lean) checks four adjacent-pair corner flips of a **single plaquette**, the reversal under a one-edge flip, abstract independent-parity weight recurrences \((t+1)^n\) and \((t-1)^n\), and elementary integer coupling identities.

**Lean does not formalize arbitrary strip geometry, the all-n link-fiber count, a continuum theory, a physical Hilbert space or the Clay mass gap.** The all-n counting proof and the logarithmic inequality above are *paper arguments*, not Lean theorems.

A separate [standard-library Python checker](../../mathos/research/ym_z2_strip_008.py) independently enumerates the **actual link configurations**, computes plaquette parities, outer boundary signs, exact weighted partition sums and numerators, all local vertex gauge flips on strips with n≤3, and exact rational rescaling inequalities. It checks n=0,…,5 and t∈{1,2,5}: **224,694 link configurations across 18 cases**. A separate [seven-test suite](../../tests/test_ym_z2_strip_008.py) rejects invalid inputs, demands exact fiber counts, confirms boundary telescoping, and prohibits promotion to a full 4D Yang–Mills claim.

Replay with Lean 4.14.0 in the repository root:

~~~sh
lean formal/YMZ2Strip.lean
python -m unittest discover -s tests -p 'test_ym_z2_strip_008.py' -v
python -m mathos.research.ym_z2_strip_008 \
  --max-width 5 --scaling-max-k 16 \
  --output artifacts/millennium008/z2_strip_audit.json
~~~

The [GitHub Actions verification workflow](../../.github/workflows/ym-z2-strip-008.yml) runs these checks and preserves an exact JSON evidence artifact with 30-day retention.

## Unresolved official Yang–Mills proof obligations

The real problem demands, for **every compact simple gauge group**, a nontrivial **four-dimensional continuum quantum field theory**, suitable Wightman/Osterwalder–Schrader-type axiomatic reconstruction, and a positive **physical spectral gap**. None is constructed here. The canonical MathOS obligations **YM.continuum**, **YM.axioms** and **YM.uniform_gap** remain OPEN / NOT_CERTIFIED.

Next serious research must address actual 4D non-Abelian lattice fields and regulator/volume-uniform **physically normalized** estimates, together with tightness, reconstruction and noncircular links to the Hamiltonian spectrum. Such estimates would still need independent mathematical expert scrutiny. No Millennium proof, mathematical novelty, peer review or automatic future-work commitment is claimed.

External context: [CMI official statement](https://www.claymath.org/millennium/yang-mills-the-maths-gap/), [Jaffe–Witten formal problem description](https://www.claymath.org/wp-content/uploads/2022/06/yangmills.pdf), and [Z₂ Wilson-loop lattice notes](https://msguima.github.io/wiki/courses/generalized-symmetries-course/notes/week-05-wegner-z2-gauge-theory).