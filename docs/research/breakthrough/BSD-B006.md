# A 5-primary Tate–Shafarevich certificate for the rank-two CM curve E₄₁

**MathOS BSD-B006 | Cycle 6 | 24 November 2026 | Scoped use case complete under cited classical theorems; not independently reviewed**

## 1. Target and conclusion

For E:y²=x³−1681x, establish triviality of Sha(E/Q)[5^∞] without assuming BSD or generalized Kato nonvanishing. BSD-B004 established rational rank and analytic rank two and trivial 2-primary Sha, using exact descent and a certified Mellin integral. We use the Coates–Liang–Sujatha (CLS) theorem and compute the relevant normalized Hecke value exactly:

c₅⁺(E)=L(bar ψ⁵,5)/Ω⁵=141800/1681, with ord₅(c₅⁺)=2.

Here Ω is the smallest positive real period of the minimal Néron differential. The conclusion is scoped to this curve and prime. No all-prime Sha finiteness is claimed.

## 2. Applicability of the arithmetic theorem

E is a quadratic twist by 41 of y²=x³−x and has CM by Z[i]. Its equation is minimal: at 2 and 41 the discriminant has valuation six, and at other primes it is a unit. The standard conductor is 32·41²=53792. The Gaussian Hecke character of the base curve has conductor (1+i)³ and finite character valued in fourth roots of unity; twisting by the rational quadratic character of conductor 41 preserves the fourth-root property. The twist character has conductor (41) over Q(i): at each of the two primes above 41 the local quadratic character on units is nontrivial. Coprimality with the base conductor gives the ideal f=(1+i)³(41), generated up to a unit by 82(1+i). Raising the character to the fifth power leaves its finite character unchanged and retains that conductor. Thus its weight-six theta newform has level 4Norm(f)=53792, trivial nebentypus and real coefficients. The CM Hecke-series construction and functional equation are classical inputs.

The square period lattice is Ω Z[i] (choose its real positive generator); for this real model the real half-period integral gives Ω=π/[√41 AGM(√2,1)]. The good prime 5 splits in Q(i), is prime to 4 (the unit group order), and the real generator has α(E)=1 in CLS normalization. Exact counting gives #E(F₅)=8, prime to 5. Also 5 is prime to 6 and rational rank equals analytic rank two, so the parity hypothesis holds.

CLS Theorem 2.2, equation (21), in arXiv:0901.3832, says that equality of the normalized valuation and rational rank under these hypotheses, together with nonanomalous reduction and p prime to 6, gives trivial p-primary Sha over the CM field. Restriction from Q to Q(i) is injective on 5-primary Sha: restriction followed by corestriction multiplies by 2, a unit on a 5-primary group. This supplies the desired conclusion over Q.

## 3. Arithmetic coefficients and rigorous analytic value

Let f₆ be the weight-six CM newform and A_n its coefficients. For good primes, compute a_p=p+1−#E(F_p), let α+β=a_p and αβ=p, and use A_p=α⁵+β⁵ via the integer recurrence s_j=a_p s_(j−1)−p s_(j−2) starting at s₀=2,s₁=a_p. The Euler recurrence for powers of good primes is A_(p^j)=A_p A_(p^(j−1))−p⁵ A_(p^(j−2)). At 2 and 41 the Euler factors are 1. Multiplicativity gives all coefficients through 5000. The local root magnitudes imply |A_n|≤d(n)n^(5/2)≤2n³ for all n, where d(n) is the divisor count.

Set c=2π/√53792 and F(t)=Σ A_n exp(−cnt). Fricke symmetry has sign ε∈{+1,−1}, with F(1/t)=ε t⁶ F(t). If ε=+1, differentiation at t=1 forces F'(1)+3F(1)=0. The outward-rounded enclosure of Σ A_n exp(−cn)(3−cn), including the infinite tail, is strictly negative (approximately −51324.5), hence ε=−1. Mellin splitting at 1, followed by elementary integration of t⁴−1, now yields

L(bar ψ⁵,5)=Σ A_n exp(−cn)[(Σ_(j=0)^4 (cn)^j/j!)/n⁵−c⁴/(24n)].

