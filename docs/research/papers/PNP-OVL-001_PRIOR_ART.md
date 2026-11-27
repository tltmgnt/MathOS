# PNP-OVL-001 prior-art gate

Status: preliminary screening, NOT_ESTABLISHED. The broad complexity dichotomy for Boolean CSP is classical. With affine equations of arbitrary arity and constants, adding an implication relation destroys the affine case and is covered by Schaefer-style classification. The direct reduction in this manuscript is a scoped exposition, not evidence of priority. Branching on non-affine relations resembles standard backdoor/parameterized CSP methods. The exact two-block encoding classification and its parameterized bound require targeted searches and comparison to existing gate/CSP/backdoor literature before any originality claim.

References for initial screening:
- T. J. Schaefer, The Complexity of Satisfiability Problems, STOC 1978, pp. 216–226.
- Complexity of Constraint Languages survey: https://www.cs.ox.ac.uk/activities/constraints/publications/ComplexityLanguages.pdf
- Refining Schaefer's theorem: https://people.cs.umass.edu/~immerman/pub/csp05.pdf
- Existing MathOS PNP-B006 and PNP-F004 (affine solver and certificates).

Review questions: Is the exact local classification already published? Is the parameterized bound merely an instance of a known backdoor theorem? Can it be improved or made tight under an explicit hypothesis? Are there stronger results for bounded incidence structure? Until reviewed, classify as scoped technical/formalization artifact, not original research breakthrough.
