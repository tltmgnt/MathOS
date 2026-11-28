# MathOS v25 — computational universality and barrier analysis

v24 passed both evidence and Lean CI (46151907433), including six
simulation controls, twelve restriction branches and ten parity
escapes. The measured source/lifted/projected inference counts were
120/246/240 respectively (projection sums both branches). This is
not a universal simulation theorem across all proof systems.

## 1. Published barriers (not re-proved here)

Baker, Gill and Solovay, *Relativizations of the P =? NP Question*
(1975), https://doi.org/10.1137/0204037: there exist oracles A,B
with P^A=NP^A and P^B!=NP^B. A proof uniformly valid relative to
every oracle cannot resolve either direction.

Razborov and Rudich, *Natural Proofs* (1997),
https://doi.org/10.1006/jcss.1997.1494: under sufficiently strong
pseudorandomness assumptions, no P-natural property is useful
against P/poly. Constructivity is polynomial time in truth-table
length, largeness is density at least 2^{-O(n)}, and usefulness
must exclude polynomial-size circuits in the appropriate
asymptotic sense. The cryptographic premise is conditional.
This is a circuit lower-bound barrier, not a blanket prohibition
on every possible proof of P!=NP.

Aaronson and Wigderson, *Algebrization: A New Barrier in
Complexity Theory* (2009), https://www.scottaaronson.com/papers/alg.pdf:
in their algebraic-oracle framework, major open separations and
inclusions including P versus NP require non-algebrizing techniques.
Their model gives an appropriate side access to a low-degree
extension of an oracle, not simply arbitrary use of algebra.
The published definitions and asymmetric inclusion/separation
conditions are essential. None of these three barriers is
declared overcome by the finite controls below.

## 2. Exact black-box query separation

Given a Boolean function f on n input bits accessible only through
point queries, decide if any f(x)=1. Even under the promise of
at most one 1, every deterministic always-correct algorithm
requires 2^n queries in the worst case: on an all-zero transcript
with any unseen index, both the identically zero table and the
singleton at that index agree with every answer. Determinism implies
the same adaptive query path and decision. Only querying all indices
removes the ambiguity. A nondeterministic positive certificate
requires one index and one query. This is a query-model theorem;
explicit CNF satisfiability allows inspection of the representation
and is not subject to this black-box lower bound. In particular,
this is not a construction of infinite separating oracles.

## 3. Stronger access changes the bound

For f with at most one 1, let its multilinear extension over GF(3)
be the sum over supported inputs of their interpolation basis
products. At point (2,...,2) every basis product is 2^n mod 3,
which is nonzero. A single exact extension query distinguishes
zero from any singleton. Constructing the extension oracle is not
free in a normal computational model; this counts oracle queries
only. With three ones the same evaluation is zero, providing a
counterexample to dropping the promise. This demonstrates why
a black-box obstruction need not survive an enriched oracle,
not the Aaronson–Wigderson theorem itself.

## 4. Restricted natural-property demonstration

Property: f depends essentially on all n input coordinates.
It is decidable in O(n 2^n) truth-table inspections by comparing
neighboring entries; hence constructive in table length.
Inclusion-exclusion counts accepted tables exactly:

    sum_{j=0}^n (-1)^j binom(n,j) 2^{2^{n-j}}.

A random table ignores a fixed coordinate with probability
2^{-2^{n-1}}. By union bound the density is at least
1-n*2^{-2^{n-1}}, approaching one. For a single-output acyclic
circuit with fan-in <=2, its ancestor subgraph has s gates and
at least n distinct input vertices when all coordinates are
essential. Connectivity requires at least s+n-1 edges and
fan-in allows at most 2s, so s>=n-1 (constants only increase
the required vertices). This property therefore yields a
linear gate lower bound, not a superpolynomial lower bound.
Parity satisfies the property and has linear-size XOR circuits
(or constant overhead per XOR in a fixed complete Boolean basis).
Thus the property is not useful against P/poly. The control
illustrates the missing usefulness obligation without claiming
to break cryptography.

## 5. Governance and reproducibility

The dossier records three published barriers as not_assessed
for any future universal proof strategy. It states separate
obligations for a uniform polynomial-time SAT algorithm and
an algorithm-independent lower bound. A syntactic validator
rejects unsupported changes to those statuses; it does not
automatically determine whether an arbitrary proof relativizes
or algebrizes. All E01/E02 claims remain unresolved.

    python -m mathos.research.pnp_barrier_frontier --checkpoint artifacts/pnp-v25.json
    python -m mathos.research.pnp_barrier_frontier --audit artifacts/pnp-v25.json

Eight dimensions (1,2,3,4,6,8,10,12); explicit transcript,
field-query and restricted circuit controls. Tests independently
enumerate small truth tables and Boolean interpolation points,
and check forged reports. Lean proves abstract transcript
agreement, incompatible decisions, and nonzero facts only.
The full published barrier results and asymptotic control
arguments are not formally verified by this release.
