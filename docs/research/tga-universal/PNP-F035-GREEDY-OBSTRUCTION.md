# F035 — Greedy elimination counterexample

PNP_RESOLUTION_STATUS = OPEN.

The existing unsimplified factored projection selector minimizes the
next clause count, not the maximum clause count over the complete
elimination sequence. A concrete five-variable twelve-clause 3-CNF
fixture disproves global peak optimality. It has initial costs
13,17,23,17,14 for variables 1..5, so the first choice is strict.

Greedy order 1,2,3,4,5 produces counts 12,13,16,22,0,0.
Order 5,4,1,2,3 produces counts 12,14,11,14,0,0.
Both reach the empty conjunction. The alternative's peak is 14
against greedy's 22, despite the larger first step.

The independent Python audit enumerates all 120 orders: minimum
peak 14, attained by four orders, maximum peak 2285. This is a
finite obstruction to global optimality, not an asymptotic lower
bound or a claim about normalized/subsumption-aware elimination,
all greedy heuristics, or SAT decision in general.

Nine new theorem candidates. Exact-head replay is required,
including the eight upstream adaptive elimination axiom audits.
No credit for duplicated upstream declarations.

Strategic gate: a local cost decrease or minimum is not a proof
of a global polynomial ceiling. To continue the positive route,
identify a representation and an exact operation sequence with
a uniform polynomial bound on every input, or isolate and prove
the precise conditional hypothesis. Merely tuning the ordering
cannot supply that theorem.
