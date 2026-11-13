# Example: Diagnosing a Coordination Bottleneck

## Observation

A team repeatedly misses delivery deadlines. The observation alone does not establish the cause.

## Competing hypotheses

- **H1 — Capacity constraint:** There is more work than available execution capacity.
- **H2 — Approval latency:** Work waits too long for decisions or authorization.
- **H3 — Information delay:** Required information arrives late or is incomplete.
- **H4 — Dependency concentration:** Many tasks depend on one person, team, or system.
- **H5 — Temporal fragmentation:** Interruptions and switching prevent sustained work.

## Evidence to collect

Use only information appropriate to the task and privacy context. Potential measures include task waiting time, cycle time, rework rate, approval delay, interruption frequency, dependency count, and workload distribution. Define each measure before comparing teams or time periods.

## Intervention design

1. Record a baseline and document how metrics are calculated.
2. Choose the hypothesis best supported by current evidence.
3. State a prediction before changing the system.
4. Make a bounded intervention where practical.
5. Compare outcomes with the baseline and account for plausible confounders.
6. Record unexpected outcomes and revise the diagnosis.

Example prediction: if approval latency is the primary bottleneck, a clearly scoped approval-time reduction should reduce waiting time. If waiting time falls but end-to-end delivery does not improve, another constraint may dominate.

## Limits

This example is illustrative, not a validated diagnostic instrument. Correlation between an intervention and an outcome does not automatically prove causation. The evaluation should account for seasonality, changing workload, measurement changes, and other plausible explanations.
