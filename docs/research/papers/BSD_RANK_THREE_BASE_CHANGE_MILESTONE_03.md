# MathOS BSD Milestone 03 — a quadratic base change with three independent sections

**Status:** exact algebraic polynomial identities and a rank-three family argument **using externally documented rank and specialization theorems**. **NOVELTY NOT ESTABLISHED / EXACT HIGH-RANK BSD EQUALITY NOT PROVED / NOT A BSD SOLUTION.**

**Relationship to existing work:** This branch is stacked on [Milestone 02 (PR #51)](https://github.com/tltmgnt/MathOS/pull/51), which in turn builds on [Milestone 01 (PR #50)](https://github.com/tltmgnt/MathOS/pull/50). It does not change the canonical open MathOS BSD proof obligations. A separate, typeset PDF and LaTeX are supplied to the author for review.

## 1. The explicit quadratic base change

The prior family over \(\mathbf Q(T)\) was

\[
E_T:\quad y^2+y=x^3+(1+T)x^2-(2+T)x,\quad P=(0,0),\quad Q=(1,0).
\]

Setting \(x=-1\) in this equation gives \(y^2+y=2+2T\). We force a third rational section by setting \(y=U\), hence

\[
T=\frac{U^2+U-2}{2},\qquad S=U(U+1).
\]

The base-changed family is

\[
\mathcal E_U:\quad y^2+y=x^3+\frac{S}{2}x^2-\frac{S+2}{2}x
\]

with **three global sections**

\[
P=(0,0),\qquad Q=(1,0),\qquad R=(-1,U).
\]

These are identities: at \(P\) and \(Q\) both sides vanish; at \(R\) the right-hand side is \(S=U^2+U\). For every **integer** \(u\), \(S=u(u+1)\) is even, so the fiber has an integral generalized Weierstrass model.

## 2. A polynomial certificate of universal nonsingularity

The generalized Weierstrass invariants are

\[
c_4(U)=4(U^2+3)(U^2+2U+4),
\]

\[
\Delta(U)=U^8+4U^7+16U^6+34U^5+65U^4+78U^3+94U^2+60U+37.
\]

Direct expansion verifies the **identity**

\[
256\,\Delta(U)=(2U+1)^8+36(2U+1)^6
+430(2U+1)^4+2868(2U+1)^2+6137.
\]

Every term on the right is nonnegative for real \(U\) and the constant is positive. Therefore **\(\Delta(u)>0\) for every real \(u\)**, in particular every rational fiber is nonsingular. Also \(j=c_4^3/\Delta\) is nonconstant (the numerator and denominator have degrees 12 and 8, respectively); the family is **non-isotrivial**.

## 3. An externally certified independent triple at U=2

At \(U=2\), \(S=6\), so

\[
\mathcal E_2:y^2+y=x^3+3x^2-4x.
\]

The coordinate translation \(X=x+1\) yields \(y^2+y=X^3-7X+6\), the minimal model of [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077/a/1). Under this isomorphism our sections become

\[
P_2\longmapsto(1,0),\quad Q_2\longmapsto(2,0),\quad R_2\longmapsto(0,2).
\]

**LMFDB externally documents these three points as independent Mordell–Weil generators of rank 3**. Their independence is not established by the local polynomial-checking script. The use of an independently reviewed rank record is part of the proof's explicit provenance.

## 4. The family-level rank theorem

**Theorem (classical specialization argument).** The three sections \(P,Q,R\) are independent in \(\mathcal E(\mathbf Q(U))\). There is a finite subset \(F\subset\mathbf Q\) such that

\[
\operatorname{rank}\mathcal E_u(\mathbf Q)\ge3\qquad\text{for every }u\in\mathbf Q\setminus F.
\]

Infinitely many of these fibers are pairwise nonisomorphic; infinitely many may be obtained by restricting \(u\) to integers outside \(F\).

**Proof.** A relation \(aP+bQ+cR=\mathcal O\) over \(\mathbf Q(U)\) would specialize at the smooth fiber \(u=2\) to a relation among the independent generators of 5077.a1, forcing \(a=b=c=0\). Thus the generic rank is at least three. Since the family is non-isotrivial, Silverman's **external specialization theorem** implies that the specialization homomorphism is injective for all but finitely many rational parameters. All real fibers are nonsingular by the preceding identity, so no rational singular fibers need be excluded. The nonconstant \(j\)-invariant assumes infinitely many values even when restricted to the cofinite subset of integers. **QED.**

**Known exceptions:** At \(u=1,-2\), the parameter \(T=(u^2+u-2)/2\) is \(0\), so the fiber is [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1) of rank 2. Consequently **both 1 and -2 must belong to \(F\)**. No complete or effective exceptional set is established. The values \(u=2,-3\) both give rank-three curve 5077.a1; the third point is inverted when \(u\) changes from 2 to -3.

## 5. Analytic information and the exact remaining gap

For every rational elliptic curve \(E\), the established Gross–Zagier–Kolyvagin theorem says that analytic rank \(0\) or \(1\) implies equality with the algebraic rank. Its contrapositive implies:

\[
\operatorname{rank}E(\mathbf Q)\ge2
\quad\Longrightarrow\quad
\operatorname{ord}_{s=1}L(E,s)\ge2.
\]

Thus for all \(u\notin F\),

\[
\operatorname{rank}\mathcal E_u(\mathbf Q)\ge3,\qquad
\operatorname{ord}_{s=1}L(\mathcal E_u,s)\ge2,\qquad
L(\mathcal E_u,1)=L'(\mathcal E_u,1)=0.
\]

If the **individual root number** is independently shown to be \(-1\), functional-equation parity raises the analytic order lower bound to \(3\). **The existence of infinitely many such negative-sign fibers is not proved here.** Neither the exact generic rank, the exact analytic rank for general \(u\), nor any equality of the two is established.

**Next open milestone:** prove a noncircular, unconditional exact analytic–algebraic equality of rank at least three for an effectively identified infinite set of rational parameters. Such a family theorem, if original, would require independent specialist validation and would **still not** settle general BSD for every elliptic curve over \(\mathbf Q\).

## 6. Exact verification and scope separation

- [Source](../../../mathos/research/bsd_rank_three_family.py) checks polynomial invariants and sum-of-even-powers discriminant identity **symbolically over Z[U]**, the three section identities, and the coordinate translation at \(u=2\).
- [Test](../../../tests/test_bsd_rank_three_family.py) checks explicit non-promotion fields and mathematical identities.
- [GitHub Actions workflow](../../../.github/workflows/bsd-rank-three-family.yml) runs the exact-algebra audit. A successful result does **not** verify external rank-three generators, Silverman's theorem, higher analytic rank, mathematical novelty or BSD.

Run after Milestone 01/02 have been merged, or on this stacked branch:

    python -m unittest discover -s tests -p 'test_bsd_rank_three_family.py' -v
    python -m mathos.research.bsd_rank_three_family

**Sources:** [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1), [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077/a/1), J. H. Silverman, *Heights and the specialization map for families of abelian varieties*, J. reine angew. Math. 342 (1983), 197–211, [Melistas on specialization](https://doi.org/10.1017/S0004972724001175), [Skinner on the low-analytic-rank theorem](https://annals.math.princeton.edu/2020/191-2/p01), [CMI official BSD target](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/).

**Research credit and disclosure:** ChatGPT assisted in proposing the quadratic base change, algebraic expansion, verification code and manuscript drafting. Human author review and proper journal disclosures are required. No mathematical novelty claim or status promotion is authorized by this note.
