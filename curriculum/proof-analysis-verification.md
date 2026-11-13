# Proof analysis verification curriculum

Suggested pace: 24 weeks at 8 to 12 hours per week, assuming undergraduate
mathematics and Python experience. This is a learning plan, not a promise to
solve a Millennium Problem or earn a certification score.

| Weeks | Study | Deliverable | Acceptance criterion |
|---|---|---|---|
| 1–4 | Logic, quantifiers, induction and counterexamples | Exact graph and SAT statements | Explicit objects, hypotheses and conclusions |
| 5–8 | Lean foundations, recursive definitions and induction | Small finite-set proofs | Successful kernel replay; no unproved placeholders or added shortcut axioms |
| 9–12 | Polynomial rings, finite products and bijections | SAT monomial-count formalization | Proof for every nonnegative m, including the empty product |
| 13–16 | DAGs, Boolean semantics and antichains | Analyzer correctness proof | Termination, soundness, completeness and inclusion-minimality for the abstract recurrence |
| 17–20 | Trusted computing bases and reproducibility | Pinned proof build and assumption inventory | Another reviewer can reproduce exactly what was checked |
| 21–24 | Specification review and audit | External assessment | Reviewer scope, defects and unresolved assumptions documented |

Keep abstract algorithm correctness distinct from concrete Python verification,
which also requires representation and resource assumptions. A correct analyzer
cannot establish that its input graph faithfully represents a mathematical proof.

## Subject prerequisites for later research

| Problem | Prerequisite path |
|---|---|
| BSD | Abstract algebra, algebraic number theory, elliptic curves, arithmetic geometry |
| Hodge | Topology, differential geometry, algebraic geometry, Hodge theory |
| Navier-Stokes | Real and functional analysis, Sobolev spaces, nonlinear PDE |
| P versus NP | Algorithms, computability, complexity theory, lower-bound barriers |
| Poincare | Algebraic topology, differential geometry, geometric analysis, Ricci flow |
| Riemann | Complex analysis, analytic number theory, spectral theory |
| Yang-Mills | Differential geometry, Lie groups, quantum field theory, constructive field theory |

Prioritize one subject and one sharply scoped lemma. Success means a correctly
stated and checked result, not a smaller count of broad unresolved work packages.
