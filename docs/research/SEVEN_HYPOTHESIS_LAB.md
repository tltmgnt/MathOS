# Seven-track Millennium hypothesis laboratory (research v1)

**Canonical proof status:** \`NOT_CERTIFIED\`  
**Exploration policy:** \`ALLOW_BLOCKED_RESEARCH_WITHOUT_PROMOTION\`  
**Scope:** all seven Clay Millennium problems and the seven MathOS authored proof routes.  
**Purpose:** start useful, falsifiable mathematical experiments even while the full problem is \`BLOCKED\`. A passing probe **never** certifies any conjecture or closes a proof obligation.

The "best" hypotheses here mean the **most immediately testable and mathematically grounded entry points** under MathOS's current finite/proof-analysis infrastructure, *not* claims that these approaches are likely to settle the original problems. Where possible, use known tractable cases to establish reliable input conventions and expose failed proof methods; move to the unsolved cases only after stating an exact new lemma.

## Seven preferred research entry points

| Problem | Working hypothesis / use case | Automated bounded check | Actual missing breakthrough |
|---|---|---|---|
| **Riemann hypothesis** | Search for an all-index positivity mechanism for Li coefficients \(\lambda_n\); a single negative coefficient would disprove RH | Numerical evaluation bracket for the known, positive first coefficient \(\lambda_1=1+\gamma/2-\tfrac12\log(4\pi)\) | Show \(\lambda_n\ge0\) **for every** \(n\), not just finite samples; a purported proof cannot assume RH to calculate the zeros |
| **P versus NP** | Study the width/length of resolution refutations for Tseitin parity contradictions on bounded-degree **expander families** | Odd XOR charge on the six edges of \(K_4\), encoded as 16 width-three CNF clauses; exhaustive truth table and a replayed resolution refutation | Quantify asymptotic lower bounds *in a declared proof system*, then address the gap to unrestricted algorithms; resolution hardness by itself does not prove \(P\ne NP\) |
| **Navier–Stokes** | Perturbatively control smooth solutions near the decaying ABC Beltrami solution, explicitly tracking vortex interactions | Exact ABC identities and a conditional \(L^2\) energy Gronwall exponent bounded by \(2K(1-e^{-\nu t})/\nu\), \(K=3\) | Establish a full critical-space continuation bound for arbitrary allowed data, or complete a valid breakdown alternative; energy control of a special flow is insufficient |
| **Yang–Mills mass gap** | Establish reflection positivity and spectral gaps that remain positive in **physical units** through continuum and infinite-volume limits | Two-state positive transfer-matrix toy: each regulated eigenvalue ratio \(r=(1-q)/(1+q)<1\), yet \(r\to1\) as \(q\to0\) | Rigorous nontrivial four-dimensional non-Abelian continuum field theory, axioms, and volume/cutoff uniform physical mass gap |
| **Hodge conjecture** | Characterize varieties whose rational \((p,p)\) classes have explicit algebraic generators | Exact hyperplane cohomology ring \(\mathbb Q[h]/(h^{n+1})\) and top pairing for \(\mathbb P^4\) | New algebraic cycle constructions for **primitive** rational Hodge classes on general smooth projective varieties |
| **Birch–Swinnerton-Dyer** | Reconcile descent/Selmer bounds with analytic rank in a declared elliptic-curve family | Independent direct and quadratic-residue counts for \(E:y^2=x^3-x\) at good primes; Hasse-bound checks | Global Selmer/rank equality and the entire leading-term formula including finiteness of \(\Sha\) and local factors |
| **Poincaré** | Independently reconstruct Perelman's established Ricci-flow-with-surgery proof, tracking every theorem dependency | Compute mod-two Betti numbers of the boundary of the 4-simplex, a triangulated \(S^3\), and check \(\partial^2=0\) | Precise complete replay of Ricci-flow analysis and topology steps; finite homology checks do not imply simple connectivity |

**Navier–Stokes status nuance:** Clay's public classification is still *Active* as of 2026-11-13 despite a September 2026 announcement of an apparently successful forced-breakdown approach. The legacy MathOS route is *unforced global regularity*, not an evaluation of that announced solution.

**Poincaré status nuance:** The conjecture is solved externally. The only MathOS blocker is its independent reconstruction task, which stays open.

## Runnable end-to-end workflow

\`\`\`sh
# All seven mathematical examples and canonical proof-status validation:
python -m mathos.research.hypothesis_pipeline --output-dir artifacts/hypotheses

# The original bounded research attempts remain independently testable:
python -m unittest discover -s tests -p 'test_millennium_attacks_001.py' -v
python -m unittest discover -s tests -p 'test_millennium_attacks_002.py' -v

# New seven-track evidence and guardrail tests:
python -m unittest discover -s tests -p 'test_seven_hypotheses.py' -v
\`\`\`

This produces \`artifacts/hypotheses/seven_hypotheses_report.json\`, including:
1. all seven explicit hypotheses, their test results and their remaining mathematical gaps;
2. per-track independent \`EXPLORATORY_TESTED\` vs \`mathematical_status=BLOCKED\`;
3. global and per-track \`certification=NOT_CERTIFIED\` and \`promoted_to_solution=false\`;
4. SHA-256 digests of the **actual canonical obligation register** and hypothesis registry used; and
5. the existing **14 open work packages** with no status edits.

The runner reads \`docs/proof-analysis/OBLIGATIONS.v1.json\`, validates exact track and obligation IDs, checks all official register states remain open and unreviewed, and refuses if the register has changed from \`NOT_CERTIFIED\`. It produces a separate report and **never writes to or promotes the canonical proof register**. Tampering tests reject false certification, fictitious novelty, missing or duplicate tracks, a wrong probe mapping, and manual closure of an obligation.

The CI workflow \`.github/workflows/millennium-research-tests.yml\` runs this end to end on **Python 3.10, 3.11 and 3.12**, retaining the previous bounded attempts. It uploads the seven-hypothesis JSON evidence as a CI artifact. Compiler/test success verifies reproducibility of the code, **not** a Millennium result.

## Hypothesis -> evidence -> mathematical review

1. Start with an exact mathematical statement, declared hypotheses, and a falsifiable specific claim. Use the machine-readable program in [HYPOTHESES.v1.json](HYPOTHESES.v1.json).
2. Run only the stated bounded check; keep input domain, numerical precision, conditioning, and proof-system scope visible.
3. Treat counterexamples as informative negative findings; distinguish an explicit certificate from a numerical observation and a finite example from a universal theorem.
4. Write the next genuinely mathematical lemma for expert review. Require a precise source, assumptions, and separate Lean/Coq/theorem-article replay if a claim warrants it.
5. Only the canonical proof-obligation promotion gate, after an actual mathematical proof and independent acceptance, may update the registry. The exploratory pipeline has **no privilege** to do so.

No currently open obligation is promoted by this PR. This is **parallel research scheduling**, not a bypass of mathematical standards.

## Sources and limitations

- [Clay Mathematics Institute — Millennium problems and official statuses](https://www.claymath.org/millennium-problems/)
- [Clay announcement for Navier–Stokes, 11 September 2026](https://www.claymath.org/news/navier-stokes-announcement/)
- [Li's criterion](https://mathworld.wolfram.com/LisCriterion.html): RH equivalent to nonnegativity of *all* Li coefficients
- [Ben-Sasson and Wigderson, *Short Proofs Are Narrow—Resolution Made Simple*](https://people.inf.ethz.ch/emo/SatSem05/Papers/BensassonWidgerson01.pdf): resolution lower bounds for Tseitin contradictions
- [2-Selmer groups and Heegner points](https://dash.harvard.edu/bitstreams/417f2568-a28d-492e-ac94-6206b70b7e35/download): limited-rank BSD progress and hypotheses

The Li coefficient check uses floating-point logarithms, **not** a certified interval package. The Fourier and exact rational checks are valid only for the explicitly stated finite models. The toy Yang–Mills transfer matrix is not a gauge theory. The projective Hodge ring and simplicial sphere computations are known elementary examples. The bounded graph's resolution certificate demonstrates one **easy** finite instance, not an asymptotic lower bound. No claim of novelty or solution is made.
