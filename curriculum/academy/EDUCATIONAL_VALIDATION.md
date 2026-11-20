# Independent educational effectiveness protocol (not yet conducted)

**Status: NOT STARTED / NOT EXTERNALLY VALIDATED.** This protocol is an implementation-ready study plan, not evidence that teaching outcomes have improved. No learners or independent referees have been recruited here.

## Target hypotheses and units

1. **Novice accessibility:** After the four-week bridge, first-time learners identify false universal inferences more accurately than a comparable baseline group.
2. **Research rigor:** Learners using MathOS audit checklists catch more injected missing assumptions and invalid generalizations than a standard worksheet group.
3. **Reproducibility:** Independent instructors can reproduce each executable teaching fixture on a pinned source commit and independently score submitted work consistently.

The primary independent unit is the **learner**, not individual questions or multiple attempts from the same learner. Classroom/instructor clustering must be accounted for if learners are grouped.

## Prespecified outcome metrics

| Outcome | Measure | Important limitation |
|---|---|---|
| Primary: invalid-inference detection | Accuracy on unseen, independently authored proof/counterexample prompts | Tasks must not appear in training material or repository |
| Secondary: proof-boundary communication | Two blinded experts score 0–4 against a frozen rubric | Preserve disagreements, inter-rater reliability and adjudication |
| Accessibility | Task completion, dropout, time-to-complete, accessible-format issues | Report barriers and missingness, not just satisfaction |
| Reproducibility | Fraction of frozen lab commands reproduced with byte-identical/justified outcomes | Record OS, dependencies, hashes and deviations |
| Transfer | Performance on unfamiliar subject-matter examples | No claim of scientific research ability from one classroom |

## Required steps before running

1. Recruit independent educational investigators and domain assessors; verify their roles, conflicts, funding and noninvolvement in solution authorship.
2. Preregister the protocol, independent units, sample-size/power rationale, minimal meaningful effect, inclusion/exclusion criteria, assignment scheme, missing-data analysis, confidence intervals, and multiple-comparison handling **before collecting outcomes**.
3. Establish a comparison condition (existing instructional materials) with equivalent time allocation. Randomize learners where ethical and feasible, or disclose confounding.
4. Freeze the MathOS commit, teaching materials, grading rubric, unseen item bank, item authorship and scoring process. Keep held-out prompts inaccessible to candidate learners and tools.
5. Obtain suitable consent and institutional review where required. Retain identifiable learner data privately; publish only permitted, deidentified aggregates and artifact digests.
6. Predeclare whether a claim concerns beginners, advanced students, independent researchers, or accessibility subgroups. Avoid cross-population extrapolation.
7. Run independent instructors on at least one separate cohort and publish results including attrition, errors, negative outcomes, adverse accessibility effects and protocol deviations.
8. Arrange another expert's review of the analysis and evidence. Specify whether replication succeeded, failed, or remains inconclusive, by cohort and claim.

## Evidence-gated acceptance

- **Mechanical readiness:** all academy metadata and unit tests pass; existing curriculum labs and relevant MathOS CI pass.
- **Content readiness:** qualified educators check mathematical examples, source licenses, pedagogy and accessibility of formats.
- **Pilot readiness:** protocol frozen, comparator, scoring and privacy plan independently accepted.
- **External outcome evidence:** independent, independently scored observations and transparent uncertainty analysis available.
- **Generalizable 10/10 claim:** **not automatically granted**. Requires repeated independent studies across learner populations, measured learning transfer, meaningful accessibility results and sustained maintenance.

Repository scripts may validate structure or hashes. They cannot authenticate external assessors or infer participant outcomes. Record unfulfilled gates as **unknown**, not zero and not passed.

## Suggested reporting format

Record source commit, dataset and item-bank digest, sample sizes and attrition per arm, assignment method, instructor independence, actual outcomes, variance/uncertainty, scoring disagreements, subgroup limitations, access restrictions and reviewer sign-off. Link actual preregistration and independent report when available. Do not fill missing results with simulated values.
