# v17.11 — canonical guarded-conclusion orbits

## Prior evidence

PR #313 evidence passed (https://github.com/tltmgnt/MathOS/actions/runs/46154141141).
On 72 fresh cases (25 UNSAT), base plain verified 17, base memo 19,
expanded plain 19, expanded memo 19. Both base-memo gains were
ternary, with no losses. Base work increased 7,278,178 to 7,725,429
ticks, aggregate time 3.712 to 4.276 s. Expanded memo increased work
12,644,832 to 13,811,250 and time 6.327 to 7.643 s, without coverage gain.
Retrospective expanded memo gained one (24 vs 23 of 32 UNSAT).
Memoization is a coverage tradeoff, not an observed speedup.
PR #313 remains open at inspection; #317 incidence run 46154403104
was queued. This independent branch uses neither unmerged method.

## Canonical equivalence

For a verified template, distinguish its guard set and last conclusion.
For each variable, compute a positive and negative occurrence profile:
counts by guard width, with a separate distinguished conclusion count.
A signed bijection preserves the unordered pair of profiles, so
partition variables by that invariant. Assign consecutive canonical
labels to groups in sorted profile order. Orient unequal profiles
so the smaller profile is positive; enumerate both orientations for
ties. Enumerate all label permutations within each tied group.
Take the lexicographically least mapped guard set and conclusion.

An isomorphism induces a bijection between the enumerated maps of
two equivalent inputs. Therefore a completed canonical key is invariant.
Conversely, equal keys give a signed bijection by composing one map
with the inverse of the other. Independently check that witness
against the guard sets and goal before deleting a duplicate.
The method identifies identical guarded entailments modulo signed
variable renaming, not all semantic equivalences or identical proof DAGs.
A representative proof may derive different intermediate consequences;
therefore removing a duplicate may affect bounded compositional retrieval.

Cap orbit enumeration at 8192 complete maps per template. An oversized
orbit is explicitly unknown and retained; no partial minimum is used.
All templates independently replay before compaction. Keep the first
representative, preserve order, and record source IDs plus signed
equivalence witnesses for every deletion. No target-derived changes.
The offline budget is separate; exhaustion aborts the experiment,
not a claim that templates differ. The mathematical argument above
is not an implementation-level Lean proof.

## Evaluation

Regenerate the v17.7 training-only expanded library and provenance.
Four arms: base, base compact, expanded, expanded compact. Same original
matcher, proof reconstruction and 4M tick/15s/100k cell cooperative
per-arm caps; independent RUP separately timed. 72 fresh cases seed
171103 and 72 seed 17903 retrospective; exact normalized overlap
checks against prior datasets, not signed-orbit split or external blinding.
Report exact/unknown/duplicate counts, offline compaction cost, library
sizes, work, wall time, coverage and paired gains/losses, admitted-entry
use mapped back to original source IDs. Audit re-derives canonical
decisions and source lineage and independently replays positive proofs;
negative outcomes and timings are not authenticated. Tests include
signed relabelings beyond four variables, explicit cap, altered goal,
forged proof, witness and unknown retention. No default changes or
unrestricted complexity claim. CI pending. P versus NP unresolved.
