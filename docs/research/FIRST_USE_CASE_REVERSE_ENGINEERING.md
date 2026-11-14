# Reverse-engineering the seven first executable Millennium use cases

**Implementation audited:** \`mathos/research/hypothesis_pipeline.py\` (merged PR #17).  
**Source of research intent:** \`docs/research/HYPOTHESES.v1.json\`.  
**Canonical mathematical status:** \`docs/proof-analysis/OBLIGATIONS.v1.json\` — **NOT_CERTIFIED**, 14 open work packages.  
**Method:** start at each recorded \`probe_result\`, work backward to the expected output, underlying mathematical object, data choices, calculation, acceptance gate, independent cross-check and smallest counterfactual that would break the asserted check. These are **bounded executable examples** and **do not imply the Millennium conjectures**.

## How to replay

\`\`\`sh
python -m mathos.research.hypothesis_pipeline --output-dir artifacts/hypotheses
python -m unittest discover -s tests -p 'test_seven_hypotheses.py' -v
python -m unittest discover -s tests -p 'test_first_use_case_reverse_engineering.py' -v
\`\`\`

Read \`artifacts/hypotheses/seven_hypotheses_report.json\`. The top-level \`certification\` must be \`NOT_CERTIFIED\`; all experiments have \`exploration_state=EXPLORATORY_TESTED\`, \`mathematical_status=BLOCKED\`, \`promoted_to_solution=false\`. Output is accompanied by SHA-256 digests for the two input registries. Generated experiment reports do not edit mathematical work packages.

## 1. Riemann — reverse the first Li coefficient check

**Expected evidence:** a floating-point estimate with \`0 < lambda1_lower_approx < lambda1_upper_approx < 0.1\`, using \`n=2048\`.

**Backward chain:** The code evaluates the known formula
\[
\lambda_1 = 1+\frac{\gamma}{2}-\frac12\log(4\pi).
\]
It approximates the Euler–Mascheroni constant via the harmonic number \(H_n=\sum_{k=1}^n1/k\), using
\[
H_n-\log n-\frac{1}{2n}<\gamma<
H_n-\log n-\frac{1}{2(n+1)}.
\]
It substitutes both ends into the formula for \(\lambda_1\). At \(n=2048\), the existing floating-point code returns approximately \([0.0230956990,0.0230957586]\).

**Inputs / code:** standard-library \`math.fsum\`, \`math.log\`, \`n=2048\`; \`probe_li_first_coefficient\`.

**Independent falsification check:** recompute from a different harmonic cutoff and compare each result to a direct Euler–Mascheroni approximation; verify both bracket endpoints and the predicted width \(\frac{1}{4n(n+1)}\) up to floating-point roundoff. Perturbing the sign of the gamma term or substituting \(\log\pi\) for \(\log(4\pi)\) would make the reference-value check fail.

**What it establishes:** a **numerical normalization check** for a known formula, not rigorous interval arithmetic and not positivity for all Li coefficients. **Missing step:** a uniform theorem for \(\lambda_n\ge0\) for every \(n\), or another genuinely equivalent proof route. The MathOS obligation is spectral operator plus zero identity, not this finite numerical check.

## 2. P versus NP — reverse the \(K_4\) Tseitin 3-CNF certificate

**Expected evidence:** \`variables=6\`, \`clauses=16\` (each exactly 3 literals), \`satisfying_assignments=0\`, \`refutation_verified=true\`.

**Backward chain:** Label the six edges of the complete graph on four vertices by six Boolean variables. Each vertex has degree three. Demand odd parity (charge 1) at the first vertex and even parity (charge 0) at the other three. Encode each local XOR condition by forbidding its four wrong 3-bit assignments, giving four 3-literal CNF clauses per vertex and 16 total. Because every edge contributes twice when parity equations are summed mod 2, the left-hand sum must be 0; the charges sum to 1. Thus the system is unsatisfiable.

**Inputs / code:** \`itertools.combinations(range(4),2)\`, local charge vector \`(1,0,0,0)\`; \`k4_tseitin_clauses\`.

**Reverse the checks:** independently evaluate all \(2^6=64\) assignments, then construct the resolution closure: resolve complementary clauses, exclude tautological resolvents, record parent indices and pivot, and replay every step in a separate checker. The last clause must be the empty clause, not merely a claim of UNSAT.

**Falsifier/control:** with all charges even (e.g. \`(0,0,0,0)\`), the all-zero edge assignment satisfies every parity equation. A certificate with an incorrect pivot or parent must fail verification.

**What it establishes:** exact unsatisfiability for a single finite example and a checkable resolution proof. **Missing step:** a rigorously quantified lower bound for an *infinite* expander family in a declared proof system, and a separate bridge to unrestricted computation if seeking \(P\ne NP\). This example has a short proof and is not general 3-SAT hardness evidence.

## 3. Navier–Stokes — reverse the ABC conditional perturbation estimate

**Expected evidence:** \`gradient_operator_bound_K=3\`; for \(\nu=1\) and \(q=e^{-\nu t}\in\{1,1/2,1/4,1/8\}\), Gronwall exponents \(\{0,3,9/2,21/4\}\). The code checks the exact ABC field identities in \`millennium_attacks_002.py\`.

**Backward chain:** Begin with the classical periodic Beltrami field \(U=(\sin z+\cos y,\sin x+\cos z,\sin y+\cos x)\) on \(\mathbb T^3\). Its full nonlinear solution is \(v(t)=e^{-\nu t}U\), \(p_v=-e^{-2\nu t}|U|^2/2\). Write a **hypothetical smooth** perturbed solution as \(u=v+w\). Subtract the two Navier–Stokes equations and take the \(L^2\) inner product with \(w\). Divergence-free transport and pressure terms cancel; the viscous term dissipates; the remaining cross term satisfies
\[
\frac{d}{dt}\|w\|_2^2+2\nu\|\nabla w\|_2^2
=-2\!\int w\cdot(w\cdot\nabla v)\,dx
\le 2e^{-\nu t}\|\nabla U\|_{L^\infty,op}\|w\|_2^2.
\]
Exactly six Jacobian entries have magnitude at most 1. Thus the operator norm is at most \(\sqrt6<3=:K\), and Gronwall gives
\[
\|w(t)\|_2^2\le\|w(0)\|_2^2
\exp\!\left(\frac{2K}{\nu}(1-e^{-\nu t})\right).
\]

**Inputs / code:** exact Fourier ABC checks from \`abc_identities\`, rational \(\nu=1\), \(K=3\), and four values of \(q\); \`probe_abc_perturbation_bound\`.

**Independent checks/control:** verify the six Jacobian entry bounds, derive the energy identity algebraically, and recompute the exponent from \(q\) and \(\nu\); a universal claim without the smoothness assumption or with \(K^2<6\) is unsupported.

**What it establishes:** a **conditional** energy inequality about one smooth periodic solution, **not** unconditional global regularity, existence, or a critical \(L^4_tL^6_x\) bound for arbitrary \(\mathbb R^3\) data.

## 4. Yang–Mills — reverse the regulated transfer-gap obstruction

**Expected evidence:** eight exact rational rows, \(q_n=2^{-n}\), \(n=1,\ldots,8\); eigenvalue ratio \(r_n=(1-q_n)/(1+q_n)\), \(0<r_n<1\) and \(r_n\) increasing toward 1.

**Backward chain:** Consider the explicitly *toy* positive 2-by-2 transfer matrix
\[
T(q)=\begin{pmatrix}1&q\\q&1\end{pmatrix},\quad0<q<1.
\]
Its eigenvalues are \(1+q,1-q\), so the exact ratio of subleading to leading eigenvalue is \(r(q)\). Define the lattice-unit gap \(\Delta(q)=-\log r(q)\). Every \(q>0\) gives \(\Delta(q)>0\), but \(q\to0\) gives \(r(q)\to1\) and \(\Delta(q)\to0\). The code uses only exact rational \(r(q)\) and \(1-r(q)=2q/(1+q)\), **not** a computed logarithmic gap.

**Inputs / code:** \`Fraction(1, 2**n)\`, \(n=1,\ldots,8\); \`probe_transfer_gap_obstruction\`. Sample \(n=1\) gives \(r=1/3\); \(n=8\) gives \(r=255/257\).

**Independent check/control:** diagonalize \(T\) directly and derive the monotonic ratio. A uniform regulator-independent lattice-step gap cannot be inferred from individual positive gaps. If the physical time lattice spacing \(a(q)\) also shrinks, the physical gap \(\Delta(q)/a(q)\) has **no determined limit** without additional data. That is a critical scope boundary.

**What it establishes:** a model-selection obstruction (pointwise positivity \(\ne\) uniform lower bound), **not** any claim about Yang–Mills field reconstruction or a physical mass gap in four dimensions.

## 5. Hodge — reverse projective-space cycle-ring checks

**Expected evidence:** \`projective_dimension=4\`, \`top_degree_pairings=[1,1,1,1,1]\`, \`h_to_n_plus_one="0"\`.

**Backward chain:** Use the *known* cohomology ring \(H^*(\mathbb P^4,\mathbb Q)=\mathbb Q[h]/(h^5)\), where \(h\) is the first Chern class of the hyperplane line bundle and is represented by an algebraic divisor. The program represents monomials as pairs \((k,c)\) and computes multiplication \((i,a)(j,b)=(i+j,ab)\) when \(i+j\le4\), otherwise coefficient 0. Hence \(\int_{\mathbb P^4}h^k h^{4-k}=1\) for all \(k=0,\ldots,4\) and \(h^5=0\).

**Inputs / code:** dimension 4, exact \`Fraction\` arithmetic, monomial multiplication; \`probe_projective_hodge\`.

**Independent check/control:** implement polynomial convolution truncated modulo \(h^5\), check unit, nilpotence and top intersection number. Using \(h^5\ne0\) would contradict the dimension-dependent ring relation.

**What it establishes:** elementary arithmetic in an **assumed known** ring for a well-understood variety, not discovery of unknown algebraic cycles or Hodge-class verification in arbitrary varieties.

## 6. Birch–Swinnerton-Dyer — reverse finite-field elliptic counts

**Expected evidence:** exact \(\#E(\mathbb F_p)\) and \(a_p=p+1-\#E(\mathbb F_p)\) for \(E:y^2=x^3-x\) and primes \(p=5,7,11,13,17,19,23,29\), with each \(a_p^2\le4p\).

**Backward chain:** For every \(x\in\mathbb F_p\), solve \(y^2=x^3-x\) by either brute-forcing all \(p\) choices of \(y\) or using the quadratic-character rule. Add **one point at infinity**. The two counts must agree. As a reference for the eight primes, the expected point counts are
\[
(8,8,12,8,16,20,24,40),
\]
and the traces are
\[
(-2,0,0,6,2,0,0,-10).
\]

**Inputs / code:** all integer pairs modulo each listed prime, and a second count using the set of quadratic residues; \`probe_elliptic_local_counts\`.

**Independent check/control:** use Euler's criterion \(a^{(p-1)/2}\pmod p\) to compute Legendre symbols separately, reconstruct \(1+\sum_x(1+\chi(x^3-x))\), and compare exact tables. Check discriminant \(\Delta=64\), so every listed odd prime is a good reduction prime. A bad count would expose input/model error, **not** a BSD counterexample.

**What it establishes:** trusted local \(a_p\) data, **not** global Mordell–Weil rank, analytic rank, Tate–Shafarevich finiteness or the leading-term formula.

## 7. Poincaré — reverse the triangulated three-sphere homology check

**Expected evidence:** simplex counts \((5,10,10,5)\) in dimensions \(0,1,2,3\); mod-2 Betti numbers \((1,0,0,1)\), Euler characteristic 0, and \(\partial_{k-1}\partial_k=0\).

**Backward chain:** Use all nonempty proper faces of the 4-simplex on five labeled vertices. The boundary is a triangulation of \(S^3\). Its \(k\)-simplices are all \((k+1)\)-subsets of the vertex set, for \(k=0,\ldots,3\). Over \(\mathbb F_2\), the simplicial boundary of a simplex is the sum of its codimension-one faces. Every \((k-2)\)-face appears twice in a double boundary and cancels. The ranks of \(\partial_1,\partial_2,\partial_3\) are \(4,6,4\), giving
\[
\beta_k=\dim C_k-\operatorname{rank}\partial_k-\operatorname{rank}\partial_{k+1}
=(1,0,0,1).
\]

**Inputs / code:** \`itertools.combinations(range(5), k+1)\`, bitmask columns for boundary maps and GF(2) elimination; \`probe_simplicial_three_sphere\`.

**Independent check/control:** recompute boundaries as **sets of faces** with symmetric difference (rather than bitmask summation), check double boundaries and matrix ranks. Remove a tetrahedral facet to produce a contractible 3-ball-like complex whose top homology vanishes, a useful negative control.

**What it establishes:** a small known triangulated \(S^3\) example. Matching homology is not equivalent to simple connectivity and does **not** replay Perelman's Ricci-flow-with-surgery proof. Poincaré is already solved **externally**; MathOS reconstruction remains open.

## Audit priorities and what to strengthen next

| Priority | Change | Why it matters |
|---|---|---|
| 1 | Add independent reverse-oracle regressions for all seven cases | Current tests frequently assert outputs from the same function; separate formulations and negative controls catch a larger class of mistakes |
| 2 | Promote Li arithmetic to directed-rounding interval arithmetic | Current \`math.log\`/floating-point computations cannot certify rigorous enclosures |
| 3 | Extend \(K_4\) to a parameterized expander family with declared proof system | A one-graph contradiction does not provide a complexity lower bound |
| 4 | Prove conditional ABC stability theorem with precise function spaces | The code checks a numeric exponent, not well-posedness or generic vortex stretching |
| 5 | Add physical lattice spacing to transfer-gap models | The dimensionless lattice gap says nothing by itself about Yang–Mills physical mass |
| 6 | Test new varieties, elliptic descent constraints, and Ricci-flow lemmas | Known ring/point-count/homology examples are baseline validation, not the hard mathematical obligations |

**Verification contract:** the reverse-oracle suite may increase confidence that the seven *bounded* examples are correctly encoded. It must **not** edit \`docs/proof-analysis/OBLIGATIONS.v1.json\`, change \`NOT_CERTIFIED\`, mark \`BLOCKED\` problems solved, or claim original mathematical discoveries.
