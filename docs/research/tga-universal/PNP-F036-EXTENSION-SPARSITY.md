# F036 — Sparse global extensions do not rescue logarithmic-depth lifting

PNP_RESOLUTION_STATUS = OPEN.

Status: mathematical argument for independent review; no new Lean credit.
This strengthens the preceding global-degree restriction: global degree
can be arbitrarily high, as long as fully expanded Boolean polynomials
are sparse. It does not rule out arbitrary circuits or all SAT solvers.

## Quantified substitution size bound

Use the same total definitional extension hypothesis as
PNP-F036-EXTENSION-DEGREE.md. Let n be the original variable count,
m the total variable count, q the number of input and extension
clauses, and s>=1 the maximum number of nonzero square-free monomials
in any fully composed auxiliary polynomial over GF(2). Original
variables have one monomial. Let D>=3 be a multilinear PC refutation
degree of the extended formula (charged multiplication convention).
Put M=sum_(i=0)^D binom(m,i), with binomial coefficients zero for i>m.

Claim: there exists an ordinary PC refutation of the original formula
with total monomial size bounded by

    poly(n,m,q) * M^O(1) * (s+1)^O(D).

The constants in the O-notation can be chosen uniformly, independent
of n,m,q,s,D. No claim that the proof can be discovered efficiently,
or that the substituted proof has small degree.

### Step 1: compress the degree-bounded proof

In the Boolean quotient ring, all multilinear polynomials of degree
at most D lie in an M-dimensional vector space. Scan any existing
degree-D refutation, maintaining an independent basis of the span
of the lines encountered, all actually derived. Ignore dependent
lines. A new independent axiom can be added directly. A linear
combination of earlier lines cannot enlarge the span. When a
multiplication step adds an independent line, reconstruct the
particular predecessor from the current basis by at most M additions,
then multiply by its specified variable and reduce square-free.
The predecessor equals the original predecessor, so the multiplication
respects the charged degree cap. At most M independent lines can
be added; reconstruct 1 at the end if necessary. The resulting
refutation has O(M^2+M) lines, each at most M monomials.
This is an existence argument based on the original proof, not
an efficient proof-search algorithm.

### Step 2: eliminate the auxiliary variables

Substitute their fully composed multilinear Boolean polynomials.
Every input extension clause maps to zero by the total definitional
property, while original clauses are unchanged. The substitution
is a homomorphism of Boolean quotient rings. Each degree-D proof
line becomes a polynomial with at most B=M*s^D monomials: each
original monomial multiplies at most D substituted factors.

Linear combinations simulate directly. For a multiplication by an
extended variable y, expand its substituted polynomial into at most
s monomials t. Derive each t times the substituted predecessor via
at most n single-variable multiplication steps. Multiplication by
one square-free monomial cannot increase the count of nonzero
monomials in the quotient. Add the resulting at most s polynomials;
all intermediate reduced lines have at most s*B monomials.
The number of new quotient-ring lines per old line is O((n+1)(s+1)).
The final line is still 1. Zero can be derived from an original
clause added to itself (the original unsatisfiable CNF is nonempty).

### Step 3: ordinary polynomial calculus size

If PC is formulated in the ordinary polynomial ring with explicit
Boolean axioms x_i^2-x_i, each single-variable multiplication of
a square-free polynomial can be followed by multilinear reduction.
For each monomial that acquired a repeated variable x_i, the
difference between it and its square-free version is the appropriate
monomial multiple of x_i^2-x_i. Derive that two-term multiple by
at most n variable multiplications and add it to the current line.
There are at most s*B such monomials to reduce in a simulated step;
the expanded line count is O(n(s*B+1)) and each line has at most
O(s*B+1) monomials. Thus the conversion costs only a fixed polynomial
in n and s*B, establishing the claimed bound. The convention using
charged inference degree differs from ordinary maximal line degree
by at most one; a linear lower bound in one is linear in the other.

## Consequence on the previous hard family

Alekhnovich and Razborov (2003) establish linear PC degree for random
fixed-density 3-CNFs over characteristic two. Choose a density above
the first-moment UNSAT threshold, as in the degree-depth note, so
there exist unsatisfiable n-variable O(n)-clause instances with linear
PC degree. The Impagliazzo–Pudlak–Sgall size-degree relation implies
that ordinary expanded PC refutations of these instances require
2^Omega(n) total monomial size. This follows by contraposition:
degree O(3+sqrt(n log S)) would contradict a linear degree lower
bound if log S=o(n).

Now suppose m,q,s are polynomial in n and the F036 hybrid uses
constant static leaf cap d and logarithmic adaptive split depth h,
including splits on auxiliary variables. The degree-depth transfer
on the extended CNF gives D<=max(4,d+1)+h=O(log n), regardless of
the global degrees of the auxiliary functions. M<=(m+1)^D,
so log S=O(log^2 n) by the size simulation. This contradicts
the exponential ordinary PC size lower bound.

More generally, with polynomial m,q, the necessary condition on
this hard family is

    D * (log(m+1)+log(s+1)) = Omega(n)

up to the additive polynomial-overhead log(n+m+q), which is O(log n).
In particular if D=O(log n), some globally composed auxiliary
polynomial must have s>=2^Omega(n/log n). This is a lower bound on
the maximum expanded monomial count of the chosen extension functions
under the total definitional extension hypothesis; not their circuit
description size. If the extension has many possible witnessing
functions, the argument excludes any simultaneous sparse choice.

## Why this matters

A long AND chain, for example, has global degree n but a single
square-free monomial. High global degree alone does not circumvent
this stronger substitution barrier. A compact OR chain can have
2^n-1 monomials; its Boolean function is 1+product_i(1+x_i).
This illustrates the distinction between circuit size and ANF
sparsity, not the sufficiency of dense functions for refutation.

## External results (not MathOS novelty claims)

Alekhnovich–Razborov, Lower Bounds for Polynomial Calculus:
Nonbinomial Case (2003), published abstract confirms the random-CNF
degree lower bound over characteristic two:
https://mathnet.ru/eng/tm403

Miksa–Nordstrom, A Generalized Method for Proving Polynomial Calculus
Degree Lower Bounds (JACM 2024), discusses PC and PCR degree and
monomial size and the Impagliazzo et al. size-degree implication:
https://doi.org/10.1145/3675668

Lagarde, Nordstrom, Sokolov, Swernofsky, Trade-Offs Between Size
and Degree in Polynomial Calculus (ITCS 2020):
https://doi.org/10.4230/LIPIcs.ITCS.2020.72

## Research decision

This closes the polynomial-size, polynomial-global-sparsity
extension version of the fixed-degree/logarithmic-depth conjecture,
conditional on review of the substitution and preceding degree-depth
derivations. Dense but succinct extension functions, larger degree
or depth, and different inference systems are not excluded. Do not
infer a lower bound on every SAT algorithm. In particular arbitrary
extended Frege remains outside this argument. Compact circuit
representation alone establishes no efficient decision procedure.

Before further implementation, specify the exact operations on dense
extension circuits and prove a noncircular completeness/resource
invariant, or pursue a different general mechanism. The current
analysis does not supply one. Main unchanged.
