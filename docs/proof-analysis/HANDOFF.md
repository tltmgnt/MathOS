# Professional Mathematical Review

Proof dependency prototype and adversarial tests

Version 3 repository integration  |  8 November 2026

## Review request

Please review two bounded contributions: the correctness specification of a finite dependency analyzer, and the validity and scope of seven fixed adversarial witnesses. The requested outcome is a corrected specification, documented defects and one feasible formalization target. A subject specialist may additionally review one Millennium-related agenda entry.

This package presents research-support software and elementary examples. It claims no new Millennium solution, no established research novelty and no formal proof-assistant certification. The seven broad problem maps are agendas, not complete proof attempts. No external mathematical review has yet been performed.

## Recommended first assignment

Start with the analyzer theorem on page 2. It is the most sharply defined verification target. The SAT monomial-count proposition on page 4 is a smaller alternative. Neither proposition is claimed to be novel. Assess novelty separately from validity and formal verification.

| Evidence | Recorded result | Interpretation |
| --- | --- | --- |
| Unit and regression tests | 46 passed; no failures, errors or skips | Tests of implementation behavior, not universal proofs |
| Separate Boolean checker | 1,000 generated graphs; 19,814 assignments | A local cross-check using seed 173, not an external audit |
| Seven original models | 32 additional assignments checked | All attempted routes retain unresolved work packages |
| Adversarial suite | Seven explicit witnesses | Each conclusion is limited to its stated shortcut |

### How to use the package

Read this brief first. Use the review response template in docs/proof-analysis to record findings. The repository contains code, reports, test output and reproduction instructions. The current software uses only the Python standard library. The generated manifest identifies source and report bytes; it does not certify correctness or authenticity.

## Finite dependency semantics and proof target

Let G be a finite directed acyclic graph with target t. Each node is either an open leaf, an externally accepted leaf, or a derived claim. A derived node has a nonempty collection of nonempty routes. Every route lists sufficient dependencies. Edges point from a claim to its dependencies.

For a subset S of the open leaves, define V(v,S) recursively. An open leaf is true exactly when it belongs to S. An external leaf is true by assumption. A derived claim is true when at least one route has every dependency true. Thus routes combine by OR and dependencies within a route by AND.

### Exact output definition

A completion set S satisfies V(t,S) = true. It is inclusion-minimal when no proper subset is a completion set. The output is the family of all such inclusion-minimal sets, together with their intersection. An empty completion set represents closure under externally accepted assumptions. It is not a mathematical proof certificate.

### Proposed theorem for review

For every valid finite acyclic G and target t, the abstract recurrence implemented by the analyzer returns exactly the inclusion-minimal completion sets under V. The proposed proof obligations are termination, soundness, completeness and minimality. In particular, deduplicating shared dependencies and deleting strict supersets must preserve all minimal alternatives.

This is a specification to prove, not a proved theorem. A mathematical proof of the recurrence must be distinguished from verification of the concrete Python implementation. The latter also requires input representation invariants and resource assumptions; recursive depth and potentially exponential output size prevent an unconditional execution guarantee on every finite input.

### Implementation and cross check

mathos/proof_analysis/gap_analysis.py builds completion candidates recursively using unions for AND routes, combines alternatives for OR routes, then removes duplicates and strict supersets. The certification audit module instead topologically evaluates the Boolean graph on every open-leaf assignment and compares its truth function with the reported completion sets. Its exhaustive check is capped at 16 open leaves.

Cycles, missing dependencies and invalid state/route combinations are rejected. Tests deliberately supply incorrect certificates, omitted alternatives, nonminimal sets and false empty certificates. The second implementation provides corroborating finite evidence; it is not independently developed or externally audited.

### Boundary requiring specialist review

Claim statements are opaque text. The program cannot establish that a route is a valid mathematical implication or that external claims are true. Generic background nodes in the seven problem maps must be replaced by exact statements, hypotheses and references before those maps can support substantive inference.

## Field scaling and zero location witnesses

### NS1  A topology only vorticity bound

Tested shortcut: fixed helicity and vortex-line topology alone give a finite upper bound on vorticity magnitude over all smooth rapidly decaying divergence-free initial velocity fields in three dimensions.

