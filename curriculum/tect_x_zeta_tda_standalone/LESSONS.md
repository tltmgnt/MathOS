# Teaching Notes — 12 Meetings in Six Weeks

This course uses a **bounded-evidence protocol**. Each claim must identify (i) the precise mathematical object, (ii) the theorem or computation actually established, (iii) the limitations of the evidence, and (iv) the unproved step needed for a broader conclusion. Each meeting is 90 minutes. Exercises and instructor solutions are in this directory.

## Week 1 — Logic: many tests are not a proof

### Meeting 1A: Quantifiers, proof and numerical evidence

**Objective:** Translate “every nontrivial zero is on the critical line” into a universally quantified mathematical assertion and contrast it with a finite observation.

**10 minutes — entry prompt.** A program verifies a property for one million inputs. Which statements follow? (a) It held for the tested inputs; (b) it holds for all inputs. Learners must choose (a) and state why (b) needs a separate argument.

**20 minutes — instruction.** Distinguish:
- \(\forall x\in D:P(x)\), a universal claim;
- \(\exists x\in D:\neg P(x)\), a counterexample;
- \(\forall x\in T:P(x)\) for a finite tested set \(T\subsetneq D\).

A single valid counterexample refutes a universal claim, but any finite set of successes usually cannot prove one without additional structure. A computer-assisted *proof* can be valid when it verifies a logically exhaustive, finite reduction with justified error bounds; mere data collection is not that.

**30 minutes — worked task.** For arbitrary positive integer \(N\), define
\[
f_N(k)=\begin{cases}1&1\le k\le N,\\ -1&k>N.\end{cases}
\]
Explain why checking the first \(N\) values cannot justify \(\forall k\ge1:f_N(k)=1\). Advanced extension: \(p_N(x)=\prod_{j=1}^{N}(x-j)\) vanishes at the tested integers but not at \(N+1\).

**20 minutes — transfer.** The Riemann hypothesis (RH) concerns **actual zeros of the analytically continued Riemann zeta** \(\zeta(s)\) in the critical strip \(0<\Re(s)<1\): all have real part \(1/2\). A numerical list of zeros checked to a finite height remains a finite observation.

**10 minutes — exit ticket.** State a bounded claim and an unbounded claim about an algorithm's output; label which was shown.

### Meeting 1B: Construct a claim–evidence–gap record

**Objective:** Explain the epistemic distinction among an example, exhaustive finite proof, conditional theorem, theorem, and open problem.

**10 minutes:** Discuss the video's screenshot-visible question about AI brute force versus mathematical insight; **do not infer speech or technical assertions from an unseen transcript**.

**20 minutes:** Introduce the claim ledger: *exact statement; assumptions; input domain; method; outcome; missing implication*.

**30 minutes:** In groups, repair the headline “one million zeta functions prove RH.” Correct it to “we computed specified numerical features for one million functions from named families; no RH conclusion follows without a theorem relating those features to every genuine Riemann zero.”

**20 minutes:** Peer review: identify one hidden assumption and one possible adverse control for the repaired headline.

**10 minutes:** Submit Exercise 1.1 and 1.2.

## Week 2 — Distinguish five zeta constructions

### Meeting 2A: Riemann and Hurwitz zeta

**Objective:** Use the defining convergent series and their domains of validity.

For \(\Re(s)>1\),
\[
\zeta(s)=\sum_{n=1}^{\infty}n^{-s},\qquad
\zeta(s,a)=\sum_{n=0}^{\infty}(n+a)^{-s}\quad(a>0).
\]
Immediately verify \(\zeta(s,1)=\zeta(s)\) in this half-plane. The Riemann zeta has a meromorphic continuation to the complex plane with its only pole at \(s=1\); the original series is **not** convergent in the critical strip. RH is about zeros of the **continued function**, not the convergent Dirichlet series itself.

**Schedule:** 10 minutes retrieve domains; 20 minutes instructor derives the \(a=1\) identity; 30 minutes evaluate first four terms of \(\zeta(2)\) and \(\zeta(2,2)\) and bound the omitted tail crudely; 20 minutes separate analytic statements from numerical approximations; 10 minutes worksheet 2.1.

**Careful tail exercise:** For \(s=2\), after terms through \(n=M\),
\[
\sum_{n=M+1}^\infty n^{-2}\le\int_M^\infty x^{-2}dx=\frac1M.
\]
This is an *inequality proof* controlling an infinite tail, unlike just printing a decimal.

### Meeting 2B: Spectral, Ihara and dynamical zeta

**Objective:** Name what varies in each construction.

