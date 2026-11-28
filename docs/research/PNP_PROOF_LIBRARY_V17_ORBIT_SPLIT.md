# v17.12 — orbit-disjoint transfer frontier

## Observations

PRs #313, #317 and #318 merged and their evidence CI passed.
v17.10 (46154403104) on 72 fresh, 26 UNSAT: plain/indexed base
both 20, expanded both 21, no paired losses or gains from filtering.
Expanded matcher calls 6747 -> 6040 (707 avoided); ticks
12,212,655 -> 11,897,634 (~2.58% reduction). Base ticks
6,922,968 -> 6,973,472 (increase). Retrospective expanded
ticks 12,644,832 -> 12,395,026, same 19/25 UNSAT.
v17.11 (46154801042) base 30 -> 30; expanded 54 -> 51,
three checked duplicates and one unresolved retained.
Fresh 72, 30 UNSAT: base 21, expanded 24, same after compaction.
Expanded ticks 12,852,609 -> 11,709,066 (~8.90% reduction),
observed search/replay seconds 12.588 -> 11.470.
Retrospective expanded 19/25 both; ticks 12,644,832 -> 11,585,081.
Offline expanded compaction 422,017 ticks and 0.245 s.
No paired gains or losses from compaction in either split.
This is finite evidence; not a guarantee of safe compositional pruning.

## Stronger split

Previous splits checked normalized literal identity only. Normalize
whole CNFs by dropping duplicate clauses, tautologies and unused
variables; dense-label active support. Use the v17.11 exact signed
canonicalization with empty distinguished goal as a whole-formula
key (the goal is a marker only, not a proof). Compare against an
explicit, hashed corpus of prior v17-family full inputs and controls,
including upstream training/evaluation rows, v17 splits, ablation,
adaptive, parameterized, signed Horn, composite, portfolio, admission,
selection and retrieval seeds listed in code. This is not a claim
to cover all MathOS research lines, every earlier unit test, or
all equivalent subformulas/guarded consequences.

Require an exact completed key for every accepted test case.
Known duplicates are checked via signed bijection, then rejected.
Unresolved cases are excluded; unresolved prior buckets are
quarantined using invariant support, width histogram and ordered
profile-group sizes and polarity-tie counts. A genuine signed
isomorphism preserves these quantities; coarse bucket collisions
can cause extra rejection, not acceptance of a same-orbit case.
Larger active support than nine cannot match the selected support.
Canonicalization resource exhaustion aborts the experiment.
The registry is also updated after every accepted case so all
selected cases are mutually orbit-disjoint. Candidate generation
and rejection do not use satisfiability or search outcomes.

Use seed 171203, pool 96 per family (288 total), first 24 accepted
binary, ternary, mixed-width instances, fail if any stratum is short.
This is rejection sampling, not the old IID distribution.
Record pool, source corpus, screening counters and registry hashes.
Recompute manifest and accepted identities during report audit.
Public seed, not external blinding. Signed-orbit disjointness of
whole normalized inputs is strictly stronger than exact-input
disjointness but weaker than semantic equivalence or separation
from local patterns; reuse of substructures is the purpose of the
library. No generalization claim outside the declared corpus/split.

## Experimental arms

Freeze original and v17.7 training-only expanded snapshots and
their v17.11 compactions. Six arms: base, base compact, expanded,
expanded compact, base memo, expanded compact memo. Identical
cooperative 4M tick/15s/100k cell limits; same proof reconstruction
and separate independent RUP and small exhaustive truth references.
No target learning or tuning. Compare original/compact at both
sizes and memoization on original and compact-expanded snapshots;
not a full factorial of all optimizations. Record lineage and
signed equivalence witnesses. Audit regenerates training admission,
compaction, screening and all positive proofs; not authentication
of measured counters, timings or misses. No hard CPU/memory limit,
no new implementation-level Lean proof, no default changes.
Pending CI. P versus NP remains unresolved.
