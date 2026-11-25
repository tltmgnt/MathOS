# F036 — Adaptive probing with bounded static algebra

PNP_RESOLUTION_STATUS = OPEN.

This phase changes the general-width mechanism rather than adding
more narrow lemmas. Combine unit propagation, exact static
square-free GF(2) lifting at degree d, and adaptively selected
binary restrictions. A branch may terminate when propagation finds
an empty clause or when the static coefficient span contains 1.
Every such closure is sound: each original equation vanishes on
every Boolean model, so every monomial multiple and GF(2) linear
combination vanishes there too. A constant 1 cannot vanish.

Define W(F,d,h) recursively: true if the leaf procedure refutes F;
otherwise false at h=0; otherwise true exactly when some unassigned
variable has both restrictions W(...,d,h-1). Unit propagation
precedes each leaf test. This exhaustive minimax audit determines
whether ANY adaptive splitting tree of height at most h succeeds;
it is not a proposed efficient tree-discovery algorithm.

For pigeonhole 4 into 3, exhaustive 4096-assignment evaluation
confirms UNSAT. Independent JavaScript calculation of the minimax
recurrence, with every candidate variable available, gave:
degree 2: minimum depth 3;
degree 3: minimum depth 3;
degree 4: minimum depth 2;
degree 5: minimum depth 1.
Hence the proposed universal degree-3 / depth-2 refutation
hypothesis is already false. Increasing degree trades branching
for larger linear spaces, not a proof of polynomial complexity.
Depth excludes propagation operations. This is a finite obstruction
to this exact static leaf procedure; it is not a lower bound for
polynomial calculus, resolution, other leaf procedures, or SAT.

A precise remaining conjecture to challenge is whether some fixed
degree d and fixed constant c suffice to refute every unsatisfiable
3-CNF by such a tree of depth <= c log2(N+1), where N is encoded input
length, AND whether a suitable tree can be found uniformly in
polynomial time. A logarithmic-depth tree would have polynomially
many nodes, but discovering it may be harder, and leaf cost must
include actual bit operations. Neither condition is established.
The conjecture must not be treated as likely true simply because
it is falsifiable. Investigate scalable adversarial families
before spending effort on proof formalization.

The Python fixture records the recurrence and expected values.
Its repository replay is separate from the completed JavaScript
experiment. No new Lean verification credit is claimed.
