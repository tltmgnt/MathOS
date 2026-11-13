TOPO-406 — Proof, Explanation, and Transfer Methodology

1. Purpose

TOPO-406 establishes the MathOS standard for determining whether a claim is logically justified, whether its mechanism is explainable, and whether its method transfers reliably to new problems.

The standard separates three distinct properties:

* Proof: Does the conclusion follow from the stated assumptions?
* Explanation: Why does the method produce the stated result?
* Transfer: Under what conditions does the method remain valid in a different context?

Success in one dimension does not establish success in the others.

2. Formal Model

Represent a candidate solution as:

[
M=(P,A,D,R,C,V,T)
]

Where:

* (P): problem statement and proposition.
* (A): assumptions and preconditions.
* (D): definitions and relevant data.
* (R): reasoning procedure or derivation.
* (C): conclusion.
* (V): verification evidence and results.
* (T): transfer conditions and known limitations.

A candidate is eligible for acceptance only when its claims are traceable to the relevant assumptions, reasoning, and verification evidence.

3. Proof Methodology

3.1 Define the proposition

State the claim precisely. Identify its domain, quantifiers, variables, constraints, and boundary conditions.

3.2 Identify assumptions

List the assumptions required for the proposition. Distinguish established facts, stipulated conditions, approximations, and unresolved hypotheses.

3.3 Construct the derivation

Present the inference sequence connecting the assumptions to the conclusion. Each material step must have a valid justification.

3.4 Verify the result

Use appropriate methods, including:

* Formal mathematical proof.
* Symbolic or numerical verification.
* Independent calculation.
* Property-based testing.
* Boundary and edge-case analysis.
* Counterexample search.
* Machine-checked proof when appropriate.

The verification method must match the strength and type of the claim.

3.5 State the proof boundary

Specify exactly what has been established. Passing finite test cases does not establish a universal theorem. A proof conditional on assumptions does not independently prove those assumptions.

4. Explanation Methodology

A valid explanation makes the mechanism of a result inspectable.

Every substantial explanation should identify:

1. The input and initial conditions.
2. The governing rules, equations, or mechanisms.
3. The intermediate transformations.
4. The reason each important step is justified.
5. The relationship between the mechanism and the conclusion.
6. The conditions under which the explanation ceases to apply.

Explanations should distinguish causal mechanisms from correlations, empirical associations, and predictive relationships.

An intuitive explanation may supplement a formal derivation but must not replace a required proof.

5. Transfer Methodology

Transfer evaluates whether a method remains valid when applied to a new problem, dataset, domain, or operating environment.

5.1 Characterize the source problem

Document the original assumptions, inputs, constraints, objective, and verified results.

5.2 Characterize the target problem

Document the target domain, differences in inputs, operating conditions, constraints, and success criteria.

5.3 Compare structural properties

Identify which properties are preserved, modified, or absent.

Examples include:

* Mathematical structure.
* Invariants.
* Causal relationships.
* Data distributions.
* Operational constraints.
* Boundary conditions.
* Required resources.
* Failure modes.

5.4 Test transfer conditions

Determine whether the assumptions supporting the original method also hold in the target setting. Test the method using independent examples and relevant stress cases.

5.5 Document transfer limitations

State where the method applies, where additional validation is required, and where known counterexamples or structural differences invalidate transfer.

Similarity between two problems is not sufficient evidence that a method transfers.

6. Counterexamples and Falsification

For every material general claim, identify meaningful ways the claim could fail.

Record:

* The proposition under examination.
* The assumptions required.
* The attempted counterexample.
* The test or derivation performed.
* The observed result.
* Whether the counterexample is valid.
* The resulting change in confidence or acceptance status.

A valid counterexample disproves a universal claim under its stated conditions. An invalid counterexample may reveal a misunderstanding, an unmet precondition, or an incorrectly specified proposition.

Failure to find a counterexample is not, by itself, proof of correctness.

7. Evidence and Verification Status

Use the following statuses:

* Verified: The stated claim passed its documented verification procedure within the procedure’s scope.
* Supported: Relevant evidence supports the claim, but important uncertainty remains.
* Hypothesis: The claim is proposed and awaits meaningful testing.
* Untested: Required verification has not been performed.
* Rejected: Valid evidence or reasoning contradicts the claim under its stated conditions.
* Contested: Material contradictory evidence remains unresolved.

Every status must identify the specific claim it describes. A verified calculation does not automatically verify the model, assumptions, or real-world interpretation that use it.

8. Transfer Acceptance Criteria

A transferred method must satisfy all applicable criteria:

1. The target problem is explicitly defined.
2. Source and target assumptions are compared.
3. Required structural properties are identified.
4. Preconditions are checked.
5. Relevant edge cases and counterexamples are tested.
6. Target-specific evidence is documented.
7. Known limitations and failure conditions are stated.
8. The verification status matches the evidence obtained.

If a critical condition is unknown, classify the transfer as unresolved rather than verified.

9. Multi-Agent Review

Independent review may improve coverage when reviewers use meaningfully different methods, assumptions, or evidence sources.

Reviewers should examine:

* Logical validity.
* Calculation accuracy.
* Alternative derivations.
* Counterexamples.
* Assumption sensitivity.
* Transfer limitations.
* Evidence independence.

Agreement among agents that share the same model, data, or assumptions is not independent confirmation. Resolve disagreements through evidence quality and reproducible tests, not majority vote alone.

10. Required Verification Record

Every substantial TOPO-406 evaluation should produce a record containing:

Field	Requirement
Claim ID	Unique identifier for the claim
Proposition	Exact statement being evaluated
Assumptions	Explicit preconditions and constraints
Derivation	Reasoning or proof supporting the result
Explanation	Mechanism connecting inputs to the conclusion
Verification method	Tests, proof method, or evidence procedure
Results	Observed verification outcomes
Counterexamples	Relevant challenges and their disposition
Transfer conditions	Preconditions for use in another context
Limitations	Known uncertainties and failure regimes
Status	Verified, Supported, Hypothesis, Untested, Rejected, or Contested
Reviewer	Responsible reviewer or verification process
Revision history	Changes resulting from new evidence

11. Acceptance Rule

A result is eligible for its intended use only when:

* The claim is precisely defined.
* Its assumptions and derivation are inspectable.
* Its explanation is consistent with the evidence.
* Its verification procedure is documented.
* Its limitations and failure conditions are explicit.
* Any claimed transfer is supported by target-specific validation.
* Its status does not exceed the strength of the evidence.

High-impact decisions may require additional domain-specific review, authorization, and risk controls.

12. Core Principle

Prove what follows from the assumptions. Explain the mechanism. Test the boundaries. Validate transfer independently. Revise the conclusion when the evidence requires it.
