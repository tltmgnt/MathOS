# F038 — Constructive witness composition and mixed-block coverage barrier

PNP_RESOLUTION_STATUS = OPEN. Mathematical derivations and finite regression, not a Lean declaration.
Verified base 479701e34de2c4f14cb5b84469d5bf425157c9fe: https://github.com/tltmgnt/MathOS/actions/runs/45701383482 (success).

## Positive theorem: pairwise seed witnesses suffice under majority closure

Let R(x,y) be a relation over m>=1 Boolean parameter bits x and q witness bits y. Assume its full satisfying assignments are closed under coordinatewise ternary majority Maj. In particular, every 2-CNF relation has this property: if majority falsifies a binary clause, at least two of the three input assignments falsify each literal, so one input falsifies both. Unit and empty clauses obey the same closure. Conjunction and existential projection preserve majority closure.

For m>=2, for each pair i<j and each bit pattern (a,b), obtain one full satisfying assignment w(i,j,a,b) with those parameter bits, if possible. For m=1 obtain both single-bit witnesses. If any seed is missing, the projection onto x is not total. Otherwise the following explicit composition proves totality and constructs a witness for any x. Denote the selected seed w(i,j,x_i,x_j) by w(i,j). With zero-based indexing, initialize U(0,j)=w(0,j) for j>0; it agrees with x on parameter 0 and j. For t=1,...,m-2 and j>t, set
U(t,j)=Maj(U(t-1,t), U(t-1,j), w(t,j)).
Both first inputs agree on parameters 0,...,t-1. The first and third agree on t; the second and third agree on j. Closure gives a full satisfying assignment agreeing on 0,...,t and j. Induction gives U(m-2,m-1) matching every parameter. For m=2 this is the original seed, and for m=1 the single-bit seed suffices.

Thus totality is equivalent to existence of the 4*binom(m,2) pair seeds (or two unary seeds). The composition uses (m-1)(m-2)/2 vector majority operations; a circuit selects each seed from its four precomputed constants and applies bitwise majority, using O((m+q)m^2) Boolean gates, with O((m+q)m^2) bits of seed storage. This constructs a Skolem circuit, not merely a decision certificate. It generalizes to majority-closed relations given seed witnesses; closure alone does not guarantee an efficient method to find them.

For explicit 2-CNF, find each seed by polynomial-time 2-SAT on the pinned formula, extracting a model by successive feasible pins or SCC assignment. Hence totality and synthesis of a repair circuit are uniform polynomial time. For the preceding guarded-selector family built from R, the synthesized model of R and deterministic clause-splitting extensions produce a branch-zero witness for every parameter assignment when the projection is total. For conjunctions of any number of explicit 2-CNF blocks, use the combined formula when finding seeds: shared witness variables are thereby reconciled. The theorem does not assert that separate local totality implies joint totality. For example y=x and y=not x are both total individually and their conjunction is never satisfiable.

## Mixed-block barrier: local constructive totality does not compose universally

Consider any quantified width-at-most-three CNF forall x exists y R(x,y), with nonempty clauses (empty clauses can be replaced by two contradictory fresh existential units). Introduce an existential copy c_i for each universal variable x_i. Replace x_i by c_i throughout the matrix, and add one separate equality block (not x_i OR c_i) AND (x_i OR not c_i). Make each original copied clause a separate block. All copied clauses now involve existential variables only, and each nonempty clause is Horn or dual Horn since its width is at most three. Equality blocks are both Horn and dual Horn.

Each block is total over x and has an explicit trivial witness circuit over the common declared witness universe: a clause sets one of its literals true and all other witness bits zero (subject to that literal's sign), while an equality sets c_i=x_i and other witness bits zero. A joint witness must satisfy all equalities and hence projects exactly onto a satisfying y of R(x,y); conversely any such y extends by c=x. The construction is polynomial time, with one block per clause plus one per universal bit.

Consequently deciding joint totality of individually total Horn/dual-Horn blocks with supplied correct local witness circuits is Pi_2^P-complete (membership by forall x exists joint witness; hardness by the reduction). One can view this as a promised input problem; the unrestricted language checking both local circuit validity and joint totality also lies in Pi_2^P and the same reduction proves hardness. This is an obstruction to a generic polynomial-time decision or total repair-composition method unless the relevant complexity classes collapse. It does not forbid efficient composition under a common tractable constraint language or additional compatibility hypotheses. It does not assert that conjunction of Horn clauses alone is hard.

If a total uniform polynomial-time synthesizer outputs a correct joint witness circuit whenever a joint total relation exists in this mixed-block domain, then P=NP: reduce ordinary 3-SAT with no universal bits (or one unused bit), run the synthesizer and verify its candidate assignment. False instances cannot yield a verified model. The converse P=NP would suffice for polynomial-time joint totality decision, but does not by itself furnish a polynomial-time procedure outputting a universally correct polynomial-size Skolem circuit; do not infer this converse for synthesis.

## Finite audit

Positive: all 4096 subsets of a fixed 12-row 2-CNF family on five variables, with one through four parameter bits. Compare pinned 2-SAT seed probes to direct model enumeration and compare the resulting totality decision with the full projection. Verify every intermediate majority witness and all synthesized outputs on total families. Expected: 16384 families, 2484 total, 13900 non-total, 172032 seed probes, 91328 missing, 6686 outputs and 1592 vector majority operations.

Negative: all 4096 subsets of the prior mixed three-variable matrix, with one or two parameter bits. Verify each explicit local repair, the Horn/dual-Horn classification, and the joined relation on every original assignment and copy assignment. Expected: 8192 families, 356 total, 7836 non-total, 24576 parameter cases, 188416 local witness checks and 196608 global equivalence checks.

The finite controls do not prove the asymptotic results. Next target: a checkable structural compatibility condition for mixed constraint languages, with explicit cost and a coverage theorem, or a genuine universal SAT construction. No unrestricted polynomial-time algorithm, class separation or Lean declaration is claimed.
