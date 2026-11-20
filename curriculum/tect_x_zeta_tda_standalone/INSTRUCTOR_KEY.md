# Instructor Answer Key and Assessment Guide

**Instructor use only.** These answers are self-contained; no TECT-X research dataset, external transcript, Sage, or internet connection is required. The rubric evaluates what learners prove, not the scale of a computation.

## Week 1

**1.1 (a)** Each factor \(x-j\) vanishes at \(x=j\), so \(p_N(j)=0\) for each tested \(j=1,\dots,N\). **(b)** \(p_N(N+1)=N(N-1)\cdots1=N!\ne0\). **(c)** The formula gives a direct counterexample at the next input. **(d)** Replacing \(N\) with one million leaves the logical gap unchanged. **10 points:** (a) 3, (b) 3, (c) 3, (d) 1.

**1.2** Accept any three explicit gaps, for example: (i) the tested objects include different zeta families and need not be the analytically continued Riemann zeta; (ii) the TDA input is a **numerical feature point cloud**, not the complex zero set; (iii) the computation uses finitely many points and finitely many scales; (iv) the feature metric/normalization can create or eliminate loops; (v) no proved implication “such-and-such Betti numbers \(\Rightarrow\) all genuine zeros lie on the critical line” was supplied. A model replacement: “For specified zeta-family descriptors and tested Vietoris–Rips thresholds, the computed sample did not have a one-dimensional loop; this does not determine the locations of Riemann zeta zeros.” **10 points:** 6 for three distinct gaps, 4 for a calibrated rewrite.

**1.3 (optional)** Example: a proof shows every counterexample would reduce to one of finitely many checkable states; a verified program checks all states; the combination is exhaustive. The finite reduction and correctness of the verification must themselves be justified.

## Week 2

**2.1(a)** \(1+\frac14+\frac19+\frac1{16}=\frac{205}{144}\). **(b)** \(\frac14+\frac19+\frac1{16}+\frac1{25}=\frac{1669}{3600}\). **(c)** \(\zeta(2,2)=\sum_{m=2}^\infty m^{-2}=\zeta(2)-1\). **(d)** For decreasing \(x^{-2}\), \(\frac1{n^2}\le\int_{n-1}^n x^{-2}dx\), so \(\sum_{n=M+1}^\infty n^{-2}\le\int_M^\infty x^{-2}dx=\frac1M\). **10 points:** parts (a),(b) 2 each, (c) 3, (d) 3.

**2.2** The five complete rows:

| Zeta construction | Underlying object | Variable and defining equation / domain |
|---|---|---|
| Riemann | positive integers / their Dirichlet series | \(s\); \(\sum_{m\ge1}m^{-s}\), initially \(\Re s>1\); meromorphically continued |
| Hurwitz | positive shift \(a>0\) and nonnegative integers | \(s,a\); \(\sum_{m\ge0}(m+a)^{-s}\), \(\Re s>1\) |
| Finite graph spectral | nonzero eigenvalues \(\lambda_j>0\) of a graph Laplacian | \(s\); \(\sum_j\lambda_j^{-s}\), finite entire sum |
| Cycle Ihara | primitive nonbacktracking closed walks of \(C_n\) | \(u,n\); \((1-u^n)^{-2}\), rational continuation |
| Full-shift Artin–Mazur | periodic points of a \(k\)-symbol full shift | \(u,k\); \(\exp(\sum_{m\ge1}k^m u^m/m)=(1-ku)^{-1}\), \(|ku|<1\) for the series |

The functions have different underlying objects and variables. Their analytic properties are not interchangeable. **10 points:** 2 per complete row.

**2.3 (optional)** The Dirichlet series \(\sum n^{-s}\) does not converge for \(\Re s=1/2\); analytic continuation gives a different representation of the same continued function, not convergence of the original series.

## Week 3

**3.1** For \(C_3\), \(Z(1)=1/3+1/3=2/3\), \(Z(2)=1/9+1/9=2/9\). Formulas give \((9-1)/12=2/3\) and \((81+90-11)/720=160/720=2/9\). For \(C_4\), \(Z(1)=1/2+1/4+1/2=5/4\), \(Z(2)=1/4+1/16+1/4=9/16\). Formulas give \(15/12=5/4\) and \((256+160-11)/720=405/720=9/16\). These are two **checks**, not an all-\(n\) proof. **10 points:** 4 for \(C_3\), 4 for \(C_4\), 2 for scope.

**3.2** Multiplication and simplification yield
\[
(2\pi/n)^2(n^2-1)/12=(\pi^2/3)(1-n^{-2}),
\]
\[
(2\pi/n)^4(n^4+10n^2-11)/720
=(\pi^4/45)(1+10n^{-2}-11n^{-4}).
\]
The limits are \(\pi^2/3=2\zeta(2)\), \(\pi^4/45=2\zeta(4)\). The signed relative errors compared with these limits are **exactly** \(-n^{-2}\) and \(10n^{-2}-11n^{-4}\), respectively. These formulas evaluate positive integer spectral exponents and no critical-strip zero location. **10 points:** 3+3 for identities, 2 for limits/errors, 2 for gap.

**3.3 (optional)** Since \(\lambda_j=4\sin^2(\pi j/n)\), \(Z(1)=\frac14\sum_{j=1}^{n-1}\csc^2(\pi j/n)=(n^2-1)/12\).

