# MathOS — 24-week agentic Clay research curriculum

**Path:** advanced undergraduate/graduate prerequisites, then a reproducible research apprenticeship.  
**Pace:** 24 weeks, 8–12 hours per week, matching the existing [proof-analysis verification curriculum](proof-analysis-verification.md).  
**Outcome:** an independently reviewable, honestly scoped mathematical research packet, not certification of a Millennium problem.  
**Certification:** \`NOT_CERTIFIED\` (all seven MathOS tracks remain \`BLOCKED\`, with 14 open proof obligations).

This course connects three existing MathOS components: [Clay full-target alignment](../docs/research/CLAY_TARGET_ALIGNMENT.md), [seven problem probes](../docs/research/SEVEN_HYPOTHESIS_LAB.md), and the [guarded four-role agent](../docs/research/AGENTIC_RESEARCH_PROCESS.md). **Clay does not provide or endorse these grades or a course certification.** Only the target statements and external prize rules originate from Clay.

## Curriculum process

<source -> prerequisite skills -> precise conjecture -> bounded check -> skeptic
 -> revision -> independent theorem review -> documented handoff>

The actual agent roles are **planner**, **proposer**, **skeptic**, and **reviewer**. The agent's review is advisory, not independent mathematical validation. The offline mode is a scripted orchestration rehearsal; a live model run requires separately authorized API credentials and may incur charges.

## Core sequence: six four-week modules

| Weeks | Module | Practical work | Required evidence | Pass boundary |
|---|---|---|---|---|
| 1–4 | **Proof statements and Clay source literacy** | Extract the official target, quantify all variables, distinguish weak examples from the universal claim; build and attack a dependency graph | Claim scope, Clay source map, dependency audit, counterexample critique | Human approves precise statements; no proof claims |
| 5–8 | **Reproducible seven-track experiments** | Replay existing probes, reconstruct independent oracles, mutate assumptions, document non-implications | Bounded report, oracle, negative control, evidence boundary | Exact bounded behavior reproduced, not global truth |
| 9–12 | **Agentic planner → proposer → skeptic → reviewer** | Run the offline agent, propose one exact lemma, challenge it, revise it, audit model use | Agent report, lemma, skeptic critique, safety audit | Human review of unverified model outputs |
| 13–16 | **Specialist mathematical attack** | Study primary sources; formulate an unproved bridge lemma; try counterexamples; write a theorem-oriented research note | Literature ledger, bridge lemma, falsification notebook, research note | Specialist reviews mathematical assumptions and novelty |
| 17–20 | **Formal proof and trusted verification** | Inventory Lean assumptions, prove a small lemma, replay real compiler/checker evidence, compare formal theorem to full target | Trusted-base report, formal file, checker record, proof-scope audit | A valid small formal theorem does not prove the Clay statement |
| 21–24 | **Independent review and handoff** | Freeze provenance, arrange independent critique, revise or record gaps, defend a scoped final packet | Reproduction manifest, separate review, revision log, final handoff | Human judges training/research work; no automatic academic grade |

The [machine-readable syllabus](agentic-clay-v1.json) makes each of the **24 individual weeks** independently addressable, with its own assignment and deliverable. This document supplies the course's context and boundaries, not a substitute for subject textbooks or supervised postgraduate expertise.

## Seven specialization tracks

At the start of week 13, select **one primary track**; the rest of the course uses its problem-specific Clay target, first executable MathOS probe and explicit missing theorem. Students may examine other tracks to practice detecting invalid transfers.

| Track | Subject prerequisites | Week 5 starter | Week 13–24 target | Critical failure to expose |
|---|---|---|---|---|
| **Riemann** | Complex analysis, analytic number theory, spectral analysis | Independent first Li-coefficient computation | All-index Li inequality or noncircular spectral zero identity | Finitely many computations ≠ statement about every zero |
| **P versus NP** | Algorithms, computational complexity, proof complexity | Verify \(K_4\) parity 3-CNF contradiction and resolution certificate | Uniform SAT algorithm with total polynomial bit complexity **or** unrestricted complexity separation | A resolution lower bound alone ≠ \(P\ne NP\) |
| **Navier–Stokes** | Functional analysis, Sobolev spaces, nonlinear PDE | Full nonlinear ABC identity and conditional perturbation inequality | One fully specified Clay alternative A/B/C/D with admissible data/force/domain | Conditional control of one periodic flow ≠ universal smoothness |
| **Yang–Mills** | Lie groups, gauge theory, constructive QFT | Regulated two-state transfer matrix | Rigorous nontrivial 4D quantum gauge continuum theory and a physical mass gap | A toy positive lattice gap ≠ a continuum physical gap |
| **Hodge** | Algebraic topology, algebraic geometry, Hodge theory | Hyperplane ring of projective space | Explicit rational algebraic cycles for a nontrivial primitive family | Known projective-space ring ≠ universal Hodge |
| **Birch–Swinnerton-Dyer** | Algebraic number theory, elliptic curves, Selmer groups | Independent finite-field elliptic-curve point counts | Full analytic/algebraic rank comparison; refined leading term separately | Local traces ≠ global rank or finiteness of Sha |
| **Poincaré** | Algebraic topology, Riemannian geometry, Ricci flow | \(S^3\) simplicial boundary and mod-2 homology | Independently audited Hamilton–Perelman Ricci-flow theorem dependency ledger | Known sphere homology ≠ proof reconstruction |

**Poincaré is already solved by Perelman**: the course is about an independent *reconstruction*, not solving a new unsolved Clay problem.

## Week-by-week assignments

| Week | Deliverable | Week | Deliverable |
|---:|---|---:|---|
| 1 | Exact claim scope | 13 | Literature ledger of three verified sources |
| 2 | Clay source and boundary map | 14 | One precise missing-bridge lemma |
| 3 | Canonical proof-dependency audit | 15 | Falsification notebook |
| 4 | Counterexample review | 16 | Theorem-oriented research note |
| 5 | Seven-hypothesis machine report | 17 | Trusted computing-base inventory |
| 6 | Independent reverse-oracle reconstruction | 18 | Supporting small formal lemma |
| 7 | Mutated-assumption negative control | 19 | Actual kernel/checker evidence record |
| 8 | Bounded-evidence non-implication | 20 | Formal versus Clay scope comparison |
| 9 | Offline agent role rehearsal packet | 21 | Reproduction manifest |
| 10 | Candidate lemma with exact conditions | 22 | Independent reviewer critique |
| 11 | Skeptic counterexamples and revision | 23 | Revision and unresolved-defect log |
| 12 | Agent safety and provenance audit | 24 | Final research handoff and defense |

## Executable curriculum check

From repository root, with Python 3.10+:

\`\`\`sh
# Verify 24 weeks, six modules, seven canonical track mappings and no-promotion gates.
python -m mathos.research.agentic_curriculum --track all \
  --output-dir artifacts/curriculum

# Rehearse agent handoffs for one selected track (scripted OFFLINE; no API).
python -m mathos.research.agentic_curriculum --track Navier-Stokes \
  --rehearsal --output-dir artifacts/curriculum/ns

# Run strict schema, mapping, negative-control and no-certification tests.
python -m unittest discover -s tests -p 'test_agentic_curriculum.py' -v
\`\`\`

The first command produces \`curriculum_plan.json\` with 24 dated-by-week assignments, seven Clay targets, exact primary sources, open obligations, source SHA-256 digests and the necessary human-review gates. The second also produces \`offline_rehearsal/agentic_research_report.json\` and \`agentic_research_handoff.md\`.

**Not an automated grade:** A passing CLI/CI run validates only curriculum structure and already-registered bounded evidence. It reports \`learning_state=CURRICULUM_PLAN_ONLY\`, \`completion_awarded=false\`, \`rubric_assessed=false\` and \`certification=NOT_CERTIFIED\`. It cannot tell whether the learner actually completed any assignment or wrote a valid mathematical proof.

### Manual capstone rubric (100 points)

| Dimension | Points | Expert must inspect |
|---|---:|---|
| Precision of mathematical claim | 15 | Quantifiers, domains, full Clay statement |
| Complete assumptions | 15 | Functional spaces, axioms, hidden hypotheses |
| Independent checks | 15 | Reproducible evidence and negative controls |
| Adversarial review | 15 | Counterexamples, circularity, repaired gaps |
| Proof-scope honesty | 20 | No unsupported implication from special result to full theorem |
| Provenance | 10 | Credible originals, software/data fingerprints |
| Communication and handoff | 10 | Clear evidence, reviewer-ready research packet |
| **Total** | **100** | **Requires accountable human assessment** |

Course completion is independent from *scientific* proof certification. No model verdict, finite example, course grade or passing Python workflow closes any of the 14 mathematical obligations.

## Quality gates

At each module boundary, the instructor must verify the required artifacts, reject fabricated citations or missing theorem assumptions, and record explicit unresolved limitations. Passing the skeptic stage means a challenge has been attempted, **not** that no counterexample exists. The formal stage must inspect actual checker output and theorem statement; tests cannot pass by adding \`sorry\`, \`admit\`, or unreviewed shortcut axioms. The final stage requires an actual independent reviewer; filling in a form or running a code pipeline cannot substitute.

When an AI-generated lemma is flawed, revise or reject it and record the counterexample; do not silently drop failed attempts. When a bounded experiment contradicts a known theorem, investigate the encoding and mathematical assumptions before reporting a breakthrough. The validated Clay target statements and canonical proof register remain read-only throughout this course.

## Next course iteration

Once a supervisor has vetted several genuinely new *sublemmas*, consider a subject-specific sequel with a proof assistant, curated literature, and independent specialists. That is distinct from a claim of a completed Millennium solution or eligibility for Clay's award process.

Sources: [CMI Millennium problems](https://www.claymath.org/millennium-problems/), [Clay rules](https://www.claymath.org/millennium-problems/rules/), [MathOS existing proof-verification curriculum](proof-analysis-verification.md), [MathOS official-target audit](../docs/research/CLAY_TARGET_ALIGNMENT.md) and [MathOS agent process](../docs/research/AGENTIC_RESEARCH_PROCESS.md).
