# F038 — Explicit affine-tape hitting and the uniformity gap

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivation and finite regression, not a Lean declaration.
Verified base 92b529c61e5e36cc6a0f17004fda3d2b6925eeb3: https://github.com/tltmgnt/MathOS/actions/runs/45707352503 (success).

## A common polynomial-size list exists under randomized coverage

Use the free-suffix polynomial-window sweep of the preceding note. For fixed a,k, concatenate the independent suffix tapes for lengths N through N^a, giving R(N)=sum_m(m-N) random bits, a polynomial in N. A deterministic execution on a tape checks witnesses independently. Suppose every satisfiable encoded input of length N has success probability at least N^(-q), for fixed q and sufficiently large N. Take t=ceil((N+1)N^q) independent R(N)-bit tapes. The probability that some satisfiable length-N input is missed by all t tapes is at most 2^N (1-N^(-q))^t <= 2^N exp(-(N+1))<1. Thus a common list of t tapes exists for ALL inputs of that length. Its encoded size is polynomial in N. If provided as length-dependent advice, exhaustive execution of the list is a deterministic polynomial-time SAT decision algorithm with advice. This is a direct nonuniform simulation; it yields NP subseteq P/poly under the stated coverage (equivalent to NP=RP for the fixed universal search), not P=NP. The union bound supplies no efficient uniform generator or way to certify the list. If R=0, there is only the empty tape and the same conclusion is immediate.

## Explicit polynomial-time list for affine-rich success sets

For an input f, let S_f be the set of successful R-bit sweep tapes for its fixed polynomial clock; success is checked by direct execution. Suppose S_f contains a nonempty affine subspace of codimension at most h in GF(2)^R. The subspace may depend on f, and neither its equations nor an element need be supplied. Here h is an a priori upper bound. An explicit, input-independent list hitting every such affine subspace can be constructed as follows.

For R>=1 let Q=2^r be the smallest power of two with Q>max(1,(R-1)2^h). Work in GF(Q); find a monic irreducible binary polynomial of degree r by deterministic enumeration and trial division by all monic polynomials of degrees 1 through floor(r/2). Existence is the elementary finite-field existence theorem. Enumeration and division cost polynomial in Q and r. Let L:GF(Q)->GF(2) be the nonzero linear functional extracting the constant coefficient in the polynomial basis. Enumerate all x,y in GF(Q) and output the tape
    v(x,y)_i = L(x y^i),  i=0,...,R-1.
The convention y^0=1 includes y=0. The list has Q^2=O((R+1)^2 4^h) entries counting repetitions; computation and explicit output cost are polynomial in R and 2^h. Duplicates may be discarded but are retained in the bias analysis.

For any nonzero a in GF(2)^R, let P_a(Y)=sum_i a_i Y^i, a nonzero polynomial over GF(Q) of degree <=R-1. The average of (-1)^(a dot v(x,y)) over x is one when P_a(y)=0 and zero otherwise: if P_a(y) is nonzero, multiplication by it is a bijection and the nonzero linear functional is balanced. The average over both x,y therefore lies between zero and (R-1)/Q. In particular the distribution has absolute bias epsilon<2^(-h) on every nonzero parity. This is the standard small-bias polynomial-evaluation construction, derived here directly.

For any consistent independent system A v=b with c<=h rows, expand its indicator as
    1[Av=b] = 2^(-c) sum_{u in GF(2)^c} (-1)^(u dot (Av-b)).
The u=0 term contributes 2^(-c); each other character is nonzero because A has row rank c, and its absolute average is bounded by epsilon. Hence the list's fraction in the affine subspace is at least
    2^(-c) - (1-2^(-c)) epsilon > 0.
The codimension-zero case is immediate. The construction hits all affine subspaces simultaneously, with arbitrary right-hand sides. It requires no enumeration of their equations or semantic recognition of the success set.

Consequently, if every sufficiently long satisfiable f has an affine subspace of successful tapes of codimension h<=C log2(N+1) for some fixed C, then the explicit list plus the fixed-clock verifier gives P=NP. Choose the integer upper bound h=ceil(C log2(N+1)) with C replaced by a fixed integer upper bound; R is polynomial in N, so Q and list size are polynomial in N. Finite exceptions are solved exhaustively. The same guarantee applies to any successful set containing even one such affine subspace, including unions of affine subspaces. This is a sufficient structural condition, not a theorem that arbitrary randomized SAT witness search has it. It does not require NP=RP separately because the structural promise itself implies useful mass. The reverse direction holds existentially for suitable clocks if P=NP: eventual success on all padded tapes gives codimension zero.

## Density alone does not give this affine promise

For fixed c<=R, every affine subspace of codimension c is described by at most cR+c bits (a matrix and right-hand side), so there are at most 2^(c(R+1)) such subspaces. A random set of tapes formed by including each tape independently with probability 3/4 contains any given affine subspace of codimension <=h with probability at most (3/4)^(2^(R-h)). The union bound over c<=h is at most (h+1)2^(h(R+1))(3/4)^(2^(R-h)), which tends to zero for h=O(log R). Meanwhile the density is at least 1/2 with probability tending to one, e.g. by Chebyshev's inequality. Hence there exist dense success sets containing no affine subspace of codimension <=h. This is a set-theoretic counterexample to inferring affine richness merely from density, not an efficient circuit construction or a lower bound for arbitrary SAT algorithms.

An even simpler limitation applies to any fixed list H: if |H|<2^(R-1), its complement is a dense set missed by H. Membership in that complement has an explicit circuit of O(R |H|+R) size (compare against each listed string). This does not preclude hitting circuits of a specified smaller size bound, and does not prove that the universal SAT success sets realize these complements. A derandomization argument must exploit additional structure or an appropriate bounded circuit class, not density by itself.

## Finite audit

For (R,h,Q,polynomial)=(2,1,4,7),(3,2,16,19),(4,2,16,19),(5,2,32,37), exhaust field inverses, all Q^2 tapes, all nonzero binary parities, and all ordered systems with h rows including zero rows and redundant or contradictory equations. Compare each system against exhaustive tape assignments. Expected four fields, 1552 generated entries, 56 characters, 37424 character evaluations, 5384 systems (5056 consistent, 328 inconsistent), 1130560 total hit multiplicities, minimum six hits among consistent systems. Also instantiate R=32,h=2,Q=128, polynomial 131: 16384 entries, 2289 distinct tapes versus 2^32 possible tapes. Verify field irreducibility by trial division and test selected rank-two systems over the longer tapes. The finite tests validate construction, not the affine-richness promise for unrestricted SAT.

Next: either prove a structural condition on actual successful tapes of a uniform algorithm, or explicitly account for the remaining unrestricted hitting-set obligation. No P versus NP resolution or Lean increment.
