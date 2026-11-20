# MathOS BSD milestone 01: an explicit rank-two elliptic family

**Status: working manuscript / mathematical novelty not established / not a BSD proof.**

This is the algebraic milestone behind a PDF and LaTeX manuscript for independent mathematical review. The MathOS [007 baseline](../MILLENNIUM_ATTACK_007.md) proves only a partial-Euler-factor information limitation; [BSD research routes](https://github.com/tltmgnt/MathOS/pull/49) point toward high-rank analytic/arithmetic comparisons.

## Explicit elliptic family and polynomial invariants

For an indeterminate T over Q, set

\[
E_T:\quad y^2+y=x^3+(1+T)x^2-(2+T)x.
\]

Two globally defined points are P=(0,0) and Q=(1,0). Direct substitution proves they lie on the generic curve.

The generalized Weierstrass invariants are

\[
c_4(T)=16(T^2+5T+7),
\]

\[
\Delta(T)=16T^4+144T^3+472T^2+696T+389,
\]

and

\[
j(T)=4096(T^2+5T+7)^3/\Delta(T).
\]

The discriminant is not the zero polynomial because Δ(0)=389. Thus the generic fiber is nonsingular and all but finitely many rational parameters give smooth elliptic curves. The j-invariant is nonconstant because the numerator has degree six and the denominator degree four, so this family is non-isotrivial.

## Rank-two family theorem (using named external results)

**Theorem.** P and Q are linearly independent in E_T(Q(T)). All but finitely many rational smooth fibers E_t(Q) have rank at least two. Infinitely many of those fibers are pairwise nonisomorphic.

**Proof.** At T=0 the curve is y²+y=x³+x²−2x, precisely [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1), whose rational Mordell–Weil group is recorded as Z² with explicit independent generators (0,0) and (1,0). See LMFDB's [reviewed reliability statement](https://www.lmfdb.org/knowledge/show/rcs.rigor.ec.q) for the provenance of its rigorous rank computations. A relation mP+nQ=O over Q(T) would specialize on the smooth fiber T=0 to mP(0)+nQ(0)=O, forcing m=n=0. Hence the generic rank is at least two.

By [Silverman's specialization theorem](https://doi.org/10.1017/S0004972724001175) (original source: J. H. Silverman, *Heights and the specialization map for families of abelian varieties*, J. reine angew. Math. **342** (1983), 197–211), almost all smooth rational fibers preserve the two independent sections. A nonconstant rational j-function takes infinitely many rational values, so infinitely many resulting elliptic curves are pairwise nonisomorphic. **QED.**

The theorem does not determine the exact generic rank. It depends on **previously established LMFDB generators** and a **published specialization theorem**, not on finite point counting.

## A rank-three benchmark at T=2

The specialization is y²+y=x³+3x²−4x. Setting X=x+1 changes the cubic to X³−7X+6. This is [LMFDB 5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077/a/1), with recorded algebraic rank **3**, analytic rank **3**, and three Mordell–Weil generators (1,0), (2,0), (0,2). The initial two generators correspond to the specializations of P and Q.

A higher-rank **specialization** is established by the cited record; this cannot be called a **rank jump** until the exact generic rank is shown to equal two.

## Exact arithmetic and reproducibility

The standard-library [Python polynomial audit](../../../mathos/research/bsd_rank_two_family.py) computes the invariants as identities in Z[T] and checks the two benchmark discriminants and coordinate translation. The [unit test](../../../tests/test_bsd_rank_two_family.py) confirms the polynomial algebra and that report labels never claim a BSD proof.

Run from repository root:

    python -m unittest discover -s tests -p 'test_bsd_rank_two_family.py' -v
    python -m mathos.research.bsd_rank_two_family

**Scope:** These checks do not independently recompute the LMFDB rank certificates or analytic orders, prove Silverman's theorem, or establish mathematical novelty.

## Next unsolved research milestone

Find an effectively specified infinite set S of rational parameters for which one proves, **without using BSD as an assumption**, the exact comparison

\[
\operatorname{ord}_{s=1}L(E_t,s)=\operatorname{rank}E_t(\mathbb Q)\ge2\qquad(t\in S).
\]

This remains an **open research goal**, not a result of the present note. Even a completed theorem for such a family would not settle BSD for every elliptic curve over Q.

## Caveats, references and review

- A rank-two family constructed by propagating known rational sections through a non-isotrivial elliptic surface uses established methods. **No claim of novelty** is made.
- External arithmetic sources: LMFDB [389.a1](https://www.lmfdb.org/EllipticCurve/Q/389/a/1) and [5077.a1](https://www.lmfdb.org/EllipticCurve/Q/5077/a/1).
- Specialization source: J. H. Silverman (1983), supplemented by M. Melistas, *Low rank specialisations of elliptic surfaces*, Bull. Aust. Math. Soc. **112** (2025), 118–127.
- BSD official target: [Clay Mathematics Institute](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/), **unsolved**.
- **AI disclosure:** ChatGPT assisted with constructing and drafting the family, calculating the invariants and typesetting. An author must independently review the mathematics and submit accurate journal declarations.
- Canonical status: NOT_CERTIFIED; ANALYTIC_FAMILY_COMPARISON_NOT_PROVED; NOVELTY_NOT_ESTABLISHED; BSD_NOT_PROVED.
