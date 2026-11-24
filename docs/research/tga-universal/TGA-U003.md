# TGA-U003: Persistent spectral obstructions and an explicit Kummer detecting cycle

**MathOS | 24 November 2026 | Scoped mathematical research; no full Millennium solution**

## 1. Full-target scope

The preceding TGA-U001 and U002 papers separate the universal hypotheses from their mathematical implications. This investigation attacks the RH and Hodge hypotheses, while maintaining the full seven-track register. Independent review is nonblocking for internal research, but an actual universal derivation is required for any mathematical solution. The current Clay list still places Poincaré under solved problems, RH and Navier–Stokes under active problems, and the other four under unsolved problems. The September 11, 2026 CMI Navier–Stokes announcement records an apparent solution under evaluation; it is not a MathOS result or prize determination. Source: https://www.claymath.org/millennium-problems/ and https://www.claymath.org/news/navier-stokes-announcement/ .

## 2. RH: a persistent finite-dimensional obstruction theorem

Let G(w)=Xi(sqrt(w))/Xi(0) as in U001/U002, with G(0)=1, real coefficients and entire order at most 1/2. Unconditionally, Hadamard factorization gives G(w)=Π_j(1−t_j w), where the t_j are nonzero reciprocal zeros with multiplicity and Σ_j |t_j|<∞. They are closed under conjugation and accumulate only at zero. The logarithmic derivative defines m_l=Σ_j t_j^(l+1); the sum converges absolutely for each l≥0. Nonpositive real zeros of G are excluded by the real-axis nonvanishing of xi (U002).

THEOREM. RH holds if and only if, for every fixed d≥0, the real matrix H_(2n,d)=(m_(2n+i+j))_(0≤i,j≤d) is positive semidefinite for an unbounded set of integers n≥0. The set of n may depend on d. In fact if RH fails, there exists a finite d such that H_(2n,d) has a negative direction for every sufficiently large n.

Proof. Under RH all t_j are positive real, so for every real polynomial q of degree at most d its Hankel quadratic form is Σ_j t_j^(2n+1) q(t_j)^2≥0.

Conversely assume there is a nonreal reciprocal zero t with modulus R>0 and multiplicity μ. List all distinct reciprocal zeros of modulus at least R. This finite set is invariant under conjugation. Its size is D. Choose c∈C with Re(t c²)<0; for instance choose c with c²=−1/t. For each n, interpolate a polynomial q_n of degree at most D−1 assigning c(R/t)^n to t, its conjugate to bar t, and zero to every other listed node. Conjugation and uniqueness give real coefficients. The interpolation nodes are fixed and all prescribed values have bounded modulus independent of n, so the coefficients and the sup norm on |z|≤R are bounded independently of n by a constant B.

The two selected nodes contribute exactly 2μ R^(2n) Re(t c²), a strictly negative multiple of R^(2n). All other listed nodes contribute zero. There is R'<R bounding the moduli of the remaining nodes: otherwise a nonzero accumulation point would exist. Their total contribution in absolute value is at most B² (R')^(2n) Σ_j |t_j|. After division by R^(2n) this tends to zero. Thus the Hankel quadratic form of q_n is negative for all sufficiently large n, with the same degree bound d=D−1. Contradiction. Every reciprocal zero must be real, and the real-axis exclusion forces it to be positive. This proves RH from the stated criterion.

This theorem strengthens the U002 logical reduction: one does not need every shift, nor a common shift threshold for every dimension. But the dimension quantifier is still unbounded. The theorem does not show positivity for these shifts of the actual xi sequence.

## 3. RH: exact adversarial calculation

