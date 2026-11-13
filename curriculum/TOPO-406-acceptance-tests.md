TOPO-406 — Acceptance Tests and Verification Criteria

1. Purpose

This document establishes testable acceptance criteria for the MathOS TOPO-406 Proof, Explanation, and Transfer Methodology.

It defines how claims, proofs, explanations, and transferred methods are evaluated before acceptance.

The tests support reproducibility, traceability, falsification, and evidence-based verification.

2. Verification Framework

Each evaluation must identify:

* Claim ID
* Proposition
* Assumptions
* Verification procedure
* Expected result
* Observed result
* Supporting evidence
* Counterexamples
* Acceptance status
* Reviewer

Acceptance must be based on documented evidence rather than confidence alone.

3. Proof Acceptance Tests

TEST-P01 — Proposition Precision

Objective: Verify that the claim is precisely defined.

Procedure:

1. Identify the proposition.
2. Extract its variables and quantifiers.
3. Identify its domain.
4. Identify constraints and boundary conditions.

Pass: The proposition is unambiguous and sufficiently specified for verification.

Fail: The proposition contains unresolved ambiguity affecting its meaning or verification.

TEST-P02 — Assumption Completeness

Objective: Verify that all material assumptions are documented.

Procedure:

1. List explicit assumptions.
2. Identify implicit assumptions.
3. Examine dependencies.
4. Determine whether assumptions are justified or stipulated.

Pass: All assumptions necessary for the derivation are identified.

Fail: A required assumption is missing or incorrectly represented.

TEST-P03 — Logical Validity

Objective: Verify that the conclusion follows from the assumptions.

Procedure:

1. Inspect each inference.
2. Verify mathematical operations.
3. Identify unsupported transitions.
4. Check for circular reasoning.

Pass: Every material inference is justified.

Fail: An invalid inference or unsupported conclusion is identified.

TEST-P04 — Independent Verification

Objective: Verify the result using an appropriate independent method.

Procedure:

1. Select an independent verification approach.
2. Execute the verification.
3. Record results.
4. Compare the outcome with the original claim.

Pass: Independent evidence confirms the claim within the documented verification scope.

Fail: Independent evidence contradicts the claim.

Unresolved: Independent verification is unavailable or inconclusive.

TEST-P05 — Proof Boundary

Objective: Prevent conclusions from exceeding the available proof.

Pass: The documented conclusion does not exceed what the proof establishes.

Fail: A limited result is presented as a stronger or universal conclusion without justification.

4. Explanation Acceptance Tests

TEST-E01 — Mechanism Identification

Verify that the explanation identifies the rules, equations, or mechanisms producing the result.

Pass: The relevant mechanism is explicit and inspectable.

Fail: The explanation merely restates the conclusion.

TEST-E02 — Intermediate Reasoning

Verify that important transformations are explained.

Pass: A reviewer can reconstruct the reasoning from the documented steps.

Fail: Material reasoning steps are omitted.

TEST-E03 — Evidence Consistency

Verify that the explanation is consistent with the available evidence.

Pass: No unresolved material contradiction exists between the explanation and its supporting evidence.

Fail: The explanation contradicts established evidence within the evaluation scope.

TEST-E04 — Explanation Boundaries

Verify that limitations and conditions of applicability are identified.

Pass: Material limitations are documented.

Fail: Known limitations are omitted.

5. Transfer Acceptance Tests

TEST-T01 — Source Definition

Verify that the original problem, assumptions, and validated results are documented.

Pass: The source method and its verified scope are identifiable.

TEST-T02 — Target Definition

Verify that the target problem, constraints, and success criteria are documented.

Pass: The target environment is sufficiently specified.

TEST-T03 — Structural Compatibility

Compare source and target properties.

Evaluate:

* Mathematical structure
* Invariants
* Data assumptions
* Boundary conditions
* Operational constraints
* Failure modes

Pass: All required structural properties are preserved or justified by additional validation.

Fail: A required property is absent and the method is applied without adequate justification.

TEST-T04 — Target Validation

Execute the method against independent target-specific cases.

Pass: Results satisfy the documented target acceptance criteria.

Fail: Results violate a required target criterion.

Unresolved: Target-specific evidence is insufficient.

TEST-T05 — Transfer Limitations

Verify that known transfer limitations are recorded.

Pass: Material limitations and failure conditions are explicit.

Fail: Known limitations are concealed or omitted.

6. Counterexample Tests

TEST-C01 — Counterexample Search

Attempt to identify valid counterexamples to material general claims.

Record:

1. Claim under examination.
2. Test conditions.
3. Counterexample candidate.
4. Verification procedure.
5. Observed result.
6. Counterexample validity.
7. Effect on acceptance status.

Pass: A meaningful search is documented and all discovered candidates are evaluated.

