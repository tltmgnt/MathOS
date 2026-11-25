# F037 — Safe noninvertible choices via linear autarkies

PNP_RESOLUTION_STATUS = OPEN.

## Result

An autarky is a partial assignment A satisfying every clause it
touches, using at least one of its own assigned literals. Overwrite
any satisfying assignment with A: untouched clauses retain their
values and touched clauses remain satisfied. Therefore restricting
to A preserves satisfiability and deletes every touched clause.
This is a noninvertible model transport, unlike the earlier
translation symmetries. A sequence of checked autarkies on successive
residuals preserves satisfiability by composition; assigned variable
sets are disjoint. An UNSAT certificate consists of this sequence
and a checked UNSAT proof for the final residual.

Use the established linear-autarky sufficient condition. For each
variable v introduce a signed real coordinate z_v. For each
normalized clause C require

    sum_{l in C} sign(l) z_|l| >= 0.

If a feasible direction z is nonzero, assign the support of z
according to its signs. In a touched clause some summand is nonzero;
if all nonzero summands were negative the sum would be negative.
Thus some assigned literal is true, exactly the autarky condition.
The independent checker verifies the partial assignment directly,
without trusting the LP result or needing to represent its weights.

## Discovery and resources

Intersect the homogeneous cone with [-1,1]^n. A nonzero solution
exists iff some coordinate has a strictly positive maximum or
strictly negative minimum. Using an exact rational LP oracle,
at most 2n coordinate optimizations find a nonzero direction or
prove the cone trivial. The number of input coefficients and
their bit lengths are polynomial in the CNF encoding, and rational
linear programming has a polynomial-time bit algorithm. Every
successful reduction removes at least one occurring variable,
so at most n rounds and 2n^2 LP optimizations suffice. This is
a polynomial guarantee for the mathematical linear-autarky
procedure, not a proof of complete decision of arbitrary CNF.

The Python candidate first attempts an aggregate objective and
then coordinate objectives using SciPy/HiGHS. Floating-point
sign extraction is only a proposal; every accepted assignment is
checked exactly. A failed numerical search stops reduction, not
a proof of the cone being trivial. The prototype does not certify
LP infeasibility or worst-case LP runtime. It uses the existing
bounded-backdoor leaf solver on the remaining formula.

## Dense family with no discovered local translations

For each of t disjoint six-variable blocks a,b,c,d,e,g, put

    (a OR b OR c),
    (d OR not a OR not b),
    (e OR not b OR not c),
    (g OR not a OR not c).

Add all positive binary clauses between variables in distinct
blocks. Add three core variables p,q,r with (p), (not p OR q),
(not q OR r), and either (r OR p) for SAT or (not r OR not p)
for UNSAT. Link the core via (a_1 OR p) and (a_1 OR not p).

Use z_a=z_b=z_c=1, z_d=z_e=z_g=2 and zero on p,q,r.
Every signed clause sum is nonnegative, so these directions
certify a partial assignment fixing all 6t block bits true.
Scaling by 1/2 gives a feasible point in the LP box.
Removing these bits leaves the indicated binary core, whose
satisfiability is immediate. Renaming variables and flipping
polarities correspond to signed coordinate permutations and
preserve the construction.

Each block's ternary constraints separately refute q-Horn
eligibility: writing a,b,c,d,e,g for positive literal weights,
the first clause requires a+b+c<=1, and the others require
a+b>=1+d, b+c>=1+e and a+c>=1+g. Together they imply
a+b+c>=3/2. A syntactic 2-CNF backdoor must hit the t disjoint
positive triples. For t>=2 the block variables form a complete
multipartite graph across blocks; deleting s vertices leaves
at least t-s untouched blocks connected if t-s>=2, so any
2/3-balanced root separator needs Omega(t) deletions.
The earlier local translation subgroup is trivial: a single
non-tautological clause on a support has only the zero
translation (its unique falsifying pattern must be fixed).
Every block bit occurs in such a clause, as does each core
bit in a distinct binary support. This refers to the discovered
local subgroup, not to the full semantic symmetry group
(which is vacuous on an unsatisfiable formula).

The example is easy, not a proven hard SAT benchmark. It
illustrates that sound choices need not arise from symmetry,
and the reduction removes a dense region before invoking a
different solver.

## Exact choice-autarky oracle is not a free operation

On a promised satisfiable formula F, an autarky assigning a
specified variable v to a specified bit b exists iff the
restriction v=b is satisfiable. In one direction overwrite
a model of F using the autarky. In the other take a full model
of the restriction extended by v=b; every full model is an
autarky. Guard an arbitrary 3-CNF H with a new variable v,
splitting width-four clauses by the earlier guarded-choice
construction. The guarded formula is guaranteed satisfiable
when the guard is true, whereas the false restriction is
satisfiable iff H is satisfiable. Hence finding whether there
exists an autarky with the specified bit is NP-hard even under
the satisfiable-input promise, and the autarky witness is
polynomially checkable. This is not hardness of finding any
nontrivial autarky on every input. It rules out treating the
exact specified-choice oracle as an established polynomial
subroutine.

## Evidence and decisions

The preceding symmetry selector exact-head replay passed at
245db97b8aff3084c4f8a252e2dc1a17221523ee (run 45689885935,
job 139472210674); Python reported 884 transported models.

Independent JavaScript evaluation of 128 random small formulas
enumerated bounded integer directions (coordinates -2..2).
It checked 2637 nonzero feasible directions and 12438 model
transport operations against exhaustive evaluation, and 85
formulas had at least one such direction. The eight dense
controls were tested with the explicit integer witness and
exhaustive binary-core evaluation, up to 99 variables. This
is not an execution of numerical discovery. The new Python
fixture tests automatic discovery, shuffled signs, sequential
replay, model transport, three malformed assignments and
the earlier 2-SAT checker. During development the inconsistent
unit-pair control was replaced by a nontrivial binary core:
the former accidentally admitted a local translation on its
core bit. The Python exact-head replay is pending.

No novelty claim for linear autarkies. No universal selector
or preservation theorem covering all 3-CNF is established.
The next central obligation remains a uniform safe selection
rule for inputs with no useful checked symmetry or autarky.
No new Lean credit. Main unchanged.
