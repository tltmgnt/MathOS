# External failure-directed 3-color repair

## Confirmed external evidence

PR #315 merged, both external workflows passed. Six-arm run 46154871502
parsed all 32 pinned inputs, no rejected files, no timeouts, no replay
exhaustion, no label disagreements. Credited results:
v16 4/32 (0 SAT, 4 UNSAT); standalone CDCL 15/32 (11 SAT, 4 UNSAT);
projected/native/incremental each 19/32 (11 SAT, 8 UNSAT);
Glucose4 32/32 (16 SAT, 16 UNSAT). Every credited result replayed.
Projected portfolio counted work 1481867, solver call total 1463.171 ms,
subprocess wall 3236.277 ms; Glucose4 call 307.495 ms, subprocess wall
2131.076 ms, separate external replay 683.527 ms. Different counted
operations, compiled vs Python implementation, no equal-work conversion.
This is a meaningful external coverage deficit, not a solver victory.

All three advanced portfolios miss all eight uuf50 UNSAT, all four
flat125 SAT, and one of four AIM SAT. Their decision and counted-work
totals are identical, while wrapper time increases. Algebraic benefit
is real on Dubois: 4/4 vs standalone CDCL 0/4; projected 24438 steps
vs v16 93855. Need separate search/proof replay ablation on uuf50 before
claiming a cause. Current work is directed at the flat SAT failures.

## Structural route

Recognize disjoint positive ternary exactly-one groups (all three
intra-group negative pairs present), and complete matching-color
edge exclusions between groups. Reject incomplete edges, overlapping
groups, other literals, or nonconforming clauses. Sorted local variable
IDs define colors, so arbitrary relabeling may fail recognition.
Construct a greedy saturation-degree coloring with deterministic
LCG tie-break; then bounded tabu min-conflict moves using neighbor
color counts and an insertion-ordered conflict set. Each move updates
only incident neighbors. This is a SAT witness proposer, not a
complete graph-coloring algorithm; no failed search credits UNSAT.
Original CNF model is independently replayed. No new proof rules.

Connector-side JS smoke, before implementation: exact same structural
families and heuristic, budget 100000, seed 192405, one of four
development flat cases solved (flat125-85, 36953 counted steps,
428 repair moves); three exhausted. This is a separate transcription,
not committed Python or portfolio evidence. Python adds explicit
intra-group checks, model construction and occasional sampling
charges. No tuning on eight fresh flat125 cases selected as the next
eight blob IDs after the original four before evaluation.

Candidate reserves 50% of work/time for eligible >=20 positive
ternary groups with only permitted clause shapes; otherwise full
unchanged projected portfolio. Same fallback remaining budget
accounting. Selected projected baseline because prior external
coverage ties native/incremental at lower measured wrapper overhead.
Not a dominance theorem. Existing solver files and tests unchanged.

## Protocol

Forty external formulas: original 32 plus eight fresh flat controls.
Four arms at original 100000 work / five-second wall configuration:
frozen projected, standalone coloring, candidate, Glucose4 (compiled
reference). Retain original source manifest and independently checked
reference methods, append pinned extra manifest; rotate order, replay
all certificates and retain unknowns. Gate no paired baseline loss,
at least one development flat gain. No heldout improvement guaranteed.
Separate paired regression audit requires 191/191 archived cases in
both portfolios. Scope limited to classic public benchmarks, heldout
only relative to route development; not blind industrial data.
Integrated results pending. No change to the existing audit protocol.
