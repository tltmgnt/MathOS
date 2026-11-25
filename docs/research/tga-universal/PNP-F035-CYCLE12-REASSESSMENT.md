# F035 — Cycle 12 reassessment

PNP_RESOLUTION_STATUS = OPEN.

## Verdict

The accelerated 12-input research budget is complete. It has not
resolved P versus NP. The 107 newly audited declarations (reported
cumulative 1535) establish correctness of several known techniques
and restricted barriers, not a proof of either answer. The prior
reported baseline of 1428 has not been re-audited repository-wide.
The accompanying JSON is a snapshot of exact-head evidence, not
an integrated release. Three remaining lanes have pending checks
and receive no credit. Main is unchanged.

## What was actually established

General branching decides finite valid CNFs, with exponential
branching. Component splitting is exact when supports are disjoint.
Existential CNF projection is exact but may expand. A blocked
variable order for equality requires exponentially many attainable
summary states, not exponentially many bits for an individual
state. Factored elimination minimizes local clause count, but the
five-variable greedy fixture disproves global peak optimality.
The full-size preflight is exact and the bounded solver is sound;
totality is conditional on the bounded supplied schedule.
Normalization preserves truth, not a global polynomial bound.

The parity family gives an elementary auxiliary-free CNF
representation obstruction; only its singleton-pattern lemma
was audited in Lean, not the full asymptotic counting theorem.
The raw all-order multiplicity barrier remains a candidate.
The affine projection and nonlinear moment theorems remain
candidates. A separate exact GF(2) computation reproduced the
static monomial span experiment: the pigeonhole 4 into 3 formula
is unsatisfiable, caps 2 through 5 do not span 1, and cap 6 does.
This does not establish an asymptotic lower bound for polynomial
calculus or unrestricted algebraic SAT solvers.

## Shortest logical route

A sufficient positive result is a uniform deterministic
algorithm A on encoded 3-CNF with A(F) = SAT(F) for every valid F,
termination on every input (including invalid inputs via a gate),
and T_A(N) <= c(N+1)^d for fixed constants c,d independent of F.
Cook-Levin and the standard 3-SAT reduction give P=NP. No specific
proof format is logically required. A negative result instead
requires ruling out every such deterministic polynomial-time
algorithm. A restricted proof-system or representation lower
bound does not suffice.

None of the explored mechanisms provides the missing theorem.
Even a short proof for every UNSAT instance would not by itself
give efficient deterministic discovery. An independently checked
certificate format does not repair the lack of completeness or
discovery. A bounded solver returning UNKNOWN is sound but not
a total polynomial decision algorithm.

## Research stop/go gate

Stop treating new fragment lemmas or fixture counts as evidence of
approaching resolution. Complete pending strict replays and
consolidate only exact verified results; do not open a PR until the
repository preflight gate is met. A further substantive research
cycle should begin only with a specific new general-width mechanism
or a precisely stated falsifiable complexity conjecture, not with
a repeat of raw elimination, local ordering, or fixed-degree lifting.
First attempt to falsify the universal claim; if it survives,
prove correctness, termination, and a uniform bound with bit costs.
Only then formalize and seek independent mathematical review.
The number of inputs to resolution cannot be estimated. No promised
resolution date or percentage is meaningful.

See f035-cycle12-evidence.json for scoped counts, exact commits,
run IDs and remaining obligations. The existing F035-F042 gap model
is not changed to mark resolution or machine-cost obligations closed.
