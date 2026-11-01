# MathOS

**A framework for turning AI-generated answers into verified, explainable, transferable, and empirically tested methods.**

MathOS connects mathematical reasoning, Topological Gap Analysis Ω, DTI Ω, and HedgeOps Ω into a disciplined workflow for analyzing systems, diagnosing structural gaps, designing interventions, and learning from observed outcomes.

> **Core principle:** A result becomes useful knowledge when we can check it, explain why it works, identify where it applies, and recognize where it fails.

## Why MathOS?

Generating an answer is not the same as understanding or safely using it. MathOS treats each consequential conclusion as a claim that must carry its evidence, assumptions, uncertainty, limitations, and a plan for verification.

MathOS separates two kinds of checking:

- **Formal verification:** Does a proof or computation follow from the stated definitions, assumptions, and rules?
- **Empirical validation:** Does a model, forecast, or intervention correspond to observed reality and achieve its intended outcome?

Success in one category does not guarantee success in the other.

## The MathOS reasoning loop

1. **Observe** — Gather relevant evidence about structure, capacity, dependencies, incentives, and outcomes.
2. **State the claim** — Make the hypothesis specific enough to test or refute.
3. **Expose assumptions** — Record definitions, preconditions, uncertainty, and alternative explanations.
4. **Verify** — Check derivations, calculations, logic, boundary cases, and counterexamples.
5. **Explain** — Identify the decisive mechanism in clear language.
6. **Test transfer** — Apply the method to a related problem and document where it does and does not generalize.
7. **Intervene** — When appropriate, test a bounded change with success and failure criteria defined in advance.
8. **Update** — Compare predictions with outcomes and revise the model when evidence disagrees.

## Conceptual acceptance rule

\[
\text{Useful Intelligence} = \text{Correctness} + \text{Explanation} + \text{Transfer} + \text{Feedback}
\]

This is a **conceptual design rule, not a validated numerical equation**. It expresses the dimensions MathOS expects a useful result to address.

## Framework integration

| Layer | MathOS responsibility |
|---|---|
| Topological Gap Analysis Ω | Map system structure, dependencies, decision rights, bottlenecks, and missing connections. |
| DTI Ω | Represent temporal capacity, flexibility, continuity, interruptions, coordination, and recovery. |
| HedgeOps Ω | Evaluate decisions under uncertainty, incentives, economic mechanisms, risk, and execution constraints. |
| Evidence and verification | Inspect claims, calculations, assumptions, counterexamples, and source quality. |
| Arbitration | Compare disagreements by evidence quality, assumptions, uncertainty, and consequences—not by simple majority vote. |
| Reality feedback | Compare predictions and interventions with observed results; record model failures and revisions. |
| Human authority | Preserve accountable human review for consequential decisions and actions. |

## Multi-agent design principles

Each agent should return more than a conclusion. A useful result should include:

- Claim or recommendation
- Evidence and provenance
- Assumptions and definitions
- Method or decisive mechanism
- Uncertainty and confidence rationale
- Counterexamples and failure modes
- Conditions under which the result applies
- Proposed verification or validation test
- Human-review requirement, when applicable

**Do not treat multiple agents as independent confirmation when they share the same data, model, or assumptions.** Agreement is meaningful only to the extent that methods and failure modes are genuinely independent.

## Example: diagnosing a missed-deadline problem

A team repeatedly misses deadlines. “Hire another person” is a possible intervention, not yet a diagnosis.

MathOS investigates competing explanations:

- Is work blocked by approval latency?
- Are dependencies concentrated around one person or team?
- Is information arriving too late or in an unusable form?
- Is the constraint labor capacity, fragmented time, or coordination overhead?
- Would adding capacity actually change the bottleneck?

The analysis should specify evidence that distinguishes these hypotheses, predict what each intervention should change, and define how results will be measured. If approval latency is the cause, adding labor may have little effect. If insufficient execution capacity is the cause, changing approvals alone may not help.

See [`examples/coordination-bottleneck.md`](examples/coordination-bottleneck.md).

## Repository map

```text
MathOS/
├── README.md
├── CONTRIBUTING.md
├── LICENSE-PLACEHOLDER.md
├── docs/
│   ├── architecture.md
│   └── reasoning-standard.md
├── curriculum/
│   └── TOPO-406-proof-explanation-transfer.md
├── examples/
│   └── coordination-bottleneck.md
└── schemas/
    └── result-contract.json
```

## Status

**Concept and specification stage.** This repository documents a proposed framework and acceptance standards. It does not claim that the full multi-agent system, measurement instruments, or validation results have already been implemented. Numerical measures and operational claims should be treated as hypotheses until supported by testing.

## Roadmap

- [ ] Define versioned claim/evidence/result contracts
- [ ] Add unit tests for mathematical examples and deterministic calculations
- [ ] Add proof-assistant integration for suitable formal proofs
- [ ] Add evaluation datasets for explanation quality and transfer
- [ ] Add uncertainty calibration and counterexample tests
- [ ] Add experiment records for interventions and observed outcomes
- [ ] Add agent-specific interfaces and orchestration
- [ ] Add audit logs, permissions, and human approval gates
- [ ] Document security, privacy, and model/data provenance

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions should make assumptions explicit, include reproducible examples where possible, and state what evidence would falsify a claim.

## Naming and attribution

MathOS is the project name used in this repository. The proof-understanding theme is a general mathematical and engineering principle. Any references to public talks or subtitles should be cited to their original source when included in a published version.

## Ω-R3B proposed replication benchmark

The [Ω-R3B specification](docs/OMEGA_R3B.md) defines matched B0–B6 comparisons,
component ablations, factorial interactions, fidelity, replication resistance, disclosure
boundaries and empirical completion gates. `mathos/r3b.py` provides four-layer adapter
contracts, a matched runner, validated metrics, paired bootstrap analysis and auditable
JSON exports. Start with the [protocol template](benchmarks/r3b/protocol.json) and
[disclosure inventory](benchmarks/r3b/disclosure_inventory.csv).

Analyze an exported record with:

```bash
python -m mathos.r3b_report run.json --metric task_success --output report.json
```

The report verifies the record digest, requires matched task/trial coverage and aggregates
tasks within trials before computing paired confidence intervals. Use `--lower-is-better`
for loss metrics. Operators must establish trial independence and enforce actual budgets.

Reference systems and independent replication results remain pending; this addition makes
no claim of integration superiority or intellectual-property protection. Existing MathOS
reasoning, agent, and welfare-model demonstrations do not establish B6 or independent
replication fidelity.

Run the dependency-free benchmark tests with:

```bash
python -m unittest discover -s tests -p 'test_r3b*.py' -v
```
