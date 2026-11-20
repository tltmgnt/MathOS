# MathOS Curriculum Academy — unified learning map

This academy is a **navigation and quality-assurance layer** over existing courses, not a new mathematical authority or a certificate issuer. The canonical course metadata is in [catalog.json](catalog.json). The structure checker does not grade students, authenticate referees, prove theorems, or claim external validation.

## Learning routes

| Route | Recommended order | Audience | Evidence to retain |
|---|---|---|---|
| No-code entry | Beginner Bridge → AI/Zeta/TDA | First-time proof students | Hand calculations, counterexamples, capstone |
| Applied topology | Beginner Bridge → Topology laboratory → TOPO-406 | Computing-oriented researchers | Worked lab, invariants, simpler-baseline comparison |
| Formal mathematics | Beginner Bridge → Proof Analysis → Agentic Clay | Advanced undergraduate/graduate | Lean assumptions, dependency proof, external critique |
| Claim assessment | Beginner Bridge → TOPO-406 | Research reviewers | Statement, assumptions, evidence record, transfer test |

No track claims to prove a Millennium problem. Per-course prerequisite waivers and progression require documented human assessment. All seven Clay specializations remain governed by their existing scope and unresolved obligations.

## Reproducible structure check

From the repository root:

```bash
python curriculum/academy/validate.py --json
python -m unittest discover -s tests -p 'test_curriculum_academy.py' -v
python curriculum/lab.py --verify
python -m unittest discover -s tests -p 'test_agentic_curriculum.py' -v
```

The validator rejects missing or unsafe syllabus paths, unexpected courses, missing quality dimensions, prerequisite cycles and attempts to change structural metadata into claims of completed certification or external validation. It deliberately cannot check the underlying mathematical truth of teaching examples or prove that students learned.

## Assessment and reproducibility protocol

For **each real learner** create a private, permission-controlled record containing course ID, instructor, assessor, dated assignment artifact references, original and revised answers, submitted counterexamples, rubric scores and rationale, prerequisite waiver (if any), and a clearly documented pass/revise decision. Publish only aggregated, consented deidentified data; never commit learners' names, grades, protected assignments, or tokens to this public repository.

For code exercises record the source commit SHA, Python version, exact command, input hashes, stdout/stderr or machine report, exit status, and environment restrictions. A passing CI job is a **software-quality signal**, not completion of a learning objective.

For expert courses obtain actual subject-matter human review, record the theorem statement and kernel/assumption scope, and separate **formal validity** from **novelty, pedagogy and mathematical significance**.

## Path to independent educational validation

Use [the educational study protocol](EDUCATIONAL_VALIDATION.md). A full external study requires independent instructors and learners, a prospectively registered comparison, blinded scoring where feasible, agreed outcome measurements, and reporting of failures. As of this implementation, this is **not established**.

## Quality scorecard

The six dimensions in catalog.json are *gates*, not self-awarded numerical scores. Curriculum coverage and mechanical checker success can be measured now. Mathematical accuracy requires expert assessment; novice accessibility requires actual novice usability evidence; external educational effectiveness requires independent study. Do not report 10/10 until credible evidence covers every dimension, and retain negative and inconclusive findings.
