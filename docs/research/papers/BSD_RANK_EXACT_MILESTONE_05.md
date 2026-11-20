# ResearchOS × TECT (five-pass) — MathOS BSD Milestone 05: exact generic rank

**Outcome:** a **proof of the exact algebraic function-field rank** of the MathOS 03/04 family, derived by a specialized use of a **previously published/general theorem**. This is **not** a new-to-literature theorem claim, **not** a statement that all specializations have rank 3, **not** an analytic-rank equality theorem and **not** a Birch–Swinnerton–Dyer proof.

**Research status:** \`EXACT_GENERIC_ALGEBRAIC_RANK_DERIVED_FROM_EXISTING_THEOREM\` / \`INDEPENDENT_EXPERT_REVIEW_PENDING\` / \`NOVELTY_NOT_ESTABLISHED\` / \`SPECIALIZATION_EXACT_RANK_NOT_PROVED\` / \`BSD_NOT_PROVED\`.

**Primary source:** F. Battistoni, S. Bettin and C. Delaunay, *Ranks of elliptic curves over Q(T) of small degree in T*, arXiv:2109.00738v1 (2021), **Theorem 1, degree-A=2 case**, [PDF](https://arxiv.org/pdf/2109.00738). **Independent geometry check:** Shioda–Tate for rational elliptic surfaces, e.g. [C. Li, *Elliptic Surfaces and Mordell–Weil Lattices*](https://www.math.columbia.edu/~chaoli/docs/EllipticSurfaces.html). Input family and benchmarks: [MathOS 03](BSD_RANK_THREE_BASE_CHANGE_MILESTONE_03.md) and [MathOS 04](BSD_PRIME_DISCRIMINANT_MILESTONE_04.md).

## 1. Exact generic rank theorem

Let \(U\) be an indeterminate and set \(S=U(U+1)\). Consider the elliptic curve

\[
\mathcal E/\mathbb Q(U):\qquad
y^2+y=x^3+\frac{S}{2}x^2-\frac{S+2}{2}x.
\]

**Theorem (application of Battistoni–Bettin–Delaunay).**

\[
\boxed{\operatorname{rank}\mathcal E(\mathbb Q(U))=3.}
\]

The three explicit sections \(P=(0,0), Q=(1,0), R=(-1,U)\) are independent (as already shown in Milestone 03 using the externally recorded independent generators of LMFDB 5077.a1), and thus form a finite-index subgroup of the free part. **No claim is made that their index is one.**

### Proof of the rank upper bound

Set \(Y=y+\frac12\) and \(X=x\). Then

\[
Y^2=A(X)U^2+B(X)U+C(X),
\qquad
A(X)=B(X)=\frac{X(X-1)}2,\quad
C(X)=X^3-X+\frac14.
\]

Here \(A,B\) have degree two and \(C\) is monic cubic. The curve is nonisotrivial (Milestone 03 computed nonconstant \(j\)). Therefore the degree-two-\(A\) formula in **Theorem 1 of Battistoni–Bettin–Delaunay** applies.

For transparency, define the factor-counting notation used in that paper: \(\Omega(H)\) counts irreducible factors **with multiplicities**, \(\omega(H)\) counts distinct irreducible factors, \(H^*\) is the monic squarefree product of the distinct irreducible factors, and \(M_{H,K}(Z)=\operatorname{Res}_X(H(X),Z^2-K(X))\). The paper's correction terms \(\Upsilon\) and square-indicator must also be checked rather than silently omitted.

The exact factorizations over \(\mathbb Q[X]\) are

\[
F(X):=B(X)^2-4A(X)C(X)
=-\frac{X(X-1)(X+1)(8X^2-9X+2)}4.
\]

The quartic-in-\(X\) subexpression is NOT an extra factor; \(F\) has **four distinct irreducible factors**: the three linear factors and the irreducible quadratic \(8X^2-9X+2\) (discriminant \(17\)). Hence \(\omega(F)=4\). Also, \(\gcd(A,B^*)=X(X-1)\) has degree \(2\), whereas \(\gcd(A,B,C)=\gcd(A,B^*,C)=1\), since \(C(0)=C(1)=1/4\). \(A\) is not a square in \(\mathbb Q[X]\).

The two resultants, normalized as monic polynomials, factor as

\[
M_{\gcd(A,B^*),C}(Z)=\left(Z^2-\frac14\right)^2
\]

and

\[
M_{F^*,A}(Z)=
Z^4(Z^2-1)\left(Z^4+\frac{23}{128}Z^2+\frac1{128}\right).
\]

The quartic factor is irreducible over \(\mathbb Q\): after multiplying by 128 it is \(128Z^4+23Z^2+1\), which is irreducible modulo \(3\) (no factors of degrees 1 or 2). Therefore

\[
\Omega(M_{\gcd(A,B^*),C})=4,
\qquad
\Omega(M_{F^*,A})=4+2+1=7.
\]

The paper's correction term \(\Upsilon_{\gcd(A,B),C}\) is zero, since its first polynomial has only linear irreducible factors. The second \(\Upsilon_{F,A}\) is also zero: the only non-linear irreducible factor of \(F\) is \(G=8X^2-9X+2\), and

\[
A(X)\bmod G(X)=\frac{X}{16}-\frac18
\]

has **nonzero linear coefficient**, which is the zero-correction case in the definition (2.5) of the cited paper. The square-indicator \(\square(A)=0\). Substituting each term in the cited exact rank formula gives

\[
r
=4+7+0-0-0-4-0-2(2)-0
=\boxed{3}.
\]

The prior Milestone 03 specialization to \(U=2\), whose three points map to independent LMFDB 5077.a1 generators, gives an independent lower bound of \(3\), agreeing with the exact formula. **QED (conditional only on the correctness and applicability of the cited established theorem and LMFDB independence fact).**

## 2. Independent geometric consistency check (a distinct weaker bound)

The integral/rational Weierstrass coefficients have degrees \(\deg a_i\le i\). Over \(\overline{\mathbb Q}\), the relatively minimal elliptic surface is rational with Picard number \(\rho=10\), by standard elliptic-surface classification.

Its discriminant is the degree-eight polynomial

\[
D(U)=U^8+4U^7+16U^6+34U^5+65U^4+78U^3+94U^2+60U+37.
\]

The **Euclidean gcd of \(D\) and \(D'\) modulo 3 equals one**, and \(D\) remains of degree eight modulo 3, so \(D\) has eight simple roots over \(\overline{\mathbb Q}\): eight finite nodal type \(I_1\) fibers. At infinity use \(v=1/U\), the usual transformation \(x=v^{-2}X_\infty,\ y=v^{-3}Y_\infty\). The transformed invariants have \(v_\infty(c_4)=0\) and \(v_\infty(D)=12-8=4\), giving a type \(I_4\) multiplicative fiber.

Shioda–Tate thus gives

\[
\operatorname{rank}\mathcal E(\overline{\mathbb Q}(U))
=\rho-2-\big((4-1)+8(1-1)\big)=10-2-3=\boxed{5}.
\]

This confirms the less precise **geometric rank five**, while the independently applied arithmetic rank formula gives **rank three over \(\mathbb Q(U)\)**. The difference involves Galois descent of sections; the geometric calculation alone would **not** establish rank three over \(\mathbb Q(U)\).

## 3. TECT ×5: five separate adversarial research gates

This is a **five-pass, TECT-inspired scoped review**, not five authenticated independent reproductions and not execution of the canonical ResearchOs \`tect_runtime\` controller. Raw record: [TECT5 JSON](BSD_RANK_EXACT_MILESTONE_05_TECT5.json). Exact-algebra code: [auditor](../../../mathos/research/bsd_rank_exact_05.py) and [tests](../../../tests/test_bsd_rank_exact_05.py).

| Gate | ResearchOS / TECT-style adversarial question | Outcome |
|---|---|---|
| 1. Claim & provenance | Is the target strictly generic algebraic rank over Q(U), with the external theorem, edition and definitions recorded? | **PASS—SCOPED** |
| 2. Independent symbolic route | Can we reproduce exact factorization, resultants and the quartic irreducibility certificate, without numerical L-values? | **PASS—SCOPED** |
| 3. Theorem hypotheses and corrections | Are the degree hypotheses, all gcd terms, both \(\Upsilon\) corrections, and the square indicator explicitly evaluated? | **PASS—SCOPED**, published theorem remains external |
| 4. Adversarial alternate geometry | Does a Shioda–Tate computation contradict the claimed rank? Does it distinguish geometric rank from arithmetic rank? | **PASS—SCOPED** (rank 5 geometrically versus 3 arithmetically) |
| 5. Novelty & overclaim attack | Has independent expert review established new-to-literature novelty or an infinite exact analytic-rank-3 family? | **UNCERTAIN / NOT ESTABLISHED** |

**Epistemic-state safeguard:** Passing an exact arithmetic audit confirms the *reported algebra*, not source authentication, theorem originality, independent reproduction, or official validation. For ResearchOs/TECT integration the claim remains \`UNVERIFIED\` at the canonical evidence-control layer until a separate authenticated review is attached. No controller state promotion is performed.

## 4. Scientific competitiveness: new state vs desired result

**Mathematical improvement over earlier MathOS milestones:** before this note MathOS only showed generic rank at least three, with no generic upper bound. We now give an **exact generic algebraic rank of three**, as a specific consequence of a published theorem. The rank theorem is technically more complete and independently checkable, but is **not yet demonstrated as original mathematical research**.

**Important distinction:**

\[
\operatorname{rank}\mathcal E(\mathbb Q(U))=3
\quad\not\Longrightarrow\quad
\operatorname{rank}\mathcal E_u(\mathbb Q)=3
\quad\text{for infinitely many explicitly given }u.
\]

Silverman's specialization theorem proves a generic-rank **lower** bound for almost all fibers; it does **not** prohibit rank jumps. The specializations \(u=1,-2\) already have rank 2, so a universal-every-fiber statement is false. No *effectively specified infinite subset with exact specialized rank three* is proved here.

Likewise, existing theorems yield lower bounds on the complete analytic central vanishing order; they do not give exact analytic rank three for this family. In particular **no new noncircular high-rank analytic–algebraic equality is proved**, and BSD remains unsolved.

## 5. Reproducibility and next open theorem

Run from a checkout of the stacked research branch:

    python -m unittest discover -s tests -p 'test_bsd_rank_exact_05.py' -v
    python -m mathos.research.bsd_rank_exact_05

The CI checks **finite exact algebra**, schema consistency and non-promotion flags. It cannot independently prove the general Battistoni–Bettin–Delaunay theorem or reproduce LMFDB's rank-three certificate.

A genuinely competitive next result would be an **original, unconditional, independently reviewed theorem** that gives an explicitly describable infinite \(S\subset\mathbb Q\) for which

\[
\operatorname{rank}\mathcal E_u(\mathbb Q)
=\operatorname{ord}_{s=1} L(\mathcal E_u,s)
=3\quad(u\in S),
\]

or proves a clearly new intermediate statement not already implied by existing literature. Current MathOS **has not established this**.

**AI research disclosure:** ChatGPT helped identify the published rank formula, work out the specialization, draft this explanatory manuscript, and generate tests. Subject-matter expert review and accurate publication disclosure remain necessary. All canonical MathOS BSD and TECT proof/assurance status records remain unchanged.
