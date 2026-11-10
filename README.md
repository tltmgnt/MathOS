# MathOS

**Research software and a proposed framework for checking, explaining, and experimentally evaluating AI-generated claims.**

MathOS connects mathematical reasoning, Topological Gap Analysis Ω, DTI Ω, and HedgeOps Ω into a disciplined workflow for analyzing systems, diagnosing structural gaps, designing interventions, and learning from observed outcomes.

> **Core principle:** A result becomes useful knowledge when we can check it, explain why it works, identify where it applies, and recognize where it fails.

## What exists and what remains to be established

MathOS combines implemented research components with a broader proposed mathematical framework. **Independent external validation of the broader framework is not yet established.** Local tests and synthetic examples support only the behavior and cases they actually check.

| Evidence level | Current scope | What it establishes |
|---|---|---|
| Implemented software | Core reasoning modules, agents/CLI, EFO integration, R3B reporting, TOPO406 checks, and proof dependency evaluation | Inspectable components for bounded research tasks; each requires its own tests and assumptions. |
| Local evaluation | Repository tests, synthetic proof graphs, and recorded curriculum checks | Scoped software correctness and reproducibility checks; these do not establish scientific benefit or independent replication. |
| Proposed framework | Broader integration of mathematical reasoning, topology, temporal capacity, decision analysis, and ResearchOS/TECT | A research agenda whose generality and practical benefit remain to be tested. |
| External validation | Independent reproduction, representative held-out comparisons, and real-provider acceptance remain open | No general effectiveness, comparative-superiority, or deployment-readiness claim is established by the current status. |

See [machine-readable implementation status](docs/portfolio/STATUS.json), [integration boundaries](docs/portfolio/INTEGRATION.md), and [proof review evaluation limits](docs/PROOF_REVIEW_EVALUATION.md). Software checks, empirical benefit, and deployment acceptance are separate milestones.

## How a lab can evaluate MathOS

Start with one bounded task: for example, reviewing the dependencies of an AI-assisted mathematical argument. Use the existing workflow as an experimental aid, with an accountable researcher reviewing conclusions.

1. **Define the claim and comparator.** State the task, scope, baseline review process, and what would count as a useful improvement.
2. **Build a review record.** Attach the claim, source evidence, assumptions, dependency graph, counterexamples, uncertainty, and a reproducible verification method.
3. **Check software behavior.** Reproduce the relevant repository examples and tests at a pinned commit. For proof graphs, remember that route analysis does not verify statement truth or mathematical sufficiency.
4. **Freeze the evaluation protocol.** Before collecting outcomes, specify held-out cases, independently adjudicated references, reviewer assignment, sample-size rationale, success thresholds, and failure handling.
5. **Measure benefit and overhead.** Compare missed dependencies, false positives, review time, and preparation cost. Retain negative and inconclusive results; repeated runs of the same example are not independent replications.
6. **Seek independent reproduction.** Have an external team repeat the scoped evaluation with its own collection records and report. Broader claims require representative tasks and operators.

The [proof review evaluation guide](docs/PROOF_REVIEW_EVALUATION.md) provides commands, observation formats, and evidence gates. This is a proposed adoption path, not a completed lab study.

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

The table describes intended responsibilities in the framework; it is not a claim that every layer is fully implemented or empirically validated.

| Layer | Intended responsibility |
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

See [`coordination-bottleneck.md`](coordination-bottleneck.md).

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
├── coordination-bottleneck.md
└── result-contract.json
```

## Status

**Bounded research software and evolving specification.** Implemented modules include `mathos/core.py`, agents/CLI, EFO integration, R3B reporting, internal-reasoning experiments and TOPO406 verification tests. The broader mathematical framework remains a research proposal, and independent external validation is not yet established. These components are not a universal theorem prover or a validated measure of general intelligence. Numerical and operational claims require their scoped evidence and tests. See the evidence levels and lab evaluation path above.

## Roadmap

These are development and evaluation goals, not evidence of completed validation. Existing partial implementations retain their documented scope.

- [ ] Preregister a bounded lab evaluation with held-out cases and matched baselines
- [ ] Publish outcomes, preparation costs, uncertainty, and negative results
- [ ] Obtain independent external reproduction before promoting broader effectiveness claims

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

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for topology choices, worked explanations, a graded laboratory and adoption boundaries. Run the offline answer key from this repository root:

```sh
python curriculum/lab.py --verify
```

[Expected answers](curriculum/expected.json) · [Recorded local validation](curriculum/VALIDATION.json). The guide states any existing dependency needed for the lab.
