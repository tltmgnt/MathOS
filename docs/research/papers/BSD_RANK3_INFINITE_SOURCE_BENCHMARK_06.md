# MathOS Milestone 06 — ResearchOS / TECT X: exact-rank-three infinite-fiber benchmark

**Scope verdict:** A **2026 mathematical preprint by David Zywina** proves an exact-rank-three infinite-fiber result for a **different explicitly presented elliptic surface**. MathOS implements a comparison and finite exact-algebra/Kummer-image audit. **No proof is supplied for infinitely many rank-three specializations of the existing MathOS E_U family.** No new-to-literature theorem, independently verified peer review, or BSD result is claimed.

**Sources:** D. Zywina, *On the infinitude of elliptic curves over a number field with prescribed small rank* (11 February 2026), [arXiv:2602.10865](https://arxiv.org/abs/2602.10865) and [author PDF](https://davidzywina.github.io/papers/LowRanks.pdf). In particular: **Theorem 4.1**, **Lemmas 5.13–5.15**, **§6.4 Rank 3 case**. Relevant earlier work: Zywina, [arXiv:2502.01026](https://arxiv.org/abs/2502.01026), exact rank zero in infinitely many fibers of a *different* nonisotrivial surface. The source is a public preprint; do not claim journal acceptance.

## 1. Explicit rank-three comparator family from Zywina §6.4

Let \(t\) be rational and set

\[
a(t)=9725-98t^2,\qquad b(t)=7^4(t^2-4)(t^2-121).
\]

The published family and its rational-2-isogenous partner are

\[
Z_t: y^2=x^3+a(t)x^2+b(t)x,
\]

\[
Z'_t:y^2=x^3-2a(t)x^2+(a(t)^2-4b(t))x.
\]

The bad parameters are

\[
B=\left\{-11,-2,2,11,-\frac{3161}{280},\frac{3161}{280}\right\}.
\]

The discriminant of the displayed model is exactly

\[
\Delta(t)=-2^{10}3^25^27^{10}(t^2-4)^2(t^2-121)^2
\left(t^2-(3161/280)^2\right).
\]

For \(t\notin B\), these are nonsingular elliptic curves. The isogeny is defined over \(\mathbb Q\) because \(Z_t\) has the rational point \((0,0)\) of order two.

Zywina's Theorem 4.1 and §6.4 establish that **infinitely many rational parameters** \(t\) yield exactly

\[
\boxed{\operatorname{rank}Z_t(\mathbb Q)=3.}
\]

**This conclusion is sourced to that published online preprint, not newly proved by MathOS.** The source proves infinitude using arithmetic-prime patterns (Kai's theorem), local Selmer calculations, and a descent argument. It does not provide a short all-integer arithmetic progression with every member proven rank three.

## 2. A noncircular certificate-defined infinite set

We can make the *mathematical acceptance criteria* for the known exact-rank-three fibers explicit, without tautologically defining the set as "parameters of rank three."

Write \(\phi_t:Z_t\to Z'_t\) for the 2-isogeny and \(\widehat\phi_t\) for its dual, and define the 2-isogeny Selmer dimensions

\[
s_\phi(t)=\dim_{\mathbf F_2}\operatorname{Sel}_{\phi_t}(Z_t/\mathbb Q),\qquad
s_{\widehat\phi}(t)=\dim_{\mathbf F_2}\operatorname{Sel}_{\widehat\phi_t}(Z'_t/\mathbb Q).
\]

These Selmer groups are defined by the usual local squareclass conditions and are finite/computable in principle. The standard two-isogeny descent inequality gives

\[
\operatorname{rank}Z_t(\mathbb Q)
\le s_{\phi}(t)+s_{\widehat\phi}(t)-2.
\]

The following specific points are supplied by Zywina §6.4, and the MathOS audit checks their equations symbolically:

- \(P_0=(0,0)\);
- \(P_1=(7^4(t-2)(t+2),\ 115248\,t(t-2)(t+2))\);
- \(P_2=(7^2(t-2)(t+11),\ 4263(t-2)(t+11))\);
- \(Q_0=(0,0)\) on \(Z'_t\);
- \(Q_1=(630t+28449/4,\ 8820t^2+(177093/2)t-995715/8)\) on \(Z'_t\).

Their isogeny-descent squareclass representatives, up to rational squares, are

\[
C(t)=\{(t^2-4)(t^2-121),\quad t^2-4,\quad(t-2)(t+11)\},
\]

\[
C'(t)=\{-9(280t-3161)(280t+3161),\quad 9(280t+3161)\}.
\]

The product with two distinct linear factors in \(C'\) follows directly from the exact identity \(a^2-4b=-9(280t-3161)(280t+3161)\). It is checked from the model rather than copying any potentially repeated factor in the source typesetting.

Let \(d(t)\) and \(d'(t)\) be the dimensions of the spans of these respective squareclasses in \(\mathbb Q^\times/(\mathbb Q^\times)^2\).

Define the **certificate-defined set**

\[
\boxed{
S_{\rm cert}=
\{t\in\mathbb Q\setminus B:
d(t)=3,\quad d'(t)=2,\quad s_\phi(t)+s_{\widehat\phi}(t)\le5\}.
}
\]

**Every member of \(S_{\rm cert}\) has rank exactly three.** Indeed, the exhibited rational points and standard two-isogeny descent identity imply
\(\operatorname{rank}Z_t(\mathbb Q)\ge d(t)+d'(t)-2=3\),
while the independently computed Selmer upper dimensions imply rank at most \(5-2=3\).

**Why is this set infinite?** The *existing* source's proof of Theorem 4.1, specifically Lemmas 5.13–5.15 combined with the rank-three data in §6.4, constructs infinitely many rational \(t\) where the relevant point-class images and two isogeny Selmer spaces have dimensions 3 and 2. Those \(t\) lie in \(S_{\rm cert}\). This is an adaptation of the **source's published proof logic**, not an independently produced new infinite prime-pattern argument.

**Important computational limit:** the MathOS script computes \(d(t),d'(t)\) from the displayed rational points for individual rational parameters but **does not compute or independently verify the Selmer upper dimensions** \(s_\phi,s_{\widehat\phi}\). Passing the MathOS script for \(t=3\), for example, certifies only the lower bound \(\operatorname{rank}Z_3(\mathbb Q)\ge3\), not exact equality. The set is explicit via *effective mathematical certificate conditions*, **not a supplied list of infinitely many numerical \(t\)**.

## 3. The bridge to the original MathOS family is blocked

Previous MathOS Milestones 03–05 concern a **different** family

\[
E_u:y^2+y=x^3+\frac{u(u+1)}2x^2-\frac{u(u+1)+2}2x.
\]

Its generic algebraic rank has been derived as three **using an older published formula**; this does not imply infinitely many fibers have exact rank three.

Two structural differences prevent a direct copy of Zywina's current isogeny argument:

1. \(E\) has no known rational 2-torsion section. In fact at the smooth specialization \(u=2\), rational 2-torsion would require a rational root of \(4x^3+12x^2-16x+1\), but the rational-root candidates \(\pm1,\pm 1/2,\pm1/4\) all fail. Nontrivial 2-torsion sections in good characteristic-zero specialization would remain nontrivial, so no global rational 2-torsion section exists over \(\mathbb Q(u)\). In contrast \(Z_t\) has the explicit order-two point \((0,0)\) everywhere smooth.
2. The MathOS discriminant \(u^8+4u^7+16u^6+34u^5+65u^4+78u^3+94u^2+60u+37\) is positive for every real \(u\). It has **no rational zero** and therefore cannot factor completely into rational linear terms, unlike \(Z_t\)'s discriminant. Zywina's §4 theorem depends on this rational bad-fiber structure.

**Thus an exact-rank-three theorem for infinitely many fibers of the *MathOS* family remains open in this project**. An independently justified alternative (e.g. upper Selmer bounds using its 2-division cubic extension) is needed. Do not transfer the theorem to \(E_u\) merely because both families have generic rank three.

## 4. ResearchOS / TECT X evidence gates

This is a **five-gate TECT-inspired review**, not execution of the ResearchOs canonical runtime or five independent reproductions. The machine-readable audit is [here](BSD_RANK3_INFINITE_TECTX.v1.json).

| Gate | What is checked | Status |
|---|---|---|
| 1 — source and quantifiers | Exact paper, date, Theorem 4.1, §6.4, comparator-versus-MathOS distinction | PASS: source-grounded |
| 2 — independent finite algebra | Discriminant/isogeny polynomial identity and rational-point substitution | PASS: exact algebra |
| 3 — lower rank evidence | For selected rational \(t\), squareclass dimensions computed with exact rational factoring | PASS: bounded rank lower bound |
| 4 — infinitude & upper bound | Zywina's theorem cited; no own Selmer-group proof or infinite prime-pattern certificate produced | EXTERNAL THEOREM ONLY |
| 5 — transfer, novelty, assurance | MathOS-family transfer and independent expert originality remain unproved | BLOCKED / UNVERIFIED |

The ResearchOS canonical TECT state for any newly claimed original MathOS theorem remains **UNVERIFIED**. Passing CI establishes only correct arithmetic and scope records, not author/source authentication, independent reproduction, journal peer review or scientific novelty.

## 5. Reproduction

The implementation uses standard-library exact integer/rational arithmetic and verifies symbolic polynomial identities for the published Zywina family and its point coordinates:

    python -m unittest discover -s tests -p 'test_bsd_rank3_infinite_tectx.py' -v
    python -m mathos.research.bsd_rank3_infinite_tectx --numerator 3 --denominator 1

The tool reports rank-lower-bound evidence but always sets **exact_rank_3_certified=false** unless independently verified Selmer upper-bound proof is actually incorporated into a future revision. Do not submit a pass/fail alone as a publication-grade mathematical certificate.

## 6. Next original research problem

Prove that there exists an effectively described infinite set \(S_M\subset\mathbb Q\) such that

\[
\operatorname{rank} E_u(\mathbb Q)=3\quad\text{for all }u\in S_M
\]

and that membership is verified by a genuinely new descent/upper-rank argument valid for the original MathOS 03–05 family.

A theorem for exact **algebraic** rank alone would remain distinct from the much stronger **analytic** order equality in the BSD conjecture.

**Research and AI disclosure:** ChatGPT performed source comparison, helped derive certificate conditions, implemented finite exact checks and drafted this audit. The cited 2026 theorem and source construction belong to the original author. Independent number-theory review is required before originality or correctness claims beyond the cited paper.
