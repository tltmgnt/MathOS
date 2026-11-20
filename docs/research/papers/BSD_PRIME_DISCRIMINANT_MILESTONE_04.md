# MathOS BSD Milestone 04 — prime-discriminant root-number certificates

**WORKING RESEARCH NOTE / MATHEMATICAL NOVELTY NOT ESTABLISHED / INFINITE EXACT RANK EQUALITY NOT PROVED / BSD NOT SOLVED.**

This milestone extends [Milestone 03](BSD_RANK_THREE_BASE_CHANGE_MILESTONE_03.md) with **exact local/global root-number computations** for integer parameters whose discriminant is prime, and verifies a **second distinct externally documented rank-three fiber**. The mathematical content is a corollary of classical elliptic-curve reduction theory and source-identified external rank results, **not a novel BSD solution**.

## 1. Family and polynomial identities

Set \(S=u(u+1)\). For any integer \(u\), \(S\) is even and gives an integral model

\[
\mathcal E_u:\quad y^2+y=x^3+\frac{S}{2}x^2-\frac{S+2}{2}x.
\]

The sections \(P=(0,0), Q=(1,0), R=(-1,u)\) lie on each fiber. Its invariants are

\[
c_4(u)=4(u^2+3)(u^2+2u+4),
\quad c_6(u)=-8S^3-72S^2-144S-216,
\]

\[
D(u)=u^8+4u^7+16u^6+34u^5+65u^4+78u^3+94u^2+60u+37.
\]

The exact integer-polynomial identities are

\[
c_4(u)^3-c_6(u)^2=1728D(u),
\]

\[
256D(u)=(2u+1)^8+36(2u+1)^6+430(2u+1)^4+2868(2u+1)^2+6137>0.
\]

Thus all rational fibers are nonsingular. The involution \(u\mapsto-u-1\) preserves \(S\), the fiber, and all invariants; it sends \(R\) to its point inverse.

## 2. Prime-discriminant root-number theorem (standard reduction theory)

**Proposition.** If \(u\in\mathbb Z\) and \(p=D(u)\) is an ordinary rational prime with \(p\ge5\), then the displayed integral elliptic model is minimal and has reduction of Kodaira type \(I_1\) at \(p\), good reduction elsewhere, and conductor \(p\). Its global functional-equation root number satisfies

\[
w(\mathcal E_u/\mathbb Q)=\left(\frac{-c_6(u)}{p}\right).
\]

**Proof.** An integral equation of discriminant \(p\) has good reduction away from \(p\). The valuation \(v_p(D)=1\) ensures minimal multiplicative reduction at \(p\); \(c_4\) is a unit there. The reduction is split multiplicative precisely when \(-c_6\) is a square modulo \(p\). The local root number is \(-1\) in the split case, \(+1\) in the nonsplit case, \(+1\) at every other finite place, and \(-1\) at infinity. Their product gives the displayed Legendre symbol. This relies on the **external standard local reduction and local-root-number theorems**.

