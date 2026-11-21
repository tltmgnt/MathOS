# TECT-X thematic analysis and research-assurance implementation

**Version:** 1.0 · **Date:** 2026-11-21 · **Scope:** source-based qualitative audit  
**Scientific status:** research and education tooling; **no RH/BSD proof, no new Selmer-infinitude theorem, no independent external validation**.

This page implements a thematic synthesis of tracked TECT-X work in [MathOS](../../README.md). Its companion
[versioned thematic evidence register](TECT_X_THEMATIC_REGISTER.v1.json) links themes to scoped, local repository
sources; the [thematic gate](../../mathos/research/tect_x_thematic_gate.py) checks referential and status consistency.
Neither file is a mathematical proof checker. Do not conflate a green CI job with corroboration of the scientific
claims that source authors make.

## Method and limits

The coding unit is a **documented claim or workflow**, not an independent mathematical observation.
Documents, source files, tests and JSON status registers were read to construct six descriptive themes.
Evidence links point to the repository's own reports or code, *not* external replications or independent proof
reports. Themes are interpretive; no numerical scoring, inter-rater reliability, causal claims, or external
assessment of learning effectiveness is implied. The thematic record is a snapshot of the stated repository
scope as of 2026-11-21, and a future substantive change requires a reviewed version update.

| ID | Inductive theme | Representative sources | Open boundary |
|---|---|---|---|
| **T1** | Epistemic control and proof-scope governance | [Selmer submission status](papers/TECT_X_SUBMISSION_STATUS.v1.json), [evidence TECT](../../evidence_tect/README.md) | Consistent declarations do not establish independent truth |
| **T2** | Finite computation versus universal proof | [1M zeta/TDA audit](TECT_X_ONE_MILLION_ZETA_TDA_GAP_ANALYSIS.md) | Finite enumeration cannot settle statements about all genuine zeros |
| **T3** | Topological identifiability and controls | [zeta/TDA metrics](TECT_X_ZETA_TDA_AUDIT.v1.json), [instructor key](../../curriculum/tect_x_zeta_tda_standalone/INSTRUCTOR_KEY.md) | Need invariant descriptors and a mathematically justified analytic bridge |
| **T4** | Adversarial spectral mathematics | [Jacobi mismatch](TECTX_RH_FIXED_JACOBI_HILBERT_POLYA_GATE.md), [theta determinant](TECTX_RH_GLOBAL_THETA_FREDHOLM.md) | A partial spectral signature or a parameter-dependent identity does not force RH |
| **T5** | Novelty and Selmer-infinitude boundary | [proof obligations](papers/TECT_X_SELMER_INFINITUDE_PROOF_OBLIGATIONS.md), [publication audit](papers/TECT_X_PUBLICATION_READINESS.md) | Uniform full Selmer calculation and a specialist prior-art review remain open |
| **T6** | Human review and research literacy | [faculty review MVP](../../apps/tect_x_faculty_review/README.md), [standalone curriculum](../../curriculum/tect_x_zeta_tda_standalone/README.md) | Teaching approval is not theorem certification; reviewer identity and field efficacy are unverified |

### Key theme intersections

**T2 × T3 — scale does not cure nonidentifiability.** The experiment records **1,000,000**
parameterized functions, four equal families, and two scalar features per function. The explicit
H0/H1 Vietoris–Rips runs use **128 feature points per family**, not a million-point H1 persistence
calculation. They do not compute Riemann zeta zero sets. The adaptive cycle-Ihara features collapse
mathematically distinct functions to the same measured descriptors. Permutation controls can produce
feature-space loops that do not follow from an intrinsic number-theoretic invariant.

**T1 × T4 — negative results constrain promotion.** A fixed arithmetic Jacobi candidate can
reproduce the appropriate leading counting law yet miss the first known zero; a theta-derived,
parameter-dependent Fredholm determinant can reproduce the completed xi function's zero divisor
without constraining where zeros occur. These are **candidate-specific** boundaries, not a
general disproof of spectral approaches. A useful next contribution must state the exact missing
global and noncircular correspondence.

