# Independent-source SATLIB comparison — research audit

## Verified predecessor and integration caveat

Native PR #307 corrected run 46152565886 passed both jobs:
191/191 (125 SAT, 66 UNSAT), as did projected portfolio.
Native candidate used 1163836 vs 879758 steps and 856.320
vs 607.536 ms observed time: it is not a general improvement.
Incremental PR #310 run 46152677154 passed both jobs, same
191/191. Native vs incremental portfolio: 1163836 vs 1120964
steps, 854.268 vs 839.143 ms, 106804 vs 102160 stored bytes.
Standalone incremental pruning reduced bytes 85629 -> 75707.
Native control native_20_1 source rows 42 -> 2 and bytes
2469 -> 336; the larger integrated speed/work gain is modest.
#310 merged into the parent research branch after #307 merged
to main; main at 07e35a042 lacks incremental files. Draft #312
carries the verified incremental commit to main. This audit
branches from current main and compares only main-available
engines; incremental comparison remains a separate follow-up.

## External protocol

Source: SATLIB https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html,
as mirrored by https://github.com/mitchellh/go-sat at immutable
revision fc0e735aff48989326f256121b5ed6fc585858c3. No solver
outcomes were used to select cases. Freeze lowest Git blob IDs
within strata before execution: eight uf20-91 SAT, eight
uuf50-218 UNSAT, four AIM SAT, four AIM UNSAT, four flat125 SAT,
four Dubois UNSAT. 32 selected, 16 each label. Manifest records
path, byte length and Git blob hash; verify bytes on ingress.
Labels are published family labels and filename/metadata
conventions, not a blind oracle. Source is externally authored,
but these are classic public benchmark instances, not modern
industrial workloads. The selected subset is not representative
of all SATLIB or general SAT. Strict parser reports invalid
DIMACS instead of repairing or substituting cases. Known risk:
some mirrored Dubois files appear to omit terminators; do not
infer corrected formulas. Keep rejected files in denominator.

## Comparison

Five arms: v16, standalone MathOS CDCL, affine-projected
portfolio, native portfolio, compiled Glucose4 through pinned
python-sat 1.8.dev24 with proof logging. Each gets a separate
subprocess timeout of 5 seconds including startup, proof output
and IPC; MathOS additionally has the original cooperative 100000
step limit and 5-second internal configuration. These are common
wall envelopes, not equivalent computational steps across
implementations. Glucose uses its own native counters; no
fabricated cross-solver work conversion. Measure internal call
time, wall elapsed (including startup), independent external
replay time, certificate bytes, coverage, timeouts, claimed
decisions and replay exhaustion. Rotate arm order. Single run
per instance; timing is noisy and not a performance theorem.

Independent replay checks original models, existing MathOS
proofs, and every external DRUP addition via existing RUP
semantics. Deletion hints are ignored (retaining all entailed
clauses is sound); proof must imply the empty clause. Missing
final empty step is accepted only if RUP proves it. The external
replay budget is 20M steps /15 cooperative seconds, distinct
from solver envelope. Existing MathOS audit budgets retained.
Exhausted replay is uncredited; malformed proof or reference
disagreement fails the run. Repeat audit from serialized
evidence. No minimum competitive coverage gate; expose every
miss and preserve selected denominator. This is a benchmark
integrity gate, not a solver performance gate. Existing solver
and tests unchanged. No new formal theorem; reuse prior
certificate checkers, not full Lean verification. Do not claim
P vs NP or industrial superiority. Modern competition suites,
full replay formalization and incremental/main integration remain
open. Results pending actual GitHub Actions execution; local
checkout unavailable (DNS), PySAT not installed locally.


## Protocol revision 2 (before solver outcomes)

#312 has now merged into main at 3e7961c7460aa75687788a8d101473e8db551928;
main-target run 46154064114 passed. The research branch integrates that
main revision as a second parent and adds the incremental portfolio
as a sixth arm, preserving the original five arms, all 32 cases, and
unchanged budgets and integrity gates. Original run 46154249766 was
still queued when this change was prepared. Schema /2 distinguishes the
expanded protocol; no result from /1 is relabeled.

Independent connector-side preflight on the pinned revision:
eight uf20 formulas had exactly 2,16,15,6,3,1,1,2 models in manifest
order (all 91 clauses, exhaustive 20-bit assignment count).
Four selected Dubois files parsed with declared 200,192,240,176
clauses respectively. Each yielded a checked direct GF(2)
contradiction from 50,48,60,44 exact parity equations. Unlike the
unselected dubois100 example, the selected four are well-formed
in the retrieved text. The committed reference implementation
recomputes uf20 model counts and the Dubois direct parity sum
without using the candidate solvers, stores results in the report,
and independently rechecks them in serialized replay. Exact-byte
checks remain mandatory on CI; preflight used fetched text, not
a verified local checkout. Remaining 20 labels are published
references until candidate certificates establish them.
No comparative solver performance has been measured here.
