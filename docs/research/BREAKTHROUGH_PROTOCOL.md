# MathOS Millennium Breakthrough Research Protocol

**Version 1.0 | 24 November 2026 | Research strategy, not a proof or novelty claim**

## 1. Mandate and starting position

The project must now target the mathematical barriers that prevent a full solution, rather than optimize test counts or produce another fixed batch of seven papers. The canonical MathOS register has 14 open work packages across seven tracks; these are author-proposed routes, not proven sufficient decompositions. Poincare is externally solved and its work is reconstruction. Prior bounded papers and their DOCX libraries remain regression evidence, not universal proofs.

## 2. Focus and decision cycle

Run at most two active tracks per cycle: primary NS.critical_bound (periodic unforced route NS.B), challenger RH.zero_identity (spectral route RH.spectral, with RH.operator as a prerequisite). The choice reflects precise exposed gaps, not estimated odds of a prize. Queue all other work packages and rotate only after a written review. Before any attempt, audit the official target and literature, including Clay's 11 September 2026 Navier-Stokes announcement, which describes an apparent solution; do not equate it with acceptance or mix forced and unforced alternatives.

For each attempt: (1) freeze one exact quantified candidate theorem, hypotheses, definitions and target claim ID; (2) write the implication to the registered obligation, with every unproved prerequisite marked; (3) derive the argument from primary sources or first principles; (4) challenge the strongest inference using known barriers, scaling, counterexamples and alternative derivations; (5) replay executable checks and formalize the exact lemma where feasible; (6) obtain independent mathematical review and record the actual verdict. A counterexample kills the candidate, not the conjecture unless it satisfies the official target. After three unsuccessful attempts on the same gap, document the obstruction and decide whether to revise, pivot or pause; no automatic promotion or forced publication.

## 3. Seven breakthrough targets

### RH | RH.spectral

Registered obligations: RH.operator; RH.zero_identity.

First attack: Define an operator from arithmetic data without using zeta zero locations; prove a domain/self-adjointness lemma and derive a complete determinant identity for the completed xi function.

Falsification: Check deficiency indices, compactness/trace class or regularized determinant hypotheses, zero multiplicities and possible extra zeros. Use Lagarias/Li/Weil as a comparator; reject an assumed RH or a finite spectrum extrapolation.

Exit criterion: An unconditional operator construction plus identity and a logically checked implication for every nontrivial zero.

### PNP | PNP.equality

Registered obligations: PNP.sat_correctness; PNP.sat_runtime.

First attack: Specify a deterministic SAT state representation and update rules, with an explicit invariant guaranteeing exact satisfiability preservation; derive a polynomial total encoding-size and bit-operation bound for arbitrary CNF.

Falsification: Attack adversarial width-three Tseitin, pigeonhole and compression instances; track expansion, bit growth, branching and uniformity. Audit relativization, natural proofs (where applicable), and algebrization. Restricted lower bounds do not settle separation.

Exit criterion: Correctness and polynomial worst-case bit complexity on all encoded SAT inputs, or a separate registered unconditional separation argument.

### NS | NS.B

Registered obligations: NS.critical_bound.

First attack: On the periodic unforced route, derive a scale-critical estimate for the actual nonlinear vorticity/velocity interaction that controls the L4_t L6_x norm up to every finite potential breakdown time for arbitrary admissible data.

Falsification: Test scaling, concentration, high-low interactions and vortex stretching; reject energy-only control, constants depending on the unknown critical norm, or bounds stopping before the possible breakdown. Independently audit any announced forced-breakdown route under its own official hypotheses.

Exit criterion: An a priori estimate under the full periodic hypotheses and a justified continuation implication, or a distinct complete official breakdown alternative.

### YM | YM.continuum_mass

Registered obligations: YM.continuum; YM.axioms; YM.uniform_gap.

First attack: Choose a specified four-dimensional non-Abelian lattice gauge action, initially SU(2), and seek a physical-unit correlation bound with constants uniform in volume and spacing along a justified renormalization trajectory; separately develop a nontrivial continuum limit and reconstruction.

Falsification: Check gauge invariance, reflection positivity, regulator removal, observable overlap, tightness and nontriviality. Reject a lattice-unit gap or two-state model as physical mass-gap evidence.

Exit criterion: A nontrivial continuum theory satisfying required axioms and positive physical spectral gap for every required compact simple gauge group; SU(2) alone is a scoped milestone.

### HODGE | HODGE.cycles

Registered obligations: HODGE.primitive_cycles; HODGE.reduction.

