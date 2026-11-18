# MathOS publication readiness

**Prepared on:** 2026-11-18  
**Baseline reviewed:** `main` at `245e94a99fc55303c15161fdb2ff4b13fce50a62`  
**Status:** PREPARATION ONLY — **not authorization to publish or submit**.

MathOS is already publicly readable on GitHub. A public repository, a green CI job, a draft GitHub Release, a compiled Lean theorem and an academic manuscript are **different milestones**. This checklist separates them. It is a maintainer decision record, not a certificate of scientific validity, legal clearance, or security.

## Choose the publication track

| Track | What may be published | Current boundary |
| --- | --- | --- |
| **Source/research software release** | A dated, versioned and reproducible research snapshot, with its actual capabilities and limitations | `LICENSE` contains Apache License 2.0; tests and workflows exist. Release commit, scope, attribution/citation metadata, artifact verification and final checks still require sign-off. |
| **Initial arithmetic research report** | The scoped results of Experiments 001–022 | [v0.1 report](research/MATHOS_RESEARCH_REPORT_v0.1.md) describes results and limitations; exact model revisions and complete pinned dependencies are not recorded there. Do not describe it as independently replicated. |
| **SAT1 mathematical note/reviewer packet** | An **unsubmitted, unrefereed technical note** for independent specialist criticism | [SAT1 note](research/papers/SAT1_FORMAL_NOTE.md), [review protocol](research/papers/SAT1_EXTERNAL_REVIEW.md) and [review register](research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json) explicitly do not establish mathematical novelty, a general SAT complexity bound, or a Millennium Prize solution. |

### Critical version/scope decision

A GitHub **draft** for `v0.1.0`, titled *Initial Research Release*, exists, but has not been published. Its text focuses on the original 22 arithmetic experiments. Since then, `main` has acquired additional modules (including bounded MathOS × discovery and finite proof tools), so **do not publish that old draft against the current `main` without reconciling the scope**.

Choose **one**, and document it in the release notes:

- Freeze a verified historical source commit for the original `v0.1.0` research-only release, confirming that the notes and artifacts apply precisely to that commit; **or**
- Prepare a new version and accurate change log for the expanded software snapshot, review its compatibility and packaging expectations, and update `mathos/__init__.py` and any release metadata consistently.

Do not invent a release date, tag, DOI, author, institutional affiliation, independent reviewer, or validation result. The publication authority and final target are maintainer decisions.

## Pre-publication checklist

### 1. Legal, identity and attribution

- [ ] Confirm all code, papers, datasets, screenshots and linked materials are owned or redistributable under the intended terms; inspect third-party model/dataset and dependency licenses separately.
- [x] Repository root contains the full [Apache License 2.0](../LICENSE); the obsolete conflicting license-selection placeholder has been removed in the publication-prep branch.
- [ ] Confirm the copyright holders, contributors and any required notices; the standard Apache license appendix is **not** an author list.
- [ ] Obtain the actual author/contributor names and affiliations (and ORCID IDs if applicable) before writing `CITATION.cff`, a manuscript title page, or a software citation. Do not silently assign credit to a GitHub username or to AI tools.
- [ ] Agree on whether documentation and datasets carry Apache-2.0 or separate notices; include required notices for external assets.

### 2. Reproducibility and technical verification

- [ ] Record the **exact** selected commit SHA and release scope. Do not equate a test on `main` with validation of a different release commit.
- [ ] Run the offline CLI smoke check from the repository root, e.g. `python -m mathos.cli "2x + 5 = 13"`; independently verify the expected answer `4` and reported `verification_status` against the supported linear-equation scope.
- [ ] Run the relevant Python test groups, for example `python -m unittest discover -s tests -p 'test_mathos_cli.py' -v` and the MathOS × tests when those modules are included. Review all workflow results relevant to the selected commit, not just one success.
- [ ] For SAT1, replay [the pinned Lean 4.14.0 CI workflow](../.github/workflows/proof-route-lean.yml), including the axiom audit. Generate the reviewer packet with `python -m mathos.research.paper_packet --verify-lean --output-dir artifacts/paper`; inspect its manifest, exact hashes and limited theorem statement.
- [ ] For claims depending on the 22 language-model experiments, capture Python/package versions, exact downloaded **model revisions**, random seeds, commands, raw result artifacts and their checksums. The existing dependency ranges are **not a lockfile** and cannot replace these records.
- [ ] Verify all referenced file links, sample commands and paths from a clean checkout of the selected commit. State platforms and Python versions actually tested.
- [ ] Assess whether a packaging manifest and installation instructions are needed. At this review baseline no `pyproject.toml` or `setup.py` is present; repository scripts are **not** thereby a published PyPI package.

