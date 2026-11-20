# MathOS BSD Milestone 07 — an explicit cubic-descent upper bound for infinitely many ORIGINAL MathOS fibers

**ResearchOS / TECT X scientific status:** \`PARAMETER_DEPENDENT_RANK_UPPER_BOUND_DERIVED\`; \`NO_UNIFORM_RANK_THREE_BOUND\`; \`EXACT_RANK_THREE_INFINITE_FAMILY_NOT_PROVED\`; \`NOVELTY_NOT_ESTABLISHED\`; \`BSD_NOT_PROVED\`. **Canonical ResearchOs TECT has not run.** Five scoped evidence gates are documented separately in [TECT X evidence](BSD_CUBIC_DESCENT_07_TECTX.json).

**What is new relative to MathOS 06:** This is a genuine, although **weak and parameter-dependent**, 2-descent upper bound for a provably infinite **explicit arithmetic progression of parameters of the original MathOS family**, not merely a theorem for someone else's elliptic surface. The bound is derived from standard published number-field-descent and Minkowski results, so novelty has not been established.

## Abstract

For the original nonisotrivial MathOS elliptic family
\[
E_u:\quad y^2+y=x^3+\frac{u(u+1)}2x^2-\frac{u(u+1)+2}2x,
\]
we specify the infinite arithmetic progression \(u=24k\), \(k\in\mathbb Z\). An integral change of coordinates gives a cubic 2-division algebra with defining polynomial \(f_u(X)\). Reduction modulo 3 proves this cubic is irreducible for every parameter in the progression; a discriminant congruence modulo 8 proves that its splitting field has Galois group \(S_3\). The cubic field is totally real. The standard \(x-\theta\) Kummer descent, a norm-square condition, \(S\)-units, and the 2-torsion of a cubic ideal class group then yield an explicit effective rank upper bound, depending on the discriminant and its prime divisors, for every such specialization. A coarse bound using Minkowski's theorem requires no class-group calculation. Combining this with the generic three-section lower bound and Silverman's specialization theorem gives two-sided inequalities for all but finitely many integer parameters in the progression. The resulting upper bound grows with the parameter and is not the desired constant rank-three bound. No exact specialized-rank-three infinitude, analytic-rank equality, original theorem novelty, or Birch–Swinnerton–Dyer proof is claimed.

## 1. Infinite set and the 2-division cubic

Let \(u=24k\), \(k\in\mathbb Z\), and put \(s=u(u+1)\). The original curve is nonsingular for every real \(u\) by the discriminant identity established in [MathOS 03](BSD_RANK_THREE_BASE_CHANGE_MILESTONE_03.md). For integral \(u\), \(s\) is even and the model above is integral.

Make the **rational isomorphism**
\[
X=4x,\qquad Y=8y+4.
\]
Then \(E_u\) becomes
\[
Y^2=f_u(X),\qquad
f_u(X)=X^3+2sX^2-8(s+2)X+16\in\mathbb Z[X].
\]
The polynomial discriminant satisfies the **exact identity**
\[
\operatorname{disc}_X(f_u)=256D(u),
\qquad D(u)=s^4+10s^3+34s^2+60s+37.
\]
For each integer \(u\), \(s\ge0\) and hence \(D(u)\ge37>0\).

**Lemma (infinite \(S_3\)-cubic progression).** For every \(u\in24\mathbb Z\), the polynomial \(f_u\) is irreducible over \(\mathbb Q\); its splitting group is \(S_3\), and \(K_u=\mathbb Q[\theta_u]\) with \(f_u(\theta_u)=0\) is a totally real cubic number field.

**Proof.** As \(3\mid u\), we have \(s\equiv0\pmod3\) and
\[
f_u(X)\equiv X^3-X+1\pmod3.
\]
For every \(x\in\mathbb F_3\), \(x^3=x\), so this cubic has value \(1\) everywhere; it has no root and is irreducible over \(\mathbb F_3\), hence over \(\mathbb Q\). As \(8\mid u\), we have \(D(u)\equiv37\equiv5\pmod8\), which is impossible for a square integer. Thus \(256D(u)=\operatorname{disc}(f_u)\) is a positive nonsquare, forcing the Galois group of the irreducible cubic to be \(S_3\). Positivity of the discriminant gives three distinct real roots. **QED.**

In particular \(E_u(\mathbb Q)[2]=0\) for every \(u\in24\mathbb Z\). This is an explicit **infinite non-2-isogeny** regime; it cannot simply inherit Zywina's separate rational-2-torsion construction in [MathOS 06](BSD_RANK3_INFINITE_SOURCE_BENCHMARK_06.md).

## 2. Cubic \(x-\theta\) descent: a proven upper bound for every parameter

For the number field \(K=K_u\), let \(\Sigma=\Sigma_u\) be the **set of prime ideals of \(K\) lying over rational primes dividing \(2D(u)\)**. Let
\[
K(\Sigma,2)=
\{\,\alpha\in K^\times/K^{\times2}:
v_\mathfrak p(\alpha)\equiv0\pmod2\ \forall\mathfrak p\notin\Sigma\,\}.
\]
The standard cubic \(2\)-descent (the \(X-\theta_u\) map for \(Y^2=f_u(X)\)) injects
\[
E_u(\mathbb Q)/2E_u(\mathbb Q)
\hookrightarrow K(\Sigma,2)\cap\ker(N_{K/\mathbb Q})
\]
where the norm is taken modulo rational squares. This relies on the **external classical descent theorem**, and the chosen \(\Sigma\) is deliberately conservative because the polynomial discriminant is \(256D(u)\). One does not need local Selmer images to derive this coarse upper bound.

The standard exact sequence of \(\Sigma\)-units and squareclasses is
\[
0\to\mathcal O_{K,\Sigma}^\times/
\mathcal O_{K,\Sigma}^{\times2}
\to K(\Sigma,2)\to \mathrm{Cl}(\mathcal O_{K,\Sigma})[2]\to0.
\]
Since \(K\) is totally real cubic, Dirichlet's unit theorem gives the unit squareclass space dimension \(3+|\Sigma|\). Because \(N_{K/\mathbb Q}(-1)=-1\) is **not** a square in \(\mathbb Q\), the norm kernel has dimension at most one less than \(K(\Sigma,2)\). As the cubic is irreducible, \(E_u(\mathbb Q)[2]=0\), so
\[
\boxed{\operatorname{rank} E_u(\mathbb Q)
\le 2+|\Sigma_u|+
\dim_{\mathbb F_2}\mathrm{Cl}(\mathcal O_{K_u,\Sigma_u})[2].}\tag{A}
\]

The number of prime ideals above a rational prime in a cubic field is at most three. Thus \(|\Sigma_u|\le3(1+\omega(D(u)))\), where \(\omega(n)\) counts **distinct** rational prime divisors. Localization gives a quotient of \(\mathrm{Cl}(\mathcal O_K)\), whose 2-rank cannot increase under quotient. Therefore
\[
\boxed{\operatorname{rank}E_u(\mathbb Q)
\le 5+3\omega(D(u))+
\dim_{\mathbb F_2}\mathrm{Cl}(\mathcal O_{K_u})[2].}\tag{B}
\]

This is a **descent-based, family-specific upper bound** for **every** \(u\in24\mathbb Z\); the class-group dimension is not evaluated by the Python script. Formula (A) could be significantly sharper if its actual prime splitting and \(\Sigma\)-class group were independently computed.

## 3. A completely explicit (large) bound using Minkowski

Define
\[
N(u)=\Big\lceil\frac{32}{9}\sqrt{D(u)}\Big\rceil.
\]
The field discriminant \(|d(K_u)|\) divides \(\operatorname{disc}(f_u)=256D(u)\) as the square of an index, hence \(|d(K_u)|\le256D(u)\). Minkowski's bound for a totally real cubic field says every ideal class has an integral ideal of norm at most
\[
\frac{3!}{3^3}\sqrt{|d(K_u)|}=\frac29\sqrt{|d(K_u)|}
\le\frac{32}{9}\sqrt{D(u)}.
\]
If \(h_K\) is the class number, the count of ideals of norm \(n\) in a degree-three field is at most the ternary divisor function \(d_3(n)\) (coefficientwise domination of its Dedekind zeta Euler factors by \(\zeta(s)^3\)). Therefore
\[
h_K\le\sum_{n\le N(u)}d_3(n)\le N(u)^3.
\]
As \(|\mathrm{Cl}(K)[2]|\le h_K\), the 2-rank is at most \(3\lceil\log_2 N(u)\rceil\).

Substituting into (B) yields the explicit theorem:

\[
\boxed{\displaystyle
\forall\,k\in\mathbb Z:\qquad
\operatorname{rank}E_{24k}(\mathbb Q)\le
B(24k):=5+3\omega(D(24k))+
3\big\lceil\log_2 N(24k)\big\rceil.}\tag{C}
\]

**The result is fully unconditional conditional only on the standard, established descent, unit, class-group and Minkowski theorems cited above; the derivation is self-contained once those theorems are accepted.** Computing \(B(u)\) requires only integer arithmetic, integer square root and factorization of the explicitly given integer \(D(u)\). A computationally cheap but weaker upper bound replaces \(\omega(D)\) with \(\lfloor\log_2 D\rfloor\).

The prior generic three-section construction plus Silverman's specialization theorem proves there exists a **finite**, not explicitly determined, set \(F\subset\mathbb Q\) such that for every \(24k\notin F\):
\[
\boxed{3\le\operatorname{rank}E_{24k}(\mathbb Q)\le B(24k).}\tag{D}
\]
Because \(24\mathbb Z\setminus F\) is infinite, this is a proven **two-sided family-specific bound on an explicitly given infinite arithmetic progression**, not a uniform exact-rank-three theorem.

## 4. Small reproducible numerical certificates

The [exact Python auditor](../../../mathos/research/bsd_cubic_descent_07.py) and [unit tests](../../../tests/test_bsd_cubic_descent_07.py) check (i) the symbolic cubic discriminant formula; (ii) the irreducibility/Galois congruences; (iii) the exact integer prime-divisor count; (iv) an exact integer-square-root implementation of \(N(u)\); and (v) the deliberately conservative status labels. It does **not** compute the cubic class group or \(2\)-Selmer group.

| Parameter \(u\) | \(D(u)\) | \(\omega(D(u))\) | Explicit upper bound \(B(u)\) |
|---:|---:|---:|---:|
| \(-24\) | 94,536,886,789 | 2 | 74 |
| \(0\) | 37 | 1 | 23 |
| \(24\) | 131,772,276,037 | 1 | 71 |

The \(u=0\) specialization has externally documented rank one, so its large bound is **far from sharp**. The other numbers are bounds, not exact-rank assertions. \(u=24\) may or may not be among Silverman's finitely many rank-lower-bound exceptions; no independent rank-three lower certificate has been computed for that particular fiber.

An **optional Magma work order** at [BSD_CUBIC_DESCENT_07_MAGMA.m](../../../mathos/research/BSD_CUBIC_DESCENT_07_MAGMA.m) is provided to compute actual \(2\)-Selmer groups and \`RankBounds\` for individual curves using a specialist CAS. **It is supplied as source, not executed or authenticated.** See the official [Magma handbook](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html).

From a checkout of this branch:

    python -m unittest discover -s tests -p 'test_bsd_cubic_descent_07.py' -v
    python -m mathos.research.bsd_cubic_descent_07 --k 1

## 5. ResearchOS / TECT X: decisive limit

The approach proves **an explicit upper bound \(B(u)\) for infinitely many original MathOS fibers**, not the strategically desired **constant** rank \(\le3\) on an infinite subset. \(B(u)\) may grow as \(u\) grows, and the class-group version includes uncomputed arithmetic invariants. No novel theorem priority is asserted. The canonical ResearchOs controller has not independently validated any mathematics.

**Next scientific gate:** Find an independently justified infinite \(S\subset24\mathbb Z\) with a *uniform* cubic \(2\)-Selmer upper bound of dimension three (or an alternative descent bound that forces rank \(\le3\)). Prove the set infinite and that the existing three sections specialize independently there. That would yield exact rank three; no such set is provided here. Additional analytic work would still be required for higher-rank BSD equality.

### References

1. Michael Stoll et al., [Lean formalization of 2-descent and unramified \(x-\theta\) classes](https://github.com/MichaelStollBayreuth/EllipticCurves), section “Explicit 2-descent and the 2-Selmer group” (external published project).
2. [Magma Handbook: Mordell–Weil Groups and Descent Methods](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html).
3. J. H. Silverman, *Heights and the specialization map for families of abelian varieties*, J. reine angew. Math. 342 (1983), 197–211.
4. M. Melistas, *Low Rank Specialisations of Elliptic Surfaces*, Bulletin of the Australian Mathematical Society (2025), [Cambridge](https://doi.org/10.1017/S0004972724001175); deals with a different rational-2-torsion situation.
5. [MathOS Milestone 05](BSD_RANK_EXACT_MILESTONE_05.md), [MathOS Milestone 06](BSD_RANK3_INFINITE_SOURCE_BENCHMARK_06.md).
6. [Clay Mathematics Institute: BSD conjecture](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/) (unsolved).

**AI-use and review:** ChatGPT assisted with this derivation, literature comparison, numerical code and manuscript. The computational tests are not a replacement for external mathematical review. No canonical MathOS proof status, TECT assurance state, or BSD truth status is promoted.
