# MathOS

<!-- research-workbench:start -->
## Research workbench

[Open this repository's private workbench](https://mathos-research-workbench.troturn31.chatgpt.site) · [All repository workbenches](https://tltmgnt-research-workbenches.troturn31.chatgpt.site)

The hosted interface requires ChatGPT sign-in and access to the private Site. It supports browser-local research records, evidence fingerprints and workspace export. It is a prototype: no live AI model or repository backend is connected, and it does not establish external validation.
<!-- research-workbench:end -->


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

## Quick start (bounded offline example)

From a checkout of this repository, use Python 3.11 to run the deterministic linear-equation CLI:

```sh
python -m mathos.cli "2x + 5 = 13"
python -m unittest discover -s tests -p 'test_mathos_cli.py' -v
```

The CLI is limited to supported linear equations; it does not prove arbitrary theorems. The optional model-backed paths require separate dependencies and configuration, and their generated responses are **unverified** unless independently checked. This repository does not currently advertise a built PyPI distribution.

## Publication and citation status

For the [publication-readiness checklist](docs/PUBLICATION_READINESS.md), use a specific source commit and select **either** a scoped software release **or** an academic-review/submission track. A draft `v0.1.0` GitHub Release exists but has **not** been published. It describes an earlier set of 22 arithmetic experiments and must not be represented as a release of all current `main` features without reconciling the version and scope. Author-approved citation metadata, independent replication and manuscript acceptance are not established by this repository.
## Experiments 023–050: executable research extension (not yet a published release)

The [follow-up arithmetic protocol](docs/research/EXPERIMENTS_023_050.md) adds 28 bounded conditions to the original 22. All 28 were [executed on both specified GPT-2 models](docs/research/EXPERIMENTS_023_050_RESULTS.md) on November 18, 2026, and [model revisions, metrics and artifact checksums were recorded](evidence/internal_reasoning/EXPERIMENTS_023_050_SUMMARY.json). This makes **50 numbered experiments with recorded execution**, not 50 independent scientific studies or validated mathematical reasoning. The v0.1.0 GitHub release draft is **still unpublished**, and its body has not yet been revised to include the new results.

## How a lab can evaluate MathOS

Start with one bounded task: for example, reviewing the dependencies of an AI-assisted mathematical argument. Use the existing workflow as an experimental aid, with an accountable researcher reviewing conclusions.

1. **Define the claim and comparator.** State the task, scope, baseline review process, and what would count as a useful improvement.
2. **Build a review record.** Attach the claim, source evidence, assumptions, dependency graph, counterexamples, uncertainty, and a reproducible verification method.
3. **Check software behavior.** Reproduce the relevant repository examples and tests at a pinned commit. For proof graphs, remember that route analysis does not verify statement truth or mathematical sufficiency.
4. **Freeze the evaluation protocol.** Before collecting outcomes, specify held-out cases, independently adjudicated references, reviewer assignment, sample-size rationale, success thresholds, and failure handling.
5. **Measure benefit and overhead.** Compare missed dependencies, false positives, review time, and preparation cost. Retain negative and inconclusive results; repeated runs of the same example are not independent replications.
6. **Seek independent reproduction.** Have an external team repeat the scoped evaluation with its own collection records and report. Broader claims require representative tasks and operators.

The [proof review evaluation guide](docs/PROOF_REVIEW_EVALUATION.md) provides commands, observation formats, and evidence gates. This is a proposed adoption path, not a completed lab study.

## External validation and broader evaluation tracks

The [external validation guide](docs/EXTERNAL_VALIDATION.md) defines independent-operator handoff, evidence gates, and separate evaluation contracts for mathematics, computational research, experiments, and operations. The new offline package auditor checks required study records and artifact digests; it does not establish scientific truth or operator independence. Start with the [study manifest template](validation/manifest.template.json). Real external observations and reviewed replication reports are still required.

```sh
python -m mathos.validation /path/to/study
```

## Why MathOS?

Generating an answer is not the same as understanding or safely using it. MathOS treats each consequential conclusion as a claim that must carry its evidence, assumptions, uncertainty, limitations, and a plan for verification.

MathOS separates two kinds of checking:

- **Formal verification:** Does a proof or computation follow from the stated definitions, assumptions, and rules?
- **Empirical validation:** Does a model, forecast, or intervention correspond to observed reality and achieve its intended outcome?

Success in one category does not guarantee success in the other.

### Video: from a proof to useful knowledge

[**Watch: Terence Tao — AI Solved It. What Comes Next?**](https://www.youtube.com/shorts/4VV0-TfxOWU) · AI Signal

This clip provides context for MathOS’s emphasis on turning a result into understanding: checking correctness, explaining the method, and identifying how it can be used elsewhere.

## MathOS ×: self-improving discovery (guarded preview)

The [MathOS × discovery engine](docs/research/DISCOVERY_ENGINE.md) adds 56 explicit mathematical research questions across seven candidate frontiers, four research directions, and two depths. Offline tests calculate exact finite causal-abstraction defects and parity obstruction certificates. Human-reviewed useful/not_useful evidence updates future question priorities without modifying code or promoting mathematical claims.

```sh
python -m mathos.research.discovery --limit 8
python -m unittest discover -s tests -p 'test_discovery.py' -v
```

This is a bounded, human-in-the-loop learning scheduler—not an autonomous theorem prover, proof of mathematical novelty, or automatic code-updating agent.

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
├── LICENSE                    # Apache-2.0 text
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── PUBLICATION_READINESS.md
│   ├── research/               # experiments, report and SAT1 review materials
│   ├── portfolio/              # scoped implementation/integration status
│   └── releases/               # release candidate notes
├── mathos/                     # core, CLI, proof review and research tools
├── mathosx/                    # bounded finite proof/discovery proposals
├── formal/                     # Lean proof artifacts
├── experiments/                # arithmetic and activation experiments
├── curriculum/                 # TOPO-406 exercises and evidence
├── validation/                 # offline study manifest template
├── verification/               # provenance/integrity scripts
└── tests/                      # unit and integration checks
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

## Licensing

The repository contains the [Apache License 2.0](LICENSE). Before republishing datasets, model artifacts or third-party materials, verify their separate terms and attribution obligations. See the [publication checklist](docs/PUBLICATION_READINESS.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions should make assumptions explicit, include reproducible examples where possible, and state what evidence would falsify a claim.

## Naming and attribution

MathOS is the project name used in this repository. The proof-understanding theme is a general mathematical and engineering principle. Any references to public talks or subtitles should be cited to their original source when included in a published version.

## ResearchOS / TECT concept integration

The [ResearchOS / Topological Epistemic Control Theory technical concept paper](docs/researchos/TECT_WHITE_PAPER.md) proposes an epistemic control and assurance infrastructure for AI-generated knowledge. Read the [repository integration status](docs/researchos/INTEGRATION.md) and [machine-readable scope](docs/researchos/integration.json) for the boundary between the concept and implemented capabilities. Performance targets are research objectives, not achieved results. This documentation addition does not implement the complete ResearchOS architecture or change operational authority.

## Portfolio implementation boundary

See [current implementation and shared-core integration](docs/portfolio/INTEGRATION.md) and [machine-readable status](docs/portfolio/STATUS.json). Independent empirical reproduction and real-provider acceptance remain separate from software checks.

## Executable proof dependency and adversarial analysis

The repository includes a deterministic offline proof-planning prototype:

```sh
python -m mathos.proof_analysis --run-tests --output-dir artifacts/proof-analysis
```

It computes inclusion-minimal completion sets for finite AND/OR dependency graphs,
cross-checks them against exhaustive Boolean evaluation, and reports seven fixed,
narrowly scoped adversarial witnesses. The reports record assumptions, limitations,
test outcomes and content hashes. **This is not a theorem prover, a certification
of a new Millennium Prize solution, or an independent external audit.**

See [the implementation guide](docs/proof-analysis/README.md),
[the mathematical review handoff](docs/proof-analysis/HANDOFF.md), and
[the verification curriculum](curriculum/proof-analysis-verification.md).

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

## SAT1 independent research review packet

The [Lean-checked SAT1 technical note](docs/research/papers/SAT1_FORMAL_NOTE.md)
documents an elementary all-`m` result for disjoint-factor choice-word
expansions. The package includes a [preliminary source ledger](docs/research/papers/SAT1_LITERATURE_LEDGER.v1.json),
an [unfilled independent-review protocol](docs/research/papers/SAT1_EXTERNAL_REVIEW.md),
the actual [Lean source](formal/SATSupport.lean), and digest-based evidence.

Generate a self-contained reviewer packet using:

```sh
python -m mathos.research.paper_packet --output-dir artifacts/paper
```

With pinned Lean 4.14.0 installed, add `--verify-lean` to replay the
exact limited theorem. **The manuscript is not submitted, independently
reviewed, proven novel, or a solution to P versus NP.** Passing CI
prepares a reproducible research handoff, not an accepted mathematical paper.

## Millennium research attempt 007: BSD inert-prime local-factor blind spot

[Research attempt 007](docs/research/MILLENNIUM_ATTACK_007.md) turns to the **Birch and Swinnerton-Dyer conjecture**. Two classical elliptic curves, `E1: y²=x³−x` and `E5: y²=x³−25x`, have distinct rational ranks (0 and 1, **established externally**) but identical good local point counts `#E(F_p)=p+1` for **every prime p≡3 (mod 4)**. The elementary proof pairs values of the odd cubic using the quadratic character; there are infinitely many such primes. A [pinned Lean theorem](formal/BSDInertPrimeBlindspot.lean) checks only the **conditional** odd-character cancellation and an exact E5 rational point, while [the finite-field checker](mathos/research/bsd_inert_007.py) independently enumerates finitely many good reductions. **This does not construct the elliptic L-functions, prove global ranks, establish the BSD conjecture, or claim mathematical novelty.**

## Millennium research attempt 008: finite Z2 gauge strip, not a 4D Yang–Mills mass gap

[Research attempt 008](docs/research/MILLENNIUM_ATTACK_008.md) attacks a **Yang–Mills proof-method limitation** using an exactly solvable **two-dimensional, finite abelian Z2 lattice gauge strip**. For a one-by-n open strip with relative positive plaquette weight t≥1, the exact Wilson-loop expectation is `((t−1)/(t+1))^n`, established by an all-n elementary parity-counting proof. For the explicit trajectory `a=1/k, t=k²+1`, the loop exponent per **physical long-side length** tends to zero, although each finite model has positive per-plaquette decay. The strip's physical width shrinks; the *area-normalized* decay coefficient instead approaches 2, so **neither rate is a physical spectral mass-gap conclusion**. [Pinned Lean](formal/YMZ2Strip.lean) checks single-plaquette gauge invariance and independent-parity polynomial recurrences; [exact enumeration](mathos/research/ym_z2_strip_008.py) checks finite strip configurations and correct units. **No 4D non-Abelian continuum Yang–Mills field, physical Hilbert space or mass gap is constructed.**

## Millennium research attempt 006: Hodge diagonal-cycle obstruction

[Research attempt 006](docs/research/MILLENNIUM_ATTACK_006.md) moves to the **Hodge Conjecture**. For any smooth projective curve of positive genus, its diagonal divisor in the self-product is not a rational linear combination of the two fiber divisors: the classical intersection matrix has determinant `2g`, with a discrepancy of `2g` against the two-fiber span. A [Lean theorem](formal/HodgeDiagonalIntersections.lean) verifies the conditional linear-algebra consequence for genus one and [exact rational regression](mathos/research/hodge_diagonal_006.py) audits arbitrary genus values. **Geometric intersection numbers are assumed as standard external input, not formally proved by the code.** The diagonal is already algebraic, the codimension-one Hodge case is already solved by Lefschetz, and this is **not a proof of the full Hodge conjecture or a new mathematical discovery**.

## Millennium research attempt 005: Riemann Li-positive-prefix obstruction

[Research attempt 005](docs/research/MILLENNIUM_ATTACK_005.md) turns to the **Riemann Hypothesis**. For any finite prefix length, an exact mathematical construction gives a **synthetic**, conjugation/reflection-symmetric multiset of six candidate zero locations, with four off the critical line, whose first N **Li-style** expressions are all positive. The accompanying [Lean proof](formal/LiPrefixObstruction.lean) checks an all-index Gaussian-integer congruence, and a rational-arithmetic program supplies finite-instance certificates. **These are not genuine Riemann zeta zeros or actual Li coefficients and do not prove or disprove RH.** The work establishes a limit of finite positivity checks under symmetry alone, not an analytic theorem about zeta.

## Millennium research attempt 004: general CNF arithmetization

[Research attempt 004](docs/research/MILLENNIUM_ATTACK_004.md) extends the formally checked Boolean arithmetic interpretation to **every finite signed-CNF formula**, including shared variables, negations, empty clauses, and contradictory instances. A separate theorem counts the arithmetic gates in the factored evaluation circuit linearly in formula size; an independent finite enumeration checks 17,113 formula–assignment evaluations. **Evaluating a given assignment does not efficiently find one.** This is not a proof of `P=NP` or `P≠NP`, nor a new Millennium Prize solution.

## Millennium research attempt 003: exact restricted SAT semantics

[Research attempt 003](docs/research/MILLENNIUM_ATTACK_003.md) adds a narrowly scoped Lean theorem relating a **Boolean evaluation** of the disjoint `(x_i + y_i - x_i y_i)` product to a conjunction of disjoint OR clauses for every finite assignment, with an explicit satisfying witness. A standard-library regression exhaustively checks the finite cases up to six clauses. This is not a general polynomial-ring theorem, a uniform SAT-complexity result, mathematical novelty, or a solution to P versus NP. Clay's official 2026 listing has five unsolved problems, Navier–Stokes active under assessment after a September announcement, and Poincaré already solved externally; MathOS has no newly certified Millennium resolution.

## Independent mathematical review invitation (SAT1)

[Open reviewer call #30](https://github.com/tltmgnt/MathOS/issues/30)
invites external mathematicians to examine the scoped SAT1 Lean choice-word
theorem, its literature context, and its weak connection to SAT complexity.
See the [external-review protocol](docs/research/papers/SAT1_INDEPENDENT_REVIEW_PROTOCOL.md)
and [author-side desk critique](docs/research/papers/SAT1_DESK_CRITIQUE.md).

The [independent-review register](docs/research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json)
begins with **zero expert reviews**; opening a public request does **not** mean
an independent evaluation has occurred. `lean_axiom_audit` checks transitive
Lean assumptions under the pinned toolchain. The external review intake
tool records submitted reports but **never** authenticates independence or
promotes any Millennium proof status automatically.

<!-- pea-assurance:start -->
## Psychometric Epistemic Assurance (experimental)

[PEA measurement tools](pea_assurance/README.md) · [Research specification](docs/researchos/PEA_RESEARCH.md)

Proposed Psychometrician × ResearchOS × TECT integration: offline calibration,
agreement and scoped advisory decisions. Includes synthetic tests and a proposed
blinded pilot; independent empirical validation and live controller integration
remain outstanding.
<!-- pea-assurance:end -->


## TECT-X: preliminary Selmer-infinitude manuscript (submission blocked)

The [preliminary LaTeX note](docs/research/papers/TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex) audits exact rank-lower-bound certificates in a nonisotrivial elliptic family and an **elementary conditional** average-size implication. It does **not** prove infinitely many 2-Selmer-dimension-three fibers. The three underlying points and Pell-type family are already in Patel--Chakraborty--Chattopadhyay (2026, [published DOI](https://doi.org/10.21136/CMJ.2026.0080-26)); they are not claimed as new. See the [explicit missing proof obligations](docs/research/papers/TECT_X_SELMER_INFINITUDE_PROOF_OBLIGATIONS.md), [publication readiness audit](docs/research/papers/TECT_X_PUBLICATION_READINESS.md), and [machine-readable blocked gate](docs/research/papers/TECT_X_SUBMISSION_STATUS.v1.json). Neither software tests nor a successful LaTeX build constitute independent mathematical proof review.
