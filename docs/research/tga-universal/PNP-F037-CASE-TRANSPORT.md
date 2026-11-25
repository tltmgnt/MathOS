# F037 — Case-dependent nonlocal branch transport

PNP_RESOLUTION_STATUS = OPEN.

The preceding frozen-model exact-head audit passed at
3254785a33af54404628b4bb091707281bc61dec
(run 45692214509, job 139480326465).

## Certificate principle

Let F be a normalized width-three CNF. To choose v=b, specify a
case scope S containing v, and enumerate all 2^|S| bit patterns
alpha on S. For each alpha, give either a reverse-unit-propagation
(RUP) refutation of F AND alpha, or a signed variable permutation
p such that every original clause C has its image p(C) implied
by F AND alpha, and the desired unit (v=b) also has its image
implied by F AND alpha. The implementation checks implications
by direct clause inclusion or by recomputing RUP.

If F is satisfiable, take any model x and its case alpha.
The refuted case is impossible. In the remaining case define
y(w) as the value in x of the signed literal p(w).
Every clause of F is true in y by the corresponding image
implication; the desired unit holds too. Hence F AND (v=b)
is satisfiable. The converse is immediate. This is an exact
satisfiability-preserving choice; no original model needs
to be supplied to discover or validate this certificate.
The individual transports can be bijections while their
case-dependent union need not be injective. For one one-hot
triple, the three satisfying assignments can all be mapped
to the same chosen color. A single bijection could not
transport all three to the singleton target.

The checker has polynomial cost for fixed case width s:
there are 2^s cases, each permutation uses O(n) signed
identifiers, and there are m+1 implication tests per case.
Direct inclusion tests enumerate at most eight subsets of
a width-three clause. RUP uses at most n propagation steps
with polynomial scans. Thus a supplied certificate has
polynomial size and validation cost in encoded input length.
If a polynomial-size list of candidate permutations is supplied,
independently checking each candidate per case also gives
polynomial discovery within that list. No claim that an
appropriate list can be found for every formula is made.

## Nonlocal repair on the frozen family

Use the preceding 768-vertex girth-six cover of K_(2,2,2)
with its one-hot 3-color encoding. Fix a vertex u to color
zero. Enumerate the eight truth patterns of its one-hot
triple. Five patterns contradict the gadget by unit
propagation. For a valid pattern with active color j,
globally permute colors so j is moved to zero. Each original
clause has an identical image clause in the original encoding,
and the target image unit is guaranteed by the case assumption.
This certificate preserves satisfiability independently of
the existence of any particular coloring. It does not need
to know the lifted coloring used to establish the fixture.

Now retain the first pin as a unit and choose a neighbor w
of u to have color one. Again consider its eight patterns.
The invalid one-hot patterns and color zero are unit-refutable.
For colors one and two use identity or the global swap
of one and two, respectively. Both preserve the previous
unit. Thus two sequential choices are certified without a
SAT oracle or a bounded-support model overwrite.

This bypasses the earlier frozen-model barrier: global
permutations may change a number of coordinates proportional
to the formula size. The prior local GF(2) translation
stabilizer does not include these variable permutations.
This example uses a known palette symmetry of a particular
encoding; neither general signed permutation discovery nor
universal branch viability is established.

## Evidence

Independent JavaScript execution constructed the 768-vertex
cover, checked 16 cases across two successive choices using
clause inclusion and RUP, and checked 12 model transports
from six known initial colorings. All passed. The independent
checker also allowed a valid implication certificate on an
impossible case instead of explicitly refuting every such case.
The Python candidate explicitly refutes invalid one-hot
patterns and the forbidden neighbor color, checks all
permutations, includes a one-hot many-to-one example and
rejects three malformed certificates. During implementation
the second-choice candidate was corrected to handle the
neighbor's already forbidden color by unit refutation.
Exact-head Python replay remains pending.

## Scope and next gate

Case-dependent nonlocal transport is a sufficient model
repair mechanism, not a general existential-only criterion.
It still transports each original model, but without a
bounded-change constraint. It is not a universal selector:
there is no guarantee of a constant-width case cover and
polynomially discoverable transformations on arbitrary
asymmetric formulas. The direct universal preservation
and polynomial bit-cost obligations remain open.
No new Lean credit; main unchanged.
