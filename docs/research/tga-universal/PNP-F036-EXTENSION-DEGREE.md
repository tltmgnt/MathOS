# F036 — Global extension degree: a substitution barrier

PNP_RESOLUTION_STATUS = OPEN.

Status: mathematical derivation for independent review. No Lean
verification credit or claim of a new general complexity separation.

## Definitions and quantified claim

Work in the multilinear Boolean ring over GF(2). Let F be a 3-CNF
on n original variables. Add any finite number of auxiliary Boolean
variables and width-at-most-three clauses E. Assume a total
definitional extension: for each original assignment x there is a
specified auxiliary assignment g(x) satisfying E (whether or not
x satisfies F). Let each coordinate of g have a fully composed
multilinear polynomial of degree at most r, with r >= 1.
This degree is measured in the ORIGINAL variables, not merely
in the immediate inputs of a gate. No assumption about the
number of extensions, efficient discovery, or their fan-in.

Write D_PC for refutation degree using the charged multiplication
degree convention in Definition 2.1 of Alekhnovich–Razborov.
For every refutation of F and E of degree D >= 3,

    D_PC(F) <= r D.

Here and below degree may be padded to 3 to include the input
axioms. In particular if the F036 hybrid refutes the extended
CNF with static leaf degree d and branch height h, the preceding
degree-depth transfer gives

    D_PC(F) <= r (max(4,d+1) + h).

## Proof of substitution simulation

Let phi be the substitution sending original variables to themselves
and auxiliary variables to their globally expanded Boolean
polynomials. This defines a ring homomorphism: every polynomial
over GF(2) in the Boolean quotient is idempotent, so phi respects
the defining relations y^2=y. A monomial of degree k maps to
a polynomial of degree at most rk, by multiplying at most k
polynomials of degree <=r. Consequently deg(phi(p))<=r deg(p)
for every nonzero p, with zero treated as degree zero for bounds.

Translate each proof line p to phi(p). Original input polynomials
are unchanged. Each extension clause polynomial maps to zero:
it vanishes at every original assignment by total definitional
extension, hence is identically zero by uniqueness of the
multilinear representation. Zero can be derived from any original
input polynomial by adding it to itself; an unsatisfiable F is
nonempty. This costs degree at most 3. Linear combination steps
translate by the homomorphism property.

For a multiplication inference p -> y*p, expand phi(y) as a sum of
square-free monomials t. From phi(p) derive each t*phi(p) by
multiplication by its constituent original variables, then add
all these products. Every such monomial t has at most r factors.
After j multiplication steps the degree is at most r deg(p)+j,
and the multiplication inference charge is at most this same
upper bound. The original inference was charged deg(p)+1<=D.
Therefore every simulated inference has degree at most
r deg(p)+r <= rD. Addition steps also obey the bound. If phi(y)
or phi(p) is zero, use the derived zero. The final line maps from
1 to 1. This proves the claim without a bound on proof size;
expanding phi(y) can itself be costly.

## Consequence

Alekhnovich and Razborov, Lower Bounds for Polynomial Calculus:
Non-Binomial Case, Corollary 4.8, gives Omega(n) PC degree
for random fixed-density 3-CNFs over GF(2). The unsatisfiable
linear-clause family used in the preceding F036 note has
D_PC(F)>=alpha*n for some fixed alpha>0. Hence

    r (max(4,d+1)+h) >= alpha*n.

If both d and r are fixed, h=Omega(n), even if an optimal extension
and split tree were supplied by an oracle. More generally, with
fixed d and h=O(log n), global extension degree r must be
Omega(n/log n) on this hard family. A polynomial-size extension
and logarithmic depth in the extended encoded input length still
have h=O(log n), since the original encoded length is O(n log n).

This excludes arbitrary many bounded-global-degree definitional
extensions as a way to rescue the fixed-degree/logarithmic-depth
conjecture. It also covers global affine extensions, such as
arbitrary parity functions, even if they depend on all original bits.
It does NOT exclude recursively composed high-global-degree
extensions. A chain of binary AND gates can represent a degree-n
monomial using n-1 auxiliary variables and degree-two local gate
definitions. Local gate degree therefore cannot replace global r
in the transfer bound.

## Sources and related work

Verified against the primary source, Definition 2.1 (printed
pp. 4–5), Corollary 4.8 (printed p. 21):
https://static.aminer.org/pdf/PDF/000/209/798/lower_bounds_for_polynomial_calculus_non_binomial_case.pdf
Published article: https://mathnet.ru/eng/tm403

Related established research on restricted extension variables:
Lower bounds for Polynomial Calculus with extension variables over
finite fields (ECCC TR22-038), https://eccc.weizmann.ac.il/report/2022/038/
The present note is an elementary substitution degree argument,
not a claim of novelty or a replacement for those size bounds.

## Next research gate

High-global-degree extension circuits escape this particular
degree transfer, but polynomial-size circuit descriptions do not
imply polynomially bounded refutations or efficient discovery.
For the positive route, formulate an explicit uniform extension
construction plus complete polynomial-cost inference/decision
algorithm, rather than assume that arbitrary extension circuits
will provide it. For a negative route, the current bound remains
restricted to a proof system and a degree-depth objective.
Do not infer exponential tree size from linear height. No
unrestricted P versus NP conclusion follows.
