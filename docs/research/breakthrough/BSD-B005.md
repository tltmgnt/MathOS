# Rank-two CM localization and the exact Kato nonvanishing gap

**MathOS BSD-B005 | Breakthrough cycle 5 | 24 November 2026 | Unreviewed technical note**

## 1. Target and scope

Registered target BSD.analytic_selmer. BSD-B004 independently obtained analytic rank two and rational rank two for E:y²=x³−1681x, using classical modularity, Tunnell's central-value theorem, explicit rational points, 2-descent and a rigorous integral enclosure. It also proved trivial 2-primary Sha for this curve. We now audit a genuine higher-rank comparison theorem for odd primes, and identify exactly which input remains unproved. No odd-primary Sha finiteness is asserted.

The curve has j-invariant 1728 and complex multiplication by the full ring Z[i] of Q(i); the automorphism (x,y)↦(−x,iy) supplies the CM action. Let p≥5 be a prime of good ordinary reduction. For this curve these are the split primes p≡1 mod 4 other than 41, by the classical CM reduction criterion. The earlier rank-two certificate supplies positive even analytic order, as needed below.

## 2. The actual comparison theorem

We consulted F. Castella, Generalised Kato classes on CM elliptic curves of rank 2, manuscript dated 13 February 2026, Theorem B on p. 5 and its hypotheses on pp. 4–5. With CM, a good ordinary prime and positive even analytic vanishing, choose auxiliary Hecke characters satisfying the paper's equation (1.5) and Theorem A(i)–(ii). These conditions include character compatibility, the three auxiliary nonzero L-values, residual distinction at the two primes over p and the indicated root-number conditions. The author explains existence of such triples after Theorem B. We have not constructed a particular triple or evaluated its associated class.

Writing S_p=Sel(Q,V_pE) for the Bloch–Kato p-adic Selmer vector space, the theorem supplies two implications in this setting:

• If the associated generalized Kato class κ_p is nonzero, then dim S_p=2.

• If dim S_p=2, the class κ_p is nonzero precisely when the local restriction res_p:S_p→E(Q_p) completed and tensored with Q_p is nonzero.

It does not conclude nonvanishing from analytic rank two alone. The paper's Theorem C also uses additional p-adic L-function orders and primary Sha finiteness; we do not import those hypotheses as established facts.

## 3. An exact equivalence on the rank-two curve

For this E, the rational rank-two certificate is independent of the odd-prime Selmer question. The standard Selmer exact sequence and cofinitely generatedness of the p-primary groups give

dim_(Q_p) S_p = 2 + corank_(Z_p) Sha(E/Q)[p^∞].

A cofinitely generated p-primary group has corank zero exactly when it is finite, so dim S_p=2 is equivalent to finiteness of this primary component. The natural rational-point localization is nonzero: a rational nontorsion point remains nontorsion in E(Q_p), by injectivity of the field extension map. At a good prime E(Q_p) has a finite-index formal group on which the p-adic logarithm becomes an isomorphism on a sufficiently small open subgroup; its kernel on the full group is torsion. Thus a nontorsion point has nonzero image in the rationalized local group. In particular res_p is nonzero independently of Sha finiteness.

Under the theorem's admissible auxiliary-character hypotheses, the two implications therefore yield the conditional equivalence

κ_p≠0  ⇔  dim S_p=2  ⇔  Sha(E/Q)[p^∞] is finite.

This is a specialization of an existing theorem, not a new general comparison theorem. The nonvanishing of κ_p and odd-primary finiteness are both unresolved by this calculation. Using the latter as a premise to claim the former and then claiming a new proof of the latter would be circular.

## 4. Explicit local arithmetic certificates

Let P=(−9,120), Q=(−64/25,8184/125) be the earlier independent rational points. For each tested good ordinary prime let m=#E(F_p), computed by exact point counting. The group law computed [m]P and [m]Q in rational arithmetic and checked the points on E. Both multiples reduce to the identity. For a formal-group point R, set z(R)=−x(R)/y(R). Its p-adic valuation is positive. For p≥5, log_E(z)≡z mod p² on pZ_p: the invariant differential has integral coefficients at good reduction, and the integrated term of degree k≥2 has valuation at least k−v_p(k)≥2. Thus the residue of z/p modulo p is the first digit of the scaled formal logarithm.

The executed results are:

p=5, #E(F_p)=8, a_p=-2; digits (P,Q)=(1,3); kernel direction mod p=(3,4).

p=13, #E(F_p)=20, a_p=-6; digits (P,Q)=(8,4); kernel direction mod p=(4,5).

p=17, #E(F_p)=20, a_p=-2; digits (P,Q)=(12,14); kernel direction mod p=(14,5).

p=29, #E(F_p)=20, a_p=10; digits (P,Q)=(0,20); kernel direction mod p=(20,0).

p=37, #E(F_p)=40, a_p=-2; digits (P,Q)=(35,35); kernel direction mod p=(35,2).

In every row the pair of digits is not zero, certifying nonzero localization already on the span of these rational points. The listed direction is only a mod-p direction for the scaled local log on the rational-point span; it is not an independently computed generalized Kato class, nor evidence for an upper bound on the entire Selmer group. In particular p=29 illustrates that one local digit can vanish while the other suffices.

Primes 3,7,11,19,23,31 are outside the chosen ordinary theorem setting (inert and supersingular; 3 also below its stated lower bound). Prime 41 is bad. The prime 2, already handled by descent in cycle 4, is outside this theorem too. These give explicit negative applicability controls. No extension of the theorem to these primes is claimed.

## 5. Next proof obligation

Compute an admissible auxiliary-character choice and a genuinely independent nonvanishing certificate for κ_p at a specified ordinary prime, or obtain an independent primary Sha bound from another rigorous route. Local logarithms alone do not determine the dimension of the full global Selmer group. Even success for one odd prime and this one rank-two curve does not prove the general conjecture, higher ranks, all primes or the refined leading-term formula.

## References and reproducibility

F. Castella, Generalised Kato classes on CM elliptic curves of rank 2, dated 13 February 2026, Theorem B and Theorem A hypotheses, pp. 4–5. https://web.math.ucsb.edu/~castella/Kato-Schoen.pdf ; preprint record https://arxiv.org/abs/2204.09608 .

F. Castella and M.-L. Hsieh, On the nonvanishing of generalised Kato classes for elliptic curves of rank 2, Forum of Mathematics, Sigma (2022), https://doi.org/10.1017/fms.2021.85 . The non-CM route has additional hypotheses; the CM theorem above is the one used here.

J. H. Silverman, The Arithmetic of Elliptic Curves, 2nd ed., formal groups and Selmer sequences. MathOS BSD-B004 provides the rank-two baseline and is replayed by the current code.

Pinned code: fb4c9faa5cf8a32c286996e80ce443d6ad0b48fe. Executed workflow: https://github.com/tltmgnt/MathOS/actions/runs/45372843485. Evidence: cycle5-evidence.json.

Run: python -m unittest discover -s tests -p 'test_breakthrough_cycle5.py' -v

Run: python -m mathos.research.breakthrough_cycle5

Independent review and formal checking remain outstanding. All canonical obligations remain open.
