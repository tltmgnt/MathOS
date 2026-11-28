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

## Theorem J scope and prior art
Canonical RREF, orthogonal decomposition of linear spaces and connected components are classical. Compare with direct-sum decompositions of linear codes/matroids and parity-aware SAT preprocessing. The exact block-group formulation and proof-carrying integration are candidates for comparison only; no new external literature search or novelty determination was performed in this cycle.

## Theorem K targeted screening
- Dechter and van Beek, Local and global relational consistency, Theoretical Computer Science 173 (1997), https://doi.org/10.1016/S0304-3975(97)86737-0 .
- Hooker, Projection, Inference, and Consistency, IJCAI 2016, https://ijcai.org/proceedings/2016/625 .
- Jeavons and Petke, Local Consistency and SAT-Solvers, https://arxiv.org/abs/1401.4613 .
- Local consistency as a reduction between constraint satisfaction problems, https://arxiv.org/abs/2301.05084 .
- SAT Solving Using XOR-OR-AND Normal Forms, https://doi.org/10.1007/s11786-024-00594-x .
These sources establish related local consistency, projection, and affine-solving research. The strict hierarchy is for the specified affine-hull operator only; the witness family is classical easy 2-SAT. No exhaustive novelty investigation or priority claim.

## Theorem L scope
The monotonicity and greatest-fixed-point argument is standard finite-lattice reasoning; affine hulls and nullspace bases are standard linear algebra. Compare the variable-order threshold complexity to local-consistency rank/width decision problems and proof-system complexity. The coNP-hardness at full order is a direct consequence of B, not a new general SAT lower bound. The exact unrestricted threshold complexity remains unresolved here. No new external literature search or priority claim in this cycle.

## Theorem M scope
The implication-graph criterion is classical 2-SAT (Aspvall, Plass and Tarjan, A linear-time algorithm for testing the truth of certain quantified Boolean formulas, Information Processing Letters 1979). Girth and bounded-treewidth examples use elementary graph theory; no new external literature search was performed in this cycle. Compare the proposed bounds on the exact affine-hull closure threshold with existing consistency-width and proof-complexity work. The constant-treewidth example is limited to the original-variable graph of this encoding and does not imply hardness of bounded-treewidth CSPs.

## Theorem N scope
The block-support distance is the usual dual-distance/projection-surjectivity connection from coding theory, generalized to grouped coordinates. Projective directions, finite-field hyperplane pencils, and deletion-minimal inconsistent cores are classical. Compare the exact recovery-order-four example and closure-specific certificate format against existing algebraic SAT and consistency-width research before any priority claim. No new external literature search was performed in this cycle.

## Theorem O scope and prior art
The probabilistic distance proof uses the classical Gilbert–Varshamov random linear code technique. See Guruswami, coding theory lecture notes on the Gilbert–Varshamov bound, https://www.cs.cmu.edu/~venkatg/teaching/codingtheory/notes/notes2.pdf ; Guruswami's coding bounds tutorial, https://people.csail.mit.edu/madhu/papers/2001/focs01-tut.pdf . Recent related explicit code constructions are discussed in Linear Time Encodable Binary Code Achieving GV Bound with Linear Time Encodable Dual Achieving GV Bound, https://drops.dagstuhl.de/storage/00lipics/lipics-vol362-itcs2026/html/LIPIcs.ITCS.2026.28/LIPIcs.ITCS.2026.28.html . These are related distance techniques, not evidence that this particular recovery-order application is original. A targeted search found classical tools; no exhaustive novelty review or priority claim. Compare with locally consistent unsatisfiable CSPs, random affine codes, and proof-width lower bounds.

## Theorem P targeted prior-art screen
Classical greedy column construction: https://www.terpconnect.umd.edu/~abarg/626/626-PartIII.pdf ; https://www.numdam.org/item/AST_1999__258__327_0.pdf . Greedy averaging and conditional probabilities for coverage: https://www.cs.ucr.edu/~neal/publication/Khuller18Greedy.pdf . These references support the underlying techniques, not the novelty of their combination in this recovery model. The deterministic algorithm remains exponential; do not describe it as an efficiently explicit asymptotically good code. No exhaustive originality review or independent reviewer contact in this cycle.

## Theorem Q targeted prior art
Guruswami's appendix to Shpilka, Constructions of low-degree and error-correcting epsilon-biased generators, Theorem 24 and Lemmas 25–26, printed pp. 25–26, https://www.cs.tau.ac.il/~shpilka/publications/Shpilka_e_bias.pdf explicitly provides polynomial-time constructible good codes with good duals. The binary expansion bounds justify the imported supplier; it is not MathOS's implementation. Classical RM distance and duality are described in https://people.csail.mit.edu/dmoshkov/courses/codes/lec5-venkat.pdf and https://doi.org/10.1016/j.jffa.2015.07.003 . The shortening construction is closely related to CSS quantum code methods; compare directly with CSS and polynomial-calculus literature before claiming originality. No exhaustive novelty determination or external reviewer contact.

## Theorem R prior art
Bounded-degree Nullstellensatz is a classical static algebraic proof system, distinct from dynamic polynomial calculus. See https://eccc.weizmann.ac.il/report/2017/154/download/ (section 2.1, degree-bounded linear systems); https://mathweb.ucsd.edu/~sbuss/ResearchWeb/nullstellensatz/token.pdf ; and https://doi.org/10.1007/s10703-022-00391-x for algebraic proof checkers. The implementation uses a stated Boolean-quotient degree convention; compare with these definitions before transferring any lower bound. The finite six-implication separation and recovery-order comparison are scoped examples, not an originality claim. No independent reviewer contacted.
