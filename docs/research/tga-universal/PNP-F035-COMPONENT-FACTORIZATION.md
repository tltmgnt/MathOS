# F035 — Component decomposition and exact residual-cache limits

PNP_RESOLUTION_STATUS = OPEN.

The candidate decomposition theorem says SAT(F ++ G) iff SAT(F)
and SAT(G) when their variable supports are disjoint. The executable
gate disjointCheck tests that premise. Its proof joins assignments on
the respective supports. Shared-variable unit clauses give an explicit
counterexample to dropping the premise. Ten public candidates, 4097
truth-table checks; strict replay required.

For a fixed selector order, let F_k contain (x_i or a_i or h) and
(not x_i or b_i or h) for i=1..k, plus (h or u or w), with all
variables distinct except the common hub h. Under each complete
selector assignment, the remaining clause for i is either (a_i or h)
or (b_i or h). Therefore all 2^k residual clause sets are distinct
even after sorting and deduplicating literals and clauses. All
residuals still share h and retain the width-three hub clause.
An exact residual cache and syntactic connected-component splitting
cannot identify these distinct states along this fixed exploration.

The family has 2k+1 clauses and 6k+3 literal occurrences.
It is trivially satisfiable by h=true; a better variable order or
semantic simplification defeats this example. It is NOT a worst-case
lower bound for arbitrary variable ordering, short-circuit search,
semantic memoization or all algorithms. It only rules out a generic
polynomial state-count proof based on exact caching and component
splitting for that schedule.

The reproducible Python stress test enumerates all selector prefixes
for k=1..12. The next useful gate is a compression invariant stronger
than syntactic equality, with exactness and an actual global
polynomial bound. Do not infer that such an invariant exists.
