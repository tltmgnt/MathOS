# v17.6 — unified certificate-checked schema portfolio

## Prior evidence

PR #296 merged at a6de9ab61231dbd1ec3d5d896a5cf89a9ab991b1.
Evidence/formal jobs passed: https://github.com/tltmgnt/MathOS/actions/runs/46137465703.
72 fresh instances (27 UNSAT): units 13, raw paths 11, composed 21,
template subsumption 21. Composed gained one beyond the two component
routes, none beyond all baselines; no component hit was lost. All four
guarded UNSAT controls uniquely succeeded via composition. Aggregate
search/replay 0.01536 seconds vs 4.96616 for subsumption, excluding
separately timed independent replay. Counts are from CI logs and timings
are not portable. PR #295 is also merged.

## New method

Build on the v17.5 composite route and the unchanged v17 learned-fragment
library. First probe cheap unit/path composition. Then optionally retrieve
verified fragments with unit or binary conclusions. After each checked
transfer, run the composite route on the augmented CNF. All consequences
must be certified; no temporary assumptions may enter the handoff.
If the probe misses, try ordinary subsumption composition on the original
input. No partial proof or unsuccessful route is credited.

The certificate records either the composite recipe, the original library
transfer recipe, or the prefix transfers and composite tail. The checker
independently checks each signed guard and partial RUP fragment, the tail
on the augmented input, and the flattened RUP proof against original
input. The independent residual-clause RUP checker is applied in scoring.
Existing Lean entailment composition lemmas apply abstractly; no new Lean
theorem or formal implementation refinement is claimed.

Designed control: (a OR z), (not a OR z) license z, then the four
z-guarded binary square clauses become contradictory. The original unit
and binary path route cannot directly refute this input. A supplied
checked fragment unlocks the composite tail. This is a constructed test,
not evidence of frozen-library transfer on fresh instances.

## Shared budget

All child route work is charged against a single cooperative budget
(4M ticks, 15 seconds, 100k cells per arm), and final replay is charged.
Composite receives 1/8 of remaining quota, handoff 1/3, final library
1/2; unused work can be reused, and the reserved remainder is available
to final replay. The child deadlines are fractions of remaining time.
These are engineering defaults, not optimal schedules. If final replay
exhausts, no verdict. Some ticks omit actual work, the budget is not a
hard process memory/CPU limit, and independent scoring replay is outside
the search budget. Failed probes and discarded partial work are charged.
Sequential skips the handoff and is a comparator, not an equal-per-route
allocation ablation: its library quota may be larger. No SAT decision
is made; all misses remain unknown.

## Experiment

Four arms: ordinary library, composite, sequential portfolio, cooperative
portfolio. Freeze one audited library. Seed 17603 generates 72 new cases
(24 each 2-CNF, 3-CNF and mixed widths 1–4). The previous 72 v17.5 cases
are retrospective only. Reject exact normalized overlap with previous
splits and upstream inputs, not signed orbit overlap. Public seed, not
externally blinded. Each verified proof must pass independent RUP and
exhaustive truth reference. Positive report audit rechecks all certificates,
input identity, route quota arithmetic and aggregate counts; timing and
negative search observations are not independently authenticated.
No held-out template admission, no solver fallback, no changes to
v18 unified decision or other research lines. Horn is not a separate
route here because unit propagation already subsumes its refutations;
this is an UNSAT-only portfolio, not a general decision engine.

Pending tests and experiment CI. No improvement assumed. P versus NP
remains unresolved.