For a finite connected graph \(G\) with Laplacian nonzero eigenvalues \(\lambda_1,\ldots,\lambda_{v-1}>0\) (multiplicity counted), define
\[
Z_{\Delta,G}(s)=\sum_{j=1}^{v-1}\lambda_j^{-s}.
\]
This is a **finite** spectral sum, not the Riemann zeta. For an undirected cycle \(C_n\), the Ihara zeta is
\[
Z_{I,C_n}(u)=\frac{1}{(1-u^n)^2},
\]
a rational function that encodes two orientations of a primitive, nonbacktracking closed cycle. For a full shift on \(k\) symbols, every \(m\)-step iteration has \(k^m\) fixed sequences; its Artin–Mazur zeta is
\[
Z_{\mathrm{AM},k}(u)=\exp\Big(\sum_{m\ge1}\frac{k^m}{m}u^m\Big)
=\frac{1}{1-ku},\quad |ku|<1
\]
with rational continuation thereafter.

**10 minutes:** retrieval comparison. **20 minutes:** define all three. **30 minutes:** construct a five-family comparison matrix of variable, input object, and convergence/singularity. **20 minutes:** explain why a shared name “zeta” does not imply identical zeros or functional equations. **10 minutes:** Exercise 2.2.

## Week 3 — Exact algebraic bridges

### Meeting 3A: Cycle Laplacian

**Objective:** Verify a graph spectral identity in a finite case.

For \(C_n\), \(n\ge3\), the nonzero Laplacian eigenvalues are
\[
\lambda_j=2-2\cos(2\pi j/n)=4\sin^2(\pi j/n),\quad j=1,\ldots,n-1.
\]
One can check these eigenvalues with Fourier modes, or treat them as a supplied standard identity in the no-code route. The standard trigonometric sums imply
\[
Z_{\Delta,C_n}(1)=\frac{n^2-1}{12},\qquad
Z_{\Delta,C_n}(2)=\frac{n^4+10n^2-11}{720}.
\]
**Check:** \(C_3\) has nonzero eigenvalues \(3,3\), so \(Z(1)=2/3\), \(Z(2)=2/9\). Both closed forms agree. For \(C_4\), nonzero eigenvalues \(2,4,2\), giving \(Z(1)=5/4\), \(Z(2)=9/16\).

**Schedule:** 10 minutes graph drawing; 20 minutes eigenvalue introduction; 30 minutes exact hand checks for \(C_3,C_4\); 20 minutes explore error from approximate sine; 10 minutes exit ticket distinguishing checked identities from proof for all \(n\).

### Meeting 3B: Scaling connects graph spectra to Riemann special values

**Objective:** Derive a genuine limit from exact finite-\(n\) formulas.

Since \(\zeta(2)=\pi^2/6\) and \(\zeta(4)=\pi^4/90\),
\[
\Big(\frac{2\pi}{n}\Big)^2 Z_{\Delta,C_n}(1)
=2\zeta(2)(1-n^{-2}),
\]
\[
\Big(\frac{2\pi}{n}\Big)^4 Z_{\Delta,C_n}(2)
=2\zeta(4)(1+10n^{-2}-11n^{-4}).
\]
The **finite-error terms are explicit**, so taking \(n\to\infty\) is a justified limiting argument. These relate **positive integer values** of spectral and Riemann zetas; they say nothing about critical-strip zeros.

**Schedule:** 10 minutes recall \(C_3\); 20 minutes algebra of rescaling; 30 minutes derive both error terms and numeric limits; 20 minutes design an invalid RH inference and explain the gap; 10 minutes complete Exercise 3.2.

## Week 4 — Identifiability and topology mismatch

### Meeting 4A: A complete aliasing counterexample

**Objective:** Distinguish an underlying function from its measured features.

Fix \(u\) with \(0<u<1\). For \(n\ge3\),
\[
Z_{I,C_n}(u)=(1-u^n)^{-2}.
\]
As \(n\) varies, \(u^n\) strictly decreases, so **fixed-\(u\) values distinguish \(n\)**.

But with an adaptive probe \(u_n=e^{-t/n}\), for any \(t>0\),
\[
Z_{I,C_n}(u_n)=(1-(e^{-t/n})^n)^{-2}
=(1-e^{-t})^{-2},
\]
which is **independent of \(n\)**.

This proves that arbitrarily many distinct functions can map to exactly one observed descriptor. Two adaptive probes \(t=1,2\) also fail: both features are constant across \(n\).

**Schedule:** 10 minutes retrieve function definition; 20 minutes derive identity; 30 minutes compare \(n=3,4,5\) at fixed \(u=1/2\) versus adaptive \(u_n\); 20 minutes redesign measurement using a common \(u\) or full rational-function data; 10 minutes Exercise 4.1.

### Meeting 4B: Three different spaces and three different notions of topology

**Objective:** Avoid conflating graph cycles, zeta functions and numerical descriptor clouds.

1. Underlying graph \(C_n\) has \(n\) vertices and \(n\) edges. For connected graphs, \(\beta_1=E-V+1=1\).
2. Its Ihara zeta is a rational function \(Z_{I,C_n}(u)\); its singularities and coefficients are **analytic/algebraic** data.
3. A cloud of points \((f_1(C_n),f_2(C_n))\in\mathbb R^2\) has a topology determined by chosen features, normalization and distance threshold. If the adaptive probes of Meeting 4A are used, the **entire cloud collapses to a single location** and has no one-dimensional cycle.

