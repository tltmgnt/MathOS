# Learner Workbook, Assessments and Capstone

**Name:** ____________________  **Cohort:** ____________________  
**Instructions:** Work from this directory only. Give exact answers when possible and label approximations. Coding is optional. No question requires a million-function dataset or access to the motivating video.

## Week 1 — What counts as proof?

**1.1 — A universal-quantifier challenge (10 points).** For an arbitrary integer \(N\ge1\), consider \(p_N(x)=\prod_{j=1}^{N}(x-j)\). (a) Compute \(p_N(j)\) for \(j=1,\ldots,N\). (b) Compute \(p_N(N+1)\). (c) Explain why checking \(N\) inputs does not prove that \(p_N(x)=0\) for every positive integer \(x\). (d) Does a million change the logical conclusion?

**1.2 — Evidence audit (10 points).** A student writes: “An AI compared one million zeta functions and found no topological loops; therefore every Riemann-zeta zero lies on the critical line.” Identify **at least three distinct missing implications**. Rewrite the claim to accurately describe what was actually observed and include what remains unproved.

**1.3 — Computer-assisted proofs (optional).** Give one logically sound circumstance in which finitely many computer checks *could* be part of a universal mathematical proof, specifying the additional proof obligation.

## Week 2 — Families named “zeta”

**2.1 — Series and a tail bound (10 points).** (a) Write the first four terms of \(\zeta(2)=\sum_{n=1}^\infty n^{-2}\) and compute their exact rational sum. (b) Write the first four terms of \(\zeta(2,2)=\sum_{n=0}^\infty(n+2)^{-2}\), and compute their exact rational sum. (c) Show by an index shift that \(\zeta(2,2)=\zeta(2)-1\). (d) Prove \(\sum_{n=M+1}^\infty n^{-2}\le1/M\) for \(M\ge1\) using integral comparison.

**2.2 — Five objects, five definitions (10 points).** Complete the matrix. Supply the **underlying object**, function variable, definition on an appropriate domain and one reason it is unsafe to identify its zeros with Riemann zeros.

| Object | Underlying mathematical object | Variable and formula/domain |
|---|---|---|
| Riemann zeta | | |
| Hurwitz zeta | | |
| Graph Laplacian spectral zeta | | |
| Cycle Ihara zeta | | |
| Full-shift Artin–Mazur zeta | | |

**2.3 — Domain error (optional).** Explain why substituting \(s=1/2+14i\) into the *convergent-series definition* of \(\zeta(s)\) is invalid, even though analytic continuation defines \(\zeta(s)\) there.

## Week 3 — Exact cycle identities

**3.1 — Verify with small graphs (10 points).** On \(C_3\), use Laplacian eigenvalues \(3,3\); on \(C_4\), use \(2,4,2\). Compute \(Z_{\Delta,C_n}(1)\) and \(Z_{\Delta,C_n}(2)\) directly and confirm they match
\[
\frac{n^2-1}{12},\qquad \frac{n^4+10n^2-11}{720}.
\]
Explain why agreement at \(n=3,4\) alone does not prove the formulas for every \(n\).

**3.2 — Exact limit with a quantified error (10 points).** Using the two closed forms, show
\[
\Big(\frac{2\pi}{n}\Big)^2 Z_{\Delta,C_n}(1)
=\frac{\pi^2}{3}(1-n^{-2}),
\]
\[
\Big(\frac{2\pi}{n}\Big)^4 Z_{\Delta,C_n}(2)
=\frac{\pi^4}{45}(1+10n^{-2}-11n^{-4}).
\]
State the limits and exact relative-error expressions. Explain why these identities do not locate any nontrivial zero of \(\zeta(s)\).

**3.3 — Optional deeper proof.** Given the trigonometric identity \(\sum_{j=1}^{n-1}\csc^2(\pi j/n)=(n^2-1)/3\), derive the closed form for \(Z_{\Delta,C_n}(1)\).

## Week 4 — Measurement aliasing

**4.1 — Two probes, opposite conclusions (10 points).** Let \(I_n(u)=(1-u^n)^{-2}\), \(n\ge3\). (a) Calculate \(I_3(1/2)\) and \(I_5(1/2)\) exactly. (b) Set \(u_n=e^{-1/n}\), simplify \(I_n(u_n)\), and show it is independent of \(n\). (c) Explain why a constant adaptive descriptor does **not** mean the underlying functions \(I_3\) and \(I_5\) are identical. (d) Propose one more informative fixed measurement.

