# F037 — Decision-specific logarithmic backdoors

PNP_RESOLUTION_STATUS = OPEN.

## Result

For normalized width-at-most-three CNF F, define a strong deletion
backdoor to 2-CNF as a set B of variables meeting every width-three
clause. Normalize by deduplicating literals and discarding tautologies.
Every assignment to B leaves a width-at-most-two formula. Conversely,
if a width-three clause is missed, it remains intact under every
assignment to B in the literal restriction operation. This is the
syntactic notion, not a claim about what further semantic simplification
could accomplish.

Find a backdoor of size at most k, if one exists, by selecting a
remaining width-three clause and recursively trying each of its three
variables. Remove all width-three clauses hit by the selected variable.
The search tree has at most (3^(k+1)-1)/2 nodes. This is complete for
the hitting-set condition because any hitting set meets the chosen
clause. Each node performs polynomial work on the explicit input.

Given B, enumerate its at most 2^k assignments, restrict F, and use
the complete 2-SAT implication criterion. A satisfiable leaf yields
a model by 2-SAT self-reduction; an unsatisfiable leaf gives either
an empty clause or two complementary implication paths. The checker
recomputes every restriction and validates the leaf evidence.
All branches must be covered to certify UNSAT. SAT models are
checked against the original unnormalized input. A failed backdoor
search yields UNKNOWN, never a SAT or UNSAT claim.

## Component parameter and uniform cost

Split the formula by connected components of its variable-clause
incidence graph. Their variable sets are disjoint, so models can be
combined and an unsatisfiable component proves the entire formula
unsatisfiable. Independently search each component with the same
budget k, rather than spend k across the whole input. Let b(F) be
the maximum minimum hitting-set size across components (zero for
the empty formula). For b(F)<=k, the solver decides F completely.
Even if a component is unsupported, another component's checked
contradiction is decisive.

For encoded input length N, the work of all components is bounded
by (3^k+2^k) poly(N), not by 2 to the sum of their backdoor sizes.
For k=floor(c log_2(N+1)), with any fixed c, this is polynomial
in N: 3^k <= (N+1)^(c log_2 3) and 2^k <= (N+1)^c.
Use dense or sorted dictionaries and ordinary bit comparisons to
avoid charging sparse identifiers as array sizes. The mathematical
bound applies to explicit deterministic implementations; the
Python code is not a formal machine-cost refinement.
The prototype accepts an explicit integer budget; the caller must
choose the logarithmic cap for the uniform polynomial guarantee.
This is a standard parameterized backdoor technique, not a novelty
claim or an unrestricted SAT algorithm.

The explicit certificate has at most 2^k leaf proofs of polynomial
size. It needs no exact full Boolean-function compilation.
In particular the previous all-order OBDD-hard hypercube family
is already 2-CNF and is decided at budget zero.

## Limitation

A connected 3-CNF can require linear-size syntactic deletion
backdoors even when satisfiable. Take t disjoint positive triples
and connect their first variables by positive binary clauses.
Every triple must be hit separately, so the sole component has
minimum backdoor t and the all-ones assignment satisfies it.
Thus the promised logarithmic bound is not universal. This does
not establish a time lower bound on SAT: the example is easy.
The resource theorem is useful precisely because the structural
parameter is discoverable or rejected, not assumed to be small.

## Evidence

The preceding all-order OBDD audit passed at
a6b96368798fb668120456c1c946c6d4bc62c208
(run 45685725072, job 139457705154); Python reported 373732
residual witness checks on 13010 balanced cuts.

Independent JavaScript execution of the new decision algorithm
tested all 4096 subsets of a twelve-row three-variable fixture
at budgets 0,1,2 (12288 decisions). At budget zero: 80 SAT,
2096 UNSAT and 1920 UNKNOWN. At budgets one and two: 1280 SAT,
2816 UNSAT and zero UNKNOWN, agreeing with exhaustive evaluation.
Also tested 128 disjoint ternary components (budget one succeeds,
zero returns UNKNOWN) and a 256-variable, 1024-clause hypercube
(budget zero succeeds).

The Python candidate adds explicit model and contradiction checking,
an unsupported-component/decisive-component control and three
malformed-proof controls. Inspection caught and fixed a degenerate
zero-literal path issue in the checker before scheduling replay.
The independent experiment tested the decision logic, not the
Python checker. Python exact-head replay is pending; no new
Lean verification credit.

## Research direction

A general positive result still requires a genuinely universal
polynomial resource invariant or a mechanism covering arbitrary
large-backdoor components without an expensive exact SAT oracle.
Do not interpret this promise theorem as solving P vs NP.
Main unchanged.
