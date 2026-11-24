# Independent analytic and Selmer rank-two certification for the curve E₄₁

**MathOS BSD-B004 | Breakthrough cycle 4 | 24 November 2026 | Unreviewed technical note**

## Abstract

We independently obtain analytic rank two, Mordell–Weil rank two and full 2-power Selmer corank two for E:y²=x³−1681x, together with trivial 2-primary Tate–Shafarevich group. The arithmetic argument uses explicit rational points and classical 2-descent; the analytic argument uses Tunnell's exact central-value criterion and an outward-rounded interval certificate for the second derivative of the completed L-function. No BSD assumption is used. The rank-two example is known in the literature; the contribution is a reproducible, independently derived certificate for a single curve, not general BSD or literature novelty.

## 1. Exact arithmetic rank

Take P=(−9,120) and Q=(−64/25,8184/125). Substituting the coordinates verifies they are on E. The standard full rational 2-torsion descent map sends a nontorsion point with x not equal to a root to (x,x−41,x+41) modulo rational squares, with the usual specializations at the roots, and has kernel 2E(Q). The three nonzero rational 2-torsion points and the identity give squareclass triples

(−1,−41,41), (41,2,82), (−41,−82,2), (1,1,1).

Good reductions at p=3 and 7 have orders 4 and 8 respectively by exact point counting. Prime-to-residue-characteristic torsion injects into good reduction, so the rational torsion group has order at most 4 and is exactly the rational 2-torsion. In particular none of these torsion classes disappears because of rational 4-torsion.

The triples for P,Q are (−1,−2,2) and (−1,−1,1); their componentwise squareclass product is (1,2,2). None lies in the torsion image. Hence P and Q are linearly independent in E(Q)/(2E(Q)+E(Q)[2]), implying rank at least two.

For an odd squarefree twist n, Monsky's classical pure 2-Selmer matrix has blocks A+D₂, D₂; D₂, A+D_−₂, using additive Legendre symbols at the odd prime factors of n and A the row-sum-zero off-diagonal symbol matrix. For n=41 there is one odd prime, A=(0), and both 2 and −2 are quadratic residues modulo 41. Thus the matrix is zero of size 2×2; the pure 2-Selmer dimension is exactly two. The exact sequence

0 → E(Q)/2E(Q) → Sel₂(E/Q) → Sha(E/Q)[2] → 0

gives rank at most two and Sha[2]=0. Therefore rank is exactly two, and Sha[2^∞]=0 (any nonzero element of 2-power order would yield an element of order two). The full 2-power Selmer exact sequence then identifies Sel_(2^∞)(E/Q) with E(Q)⊗Q₂/Z₂, of Z₂-corank two.

## 2. Exact central vanishing, separate from numerical evaluation

The standard congruent-number curve conductor is N=32·41²=53792, and the functional equation has sign +1 since 41≡1 mod 8. Both bad primes 2,41 are additive, so their Euler factors are 1. These are classical reduction and modularity facts used here.

Tunnell's unconditional central-value formula for odd squarefree n implies L(Eₙ,1)=0 exactly when Bₙ=2Aₙ, where A and B count integer triples with 2x²+y²+32z²=n and 2x²+y²+8z²=n respectively. Exact enumeration gives A₄₁=16 and B₄₁=32. This proves central vanishing without a numerical tolerance and without assuming the converse congruent-number criterion under BSD. The functional equation makes the first derivative of the completed L-function vanish as well.

## 3. Certified analytic second derivative

Write c=2π/√N and f(it/√N)=Σ_(m≥1) a_m exp(−cmt), the weight-two newform associated to E. For the completed L-function Λ(s)=(√N/(2π))^s Γ(s)L(E,s), Mellin integration and the sign +1 Fricke relation give

Λ(s)=∫₁^∞ f(it/√N)[t^(s−1)+t^(1−s)]dt.

Exponential decay justifies differentiation at s=1:

Λ''(1)=2∫₁^∞ (Σ_(m≥1) a_m exp(−cmt)) (log t)²dt.

The certificate uses exact point counts to calculate a_p at good primes, a_p=0 at the two additive primes, the recurrence a_(p^j)=a_p a_(p^(j−1))−p a_(p^(j−2)) at good primes, and multiplicativity. It uses m≤512. The Hasse bound and Euler recurrence give |a_m|≤d(m)√m≤2m for all m, where d(m) is the divisor count.

