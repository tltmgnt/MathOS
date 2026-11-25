# F036 — Degree/depth transfer rules out the logarithmic-depth hypothesis

PNP_RESOLUTION_STATUS = OPEN.

Status: mathematical derivation for review; not a Lean theorem or a new
general proof-complexity lower bound. Uses a published external lower bound.

## Claim

For a 3-CNF F, suppose the F036 hybrid has a refuting adaptive binary
tree of maximum depth h (unit propagation does not count as a split)
whose leaves use static square-free GF(2) monomial multiples of the
residual clauses at degree cap d. Then F has a multilinear polynomial
calculus (PC) refutation of degree at most max(4,d+1)+h, in the degree
convention of Alekhnovich and Razborov, Definition 2.1. This includes
their multiplication inference charge deg(p)+1 even when the reduced
result has smaller degree. The argument does not assume efficient
tree discovery, balanced trees, or a fixed variable order.

Work in R = GF(2)[x_1,...,x_n]/(x_i^2-x_i). The input polynomials are
p_C = product_(v,b in C)(x_v+b), equal to zero for a satisfied clause.
PC allows linear combinations and multiplication by a single variable
with multilinear reduction.

### 1. Leaf translation

After fixing variables by explicit branch choices, consider the
restricted clauses as axioms. Simulate unit propagation by PC without
charging one extra degree for every forced variable. If the unit
equation is x+a=0 and another clause contains x+b, write the latter
as p=(x+b)q. If a=b, discard the satisfied clause. If a differs from b,
multiply the unit polynomial by each monomial of q and add the results,
then add p. The result is q, the equation for the shortened clause.
Since deg(q)<=2, this uses degree at most 3. An empty clause or two
opposite units give 1. Repeated variables can be normalized in the
Boolean quotient; the hard family below already has distinct variables
in each input clause.

A successful static span test expresses 1 as a GF(2) sum of reduced
products m*p_C of degree <=d, with m a square-free monomial of degree
<=d. For a nonzero product, all positive-literal variables in p_C
are disjoint from m (otherwise x(1+x)=0). The degree of each
nonzero successive reduced product is the cardinality of the union
of the support of p_C and the already multiplied variables. This
follows by factoring out variables in m and retaining the remaining
clause factors; the top monomial has coefficient one. In particular
the intermediate degrees cannot exceed the final degree. Zero
products can be omitted from the linear combination. Thus each
nonzero product can be generated from the clause polynomial using
degree <=max(3,d+1) including the multiplication charge. A linear
combination gives 1. A leaf proof, including its unit propagation,
therefore has degree <=max(4,d+1).

### 2. Lift a child refutation through one split

For a split x=b let I_b be x for b=1, and 1+x for b=0.
For each parent polynomial p, in R:

    I_b p = I_b (p restricted to x=b).

A restricted nonzero clause axiom originates in a parent clause.
Derive its I_b multiple from that parent polynomial, multiplying by
x and, for b=0, adding the original polynomial. This costs degree <=4.
Translate every child proof line q to I_b q. Linear combinations
commute with this multiplication; multiplication by a variable
also commutes, and its charged degree grows by at most one.
The terminal child line 1 becomes I_b. Hence a child refutation
of degree D yields I_b from the parent using degree <=max(4,D+1).
Given both child proofs, add I_0 and I_1 to obtain 1.

Induct on the tree height, translating each node's own unit
propagation first, so arbitrarily many forced assignments cost
at most degree 3 locally. This proves the claimed max(4,d+1)+h
upper bound. No charge for unit propagation is hidden in h.

### 3. Apply the existing asymptotic lower bound

Alekhnovich and Razborov, Lower Bounds for Polynomial Calculus:
Non-Binomial Case (2003), Corollary 4.8, proves linear PC degree
with high probability for random 3-CNF at fixed clause density,
including characteristic 2. Definition 2.1 uses the multilinear
ring and the inference degree convention used above.

Source: https://www.mathnet.ru/php/archive.phtml?jrnid=tm&option_lang=eng&paperid=403&wshow=paper
Preprint: https://static.aminer.org/pdf/PDF/000/209/798/lower_bounds_for_polynomial_calculus_non_binomial_case.pdf
Definition 2.1 on printed pp. 3-4; Corollary 4.8 on printed p. 21.

Choose 8n independently sampled clauses with three distinct variables
each. A fixed assignment satisfies all clauses with probability
(7/8)^(8n), so the expected number of models is
[2(7/8)^8]^n, which tends to zero. Markov's inequality implies
unsatisfiability with probability tending to one. Intersect this
event with the published degree lower bound. Thus there exist
unsatisfiable 3-CNFs F_n with O(n log n) encoded length N and

    D_PC(F_n) >= alpha n

for a constant alpha>0 and all sufficiently large n.

Combining with the transfer lemma gives

    h >= alpha n - max(4,d+1).

For every fixed d the worst-case minimum adaptive split depth is
Omega(n), even with free unit propagation and perfect variable
selection. Therefore no fixed d and constant c can guarantee
h<=c log_2(N+1) on all UNSAT 3-CNFs. In particular the specific
F036 universal logarithmic-depth conjecture is ruled out,
subject to independent checking of the transfer derivation.
This is stronger than finite fixture evidence and makes further
experiments attempting to establish that conjecture unnecessary.

### Scope and decision

Linear maximum depth alone does not imply exponential node count:
a binary tree can be highly unbalanced. Do not infer a universal
runtime lower bound, P!=NP, or an exponential tree-size bound
from this depth argument. A separate size simulation and published
PC size lower bound could address explicit proof-generating
versions, but would still be restricted to that proof architecture.
Extension variables, richer inferences, other fields, and arbitrary
deterministic SAT algorithms are not covered.

The previous positive research hypothesis is superseded, not a
promising open conjecture. Do not silently change d or the allowed
inferences and pretend the same theorem is still being investigated.
No new verified declaration credit. Main unchanged.
