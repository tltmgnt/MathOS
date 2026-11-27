# PNP-OVL-001 prior-art gate

Status: preliminary screening, NOT_ESTABLISHED. The broad complexity dichotomy for Boolean CSP is classical. With affine equations of arbitrary arity and constants, adding an implication relation destroys the affine case and is covered by Schaefer-style classification. The direct reduction in this manuscript is a scoped exposition, not evidence of priority. Branching on non-affine relations resembles standard backdoor/parameterized CSP methods. The exact two-block encoding classification and its parameterized bound require targeted searches and comparison to existing gate/CSP/backdoor literature before any originality claim.

References for initial screening:
- T. J. Schaefer, The Complexity of Satisfiability Problems, STOC 1978, pp. 216–226.
- Complexity of Constraint Languages survey: https://www.cs.ox.ac.uk/activities/constraints/publications/ComplexityLanguages.pdf
- Refining Schaefer's theorem: https://people.cs.umass.edu/~immerman/pub/csp05.pdf
- Existing MathOS PNP-B006 and PNP-F004 (affine solver and certificates).

Review questions: Is the exact local classification already published? Is the parameterized bound merely an instance of a known backdoor theorem? Can it be improved or made tight under an explicit hypothesis? Are there stronger results for bounded incidence structure? Until reviewed, classify as scoped technical/formalization artifact, not original research breakthrough.

## Rank-sensitive refinement (Theorem D)
Targeted search found closely related literature on backdoors, reduced search trees, and parity-aware solvers:
- Backdoors to Typical Case Complexity, IJCAI 2003: https://ijcai.org/proceedings/2003/167
- SAT backdoors: Depth beats size, JCSS 2024: https://doi.org/10.1016/j.jcss.2024.103520
- CSP beyond tractable constraint languages: https://link.springer.com/article/10.1007/s10601-023-09362-3
- SAT Solving Using XOR-OR-AND Normal Forms: https://link.springer.com/article/10.1007/s11786-024-00594-x
The rank difference itself is standard rank-nullity. These references do not establish that the exact restricted model's branch count is new. Need full-text comparison to affine backdoors, parity-aware SAT and algorithms that branch on independent linear forms. No novelty promotion.

## Optimal coordinate selection (Theorem E)
A closer prior-art match than generic affine backdoors is submodular vertex cover: the cost of a set of occurrence coordinates is its quotient-matroid rank, a monotone submodular function. See Satoru Iwata and Kiyohito Nagano, Submodular Function Minimization under Covering Constraints (FOCS 2009), and related discussion at https://lsec.cc.ac.cn/~sjom/SJOMInvitedTalks/ProfSIwata.pdf . Also compare Fomin et al., Covering Vectors by Spaces: Regular Matroids (ICALP 2017), https://doi.org/10.4230/LIPIcs.ICALP.2017.56 ; their Space Cover problem requires spanning all target vectors from a disjoint candidate set and is not identical to this pair-hitting formulation. A preliminary search found these connections; full theorem-level comparison remains open. The proof uses classical Vertex Cover hardness and a standard bounded search-tree argument. Do not promote novelty, even if regression and scoped Lean checks pass.

## Generalized linear forms (Theorem F)
Targeted external screening (27 November 2026):
- An inequality for polymatroid functions and its applications, Discrete Applied Mathematics, DOI https://doi.org/10.1016%2FS0166-218X%2802%2900455-9 . Discusses space covering / subspace transversals; compare exact problem definitions, including quotient groups that may contain the zero vector.
- Hitting Subspace Problem, https://cgad.ski/math/hitting_subspace.pdf . Related affine-space hitting objective; source status and exact overlap require further review.
- Fomin et al., Covering Vectors by Spaces: Regular Matroids, https://doi.org/10.4230/LIPIcs.ICALP.2017.56 . Different target-span problem; do not conflate its parameterized complexity with pair/triple hitting.
- SAT Solving Using XOR-OR-AND Normal Forms, https://doi.org/10.1007/s11786-024-00594-x . Existing linear Boolean forms in SAT solving.
- Tradeoffs in the complexity of backdoors to satisfiability, https://www.cs.cornell.edu/gomes/pdf/2014_dilkina_amai_dynamic.pdf . Existing XOR-backdoor considerations.
The exact graph optimum preservation argument and the coordinate-vs-parity exponential pattern gap are concrete candidates for comparison, not a claim of priority. Full-text theorem-by-theorem novelty review is still required.

## Proof-carrying decomposition (Theorem G)
The budget-refutation tree uses standard exhaustive branching and the leaf certificate is classical Gaussian-elimination provenance (see PNP-F004). Compare proof logging for SAT/XOR solvers, proof complexity, and certifying optimization before asserting novelty. The contribution here is a scoped explicit format and separate checker for the chosen local-form model. No new external literature verification is claimed in this cycle.

## Theorem I prior art and scope
Connected-component decomposition is established: Bayardo and Pehoushek, Counting Models Using Connected Components (AAAI 2000), https://cdn.aaai.org/AAAI/2000/AAAI00-024.pdf ; Decomposing SAT Problems into Connected Components (AAAI 2006), https://cs.uwaterloo.ca/~vanbeek/Publications/aaai06.pdf ; AllSATCC (IJCAI 2022), https://ijcai.org/proceedings/2022/259 . External search confirms prior use of component decomposition and caching. Compare exact rank additivity and the order-specific example to existing SAT/CSP work before any originality claim. A connected rank obstruction does not prove a search lower bound. No literature priority is established.