Take a synthetic reciprocal spectrum 2,1,t,bar t,1/4 with t=(3+4i)/5. It is NOT the zeta spectrum. For n≥2 let q_n(x)=(x−2)(x−1)(A_n+B_n x) with real rational A_n,B_n chosen so q_n(t)=i t^(−n). This is solvable by equating real and imaginary parts. Since |t|=1 and |(t−2)(t−1)|>1, |B_n|≤5/4 and |A_n|≤7/4. Thus |q_n(1/4)|<5. Its shifted Hankel form is exactly −6/5+4^(−2n−1) q_n(1/4)^2<−1. The two real outer nodes vanish, the conjugate pair supplies −6/5, and the inner node is a bounded tail. The code verifies this identity with Gaussian rational arithmetic at every even shift 4 through 64 and checks all-positive spectra separately. This is a persistent negative witness of fixed degree three, not an RH counterexample.

Actual remaining theorem: for every d, establish an unbounded set of n for which H_(2n,d) is PSD using the analytic arithmetic definition of xi, without assuming all zeros real. Alternatively derive an exact negative form from those true moments. Finite synthetic controls and finite xi certificates cannot settle that hypothesis. No literature priority is claimed; real-zero Hankel criteria originate in classical work of Grommer and Hermite.

## 4. Hodge: solve the detecting-cycle use case for a Kummer family

Let E,F be nonisogenous complex elliptic curves, neither with complex multiplication. Put A=E×F, and S=Km(A), the Kummer K3 surface obtained by blowing up A at its 16 two-torsion points and quotienting by the lifted inversion. Write U=H¹(E,Q), V=H¹(F,Q). The Künneth decomposition and Lefschetz (1,1) theorem show NS(A)_Q has dimension two: cross-factor rational (1,1) classes correspond, via polarization, to rational homomorphisms between the nonisogenous elliptic curves, of which there are none. Thus T(A)=U⊗V. Pullback along the degree-two quotient identifies H²(S,Q) with the invariant H² of the blowup, which is all of H² there; the sixteen exceptional divisors add Tate classes. Consequently T(S) has rank four. The algebraic correspondence C=f_* b^* with b:Bl_(A[2]) A→A and f:Bl_(A[2]) A→S induces an isomorphism T(A)→T(S), since f^* f_* is 1+inversion on cohomology, equal to 2 on the pulled-back degree-two classes. This uses the standard finite quotient correspondence identity.

Choose rational symplectic bases u_0,u_1 and v_0,v_1 with ∫u_0 u_1=∫v_0 v_1=1. Let e_(2i+j)=u_i⊗v_j. Write δ_A=Σ_(σ∈S4) sgn(σ)e_(σ(0))⊗...⊗e_(σ(3)). U002 constructs its square but cannot extract its orientation from the orthogonal pairing alone. Here the independent factors give more algebraic generators.

For X=E or F let P_X=Δ_X−[o×X]−[X×o] in CH¹(X×X)_Q. Its class is the H¹ inverse pairing. On A^4, numbered 1 through 4, use the pullbacks of P_E to E-pairs (1,2),(3,4), and P_F to F-pairs (1,3),(2,4). Define W to be minus the product of these four divisors. The sign convention uses classes pulled back in increasing factor order: the crossing F-pairs contribute a minus from interchanging two degree-one factors; the E-pairs do not cross. Reordering from E^4×F^4 to (E×F)^4 has six degree-one swaps and sign plus. Each curve contributes two inverse pairing tensors, so their common basis sign cancels. With the exterior sign included in W, its ordinary T(A) tensor coefficient at tuple p is

(u-index(p₂)−u-index(p₁))(u-index(p₄)−u-index(p₃)) (v-index(p₃)−v-index(p₁))(v-index(p₄)−v-index(p₂)).

Here u-index(k)=floor(k/2) and v-index(k)=k mod 2. Apply the algebraic alternating correspondence Alt=(1/24)Σ_σ sgn(σ)σ^* on A^4, permuting its surface factors. These factors have total even degree, so there are no further graded signs. The resulting tensor is in the one-dimensional determinant line. Its coefficient at (0,1,2,3) is −12/24=−1/2: among the 24 permutations exactly twelve signed coefficients are −1 and twelve vanish. The exact finite computation is also an immediate enumeration of the two pairing patterns. Hence cl(−2 Alt(W))=δ_A. With identical pairing patterns the alternating coefficient instead vanishes, providing a control for the need to distinguish the two symplectic factors.