**T1 × T5 — sound partial arguments do not erase the main open theorem.** The repository's
elliptic-curve records contain rank lower-bound arguments and an explicit higher-rank first fiber.
They also identify 2026 prior art for the rank-three family. The proposed unconditional
infinitude of exact 2-Selmer-dimension-three members of the specified thin progression remains
**open**. A proof of the new uniform descent/average bound and independent novelty assessment are
required before an unconditional publication claim.

**T1 × T6 — independent people matter.** The faculty review application enforces independent
teaching assessments and admin adjudication within its local workflow, but identity is linked to
invitations rather than independently authenticated institutional credentials. Review of a
curricular item authorizes no mathematical theorem. Independent expert verification and external
reproduction remain separate, uncompleted obligations.

## Scope taxonomy

Treat each of the following as a **different kind of evidence**, not a ladder that CI automatically climbs:

- **Documented exact argument:** the repository includes a checkable mathematical derivation; this audit
  does not independently verify its correctness or novelty.
- **Bounded numerical report:** inputs, algorithm and selected outputs are declared; a rerun and a rigorous
  error/scale argument may still be missing.
- **Documented negative result or scope boundary:** evidence excludes a specified candidate or inference,
  not every possible alternative.
- **Implemented workflow:** source and tests support a specified operational behavior, not research efficacy,
  external identity assurance, or theorem certification.
- **Open proof obligation:** an unmet premise that must not be silently upgraded because a different artifact
  passes tests.

The versioned JSON assigns exactly one descriptive evidence kind and explicit limitations to each anchored
record. It deliberately does **not** assign universal confidence percentages or represent self-reported
validation as independent confirmation.

## Intelligent proof-gap verifier extension

The [TECT-X topological proof-gap prototype](TECT_X_INTELLIGENT_PROOF_VERIFIER.md)
connects this thematic register to the existing MathOS AND/OR dependency analyzer.
Its [three versioned cases](TECT_X_PROOF_VERIFIER_CASES.v1.json) cover the RH spectral
and zeta/TDA proposals, the open Selmer infinitude theorem, and the bounded
one-million-function experimental report. It calculates minimal *modeled*
completion sets, common unresolved obligations, structural dependency-graph
H0/H1, scope-transfer warnings and ranked next review actions.

Run `python -m mathos.research.tect_x_intelligent_proof_verifier` from the
repository root. The output is **not a semantic mathematical proof verifier**
or an RH/BSD/Selmer theorem certificate. A graph cycle is not a topological
invariant of any zeta zero set, and a structurally complete model would
not prove that its authored implications are sound.

## Actionable research priorities

1. **P1 — Govern claim-to-evidence traceability.** Keep T1–T6 and the evidence sources linked, guard the
   reported metrics against drift, and fail CI when the manuscript or RH status is silently promoted.
2. **P2 — Establish invariant feature-to-theorem bridges.** Define a stable descriptor, justify its
   mathematical object, document all finite-to-global hypotheses, and show how it connects (if at all)
   to actual zero locations.
3. **P3 — Solve the *actual* Selmer obstruction.** Prove uniform control of extra classes or the
   required one-parameter first-moment estimate. Check the precise contribution against prior art.
4. **P4 — Obtain independent validation.** Publish deterministic rerun instructions and error
   budgets, seek independent expert review, and record authentic provenance before considering
   any stronger scientific claim.

### Reproduce the thematic consistency check

From the repository root (standard-library Python 3.11+):

```sh
python -m mathos.research.tect_x_thematic_gate
python -m mathos.research.tect_x_thematic_gate --json
python -m unittest discover -s tests -p 'test_tect_x_thematic_gate.py' -v
```

The script checks JSON shape, six required themes, source-path existence, reference integrity,
reported experiment metric parity and Selmer manuscript blockers. It exits nonzero on mismatch.
It **does not** rerun the one-million-function numerical experiment, recalculate Selmer groups,
revalidate derivations, discover reviewer credentials, or certify a conjecture. The targeted
[GitHub Actions workflow](../../.github/workflows/tect-x-thematic-assurance.yml) executes the
same source-consistency tests on proposed changes.

For mathematical investigations, the existing
[zeta/TDA experiment report](TECT_X_ONE_MILLION_ZETA_TDA_GAP_ANALYSIS.md) and
[Selmer publication readiness note](papers/TECT_X_PUBLICATION_READINESS.md)
remain the appropriate detailed sources.
