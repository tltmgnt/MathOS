# F035/F040 — Finite implication reachability completeness

PNP_RESOLUTION_STATUS = OPEN.

Independent branch from the verified implication module
aa7f8b0a818a88000885530d92c0c298374ceedb. Path compiler repair proceeds
on its own branch; no dependence on an unverified sibling.

For each route table R and finite arc list E define the integer potential
M(R,E) = sum over (a,b) in E of 1 if b is not in R, otherwise 0.
Duplicate arcs are counted with multiplicity. M is between zero and |E|.
Relaxation never deletes or changes an existing witness. If a sweep changes
the table, it inserts a previously unknown target of some arc of E, so M
strictly decreases. Otherwise the table is already fixed. Consequently
|E| sweeps suffice to reach a fixed point (indeed M(R,E) suffice).
A fixed point is closed under every edge; induction on an arbitrary
finite walk proves its endpoint is known. This avoids a separate
simple-path elimination lemma, and requires no numerical variable bound.

The candidate theorem reach_complete establishes that for every finite
walk in E, reach E source destination returns a route. Its companion
soundness theorem from the verified baseline uses semantic paths; exact
witness correctness and end-to-end compilation are addressed by the
separate path compiler module. The 2-CNF converse (model extraction when
no mutually complementary walks exist) remains open in MathOS.
No claim of general SAT polynomial discovery, bit-cost theorem, or P vs NP
resolution is made.

23 public theorem candidates. Controls: all 512 directed graphs on three
vertices including loops, 4608 ordered source/target pairs against an
independent bounded walk oracle; 40 reversed-chain pair checks; 3 sparse
identifier / duplicate-arc / cycle pair checks; 1557 source fixed-point
checks (each checks both arc-count and potential fuel). Total 6208
control cases. Exact strict Lean replay required before credit.
