# MathOS Reasoning Standard

## The four dimensions

### 1. Correctness

- Are definitions and assumptions explicit?
- Does each inference follow?
- Are calculations reproducible?
- Have boundary conditions and counterexamples been considered?
- Is independent or formal verification appropriate?

### 2. Explanation

- What is the decisive idea or mechanism?
- Can it be reconstructed without relying on a long opaque answer?
- Which steps are essential, and which are merely presentation?
- Does the explanation distinguish evidence from interpretation?

### 3. Transfer

- Which features of the original problem make the method work?
- Which assumptions must remain true in a new setting?
- What changes would invalidate the method?
- Has the method been tested on a related problem and a counterexample?

### 4. Feedback

- What observable result would support the claim?
- What outcome would count against it?
- Was a baseline recorded?
- Were success criteria set before intervention?
- What will be updated if the prediction fails?

## Formal proof versus real-world validation

A proof assistant can check whether a formal proof follows from encoded definitions and axioms. It cannot, by that fact alone, show that the theorem is relevant to a practical decision or that a real-world model captures reality. Empirical validation requires appropriate data, study design, measurement, and scrutiny of alternative explanations.

## Minimum review checklist

- [ ] Claim is specific and falsifiable where possible
- [ ] Definitions and assumptions are documented
- [ ] Evidence is traceable
- [ ] Reasoning or computation is checkable
- [ ] Uncertainty is described honestly
- [ ] Alternative explanations and counterexamples are considered
- [ ] Transfer boundaries are stated
- [ ] A test and failure criterion are specified
- [ ] Consequential actions have appropriate human oversight
