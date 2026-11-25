# F035 — Aggregate model and conflict reachability charge

PNP_RESOLUTION_STATUS = OPEN.

Integrates verified single-query equality-probe accounting b8e29583
and wire-token module a30e9016. Let L be literal occurrences and
Q(L)=L*(L*((1+L)+(1+L)))+(1+L). Charge both complementary queries per
visited variable, even if a Boolean conjunction short-circuits.
A score visits 2L literal occurrences, and one model value evaluates
two scores. Materializing the occurrence list evaluates L values.
The UNSAT branch can repeat the two complementary path queries.
Conservatively sum all three schedules, even though the actual
solver does not take both branches on one input.

The candidate total equality-probe charge is bounded by
L*(2Q(L))+L*(2*((2L)*Q(L)))+2Q(L), of degree five in L.
It is an instrumented count of lookup comparisons, not a formal
refinement to native execution or complete time bound. Rank
arithmetic, graph construction, path allocation, inference generation,
encoding and replay remain separate obligations. Nine public theorem
candidates, 1028 executable controls. Exact-head strict replay required.
