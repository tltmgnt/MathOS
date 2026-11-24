# Topological gap analysis: universal implication theorems

**MathOS TGA-U001 | 24 November 2026 | Research note; universal conjectures not solved**

## 1. Method and scope

The existing CLAY_PROOF_TOPOLOGY.md models 11 candidate routes and 10 bridge placeholders, referencing 14 canonical open work packages. Its analyzer computes inclusion-minimal unresolved sets in an authored AND/OR graph, not mathematical necessity. Here we derive universally quantified implication theorems, separate their genuinely unproved hypotheses, and construct a distinct graph of these refined routes. The original register is unchanged. The results are mathematical reductions using established background, not new solutions or claimed literature priority. Independent review is nonblocking for this research note, not represented as performed.

## 2. Riemann: a moment-to-spectrum theorem

Let xi be the completed Riemann xi function, Xi(z)=xi(1/2+iz), and G(w)=Xi(sqrt(w))/Xi(0). Evenness makes G single-valued and entire. Xi(0) is nonzero (the alternating eta series at 1/2 is positive, and zeta(1/2)=eta(1/2)/(1−sqrt(2))). Since xi has order one, G has order at most 1/2. Its coefficients are real. Define real m_n by the Taylor series −G'(w)/G(w)=Σ_(n≥0)m_n w^n near zero; this uses the analytic function, not an assumed real zero spectrum.

THEOREM. RH is equivalent to the following universal inequalities: for every integer d≥0, both real Hankel matrices (m_(i+j)) and (m_(i+j+1)), 0≤i,j≤d, are positive semidefinite.

Proof, forward: under RH every zero of G is a positive real number w_j, with multiplicity. Hadamard factorization of an entire function of order less than one gives G(w)=Π_j(1−w/w_j), with Σ_j 1/w_j finite. The logarithmic derivative has m_n=Σ_j w_j^(−n−1). This is the moment sequence of a finite positive measure placing mass 1/w_j at 1/w_j, repeated by multiplicity. Integrating the squares of real polynomials, and t times those squares, proves both inequalities.

Proof, reverse: the classical Stieltjes moment theorem applied to the two infinite families of inequalities gives a finite positive measure μ on [0,∞) with m_n=∫t^n dμ. Since the logarithmic derivative is analytic in a disk about zero, Cauchy estimates give |m_n|≤C R^n for some finite R>0. If μ assigned positive mass to [R+δ,∞) for any δ>0, its moments would eventually exceed that bound. Thus μ is supported in [0,R]. The integral F(w)=∫(1−wt)^(-1)dμ(t) is holomorphic on the slit plane C excluding [1/R,∞), agrees with −G'/G near zero, and agrees meromorphically throughout the connected slit plane by the identity theorem. A zero of G anywhere in that plane would give a nonremovable logarithmic derivative pole, contradicting holomorphy of F. Thus all zeros of G are positive real, proving RH.

The same hypothesis constructs the required trace-class determinant: the genus-zero product now applies, and uniqueness of compactly supported moments (polynomial density) identifies μ with the discrete measure Σ_j w_j^(-1) δ_(1/w_j). Each positive atom t has multiplicity μ({t})/t, an integer. On a Hilbert space with that many orthonormal basis vectors per atom, let K act by multiplication by t. K is positive trace class, tr K=μ([0,R]), and G(w)=det(I−wK), including all multiplicities. This reconstructs the spectrum from the analytic moment measure; its existence is conditional on the universal inequalities, not a proof of them.

NEW ATTACK TARGET: Prove both Hankel families positive semidefinite for every d by an identity directly in the Taylor coefficients of xi, or find an exact violation. Finite positivity is not sufficient. For any fixed d choose d+1 distinct positive t_j and the real polynomial G_e(w)=Π_j(1−t_j w)(1+e w). At e=0 both Hankel matrices through order d are positive definite by the Vandermonde argument. For small positive e continuity preserves them, yet G_e has a negative zero. The square of Π_j(t−t_j) gives a strictly negative unshifted moment quadratic form at degree d+1, since only the negative atom at −e survives. This is a countermodel to finite-truncation inference, not evidence of an off-line zeta zero. Exact rational examples are replayed in the companion code.

## 3. P versus NP: class-level bridge and unbounded rank

For every language L in NP, Cook–Levin supplies a uniform polynomial-time many-one reduction to SAT (and the standard polynomial transformation to 3-SAT). If one uniform deterministic algorithm decides every encoded 3-CNF in polynomial total bit operations, composing reduction and algorithm puts every L in P. P⊆NP, hence P=NP. Conversely P=NP implies such a decision algorithm. A lower bound must cover every uniform deterministic polynomial-time algorithm for an NP language, not one representation.

For an arbitrary AND/affine system, each 3-CNF clause is encoded by three fresh variables equal to the negated literals, two AND gates multiplying them, and an affine equation setting the product to zero. This is a polynomial reduction and preserves satisfiability. Thus this exact general gate family is NP-complete. The disjoint-block cycle-six solver cannot cover it because variables overlap.

