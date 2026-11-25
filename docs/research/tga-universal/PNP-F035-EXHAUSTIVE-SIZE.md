# F035/F039 — Exact exhaustive generator size obstruction

PNP_RESOLUTION_STATUS = OPEN.

Parent discovery repair cd5c39f2b521289d95bbf635e3b69812100e34b1
requires fresh replay. Input-bound completeness PR #241 merged.
No theorem status promotion without exact-head strict evidence.

For each successful build q vs g path, candidate build_length proves
returned sequential trace length equals nodes(vs.length), where
nodes(0)=1 and nodes(k+1)=nodes(k)+(nodes(k)+1). Thus nodes(k)
is 2^(k+1)-1 mathematically; nodes_lower proves the weaker lower
bound 2^k. The compiler creates one batch per sequential step.
If the initial frontier has m rows and there are t steps, the
total compiled step count obeys copies(0,m)=0 and
copies(t+1,m)=(m+1)+copies(t,m+1); mathematically this equals
tm+t(t+1)/2. The recurrence is the audited target, not the
closed-form identity.

Explicit padded family: k copies of the unit clause [2] followed by
[1] and [-1]. Every input is valid with bound 2, UNSAT, has
k+2 literal occurrences, and has a one-resolution refutation.
The candidate padded_generator_lower nevertheless proves the
current occurrence-splitting generator returns an accepted proof
with at least 2^(k+2) explicit batches. Its output length alone
obstructs polynomial time for THIS implementation on the family.
A more efficient generator can avoid this artificial overhead by
deduplicating variables or recognizing the contradictory units.
This is not a lower bound on minimal certificates, the mixed
proof system, all discovery algorithms, or SAT complexity.

11 candidate declarations and 27 controls (7 actual generated
padded certificates and 20 recurrence checks).
Marker F035_EXHAUSTIVE_SIZE_OK padded=7 trees=20.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gate.
Fresh replay required. Main unchanged.