g = exp(-(x^2+y^2+z^2));  u = (2y,-2x,0)g

curl(u) = (-4xz,-4yz,4x^2+4y^2-4)g

Exact polynomial differentiation verifies divergence(u) = 0 and u dot curl(u) = 0 pointwise. Therefore the helicity integral is zero. At the origin the vorticity is (0,0,-4). All fields are smooth and rapidly decaying.

u_lambda(x) = lambda u(lambda x),  lambda > 0

The vorticity at the origin has magnitude 4 lambda squared. Positive dilation maps vortex lines to corresponding vortex lines, preserving their topology, while helicity stays zero. The displayed family therefore defeats any finite bound depending only on those fixed quantities. The code checks the exact derivatives and selected scale values; the general scaling argument is supplied here informally.

Scope: these are initial fields, not a demonstrated singular fluid evolution. The finding does not reject bounds involving additional quantitative geometry. Nor does it review any published or announced Navier–Stokes proof. Terms such as “vortex topology” require a precise definition in any proposed theorem.

### RH1  Symmetry and positivity are insufficient

f(t) = t^4 + 1;  z = (1+i)/sqrt(2)

The entire function f is even, has real coefficients and is strictly positive on the real axis. Nevertheless, z squared equals i and z to the fourth power equals −1, so f(z) = 0 and z is nonreal. The code verifies the rational complex arithmetic for z squared and z to the fourth power; the displayed expression identifies the root.

Scope: this refutes the general inference from those properties to all-real zeros. It says nothing adverse about the actual zeros of the zeta or xi functions. A successful spectral route needs an independently defined operator and a rigorous correspondence with every relevant zero, rather than symmetry alone.

### Review decisions requested

Confirm each exact calculation and the quantifiers of the shortcut being rejected. Identify any missing analytic hypotheses. Distinguish the computed finite witnesses from the general informal arguments, and identify what should be formalized if these examples are retained as regression certificates.

## Polynomial expansion and group witnesses

### SAT1  Explicit expansion size

Proposition: for every integer m at least zero, in the polynomial ring over the integers in distinct variables x_1,y_1,...,x_m,y_m, the following polynomial has exactly 3^m nonzero monomials.

P_m = PRODUCT_(i=1..m) (x_i + y_i - x_i*y_i)

Proof: a term choice from factor i produces exponent pattern (1,0), (0,1) or (1,1) on its variable pair. Different sequences of choices produce different monomials, because the variable pairs are disjoint. Every coefficient is 1 or −1 and there is no cancellation. There are 3^m choices. For m = 0 the empty product is 1, with one monomial.

The implementation expands using exact integer coefficients through m = 8 and separately checks all 64 Boolean assignments for three clauses. Expansion is capped at m = 10 for resource control. The universal claim is supported by the informal argument, not by extrapolating the finite checks.

Consequence: explicit expansion of this satisfaction indicator can be exponential even for a simple formula. This refutes a polynomial-size bound for that representation step. It does not prove a lower bound for arbitrary SAT algorithms, exclude compressed representations or resolve P versus NP.

### PG1  Abelianization is a weaker invariant

Tested shortcut: a group with trivial abelianization must be trivial. The witness is A5, the group of even permutations on five elements. The program enumerates its 60 elements, computes commutators and closes the subgroup they generate. The commutator subgroup has 60 elements, so the abelianization is trivial although A5 is nontrivial.

For a path-connected space, first integral homology identifies the abelianization of its fundamental group. Thus vanishing first homology is generally weaker than simple connectivity. This exact finite-group calculation does not construct a closed three-manifold and does not challenge the established Poincaré theorem.

### Formalization options

For SAT1, construct a bijection between three-way selection sequences and monomial support, and verify nonvanishing coefficients. For PG1, supply a checked finite-group certificate or use a properly cited theorem that A5 is perfect. In either case, record the exact statement, proof dependencies and axiom inventory. No formal replay is included in this release.

## Abstract countermodels and research boundaries

