# F035 — Width-three barrier and shortest research route

PNP_RESOLUTION_STATUS = OPEN.

The verified width-two solver is a useful implementation milestone, not
progress evidence for a universal polynomial SAT algorithm by itself.
The eight three-literal clauses containing every sign pattern on three
variables are unsatisfiable. A single positive three-literal clause is
satisfiable. The current implication arc extractor maps both to the
same empty graph. Both have declared variable bound three. The new
theorem candidates prove the cube unsatisfiable, conflict-free under
the extracted graph, and correctly rejected by the width-two solver.
A Boolean decision function of this graph alone cannot distinguish
the two formulas. This is an information-loss example, NOT a general
lower bound or a resolution-proof lower bound.

Shortest logical positive route:
1. Find an actual deterministic polynomial algorithm for general
   3-SAT (or an equivalent NP-complete problem), with correctness
   for all inputs. An accepted polynomial certificate generator is
   sufficient but not necessary.
2. Prove a total polynomial bit-machine cost and establish the
   standard NP-completeness reduction/decision bridge.
3. Independently audit mathematical scope and machine semantics.

The shortest modeled negative route requires a lower bound excluding
every uniform deterministic polynomial-time SAT algorithm, not just
this architecture. Existing proof systems' lower bounds cannot be
substituted for that claim. A polynomial UNSAT certificate existence
result alone would imply NP=coNP, not necessarily P=NP.

No finite number of prompts or additional declarations is known to
suffice. Three work packages are not three prompts. Further width-two
optimizations should be deferred relative to the generality gate
unless needed to test a concrete general-width idea. If no such idea
with universal progress and correctness is found, record the blocker,
rather than manufacture a resolution claim.

14 theorem candidates; 19 fixture checks. Strict exact-head replay
required before counting the declarations.
