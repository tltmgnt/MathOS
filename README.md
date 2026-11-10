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

### Video: from a proof to useful knowledge

[**Watch: Terence Tao — AI Solved It. What Comes Next?**](https://www.youtube.com/shorts/4VV0-TfxOWU) · AI Signal

This clip provides context for MathOS’s emphasis on turning a result into understanding: checking correctness, explaining the method, and identifying how it can be used elsewhere.

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

**Bounded research software and evolving specification.** Implemented modules include `mathos/core.py`, agents/CLI, EFO integration, R3B reporting, internal-reasoning experiments and TOPO406 verification tests. The broader mathematical framework remains a research proposal; these components are not a universal theorem prover or a validated measure of general intelligence. Numerical and operational claims require their scoped evidence and tests.

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

## ResearchOS / TECT concept integration

The [ResearchOS / Topological Epistemic Control Theory technical concept paper](docs/researchos/TECT_WHITE_PAPER.md) proposes an epistemic control and assurance infrastructure for AI-generated knowledge. Read the [repository integration status](docs/researchos/INTEGRATION.md) and [machine-readable scope](docs/researchos/integration.json) for the boundary between the concept and implemented capabilities. Performance targets are research objectives, not achieved results. This documentation addition does not implement the complete ResearchOS architecture or change operational authority.

## Portfolio implementation boundary

See [current implementation and shared-core integration](docs/portfolio/INTEGRATION.md) and [machine-readable status](docs/portfolio/STATUS.json). Independent empirical reproduction and real-provider acceptance remain separate from software checks.

## Proof dependency evaluation

See [proof dependency and expert review evaluation](docs/PROOF_REVIEW_EVALUATION.md) for
an AND/OR route analyzer, exhaustive Boolean baseline, matched local timing/allocation
measurements, dependency coverage metrics and paired review observations. The included
example is synthetic. Comparative superiority and external validation remain unestablished.

**∞**

## Topology compatibility and curriculum

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for topology choices, worked explanations, a graded laboratory and adoption boundaries. Run the offline answer key from this repository root:\n\n```sh\npython curriculum/lab.py --verify\n```\n\n[Expected answers](curriculum/expected.json) · [Recorded local validation](curriculum/VALIDATION.json). The guide states any existing dependency needed for the lab.
