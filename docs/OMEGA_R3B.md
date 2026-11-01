# Ω Architecture Reverse-Engineering Resistance & Replication Benchmark

Version 1.0 — proposed technical research and intellectual property strategy specification.
Associated systems: ResearchOS, MathOS, TGA Ω, DTI Ω, HedgeOps Ω, Evidence & Verification.
**Status: empirical validation required.** Infrastructure is implemented; reference architectures,
independent replications, hidden datasets, and empirical results are not supplied.

## 1. Research objective

Test whether shared representations, cross-framework dependencies, coordinated decision
logic, and evidence-governed transitions yield capabilities beyond independently combined
modules. Establish a reproducible public-information baseline, audit reconstructable and
unavailable components, measure replication and separation losses, test sensitivity to
missing information, and document differentiation without presuming it exists.

## 2. Architecture and adapter contracts

All four layers implement `IntelligenceLayer.evaluate(task, shared_state) -> LayerResult`
in `mathos.r3b`. Representations are domain-specific mappings; claims and propagated
constraints are explicit. A disposition is accept, reject, defer, or revise. Generated
results do not automatically enter accepted knowledge. ResearchOS supplies a separate evidence-state prototype; MathOS adapters must
explicitly connect any acceptance policy to their verification workflow; its caller-provided verification flags are not
independent proof.

| Layer | Representation | Required interpretation |
| --- | --- | --- |
| TGA Ω | S=(V,E,D,C,B,A) | Components, relationships, dependencies, constraints, bottlenecks, authority |
| DTI Ω | T=(C,F,K,I,R,X) | Capacity, flexibility, continuity, interruptions, recovery, coordination |
| HedgeOps Ω | argmax E[U(a\|X)] | Resource, risk, temporal, strategic, operational constraints |
| Evidence | E=(K,R,V,P,F,C) | Claims, references, verification, provenance, falsification, confidence |

TGA diagnoses topology, missing paths, decision rights, and transformations. Structural
gap `S* − St` requires a preregistered distance over topology, constraints, and relationships;
it is not literal tuple subtraction. DTI evaluates `TF(a)=f(C,F,K,I,R,X|a)` and recovery.
HedgeOps evaluates expected and realized utility, incentives, and execution feasibility.
Evidence decomposes claims, checks calculations and assumptions, generates counterexamples,
and preserves uncertainty and provenance. Specialized inference and calibration are adapter
responsibilities; no proprietary algorithms are inferred from these definitions.

## 3. Threat model

| Scenario | Allowed information | Restrictions |
| --- | --- | --- |
| A | Public repository, equations, docs, diagrams, demos, benchmarks | No private code, data, configuration or documentation |
| B | A plus reference black-box queries | Log inputs, outputs, errors, performance and exposed transitions; no internal inspection |
| C | Independent reconstruction using A or B | No original proprietary code; record parent access scenario |
| D | Independent reconstruction of all four layers and integration | Document component and combined behavior |

Record personnel, tools, elapsed time, compute, external dependencies and exact access logs.
Freeze public snapshots and query budgets before reconstruction. Independence requires
operator verification; an interface label cannot establish it.

## 4. Disclosure inventory

Audit actual artifacts at a pinned commit before asserting exposure. D0=public,
D1=reasonably derivable, D2=partial, D3=restricted, D4=independently unverified.
D3 is not a legal conclusion. The inventory template starts unaudited items at D4.

| Area | Potential public content | Potential undisclosed content |
| --- | --- | --- |
| TGA | Graph concepts, equations | Inference, calibration, transformation logic |
| DTI | Variables, models, metrics | Inference, calibration, prediction |
| HedgeOps | Objectives, formulations, risk definitions | Incentives, optimization, execution policies |
| Evidence | Workflow, categories, tests | Acceptance thresholds, verification, falsification orchestration |
| Integration | Interfaces, diagrams | Shared state, protocols, transitions |
| Training/calibration | Published data, results | Private data, parameter history, procedures |
| Operations | APIs, deployment instructions | Private configuration and operational feedback |

## 5. Experimental design

B0 conventional baseline; B1 TGA only; B2 DTI only; B3 HedgeOps only; B4 evidence only;
B5 four independently combined modules; B6 coordinated integrated system. B5 and B6 must
have separately documented implementations; identical component membership is insufficient.
`run_matched` requires all seven adapters and isolates equal task inputs, seeds and declared
budgets. Operators must enforce actual budgets and audit external-information equality.
Use fresh/reset system state per independent trial and log state reset policy.

Conditions: complete information, missing structure, temporal disruptions, economic
uncertainty, conflicting incentives, incomplete evidence, adversarial counterexamples,
and simultaneous constraints. Include synthetic and independently verified real-world
problems plus out-of-distribution tasks. Never expose hidden labels to decision adapters.

## 6. Metric registry

Preregister units, direction, denominator, ground truth, primary/secondary status, missing
value policy, and practical improvement threshold for every metric. Do not collapse unlike
units into an unregistered composite.

| Dimension | Required measures |
| --- | --- |
| Structural | Gap precision/recall, dependency accuracy, bottleneck accuracy, false-positive gap rate |
| Temporal | Feasibility accuracy, continuity/recovery error, interruption sensitivity, coordination feasibility |
| Decision | Expected/realized utility, violations, risk-adjusted performance, regret, execution success |
| Evidence | Verification accuracy, unsupported rate, counterexample detection, reproducibility, provenance completeness, calibration error |
| Integration | Cross-framework consistency, propagation accuracy, integration failures, state consistency, end-to-end success, verification completeness |

## 7. Integration, ablations and interactions

