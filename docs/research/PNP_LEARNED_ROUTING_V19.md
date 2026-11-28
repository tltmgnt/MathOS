# Unified discovery v19 — frozen learned routing candidate

This is the routing follow-up to merged unified-discovery PR #285.
The repository already has a separate v19 multi-wave/compact-retrieval
line (PR #282); this change does not replace or renumber it. It leaves
all upstream proof semantics, formal checks, and other research branches
unchanged.

## Motivation and policy

V18's public development run solved 22/22, as did v16 and v18 without
retrieval. The reported wall times were about 1.201, 1.053 and 1.070
seconds respectively. There is no demonstrated incremental retrieval
coverage on that experiment. Rather than tune on a new evaluation set,
fit a four-bucket gate from a separately replayed v18 calibration
report, using active support <=16 and syntactic Horn/2-CNF recognition
as cheap features. Require at least three paired calibration cases,
at least one v18 coverage win over v16, and no v18 coverage loss to
select the v18 integrated route. Otherwise dispatch directly to v16
with its full allocation, avoiding the upfront retrieval reservation.
Empty libraries always dispatch to v16.

Coverage means a checked SAT or UNSAT decision, not an estimate of
hardness. Timing and work counters are deliberately excluded from the
fit criterion. A tie does not select retrieval. This policy may miss
cases where retrieval helps, and a calibration win need not generalize.
It is a conservative empirical routing heuristic, not a theorem of
dominance, optimality, or statistical significance.

The gate is frozen by digest and bound to its library and calibration.
A caller supplying a gate must verify provenance separately; validating
its structure is not evidence that its counts are authentic. The
experiment audit reconstructs the gate from the replayed v18 report.
A gate prediction itself never authorizes a verdict: the unchanged
v16 or v18 verifier checks the selected payload against the original
input. No additional inference rule or Lean theorem is introduced.

## Frozen evaluation

Use the v18 22-case report as calibration, then evaluate four matched
arms (v16, v18, v18 without retrieval, v19 gate) on 24 newly seeded
random2/random3 CNFs and six deterministic chain twins (24,48,96
variables). Reject normalized exact duplicates against upstream,
library splits and calibration. This does not guarantee disjointness
under all signed permutations or logical equivalence. The public seed
19029 is not a third-party blind holdout. No feedback from evaluation
changes the gate or library.

All arms inherit the v18 one-core, 512 MiB address-space, ten-second
wall and five-second cooperative limits, plus 100000 reported work
steps. Offline calibration is excluded from per-case timing; its
cost is real and must be amortized separately. Work counters omit some
verification and bookkeeping; they are not common CPU instruction
units. Wall observations include worker startup and are single-run
measurements, not a statistically established speedup. The report
records family coverage, paired wins/losses, actual gate route choices,
wall time and observed RSS. All positive decisions and aggregate counts
are audited independently of routing prediction; timings, resource
signals and unknown search claims are not mathematical certificates.

The workflow publishes calibration, evaluation, audit and SHA-256
manifest. A completed experiment may report a tie or regression; it
does not assert superiority. Keep the candidate draft until actual
artifacts are reviewed, baseline losses investigated and independent
external evaluation performed. P versus NP remains unresolved.
