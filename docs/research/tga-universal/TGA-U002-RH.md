# A tail-Hankel criterion and arithmetic certificates for Riemann xi

**MathOS TGA-U002-RH | 24 November 2026 | Research note, RH not solved**

## 1. Target and refinement

TGA-U001 reduced RH to simultaneous positivity of the unshifted and shifted Hankel towers of the logarithmic derivative of the even xi function. Here we reduce this to one tower, even after discarding an arbitrary fixed initial segment, and attack the coefficients directly via the classical theta kernel rather than inputting any zeta-zero locations. The one-tower criterion has related prior work; no literature priority is claimed.

Let Xi(z)=xi(1/2+iz), G(w)=Xi(sqrt(w))/Xi(0), and define real coefficients m_n by F(w)=−G'(w)/G(w)=Σ_(n≥0)m_n w^n near zero. As in TGA-U001, G is entire of order at most 1/2 with G(0)=1.

THEOREM. For each fixed integer k≥0, RH holds if and only if all real Hankel matrices H_(k,d)=(m_(k+i+j))_(0≤i,j≤d) are positive semidefinite for every d≥0. Equivalently every leading principal determinant in that tower is strictly positive.

Proof, forward: under RH the genus-zero factorization gives m_n=Σ_j t_j^(n+1) for the positive reciprocals t_j of zeros of G, counted with multiplicity. Thus m_(k+n) is the moment sequence of the positive measure Σ_j t_j^(k+1)δ_(t_j). Its moments converge and the support is bounded. There are infinitely many distinct zeros (nontrivial zeta zeros are infinite in number and each has finite multiplicity), so the integral of the square of any nonzero real polynomial is strictly positive. Hence all these Hankel matrices are positive definite.

Proof, reverse: the classical Hamburger moment theorem supplies a finite positive measure μ on R with moments m_(k+n). Analyticity of F at zero gives Cauchy bounds |m_n|≤CR^n with R>0. Applying the bounds to the even moments gives μ supported in [−R,R]: positive mass outside any slightly larger interval would violate the even-moment growth bound. The generating function ∫(1−wt)^(-1)dμ(t) is holomorphic on the connected plane with the two rays (−∞,−1/R] and [1/R,∞) removed. Near zero it equals the shifted Taylor series F_k(w)=(F(w)−Σ_(n<k)m_n w^n)/w^k, with a removable value at zero. Meromorphic continuation and the identity theorem force agreement on the entire slit plane. Any zero of G off the real axis would give a nonremovable pole of F_k there; subtracting a polynomial and dividing by w^k cannot remove a nonzero pole. Therefore every zero of G is real.

In fact G has no nonpositive real zero. It is nonzero at zero. A negative w gives a purely imaginary square root, so Xi(sqrt(w)) equals xi(s) at a real s. The completed xi function is nonzero on the whole real axis: for s>1 all factors are nonzero, for 0<s<1 the positive alternating eta series and the factor 1−2^(1−s) give nonzero zeta, at 0 and 1 the removable values equal 1/2, and the functional equation covers s<0. Thus every zero of G is positive, giving RH. The equivalence with strictly positive leading determinants follows from the forward strictness and Sylvester's criterion.

This eliminates the shifted tower as a separate logical dependency, and shows that deleting any fixed initial segment does not remove the actual obstruction. It does not prove positivity for an unbounded number of rows.

## 2. A zero-independent arithmetic calculation

For real t≥0, write u_n(t)=πn² exp(2t). The classical Riemann cosine kernel gives

Xi(z)=2∫₀^∞ Φ(t) cos(zt) dt,

Φ(t)=Σ_(n≥1) (4u_n(t)²−6u_n(t)) exp(t/2−u_n(t)).

The kernel is positive because u_n≥π>3. Its superexponential decay permits differentiation under the integral for complex z. The constant factor 2 cancels in normalization. Define J_j=∫₀^∞ Φ(t)t^(2j)/(2j)! dt. The coefficients g_j of G are g_0=1 and g_j=(−1)^j J_j/J_0. The relation −G'=F G yields the exact recurrence

m_n=−(n+1)g_(n+1)−Σ_(j=1)^n g_j m_(n−j).