An exact rank-adaptive extension solves the affine equations first; the affine solution space is x0+V. Project onto the selected first operands of all AND gates, let r be the dimension of the projected V, enumerate its 2^r values, and solve each affine linearization. Every original solution appears in one branch and each accepted branch lifts to an original solution. Its complexity is O(2^r poly(input length)). The example a_i+b_i=1, y_i=1, y_i=a_i b_i for k independent triples has r=k and no solution; this enumeration requires all 2^k branches. This rejects a universal logarithmic bound for this algorithm, not P=NP. The actual missing theorem is an unrestricted polynomial-time algorithm (or unrestricted separation).

## 4. Navier–Stokes: critical bound implies continuation

Fix viscosity ν>0 and either R³ with the official rapidly decaying smooth divergence-free initial data or the periodic three-torus with smooth divergence-free data. Suppose the local smooth unforced solution has finite integral I_T=∫_0^T ||u||_6^4 dt at every finite candidate maximal smooth lifespan T. Then the local solution extends globally.

Proof: take the L² inner product of the momentum equation with −Δu. The pressure contribution vanishes by incompressibility and integration by parts. With X=||∇u||₂² and Y=||Δu||₂²,

X'/2+νY ≤ ||u||₆ ||∇u||₃ ||Δu||₂ ≤ C||u||₆ X^(1/4)Y^(3/4).

The last inequality uses interpolation and Sobolev for ∇u (zero mean in the periodic case), plus equality of the Hessian and Laplacian L² norms. Young's inequality bounds the right side by νY/2 + C_ν ||u||₆⁴ X with C_ν proportional to ν^(-3). Gronwall gives sup X ≤ X(0) exp(2 C_ν I_T). Together with the energy bound this controls the H¹ norm. Standard local strong-solution existence in H¹ with lifespan bounded below by a function of that norm and ν, followed by smoothing and uniqueness, extends past T, a contradiction. The energy identity supplies the required L² bound on R³; on the torus it also controls the constant mode. Pressure is reconstructed by the usual Poisson equation. This recovers the unforced continuation bridge; it does not establish I_T for all solutions.

ACTUAL GAP: prove the stated critical estimate for either entire official unforced data class, or establish an official forced-breakdown alternative. NS-B002 shows that exact integrated kinetic energy and enstrophy balances alone are insufficient for a critical bound, and NS-B003 excludes that particular compact-support path from true dynamics, not all possible concentration. The CMI September 11 announcement concerns an apparent solution under evaluation; the CMI problem page still lists Active at the source check. Forced and unforced routes are separate.

## 5. Hodge: primitive reduction for every dimension and codimension

THEOREM. Fix a smooth complex projective variety X of complex dimension n, with rational ample hyperplane class h, and write Lα=h∪α. If every rational primitive Hodge class in degree 2q≤n has an algebraic rational cycle representative on X, then every rational Hodge class of every codimension on X has an algebraic rational cycle representative.

Proof: Hard Lefschetz gives the rational Lefschetz decomposition of H^(2p)(X,Q) as a direct sum of L^j P^(2p−2j)(X,Q), over the admissible nonnegative j, with primitive degrees at most n. Here P^k=ker(L^(n−k+1):H^k→H^(2n−k+2)), k≤n. Each primitive subspace is a rational Hodge substructure because L has bidegree (1,1), and each summand L^j P is a rational Hodge substructure of H^(2p). Thus if α is rational of type (p,p), its uniquely determined components are rational of type (p,p). Injectivity of L^j on the relevant primitive subspace and its Hodge bidegree imply the primitive preimage β_j is rational of type (p−j,p−j). By hypothesis choose a rational algebraic cycle Z_j with class β_j. The product of the hyperplane cycle class j times with Z_j is a rational algebraic cycle in the Chow ring of the smooth variety, whose cohomology class is L^j β_j. Summing these cycles represents α. This includes high-degree classes; no claim that an inverse Lefschetz correspondence is algebraic is needed.

Consequently the universal primitive conjecture, quantified over ALL smooth complex projective varieties and ALL primitive rational (q,q) classes, is equivalent to the full rational Hodge conjecture. The converse is immediate by restriction to primitive classes. This derives the logical reduction rather than assuming it. It does not construct cycles for the unknown primitive classes. In dimensions ≤3 the only nontrivial primitive even degree is 2, covered by Lefschetz (1,1); degree zero is algebraic. For higher dimensions the actual primitive-cycle theorem remains missing. Reduction to one convenient product family or only one codimension is insufficient.

## 6. Yang–Mills: dense-sector mass-gap theorem

THEOREM. Let H≥0 be self-adjoint on a reconstructed Hilbert space with a normalized vacuum Ω, HΩ=0. Let D be a dense subset of Ω-perp. If for one Δ>0 and each ψ∈D there is a finite Cψ such that <ψ,e^(−tH)ψ>≤Cψ exp(−Δt) for every t≥0, then the spectrum on Ω-perp lies in [Δ,∞). Conversely such a gap implies the bounds with Cψ=||ψ||².

