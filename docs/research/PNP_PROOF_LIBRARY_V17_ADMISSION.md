# v17.7 — offline certificate-verified knowledge admission

## Prior result

PR #301 merged at b7a3855ae349f1d5e504fc61bc7257946456f0e9.
Evidence CI passed: https://github.com/tltmgnt/MathOS/actions/runs/46139162310.
On 72 fresh inputs (28 UNSAT), library 19, composite 18, sequential 19,
cooperative 20. Cooperative gained one beyond all baselines, a mixed
instance, and used two handoffs. No baseline hit was lost. Fresh
3-CNF coverage was 1/8 for cooperative, sequential and library, zero
for composite. Aggregate search/replay wall seconds were 5.540 for
cooperative vs 4.607 sequential, excluding separate independent replay.
Retrospective cooperative and sequential both verified 23/27.
Thus finite cooperative coverage improved but cost also increased.
Do not claim general superiority.

## Offline admission protocol

Solve only training cases with the frozen v17 library and the v17.6
cooperative portfolio. Reconstruct each successful original-formula
certificate and independently replay it. For a proof of at most 64
additions and at most 48 normalized original clauses, consider the first
two novel short nonempty conclusions and the final empty conclusion.
Use each proof prefix as a candidate. Greedily delete guards only when
the entire prefix still replays by RUP; no globally minimal or
dependency-minimal proof is claimed. Dense-label at most nine active
variables. Check source guard membership and exact source proof-prefix
embedding. Independently refute the guard plus the negated conclusion
using a separate residual-clause checker. This certifies a conditional
entailment, not a theorem without assumptions.

Append at most 24 templates; keep the base library unchanged. This
experimental expansion can exceed the original v17 build cap of 128
by at most 24, but does not alter that build cap. Deduplicate using
the existing small signed-orbit structural key (up to four variables;
labelled key otherwise). This is not semantic equivalence; differing
edge/proof records may retain logically equivalent entries. Each
admitted entry records source and proof hashes, source prefix, original
guard embedding and final library ID. No target-derived admissions
during discovery or held-out scoring; no online self-modification.

## Experiment

Fixed seeds 17701 (36 training), 17702 (24 discovery), 17703 (72 heldout).
Each contains equal random binary, ternary and mixed-width strata.
Reject exact normalized duplicate inputs across these splits and prior
v17-family splits and upstream cases; public seeds and no signed-orbit
exclusion or external blinding. Training uses only the base library.
Admission is completed before discovery scoring, and discovery is not
used to tune. Compare standalone subsumption reuse with base and expanded
library on the same targets under identical cooperative search/replay
caps (4M ticks, 15 seconds, 100k cells); independent replay outside those
caps. This isolates a library expansion policy, not the effect of equal
library sizes. Report offline training/admission time and steps, storage
bytes, paired gains/losses and whether successful recipes actually
reference newly admitted templates. A gain with an admitted fragment
is evidence of bounded transfer, not novelty or unrestricted learning.
Zero gains or losses are valid results. No SAT decision is claimed.

Audit regenerates the admitted snapshot from recorded checked training
proofs and verifies every positive target certificate, source identity,
lineage, fixed split and aggregate counts. It does not authenticate timing
or negative search observations. Existing abstract Lean entailment
lemmas apply; no new theorem or implementation-level formal refinement.
Offline admission has a separate generous cooperative limit and fails
closed if exhausted; no hidden fallback. New tests and experiment pending
CI. P versus NP remains unresolved.