Fail: Required counterexample analysis is omitted.

Passing this test does not establish that no counterexample exists.

TEST-C02 — Falsification Response

Objective: Ensure valid contradictory evidence changes the evaluation outcome.

Pass: A valid counterexample causes the affected universal claim to be rejected or appropriately revised.

Fail: The claim remains accepted despite a valid, applicable counterexample.

7. Evidence Classification

Every evaluated claim must receive one of the following statuses:

* Verified
* Supported
* Hypothesis
* Untested
* Rejected
* Contested

A status must apply to a specific proposition and verification scope.

Verification of one component does not automatically verify related assumptions or conclusions.

8. Acceptance Decision Rules

Each applicable test receives one outcome:

* PASS
* FAIL
* UNRESOLVED
* NOT APPLICABLE

A test marked NOT APPLICABLE must include a justification.

Acceptance conditions

A claim may be accepted for its specified use when:

1. All required tests pass.
2. No unresolved critical contradiction exists.
3. Evidence supports the assigned verification status.
4. Material limitations are documented.
5. Required independent validation is complete.
6. Any claimed transfer passes target-specific validation.

Rejection conditions

Reject a claim when a required logical condition fails or valid evidence disproves the proposition under its stated conditions.

Unresolved conditions

Mark the evaluation unresolved when critical evidence, assumptions, or validation results are missing.

An unresolved result must not be reported as verified.

9. Traceability to the MathOS Reasoning Standard

Reference: docs/reasoning-standard.md

TOPO-406 acceptance testing is intended to operationalize the MathOS reasoning standard.

The following traceability relationships must be checked against the actual reasoning-standard document before being treated as verified mappings.

Acceptance area	TOPO-406 tests	Reasoning-standard alignment
Claim definition	TEST-P01	Precise reasoning inputs
Assumptions	TEST-P02	Explicit premises
Logical validity	TEST-P03	Justified inference
Verification	TEST-P04	Evidence-based validation
Proof boundaries	TEST-P05	Calibrated conclusions
Explanation	TEST-E01–E04	Inspectable reasoning
Transfer	TEST-T01–T05	Context-dependent validity
Falsification	TEST-C01–C02	Error detection and correction
Acceptance	Section 8	Evidence-calibrated decisions

These mappings are provisional until the referenced requirements are inspected and their exact section identifiers recorded.

10. Required Test Record

Every substantial evaluation must produce the following record:

Field	Requirement
Evaluation ID	Unique evaluation identifier
Claim ID	Claim being evaluated
Test ID	Applicable acceptance test
Proposition	Exact evaluated statement
Assumptions	Required preconditions
Procedure	Reproducible test instructions
Expected result	Defined success condition
Observed result	Actual test outcome
Evidence	Supporting artifacts or references
Counterexamples	Relevant challenges and findings
Outcome	PASS, FAIL, UNRESOLVED, or NOT APPLICABLE
Claim status	Evidence classification
Reviewer	Responsible reviewer
Timestamp	Evaluation date and time
Revision	Evaluation revision identifier

11. Example Verification Cases

CASE-001 — Valid Deductive Proof

Claim: The sum of two even integers is even.

Assumptions: Both integers are even.

Derivation:

Let a = 2m and b = 2n, where m and n are integers.

Then:

a + b = 2m + 2n = 2(m + n).

Since m + n is an integer, the sum is even.

Expected: PASS for proposition precision, assumptions, logical validity, and proof boundary.

CASE-002 — Invalid Generalization

Claim: Every prime number is odd.

Counterexample: 2 is prime and even.

Expected: REJECTED.

The valid counterexample disproves the universal proposition.

CASE-003 — Unsupported Transfer

Source: A method validated on one dataset.

Target: A dataset with materially different characteristics.

Condition: No target-specific validation is available.

Expected: UNRESOLVED.

Source success alone does not establish successful transfer.

CASE-004 — Incomplete Explanation

Claim: An algorithm produces a correct result.

Evidence: Selected outputs match expected values.

Missing: An explanation of why the algorithm works generally.

Expected: Explanation acceptance remains unresolved or fails applicable explanation requirements.

Passing examples alone do not establish general correctness.

12. Completion Criteria

This acceptance-testing component is ready for use when:

* All required test definitions are present.
* Test outcomes are reproducible.
* Evidence records are traceable.
* Counterexample handling is documented.
* Transfer validation is independent.
* Acceptance decisions follow explicit rules.
* The relationship to the reasoning standard is documented.
* Provisional traceability mappings are verified before being claimed as authoritative.

13. Core Principle

Define the claim. Examine the assumptions. Verify the reasoning. Explain the mechanism. Search for counterexamples. Validate transfer independently. Accept only what the evidence supports.
