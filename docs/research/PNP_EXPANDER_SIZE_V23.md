# MathOS v23 — exponential resolution size versus algebraic escape

v22 passed both CI jobs (46138183884), all 12 affine decisions and
balanced cuts, up to 512 variables. Its torus width bound is only
order sqrt(N), so the width–size theorem alone yields no growing
exponent from that bound. v23 uses a bounded-degree expander.

## Imported theorems and provenance

* Margulis–Gabber–Galil expander spectral theorem: for the 8-regular
  multigraph on Z_s^2, the second adjacency eigenvalue is at most
  5 sqrt(2). See Gabber and Galil, *Explicit constructions of
  linear-sized superconcentrators*, JCSS 22 (1981), 407–420,
  https://doi.org/10.1016/0022-0000(81)90040-4 ; construction and
  bound also stated in Wigderson, *Mathematics and Computation*,
  chapter on the Margulis construction
  (https://www.math.ias.edu/~avi/BOOKS/expanderbookr1.pdf).
  See https://networkx.org/documentation/stable/reference/generated/networkx.generators.expanders.margulis_gabber_galil_graph.html
  for the eight-neighbor multigraph convention.
* Ben-Sasson and Wigderson, *Short Proofs Are Narrow—Resolution
  Made Simple*, JACM 48 (2001), 149–169,
  https://doi.org/10.1145/375827.375835 , Corollary 3.6:
  ordinary resolution refutation size S(F) is
  exp(Omega((W(F)-w0)^2/N)), as a lower bound, where W is minimum
  refutation width, w0 maximum initial clause width, and N variables.

These published results are imported, not novel theorems of MathOS.
Their general proofs are not formalized by this release.

## Construction and separation

For s>=2, each vertex (x,y) of Z_s^2 emits four undirected edge
occurrences to (x+2y,y), (x+2y+1,y), (x,y+2x), (x,y+2x+1),
modulo s. This gives the four generators and their inverses.
Retain multiplicity, discard self-loops (they cancel in parity and
contribute nothing to cuts). Each remaining edge occurrence is a
separate variable. Set V=s^2. The Laplacian is unchanged by deleting
loops, and its first nonzero eigenvalue is at least
8-5 sqrt(2)>9/10. For a subset U the quadratic-form inequality,
applied to its centered indicator, yields

    |delta(U)| >= (9/10) |U|(1-|U|/V).

For V/3 < |U| <= 2V/3 this implies |delta(U)| >= V/5.
In particular the graph is connected. Put odd total charge on the
vertex parity equations and encode each as the clauses forbidding
wrong-parity local assignments. Degree at most eight means initial
width w0<=8 and at most 128 clauses per vertex. Edge count N<=4V,
and by connectivity N>=V-1. Input clause/literal counts are O(V)
(and ordinary bit encoding O(V log V)).

Apply the v22 minimum equation-support argument: proper subsets of
vertex equations are consistent by connectivity and linear
independence, so mu(empty)=V and mu(axiom)<=1. The first derived
clause above V/3 support has support <=2V/3 by binary subadditivity.
A minimum support U for a clause must have delta(U) contained in
its variable support: fixing its falsifying assignment and summing
a conflicting subset of rows gives a cut contained in those fixed
variables, and minimality forces that subset to be U. Thus
W(F)>=ceil(V/5). This also covers tautologies (mu=0), which cannot
be the crossing clause.

The imported width–size theorem now gives S(F)=2^{Omega(V)}
as a lower bound, equivalently 2^{Omega(N)}. This is exponential
in variable count and superpolynomial in ordinary input bit length.
Do not interpret it as a concrete numeric proof-size lower bound
at the tested sizes: the universal constant in Omega is unspecified.
The report stores only the rational exponent expression
max(0,ceil(V/5)-w0)^2/N, not a predicted proof count or runtime.

## Exact finite premises and independent decision replay

For supported sides, the verifier reconstructs all eight directed
neighbor occurrences, checks edge multiplicity, exact local CNF
truth tables, and both charge patterns. It verifies the finite
spectral premise with integer Bareiss elimination on a principal
minor of M=10 V L-9 V I+9 J. All leading principal determinants
must be positive. M annihilates the constant vector; any vector can
be shifted by a constant to zero its final coordinate. Hence
positive definiteness of the minor gives the claimed Laplacian
inequality by Sylvester's criterion. This is an exact integer
check, not floating-point eigenvalue estimation. Its work is
cubic in V arithmetic operations with polynomial-size integers,
not a hard CPU or memory bound.

Odd charge: sum all rows, cancel every variable twice, derive
0=1 with O(V) row references. Even twin: charge two vertices,
compute a spanning-tree assignment bottom-up and independently
check every original clause. This generalizes the affine escape
beyond the v7 arity-four compiler. No full resolution search is
required. SAT and UNSAT twins share graph and spectral premise;
only the odd case receives a refutation lower bound.

The exponential separation is between ordinary resolution
proof size and parity reasoning on this family. It is not an
algorithm-independent lower bound for SAT, nor a proof of P != NP.
A proof system with extra rules can escape the obstruction.

## Execute

    python -m mathos.research.pnp_expander_frontier --checkpoint artifacts/pnp-v23.json
    python -m mathos.research.pnp_expander_frontier --audit artifacts/pnp-v23.json

Six side lengths 2,3,4,6,8,10, both charge variants. Tests include
small exhaustive SAT and cut controls, tampering and report replay.
The finite spectral and parity certificates are computational;
full support-width and imported width–size arguments are not Lean
verified in this release. All universal obligations remain open.