Now apply C on all four factors, meaning pull back along b^4 and push forward along f^4. The image of −2 Alt(W) is an algebraic codimension-four cycle on S^4 with class δ_S for the transported basis C(e_i). This solves the exact determinant detecting-cycle use case on this Kummer family. Its self-pairing is 4! det(q_S)≠0 by nondegeneracy, so it also satisfies the U002 detection condition.

## 5. All powers of this Kummer family

The rational Hodge group of U⊕V is SL(U)×SL(V): each non-CM elliptic curve has group SL2; the connected subdirect group is the full product because a diagonal identification of the simple factors would induce a Hodge identification of the standard two-dimensional representations, and hence an isogeny. Equivalently use the standard Hodge-group result for products of pairwise nonisogenous non-CM elliptic curves. Its image on U⊗V is SO(T(A),q) (the spin double cover in rank four), transported to T(S). The orthogonal invariant theorem as used in U002 then supplies all invariants on tensor powers from pairings and the alternating determinant. The Tate components of K3 cohomology are already algebraic. The pairing is represented by the transcendental projector of U002 and the determinant by the explicit cycle above. Products, permutations and correspondences therefore represent every rational Hodge class on every power S^m. This is a known special family (also obtainable by transfer from powers of abelian surfaces), not a new full Hodge proof or literature novelty.

The essential missing theorem for a general K3 remains an orientation-sensitive algebraic correspondence with no assumption of an elliptic product source. For example the very general Picard-rank-one K3 has rank 21, not rank four. The Kummer correspondence cannot be transported there merely by continuity or an arbitrary cohomology isomorphism. The universal Hodge conjecture would furthermore require arbitrary smooth projective varieties, not only K3 surfaces.

## 6. Full Millennium gap map and result

RH: all-order, possibly sparse-shift positivity (or actual exact negative witness); not established.
Hodge: all primitive rational Hodge classes on all smooth projective varieties; Kummer family completed, universal gap remains.
P vs NP: uniform polynomial-time correct SAT algorithm or unrestricted separation; neither follows from the rank-adaptive solver.
Navier–Stokes: a full official alternative with all PDE and data assumptions; U001 supplies continuation implication, not its universal bound.
Yang–Mills: nontrivial four-dimensional continuum construction, required axioms and regulator-uniform physical spectral gap for every compact simple gauge group.
BSD: rank equality on every elliptic curve over Q; full Sha finiteness and refined leading term are additional MathOS targets.
Poincaré: established externally by Perelman; MathOS reconstruction is distinct.

The two mathematical results are a universal conditional criterion and a genuinely completed geometric subfamily. The full-target AND across the unresolved problems remains blocked. No canonical obligation is closed by this paper. No software output is equated with a proof of a conjecture. Clay's external prize requirements are separate from internal use-case completion.

## References and reproduction

MathOS TGA-U001, TGA-U002-RH and TGA-U002-HODGE. Base commit ea8cba699f765156e5da9850a544072a08104493. Classical Hadamard factorization; Hermite matrix real-root criteria; Hamburger moment theorem. For a related finite real-root criterion see H. Yang, Semidefinite Optimization and Relaxation, Chapter 4, https://hankyang.seas.harvard.edu/Semidefinite/SOS.html .

D. Huybrechts, Lectures on K3 Surfaces, Cambridge University Press (2016), Kummer construction and Hodge conjecture for powers, https://ncatlab.org/nlab/files/HuybrechtsLecturesOnK3.pdf . M. Varesco, The Hodge conjecture for powers of K3 surfaces of Picard number 16, https://arxiv.org/abs/2203.09778 . Classical first fundamental theorem of the special orthogonal group; standard Hodge group of products of nonisogenous non-CM elliptic curves. This construction does not rely on any withdrawn Kuga–Satake claim.

Replay: python -m mathos.research.tga_u003

Tests: python -m unittest discover -s tests -p 'test_tga_u003.py' -v

No independent review performed; no formal proof certification, conjecture solution or prize eligibility claimed.