First attack: Pick a precise smooth projective family beyond divisor-generated cohomology; compute the rational Hodge subspace and isolate a primitive class not accounted for by known cycle generators; attempt an actual algebraic correspondence or cycle construction.

Falsification: Audit rationality, Hodge type, smooth projectivity, cycle-class map and primitive reduction. Distinguish a gap in a chosen generator span from a nonalgebraic class.

Exit criterion: Proved algebraic representatives for the remaining rational Hodge classes and a valid reduction covering all varieties/codimensions, or a valid counterexample.

### BSD | BSD.rank_refined

Registered obligations: BSD.analytic_selmer; BSD.sha_finiteness; BSD.leading_term.

First attack: Choose a rank-at-least-two family over Q with rigorously sourced analytic order and descent/Selmer data; isolate the exact missing comparison map or bound and attempt a theorem beyond known rank-zero/one cases.

Falsification: Audit analytic-order certificates, Mordell-Weil rank versus Selmer rank, local conditions, Sha finiteness, regulator, periods and Tamagawa factors. Do not use BSD to compute the evidence intended to prove BSD.

Exit criterion: Universal analytic/algebraic rank equality; for the refined route also Sha finiteness and normalized leading-term identity.

### POINCARE | POINCARE.replay

Registered obligations: POINCARE.reconstruction.

First attack: Reconstruct the externally established proof one theorem at a time, starting with coherent transport of the nontrivial sweepout class and the precise surgery comparison-map hypotheses.

Falsification: Check original Perelman and Kleiner-Lott/Colding-Minicozzi statements, local finiteness of surgeries, class transport, extinction and topological classification. A scalar inequality is not geometric reconstruction.

Exit criterion: Complete independently reviewed proof-dependency chain. Already solved externally; not a new prize target.

## 4. Evidence and publication gates

Record a candidate packet with exact statement, hypotheses, source locators, proof or explicit gap, implication to the registered claim, adversarial findings, formal status, novelty status and reviewer evidence. A proof candidate, a rigorous scoped theorem, a counterexample to a method and a complete solution are distinct outcomes. Finite experiments support or falsify a stated claim only within their scope. The automated intake gate checks metadata and coverage, never mathematical truth or external identity.

For a genuine new verified milestone, publish a standalone numbered Markdown paper and editable DOCX, with evidence, assumptions, proof, limitations, prior-art review status and next obligation. Retain negative results and revisions; do not promote novelty from project novelty or publish a placeholder as a breakthrough. A global solution claim requires a complete unconditional mathematical argument, validated route-to-target implication, independent specialist review and no unresolved proof dependencies. Clay consideration additionally requires qualifying publication, at least two years, and general mathematical acceptance. No automatic modification of canonical proof status is permitted.

## 5. First-cycle deliverables and execution

Primary: a quantified periodic continuation candidate, proof attempt, and explicit scaling/circularity audit. Challenger: an independently defined operator/determinant candidate with a domain and multiplicity audit. Each dossier must either contain a rigorous derivation or identify the first precise invalid or unproved inference. If neither survives, record both negative outcomes and review the queue; do not increase case counts as a substitute for a proof.

Run the local queue and intake checks:
```sh
python -m mathos.research.breakthrough_focus
python -m unittest discover -s tests -p 'test_breakthrough_focus.py' -v
```
The runner emits the seven-track work plan and validates candidate metadata; it does not run open-ended AI research, solve a conjecture, or authenticate reviewer identities. Existing agentic research may be used with explicit claim/route selectors and authorized budgets. No API calls or continuous scheduling are enabled by this protocol.

## 6. Source anchors

MathOS canonical register: docs/proof-analysis/OBLIGATIONS.v1.json; route graph: docs/research/CLAY_PROOF_ROUTES.v1.json; existing process: docs/research/AGENTIC_RESEARCH_PROCESS.md. Baseline commit: bd4f6effb8fabe2bb5f1166d6bb5020c901aecaa.

Clay problem statements: https://www.claymath.org/millennium-problems/

Clay rules: https://www.claymath.org/millennium-problems/rules/

Navier-Stokes announcement: https://www.claymath.org/news/navier-stokes-announcement/

RH comparator: J. C. Lagarias, Li coefficients for automorphic L-functions, https://doi.org/10.5802/aif.2311

Complexity barrier comparator: S. Aaronson and A. Wigderson, Algebrization: A New Barrier in Complexity Theory, https://eccc.weizmann.ac.il/report/2008/005/

These are starting anchors, not a completed literature review. All 14 work packages remain open.