Hence the first Hankel determinants can be bounded entirely by theta-kernel integrals without computed zeta-zero locations.

## 3. Interval arithmetic and tail proof

The companion implementation uses 65-decimal fixed-point integer intervals. On [0,2] it uses 65,536 equal subintervals and sums n=1,...,5. The first attempt at 4,096 intervals was insufficient to certify the shifted 2×2 determinant and failed its test; the mesh was refined rather than treating a numerical estimate as proof.

At each interval endpoint exp(t/2) is enclosed by multiplication by the positive Taylor enclosure for exp(h/2), h=2/65536. The degree-20 Taylor polynomial is a lower bound and twice the next term bounds its tail since h/2≤1/2. π is enclosed by Machin's identity using alternating arctangent series. For exp(−u) with u<128 at the lower endpoint, divide u by 256, use alternating degrees 25 and 26 to enclose exp(−u/256), and square eight times with outward rounding. The divided upper endpoint remains ≤1 (checked). If the lower endpoint is at least 128, the enclosure [0,2^(-128)] follows from e>2. All operations round outward.

The positive prefactor A_n(t)=(4u_n²−6u_n) exp(t/2) increases in t; exp(−u_n) decreases. On each subinterval their left/right products bound every kernel value, and multiplying by the left/right endpoints of t^(2j)/(2j)! gives an interval rectangle integral. This is not point sampling without an error term.

For tail control use u² exp(−u/2)≤16 (by differentiation), hence each kernel term times t^(2j)/(2j)! is at most 64 exp(3t/2) exp(−u_n/2). For t=2+s≥2, e^4>50 and π>3 give u_n≥150n²(1+2s). With e³<27, integrating yields at most (1728/148) exp(−75n²). Summing over n is bounded by (1728/148)·2^(-75)/(1−2^(-75)), since e>2 and n²≥n. For n≥6 and all t≥0, u_n≥3n²(1+2t), so the time integral is at most 64 exp(−1.5n²)/(3n²−1.5). Since e^(3/2)>4, this is bounded on summation by 64·4^(-36)/(1−1/4). The combined positive omitted tail is less than 10^(-17), checked by exact rational arithmetic. Counting their overlap twice is safe.

The program encloses J_0 through J_4, then m_0 through m_3 and the determinants m_0m_2−m_1² and m_1m_3−m_2². The replay report records decimal strings for integer interval endpoints and the exact scale, avoiding loss of precision during JSON interchange. A determinant is certified positive only if its lower endpoint is strictly positive. This is a finite certificate, not extrapolation to all d.

## 4. Remaining universal theorem

For any fixed k, the exact missing condition is positivity of H_(k,d) for every d, or an identity expressing every finite Hankel quadratic form as a nonnegative quantity. TGA-U001's finite countermodels still explain why bounded certificates alone cannot supply this theorem. The arithmetic route now supplies explicit computable input with provable truncation errors and separates the one infinite positivity hypothesis from the spectral construction. The latter is conditional, not unconditional.

Next: replace rectangle bounds by high-order certified quadrature for larger determinants, then investigate exact analytic inequalities controlling the entire Hankel family rather than extrapolating determinant signs.

## References and reproduction

TGA-U001, previous two-tower proof. Classical Riemann theta-kernel representation, Hamburger moment theorem (K. Schmüdgen, The Moment Problem), and Hadamard factorization. Related recent one-tower criterion: B. Rouyea and C. Bourgeois, The Cubic Descent of the Riemann Xi Function, https://www.alphaxiv.org/abs/2608.riemann-xi-hankel-criterion (preprint; no independent novelty assessment).

Pinned calculation source: e2da79ba836c37b5177fe205dc462ef7cbd8e54c. Replay workflow: https://github.com/tltmgnt/MathOS/actions/runs/45377339649. Original coarse-mesh failure: https://github.com/tltmgnt/MathOS/actions/runs/45377268965.

Run: python -m unittest discover -s tests -p 'test_tga_rh_hodge.py' -v

Run: python -m mathos.research.tga_rh_hodge

The universal criterion is an analytical derivation using classical theorems. Its finite computational checks do not prove RH. No canonical obligation promoted.
