# v17.5 — compositional unit and implication-path schemas

## Observed v17.4 results

PR #295 was still open at observation; both evidence and formal jobs
passed in https://github.com/tltmgnt/MathOS/actions/runs/46137195509.
On 72 fresh formulas (39 UNSAT), exact template composition verified
5, subsumption 31, ordinary Horn subset 21, signed Horn 22.
All 22 signed Horn refutations came from the restricted signed-Horn
family (22 UNSAT of 24). No unique signed Horn success beyond the other
arms. Aggregate search/replay seconds were 0.0164 for signed Horn
versus 4.171 for subsumption. These are logged finite observations,
not portable timing claims. PR #293 (implication paths) is merged.
Build on main without depending on the unmerged signed-Horn PR.

## Composition rather than independent routing

Use standard unit propagation on the full input to establish forced
signed literals. Record original clause IDs and replay each deduction.
If a contradiction is reached, label this unit-only evidence. Otherwise
derive binary residual clauses by deleting literals falsified by those
forced facts from unsatisfied original clauses. The residual clauses are
logical consequences, not merely conditional assumptions. Add verified
units and binary residuals to the original formula, then seek opposite
implication paths using the v17.3 engine. The verifier reconstructs the
prefix, checks each indexed residual clause, checks each path edge on
the augmented formula, and replays the entire flattened RUP sequence
against the original input. Independent residual-clause RUP replay is
mandatory in evaluation. No target solver fallback or learned-template
admission. Any missed or exhausted search is UNKNOWN.

A designed control is (z) plus the four clauses
(not z OR a OR b), (not z OR a OR not b),
(not z OR not a OR b), (not z OR not a OR not b).
Unit closure fixes z but has no conflict. Original binary paths do not
refute. Their composition exposes four contradictory binary clauses.
Removing one guarded clause gives a SAT twin. This is standard
preprocessing and 2-SAT reasoning, not a new theorem or discovery
on an independent distribution.

Lean expresses abstract residual-clause preservation and composition
of entailments; it does not formalize Python verification, propagation
completeness or the path search. Existing limits can block even a
valid finite proof; augmenting input may exceed original dimension
caps. Unit closure alone and raw paths are explicit baselines.

## Evaluation

Compare units only, raw paths, composed units + paths, and existing
subsumption composition with the frozen audited v17 library. Shared
per-arm cooperative search/reconstruction budget 4M steps, 15s, 100k
cells; independent checking separately timed. 72 fresh formulas (24
each random 2-CNF, 3-CNF, mixed widths 1–4), seed 17503; eight
constructed guarded SAT/UNSAT controls scored separately. Reject exact
normalized duplicates against upstream and previous splits, including
the v17.4 restricted generator; not signed-orbit disjoint or blinded.
Reference labels from exhaustive truth tables. Report composition-only
gains relative to the two components, losses, and gains versus all
baselines. Control success is required but is not fresh evidence.
Positive report audit verifies recipes and counts, not timing or search
completeness. No claim of equal machine-level operations or hard
resource limits. New tests and formal jobs pending.

P versus NP remains unresolved.
