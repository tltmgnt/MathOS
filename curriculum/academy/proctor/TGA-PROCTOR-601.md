# TGA-PROCTOR-601 — Advanced formal verification and research supervision

**MathOS Academy | 10/10 design target | 8-week advanced extension | 64–80 hours**

Prerequisite: TGA-PROCTOR-501 or documented equivalent. Together the 12-week foundation and 8-week extension provide 160–200 hours. The objective is defensible proctor competence, not a Clay award or academic accreditation. This edition implements technical improvements; independent educational effectiveness and live model operation remain unvalidated. No numerical quality score can be inferred from CI.

## Advanced eight-week sequence

### 1 — Formal specification and proof kernel
Learn the distinction between a proposition, proof term, explicit hypothesis, transitive axiom and mathematical interpretation. Open formal/Proctor601.lean. Derive route_split on paper and then explain both directions of the checked Lean term. Compile using Lean 4.14.0 with warnings as errors; inspect the eight printed axiom reports. Produce a theorem statement, proof, toolchain, source hash and actual output. Negative control: use a separate file asserting (0 : Nat) = 1 by decide; it must fail. No formal claim if the tool cannot run.

### 2 — Dynamic proof-route graph
Version an illustrative graph (A AND B) OR C; replace A by a hypothetical sufficient route D AND E. Predict completion sets before and after; run the graph lab and compare. Inject a dependency cycle; show rejection. Explain why adding a proposed reduction does not make its edge mathematically true. Deliver both versions, source statement and scope. Never mutate the canonical register during an exercise.

### 3 — Agentic proctor and adaptive remediation
Use the six module and four capstone rubric scores from a manually assessed practice record. Use remediation() to target weak modules. Work two cases: high aggregate with a zero module; passing scores with failed integrity. Explain why both need remediation. The deterministic recommendation function is not an AI tutor and does not award grades. In a supervised live agent session, the existing four AI roles may propose feedback; the proctor checks it against the frozen rubric, verifies citations, and records model and usage. No API call required to finish this course. Use an equivalent offline role critique if unavailable.

### 4 — Exact specialist mathematics
Run the seven finite labs. For each, produce a hand calculation and explain the limit. Then select one track for the deeper problem in the lab guide. Distinguish the elementary Lean logical bridge from the actual unproved mathematical theorem. No lab result can close a universal research obligation.

### 5 — Evidence integrity and trust
Build a two-entry HMAC-SHA256 chain using seal and verify_ledger. Store a random secret of at least 32 bytes separately, never in Git or a learner dossier. Retain the expected terminal tag and count in a protected external record. Change a payload, reorder entries, truncate the chain, and substitute a wrong key. Verify each fails. Explain why a key holder can forge the entire history and why anchoring is needed for truncation. This is keyed integrity, not independent attribution, timestamping, public signatures or distributed consensus.

### 6 — Research deployment and moderation
Replay 501's proctor audit on an unmodified checkpoint; simulate a failed request and a recovered batch. Inspect an existing TGA role packet and classify its proof scope. Optional authorized live model batch: use the existing main-only workflow with a defined call budget; preserve role outputs, token usage and directed-check results. Do not claim live validation for offline runs. Produce an operational runbook and incident record. Separate proposal generation from actual Lean acceptance.

### 7 — Educational measurement and fair assessment
Design a preregistered pilot with unseen assessment variants, two accountable scorers, accessibility accommodations, private records and an equivalent-time comparator. Use learner-level analysis, not treating multiple questions as independent learners. Freeze rubric and analysis before recruitment. Produce a consent and retention plan, simulated blank reporting template (not simulated outcomes), and documented scoring disagreement process. No outcome claim until real data exist.

### 8 — Advanced capstone and defense
Submit a pinned evidence packet containing a proof-kernel replay (or explicitly record incomplete), dynamic graph comparison, exact specialist derivation and negative control, checkpoint audit, HMAC tamper checks, remediation plan and oral explanation. The assessor checks that the learner can reproduce an unseen equivalent task unaided by AI. No proof completion or certification follows from a course pass.

## Assessment matrix (100 points)

Formal kernel and theorem-scope audit 20; graph refinement and cycle rejection 15; exact specialist lab with independent derivation 20; checkpoint and authenticated-integrity demonstration 15; adaptive proctor and incident handling 10; capstone oral defense and reproducible dossier 20. Award full points for correct independently explained evidence, half for partial valid work, zero for absent/invalid evidence. Proposed threshold 85/100, at least half in every dimension, at least 15/20 in formal verification and oral defense, and all 501 critical gates. Human assessment only. Missing kernel execution means formal component incomplete; offer a supervised accessible workstation or reschedule, not automatic credit. Preserve feedback, offer an equivalent reassessment and an appeal to another accountable assessor. No automated qualification.

## Operating commands

```sh
python -m unittest discover -s tests -p 'test_tga_proctor*.py' -v
python -m mathos.research.tga_proctor_advanced
lean -DwarningAsError=true formal/Proctor601.lean
python -m mathos.research.tga_proctor_advanced --assessment PRIVATE_RUBRIC.json
```

The assessment file contains scores M1–M6, capstone keys oral_scope, practical_replay, adversarial_mathematics, dossier_and_defense, and integrity true/false. Keep all personal data outside public repository. The rubric tool only applies 501 practice thresholds, not the 601 capstone rubric.

## Ten quality dimensions: acceptance evidence

1. Structure — existing 501 manifest and eight-week extension, mapped outcomes and assessments. Mechanical coverage check; human curricular judgment pending.
2. Mathematical rigor — worked finite labs and scoped Lean logical lemmas; specialist content review and novel theorem proof separate.
3. Architecture — versioned hypothetical graph refinement with cycle rejection; not dynamic canonical proof acceptance.
4. Agentic AI — existing live provider plus structured critique and deterministic remediation; live API exercise pending authorized execution.
5. Assessment — full rubrics, practice controls and unseen-task protocol; actual learner assessment pending.
6. Reproducibility — pinned source, tests, Lean version and axioms; separate operator replication pending.
7. Research methodology — explicit scope, negative controls, revision and evidence chain; real research outcomes not measured.
8. Formal verification — actual Lean workflow for eight elementary lemmas, false theorem control and transitive axiom check. Not formal verification of arbitrary model proofs.
9. Accessibility — supervised/no-code alternatives for nonprogramming goals, accommodations and equivalent evaluation; real usability evidence pending.
10. External validation — independent study protocol, frozen criteria and reporting template; not conducted.

A 10/10 claim is a target, not an awarded rating. All ten require credible evidence; tests cannot replace independent learner observations, external expert content assessment or reproducibility by another operator. See 601-PILOT.md for execution-ready study design. Original 501 course and global mathematics register are unchanged.
