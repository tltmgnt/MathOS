TOPO-406 — Requirements Traceability Matrix

1. Purpose

This document establishes traceability between the MathOS reasoning standard, TOPO-406 methodology, acceptance tests, and verification evidence.

Its purpose is to ensure that every applicable reasoning requirement has a defined verification procedure and documented acceptance decision.

2. Source Documents

The traceability framework references:

1. docs/reasoning-standard.md
2. curriculum/TOPO-406-proof-explanation-transfer.md
3. curriculum/TOPO-406-acceptance-tests.md

The exact requirements of the reasoning standard must be inspected before mappings are classified as verified.

3. Traceability Matrix

Requirement ID	Requirement Area	TOPO-406 Test	Evidence Required	Status
REQ-001	Proposition precision	TEST-P01	Defined proposition	Pending mapping
REQ-002	Explicit assumptions	TEST-P02	Assumption record	Pending mapping
REQ-003	Logical validity	TEST-P03	Verified derivation	Pending mapping
REQ-004	Independent verification	TEST-P04	Verification results	Pending mapping
REQ-005	Proof boundaries	TEST-P05	Scope statement	Pending mapping
REQ-006	Mechanism identification	TEST-E01	Mechanism description	Pending mapping
REQ-007	Intermediate reasoning	TEST-E02	Reasoning sequence	Pending mapping
REQ-008	Evidence consistency	TEST-E03	Evidence comparison	Pending mapping
REQ-009	Explanation limitations	TEST-E04	Limitation record	Pending mapping
REQ-010	Source definition	TEST-T01	Source specification	Pending mapping
REQ-011	Target definition	TEST-T02	Target specification	Pending mapping
REQ-012	Structural compatibility	TEST-T03	Compatibility analysis	Pending mapping
REQ-013	Target validation	TEST-T04	Target test results	Pending mapping
REQ-014	Transfer limitations	TEST-T05	Transfer boundary record	Pending mapping
REQ-015	Counterexample search	TEST-C01	Counterexample record	Pending mapping
REQ-016	Falsification response	TEST-C02	Revised claim status	Pending mapping

These identifiers are provisional TOPO-406 tracking identifiers, not confirmed section identifiers from the reasoning standard.

4. Verification Requirements

Each mapped requirement must include:

* Exact source document reference.
* Source section or requirement identifier.
* Requirement statement.
* Associated TOPO-406 test.
* Verification procedure.
* Expected outcome.
* Observed outcome.
* Evidence reference.
* Reviewer.
* Verification status.

5. Traceability Status

Use the following statuses:

Verified Mapping: The requirement exists in the source standard and the mapping has been checked.

Pending Mapping: The relationship is proposed but has not been verified against the source.

Unmapped: A source requirement has no corresponding test.

Conflict: A material inconsistency exists between the requirement and its implementation.

Not Applicable: The requirement does not apply, with documented justification.

Mapping verification is distinct from test execution. A verified mapping does not establish that the corresponding test has passed.

6. Acceptance Criteria

The traceability matrix is complete when:

1. Every applicable reasoning-standard requirement is identified.
2. Each requirement has an exact source reference.
3. Each requirement maps to at least one applicable verification test.
4. Every required test has explicit acceptance criteria.
5. Verification evidence is traceable to the evaluated claim.
6. Unmapped requirements are documented.
7. Conflicts are resolved or explicitly recorded.
8. No provisional mapping is represented as verified.

7. Change Control

Changes to the reasoning standard must trigger a review of affected TOPO-406 mappings.

Changes to acceptance tests must trigger a review of associated requirements.

Every material revision should record:

* Revision identifier.
* Date.
* Changed requirement.
* Affected tests.
* Reason for change.
* Reviewer.
* Verification outcome.

8. Automated Verification Readiness

The matrix should support future machine-readable validation.

Automation should eventually detect:

* Missing requirement mappings.
* Invalid test identifiers.
* Missing evidence references.
* Unresolved critical failures.
* Outdated verification results.
* Conflicting acceptance statuses.

Automated checks must not be treated as proof of mathematical correctness unless they actually establish the relevant proposition.

9. Current Verification State

TOPO-406 methodology: Committed.

TOPO-406 acceptance tests: Committed.

Traceability mappings: Provisional.

Reasoning-standard requirement inspection: Pending.

Automated verification implementation: Pending.

10. Core Principle

Every requirement must be traceable to a test, every test to evidence, and every acceptance decision to a justified conclusion.
11. Reasoning Standard — Confirmed Source Mappings

Source: docs/reasoning-standard.md

The following mappings are supported by the reasoning-standard sections reviewed on October 27, 2026.

Source section	Related acceptance tests	Mapping status
Purpose	TEST-P01, TEST-P02, TEST-P04	Confirmed
Reasoning Pipeline — Step 1	TEST-P01, TEST-P02	Confirmed
Reasoning Pipeline — Step 2	TEST-P01	Partial
Reasoning Pipeline — Step 3	TEST-P02, TEST-P03, TEST-P05	Confirmed
Reasoning Pipeline — Step 4	TEST-E01, TEST-E02	Confirmed
Reasoning Pipeline — Step 5	TEST-C01, TEST-C02	Confirmed
Reasoning Pipeline — Step 6	TEST-T01–TEST-T05	Confirmed
Reasoning Pipeline — Step 7	TEST-P04, TEST-T04	Partial
Reasoning Pipeline — Step 8	TEST-C02	Partial
Mathematical Verification	TEST-P01–TEST-P05, TEST-C01	Confirmed
Empirical and Causal Validation	TEST-E03, TEST-P04	Partial
Transferability	TEST-T01–TEST-T05	Confirmed
Multi-Agent Review	No dedicated test	Coverage gap
Human Oversight	No dedicated test	Coverage gap
Evidence Status	Pending detailed mapping	Pending

11.1 Mapping Interpretation

Confirmed means the acceptance test addresses the identified source requirement.

Partial means the test addresses only part of the requirement.

A confirmed mapping does not mean that a test has been executed or passed.

11.2 Identified Coverage Gaps

The following requirements need additional acceptance tests:

1. Independent multi-agent review.
2. Human oversight and approval.
3. Empirical versus causal reasoning.
4. Revision of conclusions after contradictory evidence.
5. Complete evidence-status classification.

11.3 Verification Rule

A requirement is fully covered only when its corresponding tests address all material obligations and have documented acceptance criteria.

Uncovered requirements must remain explicitly identified until additional tests are implemented.

12. Next Implementation Milestone

Create machine-readable acceptance tests and automated validation for:

* Requirement-to-test traceability.
* Missing evidence detection.
* Invalid verification statuses.
* Unresolved critical requirements.
* Coverage gaps.
* Test-result consistency.

Automation must distinguish structural compliance from substantive mathematical proof.