If the algebraic rank of one such fiber is *independently established to be at least two*, Gross–Zagier–Kolyvagin implies analytic rank at least two. If in addition the sign is \(-1\), the completed functional equation implies analytic rank at least three, hence \(L(E_u,1)=L'(E_u,1)=L''(E_u,1)=0\). Neither the exact analytic order nor the full BSD equality follows from these two inputs alone.

## 3. Two **distinct** external rank-three benchmarks

**u=2 (and its mirror u=-3).** Here \(S=6\) and \(D=5077\). The substitution \(X=x+1\) identifies the fiber with \(y^2+y=X^3-7X+6\), [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077a1/). Under this change the three sections become \((1,0),(2,0),(0,2)\), the listed independent Mordell–Weil generators. LMFDB records algebraic and analytic rank \(3\). Exact integer arithmetic gives \(c_6=-5400\), prime discriminant 5077, and \((5400/5077)=-1\).

**u=3 (and its mirror u=-4).** Here \(S=12\) and \(D=43669\). The substitution \(X=x+2\) identifies the fiber with \(y^2+y=X^3-19X+30\), [LMFDB 43669.a1](https://www.lmfdb.org/EllipticCurve/Q/43669a1/). The three sections become \((2,0),(3,0),(1,3)\), the listed independent generators. LMFDB records algebraic and analytic rank \(3\). Exact arithmetic gives \(c_6=-26136\), prime discriminant 43669, and \((26136/43669)=-1\).

These yield **four integer parameters but only two distinct elliptic-curve isomorphism classes**. The local audit verifies equations and signs; the **rank 3 and exact analytic order 3 assertions are sourced from LMFDB, not newly proved by the code**.

Other useful sanity checks:
- \(u=0,-1\): \(D=37\), sign \(-1\), and externally recorded rank 1 ([37.a1](https://www.lmfdb.org/EllipticCurve/Q/37a1/)).
- \(u=1,-2\): \(D=389\), sign \(+1\), and externally recorded rank 2 ([389.a1](https://www.lmfdb.org/EllipticCurve/Q/389a1/)).
- \(u=7,-8\): \(D=11700677\) is prime and sign is \(-1\), but **no rank certificate is claimed for those fibers**.

## 4. Deterministic computation and adversarial limits

[Python exact audit](../../../mathos/research/bsd_prime_discriminant_04.py) checks primality **by trial division through the integer square root**, computes invariants, computes the Legendre symbol by Euler's criterion, and checks mirror fibers. It uses no network data or approximate L-values. The finite default scan \(u=-8,\ldots,7\) finds ten parameters with prime discriminant, representing five isomorphism classes.

Run from the repository root:

    python -m unittest discover -s tests -p 'test_bsd_prime_discriminant_04.py' -v
    python -m mathos.research.bsd_prime_discriminant_04 --start -8 --end 7

**Limitations:**
1. The code does **not** establish whether \(D(u)\) is prime for infinitely many integers.
2. It does **not** establish algebraic rank or analytic rank for newly scanned fibers; reported 37/389/5077/43669 ranks are attributed to external LMFDB entries.
3. Exact root number \(-1\) imposes odd analytic order, **not exact order 3**.
4. It does **not** identify the finite exceptional set of Silverman's specialization theorem for the generic three-section family.
5. It does **not** prove higher-rank BSD for an infinite family or the general BSD conjecture, nor establish mathematical novelty.

## 5. The next mathematically open bridge

Establish an effectively described **infinite** set \(A\subset\mathbb Q\) for which the algebraic and complete complex analytic ranks are both independently certified and are **proved equal to a value at least 3** for each \(u\in A\), with all quantifiers and hypotheses explicit. Two rank-three benchmarks, sign calculations, and numerically approximated special values are **insufficient**.

## Provenance and independent review

- [MathOS 03](BSD_RANK_THREE_BASE_CHANGE_MILESTONE_03.md), [MathOS 02](BSD_ANALYTIC_DOUBLE_ZEROS_MILESTONE_02.md), [MathOS 01](BSD_RANK_TWO_FAMILY_MILESTONE_01.md)
- [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077a1/) and [LMFDB 43669.a1](https://www.lmfdb.org/EllipticCurve/Q/43669a1/), with documented generators and algebraic/analytic rank 3
- [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389a1/), [LMFDB 37.a1](https://www.lmfdb.org/EllipticCurve/Q/37a1/)
- J. H. Silverman, *Heights and the specialization map for families of abelian varieties*, J. reine angew. Math. 342 (1983), 197--211
- Gross--Zagier and Kolyvagin low-analytic-rank theorems (external)
- [On the fibres of an elliptic surface where the rank does not jump](https://www.cambridge.org/core/journals/bulletin-of-the-australian-mathematical-society/article/on-the-fibres-of-an-elliptic-surface-where-the-rank-does-not-jump/65EB1F7EF72A498724E6D7551A76C920) (standard local-root-number conventions)
- [CMI BSD problem](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/)

**AI disclosure:** ChatGPT assisted in proposing and implementing this benchmark, algebraic checks, testing, and manuscript drafting. Author and independent specialist review are required before submission. No canonical MathOS proof-obligation or Clay problem status is changed.
