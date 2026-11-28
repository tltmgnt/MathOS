# v17.14 — counterexample-guided guard refinement and proof repair

## Motivation

v17.12 merged; evidence run 46158758877 verified 20/23 UNSAT
with the expanded compacted library, including 2/5 ternary
UNSAT. v17.13 #325 was open and its evidence run 46159517003
queued at inspection. No v17.13 outcomes assumed. This
independent branch uses the merged v17.12 infrastructure.

The prior v17 refinement of whole refutation guards already uses
semantic counterexamples and replay. Extend it to every guarded
conclusion, including nonempty goals, and distinguish semantic
necessity from dependence on a particular proof.

## Algorithm

For each guard clause, test whether deleting it permits a complete
assignment satisfying the remaining guard and falsifying the goal.
A witness proves that deletion is invalid. Otherwise try replay of
the existing proof under the weaker guard. If replay fails, the
repair arm can generate bounded resolution on the weakened guard
plus unit negations of the goal. Independently verify its DAG and
lift each resolvent by adjoining the goal literals. Omit tautological
lifted clauses; independently check each emitted addition and final
goal by RUP against the weaker guard, then by independent RUP on
guard plus negated goal. A direct RUP goal is attempted first.
A valid repaired proof is bounded to 64 additions. A failed repair
never authorizes deletion. If the template's cooperative budget
exhausts, revert the entire template to its original version.

A rejected deletion's counterexample remains valid after later
deletions. If every surviving clause has such a witness, the final
guard is inclusion-minimal for that goal (not globally smallest).
A blocked search or exhausted budget is not a minimality witness.
Preserve source variable numbering and IDs, even if unused; this
isolates guard refinement from support reduction. Proof repair can
change intermediate clauses and therefore affect compositional
reuse; do not assume identical bounded search behavior.

## Experiment

Reconstruct v17.7 training-only expanded library, compact using
v17.11, then freeze three versions: unrefined compact baseline,
counterexample/replay-only, and counterexample/replay plus repair.
No target proof generation or learning. Same template count and
order in each arm. Record guards, proof steps, serialized bytes,
deletion witnesses, replay blocks, repair counts, minimality and
offline work. Cap each template refinement at 4M ticks, 60s,
100k cooperative cells; independent checker time is not a hard
limit. Audit regenerates refinements including source/result digests
and witnesses, verifies source admission and target certificates.

Use the v17.12 registry against declared prior corpus plus the full
v17.12 and planned v17.13 candidate pools. New seed 171403, 96
candidates per family, 24 accepted per family; 72 orbit-disjoint
targets, 216 paired evaluations. Same 4M tick/15s/100k-cell online
limits, original retrieval and separate independent RUP/truth oracle.
Public seeds and bounded whole-formula orbit separation, not
semantic disjointness or external blinding. Screening and refinement
decisions are reproducible subject to cooperative deadlines. Negative
outcomes and timings not independently authenticated. No new Lean
implementation-level proof, no novel theorem or general complexity
claim. No default changes. CI pending.
