# PNP-F034 — Joint iterator structural overhead ledger

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base a60279a027a777996ca7f2eb5d60c27b0eaadbac (PR #201).
Four dispatch-ledger files copied byte-identically from verified PR #202
head 4fc98bb04148378b9aca7360fb75e2224e685948; preflight 45535556364/job 138941154923,
artifact 14985909484, seven zero-axiom declarations and 2052 controls.
Do not open the next PR until #202 merges and exact candidate replay passes.

Joint meter projects onto the prior dispatch ledger. Charge one selected
event per visited word cell including the empty terminator, and one per
constructed doubled-transition wrapper. Failure on a set bit short-circuits
before building the next wrapper. Overhead <=2*width+1, with equality for
successful iteration. Combining with the previous dispatch bound gives
K*value+2*width+1; unit base invocation at the actual list limit of 100000
and width 17 gives <=200035 selected events per list invocation, including
failure. Six candidate declarations. The exact overhead expectation on
failure is independently checked using remaining permitted base steps.
2044 small and eight 17-bit boundary controls. Marker F034_ITERATOR_OVERHEAD_OK small=2044 boundary=8.
These are source-level charges, not allocation counts, instruction counts
or proof of compiler behavior. Boundary encoding, parser transition work,
nested aggregation, list reversal, data memory and full machine cost remain.
Strict Lean 4.14.0 warnings and zero-axiom gates unchanged. No local Lean
execution. No independent review or resolution claim.

## Exact-overhead proof repair

PR #202 merged at 6135f07bd8b524e34b80366a966bb41a1c979dff.
Exact candidate 28ddfcfc068b34895a275481a99a09b5fd633810 failed
[45536117967 / job 138943011446](https://github.com/tltmgnt/MathOS/actions/runs/45536117967/job/138943011446), artifact 14986243665.
Five of six named declarations printed no axioms, including the joint
bound and 200035 list bound. Only success_overhead_exact failed:
case splitting rewrote the conclusion but not the local success
hypothesis. Explicitly rewrite that hypothesis using the case equation
before reducing it. No change to executable definitions, theorem
statements, fixtures, warnings or strict axiom gate. Required executable
marker was not reached; new exact SHA must pass replay before PR.