**Schedule:** 10 minutes draw \(C_n\); 20 minutes explain the three spaces; 30 minutes prove graph \(\beta_1=1\) and descriptor \(\beta_1=0\) in alias case; 20 minutes adversarial review (“same source, different spaces”); 10 minutes complete Exercise 4.2.

## Week 5 — TDA from first principles

### Meeting 5A: Vietoris–Rips filtrations and homology

**Objective:** Compute \(\beta_0\) and \(\beta_1\) of a small point set.

For a finite set of points \(X\) in Euclidean space and radius \(r\ge0\), the Vietoris–Rips complex \(VR_r(X)\) includes an edge between points at distance **at most \(r\)**. Every triple whose three pairwise edges appear becomes a **filled triangle**, and similarly for higher cliques. In these exercises we only need the 2-skeleton.

Over \(\mathbb F_2\), orientational signs disappear. Let \(C_0,C_1,C_2\) be vector spaces spanned by vertices, edges, triangles, with boundary maps
\[
\partial_1([i,j])=[i]+[j],\quad
\partial_2([i,j,k])=[i,j]+[j,k]+[i,k].
\]
Then \(\partial_1\partial_2=0\), and
\[
\beta_0=V-\operatorname{rank}\partial_1,\qquad
\beta_1=E-\operatorname{rank}\partial_1-\operatorname{rank}\partial_2.
\]

**Example: four corners of a unit square.**
At \(r=1\): \(V=4,E=4,F=0\), connected, so \(\operatorname{rank}\partial_1=3\), \(\beta_0=1,\beta_1=1\).
At \(r=\sqrt2\): \(V=4,E=6,F=4\); \(\operatorname{rank}\partial_1=3,\operatorname{rank}\partial_2=3\), so \(\beta_0=1,\beta_1=0\). The loop becomes filled, not “disproved.”

**Schedule:** 10 minutes square geometry; 20 minutes define VR and boundaries; 30 minutes draw simplices for both radii; 20 minutes compute ranks and verify \(\partial_1\partial_2=0\); 10 minutes worksheet 5.1.

### Meeting 5B: Control experiments

**Objective:** Compare feature clouds with positive and negative controls and state the range of an observed result.

Use the included lab.py (or hand-built square). Compute:
- a square at \(r=1\): positive one-loop control;
- the same square at \(r=\sqrt2\): filled/zero-loop control;
- four collinear points \((0,0),(1,0),(2,0),(3,0)\) at \(r=1\): connected with no loop.

If the test is negative at one radius, it is **not** a proof that the point cloud has no persistent loop at any radius. If the cloud has a loop, that is **not** a proof that the original zeta has an off-critical-line zero.

**Schedule:** 10 minutes recall \(\beta_1\); 20 minutes predict outcomes; 30 minutes execute or hand-calculate controls; 20 minutes discuss threshold dependence and precision; 10 minutes Exercise 5.2.

## Week 6 — A reproducible bounded research claim

### Meeting 6A: Validate without overclaiming

**Objective:** Pre-register a finite claim, reproduce it, test adversarial controls, then specify what would be needed for generalization.

**10 minutes:** quick quiz (finite test vs proof). **20 minutes:** choose a question: compare fixed and adaptive Ihara probes; verify small cycle spectral sums; or test Betti numbers of a square. **30 minutes:** record input range, code/hand method, precision/exact values, controls, and all output values. **20 minutes:** adversarial redesign (different radius, alternate feature normalization, false positive challenge). **10 minutes:** outline capstone.

Required evidence record:

- Mathematical objects and exact statement.
- Finite experiment and assumptions.
- Independent check or negative/positive control.
- What the experiment demonstrates.
- What it does **not** demonstrate.
- Numerical precision or symbolic exactness.
- Possible falsification test.
- Unproved theorem-level bridge.

### Meeting 6B: Capstone defense and transfer

**Objective:** Defend a bounded claim without turning it into RH, BSD or an unproved infinite result.

**10 minutes:** peer-review contracts; **40 minutes:** 5–7 minute presentations or written poster walk; **20 minutes:** cross-examination (students each ask “Where does the universal quantifier enter?” and “Which topology was computed?”); **10 minutes:** revise claim language; **10 minutes:** self-reflection and course survey.

**Capstone success means:** a correct exact result, accurate finite evidence, a meaningful countercheck, and an explicitly open next mathematical step. A million variants are **not required** for this capstone; small models are preferable because they can be checked.

## Instructor guidance on discussion quality

When a learner says “we found a pattern,” ask **“in which space, with which features, distance, radius, and error budget?”** When someone says “AI has proved it,” ask for the statement of the theorem, the complete proof artifact and an independently checkable logical implication. Conversely, do not dismiss computer-assisted proofs: exhaustive finite verification can be rigorous when finiteness and coverage follow from a proof and the calculation is certified.

This course can be taught without watching the motivating video. The screenshot-visible theme is enough; no part of a student's score depends on media access.