### 3. Safety, provenance and claim control

- [ ] Check the full commit history and release artifacts for secrets, private data, large model files and unlicensed material. Passing tests **does not** complete a security review.
- [ ] Audit permissions and scheduled workflows, especially the [automated code-proposal workflow](../.github/workflows/mathosx-code-proposals.yml); keep its generated changes human-reviewed and avoid any auto-merge or release automation not expressly approved.
- [ ] Distinguish deterministic/local proof checks, empirical experiments, external replication, novel mathematics, production suitability and deployment authorization in every public abstract or announcement.
- [ ] Preserve negative and inconclusive findings and the documented scope of synthetic examples; no demonstration of general mathematical intelligence, general theorem proving or universal SAT hardness is established.
- [ ] Decide how vulnerabilities, errata and later corrections will be reported, and whether a `SECURITY.md` with a real maintained contact is appropriate.

### 4. Software release handoff

- [ ] Review [draft v0.1.0 release notes](releases/v0.1.0.md) against the exact intended commit and artifacts; update the GitHub draft and repository `__version__` only after deciding version/scope.
- [ ] Run CI on the final release candidate **commit** and record each relevant workflow URL, conclusion and SHA; download and verify artifacts before any retention deadline.
- [ ] Prepare a concise change log and explicit known limitations. Obtain a reviewer sign-off, then create a protected immutable source snapshot/tag and publish the release **manually**.
- [ ] Decide whether archiving a DOI-backed snapshot is appropriate; only populate a real DOI after the external archive exists.
- [ ] Recheck all public-facing links after release; keep the source SHA, paper/report status and code release status independently traceable.

### 5. Academic note / paper submission gate (separate from GitHub Release)

- [ ] Confirm corresponding-author consent, author order, venue-specific formatting, conflicts and content permissions.
- [ ] Carry out and log **independent** specialist review and meaningful prior-art searching. The current [SAT1 independent review register](research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json) contains no authenticated expert reviews; a public invitation is not a review.
- [ ] Check that all claims in the abstract follow from the exact Lean statement, and that the polynomial-ring interpretation remains explicitly **informal** unless later formalized.
- [ ] Decide whether the contribution merits expository, formalization, educational, or archival publication. Do not submit the SAT1 note as a P versus NP solution.
- [ ] Make a submission decision **only after** independent critique, revisions and a human sign-off; capture the real submission/acceptance identifiers rather than inferring them from CI.

## Evidence available at this preparation baseline

At `245e94a9` on 2026-11-18, observed GitHub Actions runs for TOPO-406 verification, EFO integration, R3B tests, TECT integrity/smoke and PEA software consistency reported **success**. These checks cover their own workflows and do not certify all of MathOS or establish external replication. Check the [repository workflow runs](https://github.com/tltmgnt/MathOS/actions) again on the *selected release commit*.

There is an unpublished `v0.1.0` draft in [GitHub Releases](https://github.com/tltmgnt/MathOS/releases), and there are no author-approved citation coordinates in this file. For scientific claim boundaries see [the repository implementation status](portfolio/STATUS.json) and [external-validation protocol](EXTERNAL_VALIDATION.md).

## Maintainer release decision record (fill before publishing)

| Field | Required value |
| --- | --- |
| Publication track and intended audience | **TBD — maintainer** |
| Version / exact source SHA | **TBD** |
| Release note or manuscript revision | **TBD** |
| Legal/attribution reviewer and date | **TBD** |
| Reproduction environment and artifact hashes | **TBD** |
| CI run URLs for final source SHA | **TBD** |
| Security/provenance reviewer and date | **TBD** |
| Independent scientific reviewer, if claimed | **NOT ESTABLISHED** |
| Known limitations accepted by | **TBD** |
| Final human approval and release date | **NOT GRANTED / NOT PUBLISHED** |

**Publication rule:** all relevant boxes must be checked and the decision record must be completed by responsible humans before claiming release readiness. Filling this document alone does not publish software or submit a paper.
