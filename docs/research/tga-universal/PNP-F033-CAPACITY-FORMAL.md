# PNP-F033 — Formal signed generalized capacity soundness

PNP_RESOLUTION_STATUS = OPEN. PR #159 merged at
1c23d5bde910fc262e8439117e4f0aa88300a2e5. Actual CI run 45463044804
job 138690518094 passed six tests, 1600 random formulas at two
capacities and two polarities (6400 runs), 30 certified UNSAT and
3170 UNKNOWN on the unflipped capacity runs, 26 noisy signed
capacity fixtures and 26 equal-capacity controls. Capacity two at
16 holes: 87857 clauses, 33 demands, 32 slots, 1584 matching edge
scans, zero BVE pairs and search nodes at both seeds.
Artifact 14955235092.
https://github.com/tltmgnt/MathOS/actions/runs/45463044804/job/138690518094

## Candidate formal theorem

ProctorCapacityDeficiency.lean extends the unchanged, previously
kernel-verified ProctorHallDeficiency source. It uses signed
(Nat, Bool) literals and arbitrary finite natural capacities;
the Python recognizer only searches capacities one and two.

Each group has a distinct list of literals and a natural capacity.
For every distinct sublist of literals of size cap+1, require a
clause of the original formula whose literals are complements of
members of that sublist. A stronger clause using only some of
the complements suffices; the existing Python certificate demands
the exact complementary set. Order and repetitions in the original
clause do not matter. Under a model, filter each group to its true
signed literals. If that list were longer than the capacity, a
constructive prefix of size cap+1 would contradict the cited
clause. Hence each filtered list length is bounded by capacity.

Concatenate the true lists. Their total length is bounded by the
sum of group capacities. Finite witness selection chooses one true
literal per demand. Variable-disjoint demands ensure distinct
choices, and coverage places each chosen literal in the concatenated
list. The first-occurrence index map is injective on these choices.
The previously proved bounded_injection theorem bounds the demand
count by that list length. Strict deficiency is impossible.
Groups need not be disjoint for this sufficient theorem:
overcounting slots only weakens the capacity bound. The Python
checker additionally requires a partition and exact coverage.

Fourteen candidate declarations are audited: true-list membership,
distinctness and prefix, opposite literal conflict, per-group bound,
three append facts, total bound, coverage, finite choices, index
bound and injectivity, and final capacity_cnf_unsat. No classical
choice is intended. A new strict gate requires exact zero-axiom
output with Lean 4.14.0 and warnings-as-errors. Existing Hall
kernel run and earlier gates remain unchanged.

## Limits and acceptance

This is local semantic soundness with supplied group distinctness,
coverage, disjoint demand supports and clause evidence. It does
not formalize Python indices, hypergraph discovery, matching,
certificate parser, or the derivation of these hypotheses from
the actual serialized certificate. It is not a completeness
or time bound for unrestricted SAT. No local Lean executable
is available; new declarations remain candidates until actual
CI confirms the kernel and strict axiom gate. No independent
review, machine refinement or original scratch port. Main
untouched; no global promotion. Next: combined inference adversarial
audit, distinguish certificate expressiveness from recognition.