Proof: the spectral measure μψ is finite and positive. For any 0≤b<Δ, e^(−bt) μψ([0,b])≤∫e^(−Et)dμψ(E)≤Cψ e^(−Δt). Let t→∞, obtaining μψ([0,b])=0. The spectral projection of [0,b] annihilates D, hence annihilates its closure Ω-perp by boundedness. Taking a sequence b increasing to Δ gives the claimed gap, including exclusion of additional zero-energy states. The converse follows directly by spectral calculus.

If regulator-dependent positive-time connected correlations converge to the reconstructed matrix elements on such a dense family at each fixed physical t, and satisfy a common exp(−Δt) bound with finite regulator-independent constants per state, the inequality passes to the limit. No uniform constant across states is needed. A single channel is insufficient: a diagonal Hamiltonian with vacuum energy 0, another energy 1 and energies 1/j for j≥2 has no gap, while the channel at energy 1 decays exactly as e^(−t). This proves the gap transfer implication conditional on reconstruction, convergence and dense uniform physical-rate control. It does not construct 4D Yang–Mills or prove the uniform estimate for any non-Abelian gauge theory. Each compact simple gauge group must be covered, with a nontrivial continuum theory and the required axioms.

## 7. BSD: separate core rank from refined formula

For any elliptic curve E/Q and prime p, the standard full p-power Selmer exact sequence is

0 → E(Q)⊗Q_p/Z_p → Sel_(p^∞)(E/Q) → Sha(E/Q)[p^∞] → 0.

The groups are cofinitely generated over Z_p, and taking coranks gives corank Sel=rank E(Q)+corank Sha[p^∞]. Thus for any fixed prime p, if for every E the analytic order equals that Selmer corank AND the p-primary Sha is finite, then analytic order equals rational rank for every E. It is enough to prove the two hypotheses at the same prime for each E; full Sha finiteness is not needed for the core rank statement. This bridge is universal, but the hypotheses remain unproved. The cycle-six special curve and primes do not supply them for every E.

For refined BSD, full Sha is finite iff some integer N>0 annihilates Sha: the reverse follows because Sha[N] is finite by finite-level descent. Equivalently all primary components are finite and only finitely many nonzero. Even finite primary components for every prime cannot imply the support bound (direct sum of Z/pZ over primes). The refined leading-term identity with the prescribed period, regulator, Tamagawa factors, torsion and finite Sha remains a separate arithmetic theorem. No general equality or finiteness is obtained.

## 8. Poincaré and structural gap theorem

Poincaré is externally established via Perelman's proof. MathOS's separate reconstruction is still an open project. No new universal conjecture is required here; the reconstruction cannot be declared complete from a graph.

For any finite acyclic AND/OR dependency graph with correctly justified edges, the inclusion-minimal sets of open leaves sufficient for a target are obtained by taking unions across AND prerequisites, alternatives across OR, and deleting supersets. Induction on topological order proves this: at a leaf the empty set or singleton is correct, at an AND any sufficient set contains sufficient subsets for all children, and at an OR it contains one for a successful child. The union/minimalization recurrence is therefore exact. Moreover an inclusion-minimal set of leaves whose failure intersects every completion set is a minimal transversal of this hypergraph; it blocks every modeled alternative, not every possible mathematical proof. Neither theorem creates the truth of missing leaves.

The companion code builds a second graph with these explicit derived implications and open mathematical hypotheses. In particular Hodge now has one primitive gap in this derived route, RH one all-order positivity gap, BSD core is separated from its stronger formula, and NS alternatives have distinct scope. Counts describe modeled dependencies, not progress percentages or certification. The code cross-checks minimal completion sets by exhaustive truth assignments and tests exact rational finite-Hankel countermodels. The canonical 14-work-package register stays open.

## References and reproducibility

Repository: docs/research/CLAY_PROOF_TOPOLOGY.md; CLAY_PROOF_ROUTES.v1.json; mathos/proof_analysis/gap_analysis.py; previous NS-B002/003, RH-B001/002/003, PNP-B006, BSD-B004/006. Pinned base: 345e8d6578e38d04f94d08d49aaeb826ea20a00a.

Stieltjes moment theorem: K. Schmüdgen, The Moment Problem, Springer (2017), Theorem 3.12; https://link.springer.com/article/10.1007/s00013-021-01599-9 . Classical xi function: https://encyclopediaofmath.org/index.php?title=Riemann_xi-function .

Official statements (Deligne, Fefferman, Jaffe–Witten and others): https://www.claymath.org/millennium-problems/ . Continuation uses the classical strong-solution theory and Prodi–Serrin criterion. CMI announcement: https://www.claymath.org/news/navier-stokes-announcement/ .

Standard algebraic geometry: C. Voisin, Hodge Theory and Complex Algebraic Geometry I, Lefschetz decomposition; standard arithmetic: J. H. Silverman, The Arithmetic of Elliptic Curves, descent. Spectral theorem and Cook–Levin are standard established background. No new claim of literature priority.

Replay: python -m mathos.research.tga_universal_bridges

Tests: python -m unittest discover -s tests -p 'test_tga_universal_bridges.py' -v

No independent review performed. No universal Millennium solution, formal verification, or canonical proof promotion asserted.