**4.2 — Three kinds of topology (10 points).** For a cycle graph \(C_n\) identify \(V\), \(E\), and its graph \(\beta_1\). Then take the adaptive feature vector \((I_n(e^{-1/n}),I_n(e^{-2/n}))\). How many distinct locations occur as \(n\) varies? What is the \(\beta_1\) of the **feature point cloud** at any finite VR threshold? Why is there no contradiction?

## Week 5 — From point clouds to homology

**5.1 — Rips complex of a square (10 points).** Take
\[
X=\{(0,0),(1,0),(1,1),(0,1)\}.
\]
At each \(r=0.9\), \(r=1\), and \(r=\sqrt2\), count vertices, edges and filled triangles in the Vietoris–Rips complex. Compute \(\operatorname{rank}\partial_1\), \(\operatorname{rank}\partial_2\), \(\beta_0\) and \(\beta_1\), where
\[
\beta_0=V-\operatorname{rank}\partial_1,\quad
\beta_1=E-\operatorname{rank}\partial_1-\operatorname{rank}\partial_2.
\]
At which threshold does a one-dimensional hole appear, and at which does it fill?

**5.2 — Controls, limitations (10 points).** Compare the square at \(r=1\) with the line points \((0,0),(1,0),(2,0),(3,0)\) at \(r=1\). Supply the Betti numbers for both and identify which is a positive \(H_1\) control and which is negative. Explain why neither controls the location of Riemann-zeta zeros.

**5.3 — Optional programming (ungraded).** Run python lab.py --radius 1 and python -m unittest discover -s . -p test_lab.py -v. Interpret the reported \(\beta_0,\beta_1\), and explain why passing tests is not a theorem about the actual zeta function.

## Week 6 — Audit, inference and communication

**6.1 — Adversarial review (10 points).** A draft report states: “Every sampled descriptor cloud has \(\beta_1=0\) at seven thresholds. Therefore the space of zeta functions is contractible, and RH follows.” Provide a structured **claim–evidence–gap** response addressing:
- which functions and descriptors are included;
- the numerical precision and filtration convention;
- whether sampling was exhaustive;
- whether no loop at selected radii means contractibility;
- what mathematical theorem would actually connect this to Riemann zeros.

**6.2 — Final independent capstone (30% of course grade).** Choose **one**:
- **Track A: Exact arithmetic.** Verify \(C_3,C_4,C_5\) spectral zeta values and their asymptotic bridge. Include an exact derivation and numerical cross-check.
- **Track B: Measurement aliasing.** Prove that \(I_n(e^{-t/n})\) is constant in \(n\), contrast with a fixed probe, and design a more identifiable measurement.
- **Track C: Small TDA laboratory.** Compute a full 2-skeleton and Betti numbers for a square at three radii, including line control and one adversarial feature transformation.

Submit a **1,200–1,800-word report** or a **10–12-minute oral defense** with a one-page evidence record. Every submission must contain the following:

1. Exact mathematical objects and a falsifiable bounded research question.
2. One complete exact derivation or proof, with all assumptions.
3. Finite numerical, coding or hand-computation evidence, labeled accurately.
4. A positive and/or negative control plus one adversarial check.
5. A clear result limited to the stated input domain, precision and threshold.
6. At least two limitations, including the missing RH or universal-inference bridge.
7. Reproducible instructions for a peer.
8. A two-sentence reflection on when AI-assisted exploration can help mathematicians but cannot replace a logical argument.

**Required phrasing:** distinguish “verified for these inputs” from “proved for every input.” No submission is allowed to claim it proves RH, BSD, or new Selmer-infinitude results.

## Student evidence-record template

**Claim:** ____________________________________________

**Definitions and domain:** ____________________________

**Assumptions:** ______________________________________

**Exact argument:** ____________________________________

**Experiment / parameters / precision:** ________________

**Controls and adverse checks:** ________________________

**Observed or proved conclusion:** ______________________

**What is still unproved:** ______________________________

**Reproduction instructions:** __________________________

**Peer reviewer and corrections:** ______________________

## Marking checklist for instructor and peer review

Weekly scores are formative; the course grade is weighted as in the syllabus README. Final defense rubric (100 points within its capstone component): precise definitions (15), exact mathematical reasoning (20), controlled reproducibility (20), adversarial checks (15), calibrated conclusions and proof gaps (20), and clear communication (10). A student must explicitly retract any universal claim based only on finite computation to pass the capstone.