For higher-is-better metrics, IA=SL=PΩ−Psep, IA%=100·IA/|Psep|,
SL%=100·SL/|PΩ| when PΩ is positive. Undefined denominators return null.
For errors reverse direction; percentages require meaningful scales. Negative results
remain negative. Ablation loss is the direction-aware difference PΩ−PΩ-minus-i.
Use `factorial_design()` for all 16 component subsets; do not assume additive effects.
Pairwise interaction is P(i+j)−P(i)−P(j)+P(B0), direction-adjusted for losses.

## 8–9. Fidelity and replication resistance

RF is a weighted sum of functional, mathematical, behavioral, integration, operational
fidelity. All five scores are in [0,1]; preregister explicit acceptance rubrics and weights
summing to one. Interface equivalence does not establish implementation equivalence.

Ω-RRI=α(1−RF)+β(1−NRP)+γ(1−IF), weights sum to one. NRP is normalized
reference-performance reproduction and IF integration fidelity; preregister normalization
anchors and treatment of better-than-reference results. No universal raw utility ratio is
assumed. IF also appears within RF: disclose this intentional overlap or revise weights
before testing. High RRI measures difficulty only under the documented access/resources;
it does not establish legal protection, patentability, or secrecy.

## 10. Statistical validation

Report independent trials, task sample size, dataset description, means, standard
deviations, confidence intervals, effect sizes, missing data and reproducibility commands.
`paired_comparison` uses a seeded 95% percentile bootstrap on matched independent units,
rejects unmatched/missing units, and reports paired dz (null for zero variance).
Aggregate correlated tasks within a trial or use an appropriate hierarchical analysis;
do not count correlated observations as independent trials. Supply justified statistical
tests where appropriate and apply `holm_adjust` across the preregistered comparison family.
A CI alone does not establish practical significance. No advantage follows from one demo.

## 11. Adversarial protocol

Test missing dependencies, incorrect structural assumptions, sudden interruptions,
resource constraints, conflicting incentives, manipulated evidence, contradictory sources,
incorrect mathematical assumptions, unforeseen states and verification exploitation.
Record expected ground truth, observed disposition, failures, and whether the system
appropriately rejected, deferred or revised. Deferral is not automatically task success.

## 12. Data governance

Separate development, validation, hidden evaluation, adversarial and operational data.
Exclude hidden data from public commits, development adapters and calibration. Freeze
versions and protect access logs. Every result records dataset/model versions, configuration,
seed, environment, timestamp and source provenance. `write_record` exports raw observations,
required metadata and a canonical SHA-256 fingerprint; this digest is not a signature or
proof against a malicious operator. Independent operators must verify ground truth and
maintain their own auditable records.

## 13. Disclosure strategy

Public material may include concepts, general mathematics, reproducible demonstrations,
methodology and selected results. Proprietary material may include specialized algorithms,
calibration, integration, optimization and nonpublic data. Restricted material may include
confidential implementation, unpublished inventions, secrets and sensitive deployment
knowledge. Determine actual boundaries through an IP audit. Copyright, patents, trademarks
and trade secrets are distinct. The specification calls for qualified patent review of
potential inventions before release; this benchmark does not provide legal conclusions.

## 14–15. Deliverables and completion gate

Produce: disclosure inventory; public reconstruction report; independent replication
protocol; ablation benchmark; integration report; adversarial results; statistical report;
RRI; IP exposure assessment; commercialization/licensing recommendations. Reports must
link raw records and separate observations from interpretations.

Experimental completion requires all four interfaces implemented, B0–B6 evaluated,
independent replication attempted, ablations and adversarial tests completed, uncertainty
reported, independent reproducibility, and audited disclosures. **These gates remain
pending.** Superiority requires statistically and practically meaningful primary-metric
improvement. Resistance requires documented independent reconstruction under a threat model.

## 16. Falsifiable hypotheses

H1 structural diagnosis improves; H2 temporal feasibility/recovery improves; H3 decision
quality improves; H4 unsupported conclusions decline and reproducibility improves;
H5 integration improves end-to-end performance; H6 public reconstruction differs in
fidelity; H7 adversarial decision/verification performance improves. Evaluate each separately,
with preregistered comparator, endpoints, thresholds and rejection criteria.

## 17. Technical position

Structural intelligence identifies missing structure; temporal intelligence assesses
feasibility; economic intelligence assesses strategic viability; epistemic intelligence
assesses justification. Whether their coordination produces a reproducible advantage is
an open empirical question. Replication requires equivalent behavior, verified performance,
reproducibility and operation under equivalent constraints.

## Reproduction and extension

Run `python -m unittest discover -s tests -p "test_r3b*.py" -v` from the repository root. Implement `BenchmarkSystem`
adapters, freeze a protocol using the template, call `run_matched`, then `write_record`.
Compare B6/B5 and B6/ablations on independent units using `paired_comparison`. No empirical
reference result or synthetic superiority demonstration is shipped with this infrastructure.

### Analyze an exported record

```bash
python -m mathos.r3b_report run.json --metric task_success --output report.json
python -m mathos.r3b_report run.json --metric regret --lower-is-better --output regret.json
```

The CLI verifies the canonical record digest, validates observations, rejects mismatched
implementation or trial coverage, and averages task scores within each trial before a
paired bootstrap. Trials must be independent; repeated deterministic runs do not establish
independence. Default comparison is B6 versus B5; `--reference` and `--comparator` also
support ablation labels. Tasks receive equal weight, and metric direction must be selected
explicitly for losses. Reports retain the source digest and dataset version. A matching
digest checks content consistency, not authorship. These descriptive reports do not
establish statistical significance, practical importance, or replication resistance.
