# F037 — Checked one-way literal retractions

PNP_RESOLUTION_STATUS = OPEN.

The preceding linear-autarky workflow passed at
e7f4a462a82323c727149af7d3a89b124790cf66
(run 45691015496, job 139476148307). Its Python sample reported
89 changed formulas and 149 autarky steps.

## Exact satisfiability-preserving rule

Let F be normalized CNF. Let a literal substitution rho map
some variables to signed literals on other variables; require
the target variables of the substitution to be disjoint from
all source variables in its replacement literals. Extend rho
to all literals by complementarity and identity on unassigned
variables. For every original clause C, require that rho(C)
is tautological or contains all literals of some original
clause D. Unchanged clauses automatically satisfy this check.

For any model x of F, the repaired assignment y defined by
y(v)=x(rho(v)) satisfies F: each original clause evaluated
on y equals the image clause evaluated on x, and every image
clause follows from its original witness or is tautological.
Therefore x satisfies rho(F). Conversely every model of rho(F)
extends to a model of F by assigning each replaced variable
the value of its replacement literal. Consequently F is
satisfiable iff rho(F) is satisfiable. The repaired assignment
is a retraction because applying the substitution twice has
the same effect. It need not be invertible, preserve model
counts, or assign a constant value to any variable. This is
a safe elimination rule, not a complete constant-bit selector.

Normalize each image and remove duplicate clauses. Each
successful step removes at least one occurring variable.
Compose these checked steps on residual formulas; lift a
final model by reversing the substitutions. An UNSAT witness
consists of the sequence of valid retractions and a checked
UNSAT proof for the final residual. The checker does not rely
on the discovery algorithm, and performs no SAT queries.

## Uniform bounded discovery

For width at most three, the image of a clause has at most
eight subsets. Check inclusion of an original witness by
an explicit clause dictionary (or deterministic sorted lookup).
For fixed r one may enumerate all substitutions of at most
r distinct variables by signed literals of the remaining
variables, at most O((2n^2)^r) candidates, then repeat for at
most n successful eliminations. This is polynomial for fixed r.
The implemented search is narrower: enumerate recognized signed
one-hot triples, try each ordered pair of disjoint triples and
all six bijections between their literals. A one-hot triple is
certified by its positive-in-the-signed-vocabulary clause
and the three opposite pair clauses. This uses polynomially
many candidates; it does not require a supplied graph or color
partition. The bit-cost argument uses explicit normalized
lists and dense or sorted identifiers. No formal machine-cost
refinement is claimed.

## Family outside the preceding linear-autarky promise

Encode proper 3-coloring of a complete multipartite graph
with p nonempty parts of size t. There are 3pt Boolean bits
and disjoint one-hot triples; for each graph edge include
the three negative same-color conflicts.

The simultaneous local translation subgroup used in the
preceding symmetry selector is trivial: the lone positive
clause on each triple support has only the zero translation.
The linear-autarky cone is also trivial. Within each triple,
the signed clause inequalities require a+b+c>=0 and
a+b<=0, a+c<=0, b+c<=0. Adding the pair inequalities gives
a+b+c<=0. Equality forces all three pair sums to be zero,
hence a=b=c=0. These obstructions survive signed renaming.
The q-Horn constraints on the same gadget are inconsistent,
and any syntactic deletion backdoor to 2-CNF must meet all
pt disjoint triples. None of these statements rules out
other symmetries, arbitrary autarkies, or other SAT solvers.

Any two vertices in the same part have identical neighbors.
Copying one vertex's three color bits onto the other is a
checked retraction: the image of its one-hot gadget is the
source gadget and each image conflict already occurs at the
source. Vertices in different parts cannot be folded by this
checker: an edge between them yields a conflict image on
the same source triple. If a proposed color bijection has a
fixed color, the image gives a negative unit, which has no
original subsuming clause. If it has no fixed color (a
three-cycle), the conflict with a third vertex in a different
part produces an off-color binary conflict absent from the
formula. For p>=3, even same-part folds with a nonidentity
color bijection fail by this latter argument using any vertex
in a different part. Thus every accepted gadget fold in the
family is a same-part, color-aligned fold. It preserves the
same construction with one vertex deleted. Continue until
one vertex remains in each part, leaving the encoding of K_p.

For p=3 this is satisfiable and for p=4 it is unsatisfiable.
The reduced instances have respectively nine and twelve
bits, and the prior bounded-backdoor solver decides them
with budget four. This family is not a hard SAT benchmark;
it demonstrates a type of certified nonconstant elimination
missed by two previous local mechanisms. Greedy retraction
discovery is not universally complete.

## Evidence

Independent JavaScript execution checked all accepted signed
single-variable substitutions on 128 random small CNFs:
705 maps, 1513 satisfying-model transport checks, and
exhaustive original/residual satisfiability comparison.
Eight signed-renamed multipartite cases (p=3,4; t=2,4,8,12)
reduced to exactly 9 or 12 bits with p(t-1) accepted folds.
The largest input had 144 bits. Exhaustive residual evaluation
gave the expected decisions. The Python fixture adds use of
the prior certificate-producing leaf solver, standalone
retraction-sequence replay and three malformed-map checks.
Its exact-head replay is pending. No new Lean credit.

## Decision

Satisfiability-preserving model transport can identify variables
even when a constant-setting rule is unavailable. The direct
universal preservation obligation remains open: there is no
guarantee that any permitted retraction exists on arbitrary
irreducible input. This is an integration of elementary
substitution and subsumption principles, not a novelty claim
or a proof of P=NP. Main unchanged.
