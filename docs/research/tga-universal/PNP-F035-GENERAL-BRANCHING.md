# F035 — General CNF branching with width-two leaves

PNP_RESOLUTION_STATUS = OPEN.

This candidate generalizes the decision interface to arbitrary finite valid
CNF, by Shannon restriction. Satisfied clauses disappear, false assigned
literals are removed, and remaining literals retain their identifiers.
At any width-two residual, the existing verified solver is invoked.
Otherwise both assignments of the next supplied variable are explored.
The variable occurrence list covers the original formula, ensuring that
all leaves reach width two or less. The candidate proves total correct
decision, not polynomial discovery. The number of leaf calls is bounded
by 2^k, where k is the supplied list length (including duplicates).
The algorithm is a known general mechanism, not a P vs NP breakthrough.

The critical next question is whether a genuinely polynomial-size
representation of the branching obligations can be constructed for
all CNFs, rather than merely optimizing a leaf solver. No such bound
is established here. A universal polynomial backdoor is not assumed.
Do not report proof-size or runtime progress from these semantic
lemmas alone. 17 public candidates; 4098 fixtures; strict exact-head
replay required.