## Week 4

**4.1(a)** \(I_3(1/2)=(1-1/8)^{-2}=(8/7)^2=64/49\). \(I_5(1/2)=(1-1/32)^{-2}=(32/31)^2=1024/961\), so the functions differ. **(b)** Since \((e^{-1/n})^n=e^{-1}\), \(I_n(e^{-1/n})=(1-e^{-1})^{-2}\), independent of \(n\). **(c)** The measurement points change with the function; the map from a function to the chosen adaptive reading is many-to-one. **(d)** A common fixed \(u=1/2\) or coefficients of the Taylor series distinguish cycle sizes. **10 points:** (a) 4, (b) 3, (c) 2, (d) 1.

**4.2** \(V(C_n)=n\), \(E(C_n)=n\). The graph is connected and \(\beta_1=E-V+1=1\). Both adaptive coordinates are constants \(((1-e^{-1})^{-2},(1-e^{-2})^{-2})\); the descriptor cloud has just **one unique point**, so \(\beta_1=0\) at every radius. It is a different space from the original graph, so no contradiction exists. **10 points:** graph 3, alias 4, topological distinction 3.

## Week 5

**5.1** With square vertices labeled in cyclic order:

| Radius | \(V\) | \(E\) | Triangles \(F\) | \(\operatorname{rank}\partial_1\) | \(\operatorname{rank}\partial_2\) | \(\beta_0\) | \(\beta_1\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| \(0.9\) | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| \(1\) | 4 | 4 | 0 | 3 | 0 | 1 | 1 |
| \(\sqrt 2\) | 4 | 6 | 4 | 3 | 3 | 1 | 0 |

At \(r=1\), the perimeter gives a single unfilled cycle. At \(r=\sqrt2\), the diagonals create triangles, and their boundaries span all three independent cycles of \(K_4\). **10 points:** 3 for simplex counts, 4 for ranks, 3 for Betti explanations.

**5.2** Square at \(r=1\): \((\beta_0,\beta_1)=(1,1)\), positive \(H_1\) control. Line points at \(r=1\): the VR 1-skeleton is a three-edge path, \((1,0)\), negative \(H_1\) control. These are checks of a **small finite-complex calculation**, not information about Riemann zeros. **10 points:** 3+3+4.

**5.3 (optional)** The code prints the same square/line Betti values and elementary cycle formula checks. Software tests establish only correctness within their assumptions and tested cases; they do not examine genuine Riemann zeros.

## Week 6

**6.1** A strong answer gives:
- The source objects and descriptor map; these need not be actual Riemann zeros.
- An explicit Euclidean or other metric, threshold convention (edges at distance \(\le r\)), sampling and normalization, and numerical-precision statement.
- A warning that finitely many sampled function descriptors at seven radii are not a universal statement about all functions, all radii, or any underlying analytic spaces.
- The distinction “no \(H_1\) at these radii” versus “the whole space is contractible”; contractibility is vastly stronger.
- The absent bridge: a proved stable invariant and theorem relating it to \(\Re\rho=1/2\) for **every actual nontrivial Riemann zero**. No such bridge is supplied.

**10 points:** 2 each for the five required elements.

### Final capstone marking rubric

| Criterion | Points | Evidence for full credit |
|---|---:|---|
| Precise mathematical definitions | 15 | Domain, variables, measured space clearly stated |
| Exact reasoning | 20 | Complete correct derivation, not just code output |
| Controlled reproducibility | 20 | Inputs, arithmetic precision, algorithm/hand steps and checkable outputs |
| Adversarial testing | 15 | Meaningful positive/negative control, parameter or feature perturbation |
| Calibrated conclusions and proof gaps | 20 | No inflated RH claim; explicit missing implication and limits |
| Communication | 10 | Logically organized explanation and correct notation |

**Model capstone claim for Track B:** “For \(I_n(u)=(1-u^n)^{-2}\), the two adaptive features \(I_n(e^{-1/n})\) and \(I_n(e^{-2/n})\) are exactly independent of \(n\), although the family functions are distinct because \(I_n(1/2)\) differs for \(n\ne m\). Thus this measurement map is non-injective. This shows how experimental feature choices can erase information; it does not imply anything about the critical-strip zeros of the Riemann zeta function.”

**Condition for course completion:** minimum overall weighted score 70/100 **and** correction of any claim that finite observations alone establish RH, BSD, or a general all-input theorem. A learner may earn full credit without programming.

## Recommended teaching response to common mistakes

- “A million is almost infinity.” Answer: cardinality and quantification are different; the polynomial \(p_N\) provides an explicit all-\(N\) counterexample.
- “Zeta functions must have the same zeros.” Answer: each of the five functions has different input objects and often different variables and analytic structure.
- “The cycle graph has a loop, so its feature cloud must have one.” Answer: graph topology and descriptor topology are distinct.
- “The VR square loop persisted forever.” Answer: it vanishes when diagonals/triangles enter at \(r=\sqrt2\).
- “A passing automated test certifies the Riemann hypothesis.” Answer: it certifies only the tested program behavior on declared inputs. A proof needs a complete logical bridge to the universal mathematical statement.

**Instructor ethics note:** the motivating video is an optional question prompt, not a cited proof, and neither its audio/transcript nor its presenter's precise mathematical position was independently assessed for this curriculum.