Compute π with Machin's arctangent identity and alternating series; bound Ω by arithmetic–geometric mean iterates, whose arithmetic and geometric values bracket their common limit. Compute exp(−c) using alternating Taylor degrees 49 and 50 at the appropriate interval endpoints. All interval operations use integer fixed point with denominator 10^65 and outward rounding. Each exponential power and each rational factor is enclosed before summation.

For n≥5001 use 1/40<c<3/100, r=40/41>exp(−1/40), and |A_n|≤2n³. The absolute L-value summand is at most 12n²r^n (using c<1); the sign-test summand is at most 8n⁴r^n. For n=m+j with m=5001, n^k≤m^k(1+j)^k≤m^k k! binom(j+k,k), so summing the geometric generating series bounds the two tails by 12m²·2r^m/(1−r)³<10^−35 and 8m⁴·24r^m/(1−r)^5<10^−25 respectively. Both rational comparisons are executed exactly.

## 4. Exact denominator, not heuristic recognition

Use the trace identity of CLS Theorem 2.3, equation (24), with the erroneous factor w removed as specified in arXiv:1005.4206v2 after equation (79). The fifth Eisenstein series is −wp'''/24, and for our model wp'''=24xy, so its value at Ω/f is −xy at an f-torsion point. The primitive and f-imprimitive L-functions agree here since the conductor is unchanged.

This torsion is annihilated by the integer m₀=164 because 164/f is a Gaussian integer. At any nonarchimedean place, a point with nonintegral x is in the formal group of the integral equation, with parameter z=−x/y of positive valuation, v(x)=−2v(z), v(y)=−3v(z). In the integral formal multiplication series [m₀](z)=m₀z+O(z²), if v(z)>v(m₀) the linear term has strictly smaller valuation than every higher term, contradicting [m₀](z)=0. Consequently m₀²x and m₀³y are integral at every finite place (integral-coordinate points already satisfy this). The trace of m₀⁵xy is therefore a Gaussian algebraic integer. A conservative extra factor 24 retains integrality. Since f⁵=−4·82⁵(1+i), the integer 8·82⁵ is divisible by f⁵ in Z[i]. Therefore

D=24·8·82⁵·164⁵=84448070452814184185856

has D c₅⁺ integral in Z[i]. CLS Theorem 2.2 gives rationality of c₅⁺, so D c₅⁺ is a rational integer. The earlier tentative factor 4 was strengthened to 8 to ensure Gaussian divisibility, and the computation replayed. The modulus 125 residue changed from 25 to 50, leaving valuation two.

The executed interval for D c₅⁺ is contained within 1/1000 of the unique integer 7123579054258805066956800. The interval endpoints and scale are stored as decimal strings in the evidence file, preserving every digit. Dividing by D and reducing gives 141800/1681. Since D is prime to 5 and the scaled integer is 50 mod 125, the exact valuation is two. This is an integer-reconstruction certificate under the proven denominator bound, not a guess based on floating digits.

## 5. Result and limitations

All arithmetic conditions of CLS Theorem 2.2 are met. Sha(E/Q)[5^∞]=0 and the full 5-power Selmer group has corank two. The p=5 use case is complete under the stated classical inputs; no BSD assumption or Kato nonvanishing input is used. No explicit admissible generalized Kato class has been constructed. Other odd primes, the full Sha group, the refined leading-term formula and general rank comparison remain outside this result. No literature priority or independent review is asserted.

## References and reproduction

J. Coates, Z. Liang and R. Sujatha, The Tate-Shafarevich group for elliptic curves with complex multiplication, Theorems 2.2 and 2.3, https://arxiv.org/abs/0901.3832 . Correction to the trace formula in their sequel, arXiv:1005.4206v2, after equation (79), https://arxiv.org/abs/1005.4206 .

Classical CM Hecke theta series and formal group theory: J. H. Silverman, Advanced Topics in the Arithmetic of Elliptic Curves, Chapters II and V; The Arithmetic of Elliptic Curves, Chapters IV and VII. See also MathOS BSD-B004 and BSD-B005 for the independently derived rank and local data.

Pinned source: dac9239e4bd2787e373a11322e4d8dbb3dd986d2. Executed workflow: https://github.com/tltmgnt/MathOS/actions/runs/45374313360. Evidence: cycle6-evidence.json.

Run: python -m unittest discover -s tests -p 'test_breakthrough_cycle6.py' -v

Run: python -m mathos.research.breakthrough_cycle6