For the finite rectangle quadrature integrate over 1≤t≤512 using intervals of width 1/2. Since 231<√N<232 and 3.14<π<22/7, we have 27/1000<c<28/1000. At t=j/2, bound exp(−ct) by powers of q in [q_low,q_high], using the alternating Taylor lower degree-three sum at 0.014 and upper degree-four sum at 0.0135 to bound exp(−c/2). All powers and products are evaluated with outward-rounded integer fixed point at scale 10^18. Separate positive and negative coefficient sums and use monotonicity of each exponential on a time interval for rigorous lower and upper bounds of the truncated newform. For each interval use k=floor(log₂ t) at its left endpoint and k'=floor(log₂ t) at its right endpoint, bounding log t by (2/3)k and (7/10)(k'+1). Take min and max of the four endpoint products of the two independent enclosures for the newform and squared logarithm. The factor 2 in the derivative cancels the mesh width 1/2.

For the coefficient tail beyond 512, use log t≤t−1, c>1/40, and r=40/41>exp(−1/40). Integrating (t−1)² against the exponential yields a total absolute derivative error at most

8·40³·41·r^513/513² < 1.

For the time tail t≥512, use Σ 2m exp(−mt/40)≤8 exp(−t/40) (since exp(−512/40)<1/2) and (log t)²≤t for t≥1. The absolute derivative error is at most

16·40·(512+40)·r^512 < 2.

The code establishes exact rational comparisons for these bounds. Counting both tails separately overestimates their overlap and is safe.

## 4. Observed certificate and implication

The executed 1,022 interval quadrature encloses the truncated derivative between 315 and 819 (rounded outward to integers). Adding the two rigorous absolute tail allowances gives the deliberately conservative enclosure

300 < Λ''(1) < 850.

The zero of L(E,s) at s=1 is therefore exactly order two, since the gamma and conductor factors are analytic and nonzero there. Combining the independent analytic and arithmetic arguments gives analytic rank = rational rank = full 2-power Selmer corank = 2, and Sha[2^∞]=0.

This enclosure is for the second derivative of the COMPLETED L-function in the specified normalization, not the uncompleted L-function or its leading coefficient. It is an interval certificate using explicit rational bounds, not a claim of formal proof checking of the external theorems. The known rank-two curve is used to audit the two proof paths rather than to assume the desired result.

## 5. Generalization barrier and next obligation

For arbitrary E/Q and prime p, the full Selmer exact sequence gives corank Sel_(p^∞) = rank E(Q) + corank Sha[p^∞]. An analytic order comparison requires additional arithmetic input; a Selmer bound or a numerical central value does not by itself establish it. In this curve exact central vanishing is available through the special Tunnell formula, and the rank upper bound through the special full 2-torsion descent. Neither method automatically generalizes to arbitrary elliptic curves. A finite bound for one primary component does not establish global Sha finiteness. The refined leading-term equality has not been evaluated here.

Next: isolate which additional hypotheses of known higher-rank Euler-system or generalized Kato-class results connect analytic order to full Selmer corank; identify an explicit test family where they apply and one where they fail. Compare with the rank-two certificate here without using BSD as an input.

## 6. Sources and replay

J. B. Tunnell, A classical Diophantine problem and modular forms of weight 3/2, Invent. Math. 72 (1983), 323–334. https://doi.org/10.1007/BF01389327

D. R. Heath-Brown, The size of Selmer groups for the congruent number problem II, with appendix by P. Monsky, Invent. Math. 118 (1994), 331–370. See also the explicit odd Monsky matrix in Families of non-congruent numbers with odd prime factors of the form 8k+3, https://www.sciencedirect.com/science/article/pii/S0022314X2100322X .

P. Molin, Nombres congruents, notes on functional equation and Tunnell's central values: https://webusers.imj-prg.fr/~pascal.molin/cours/cimpa2016/congruent.html . Standard full 2-descent: J. H. Silverman, The Arithmetic of Elliptic Curves, 2nd ed., Chapter X.

Pinned source: b4623c70d99ca05363681e709e9dc9191e93fd9d. Executed workflow: https://github.com/tltmgnt/MathOS/actions/runs/45371621490. Evidence: cycle4-evidence.json.

```sh
python -m unittest discover -s tests -p 'test_breakthrough_cycle4.py' -v
python -m mathos.research.breakthrough_cycle4
```

The certificate is scoped to one curve and relies on established classical theorems. No general BSD theorem, independent peer review, or novelty claim. BSD.analytic_selmer remains open.