The next three witnesses expose missing implications in deliberately weak abstractions. They do not satisfy the full arithmetic or geometric hypotheses of the corresponding Millennium Problems. Their role is diagnostic; they must not be advertised as counterexamples to those problems.

### BSD1  Duality does not fix dimension

Nondegenerate alternating forms exist on rational vector spaces of every positive even dimension, by taking block diagonal copies of the matrix with rows (0,1) and (−1,0). Exact elimination checks ranks 2, 4 and 8. Hence existence of such a pairing alone does not determine a dimension. These examples are not Selmer groups and do not evaluate the complex L-function. An actual BSD comparison requires additional arithmetic theorems.

### HD1  A type label does not force surjectivity

The rational map q maps to (q,0) has a one-dimensional image in a two-dimensional rational space. Merely assigning a formal type label to the ambient space does not put (0,1) in that image. Exact rank computation checks this. The example is not the cycle map of a smooth projective variety; actual geometry is precisely the missing input.

### YM1  Positivity need not survive a limit

Let lattice spacing a_n = 1/n and dimensionless gap mu_n = 1/n squared. Each mu_n is positive, but the physical gap mu_n/a_n = 1/n tends to zero. Exact rational calculations reproduce selected values. This is an abstract sequence, not a construction of Yang–Mills theory. A positive continuum gap requires a uniform physical estimate along a valid nontrivial continuum limit.

### Outstanding agenda for subject review

| Problem | Substantive obligation remaining |
| --- | --- |
| BSD | Exact analytic/arithmetic comparisons, control of Sha and leading-term identity |
| Hodge | Construct actual rational algebraic cycle representatives with full coverage |
| Navier Stokes | Close a quantitative global regularity estimate for the selected unforced route |
| P versus NP | Give a correct algorithm with a polynomial total bit-complexity proof, or pursue a separately justified lower-bound route |
| Poincare | Review or formalize a component of the established proof |
| Riemann | Construct and justify a noncircular spectral or geometric realization |
| Yang Mills | Construct the required continuum theory and prove a positive physical gap |

## Reviewer workflow and reproducibility

### Requested review sequence

First, review the exact finite-graph specification and one concrete witness. Record validity, scope and defects before assessing novelty. Second, a subject specialist may select one agenda entry, replace background placeholders with precise sourced theorems and identify a smaller nontrivial target. Review of all seven areas is not requested from one person.

For each finding, record the claim ID, exact statement reviewed, added assumptions, proof or counterexample, cited source and verdict. Suggested verdicts are valid as stated, valid with changes, unsupported, incorrect, or outside scope. A verdict is not formal certification unless its proof artifact has actually been checked.

### Reproduce the recorded results

From the MathOS repository root, using Python 3.10 or newer, run:

python -m mathos.proof_analysis --run-tests

Expected current result: 46 proof-analysis tests pass; all seven original attempted routes remain blocked; seven narrowly scoped shortcut findings are produced. The run regenerates reports and content hashes. Test elapsed times vary. There is no network requirement or external runtime dependency beyond Python for this package.

| File or directory | Purpose |
| --- | --- |
| docs/proof-analysis/README.md | Entry point and limitations |
| mathos/proof_analysis | Single reproduction command |
| Generated adversarial results | Claim statements, witnesses, limits and route links |
| Generated test record and log | Recorded test results |
| Generated certification audit | Boolean checks and unmet certification gates |
| Review response template | Structured reviewer response form |
| Generated SHA256SUMS.json | Content hashes for source and report files |

### Sources and provenance

The prototype was developed with AI assistance and integrated into MathOS. The adversarial examples were selected in advance; the implementation is not autonomous mathematical discovery. It is implemented in MathOS and inspired by ResearchOS. No external reviewer endorsement, institutional affiliation or novelty claim is asserted.

ResearchOS controller: https://github.com/tltmgnt/ResearchOs/blob/main/core.py

ResearchOS specification: https://github.com/tltmgnt/ResearchOs/blob/main/TECT_SPEC.md

MathOS architecture: https://github.com/tltmgnt/MathOS/blob/main/architecture.md

Official problem descriptions: https://www.claymath.org/millennium-problems/
