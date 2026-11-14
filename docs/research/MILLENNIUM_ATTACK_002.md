# Millennium mathematical research attempt 002 — nonlinear ABC flow and 3-CNF resolution

**Status:** BOUNDED_RESEARCH / NOT_CERTIFIED.  
**Date:** 2026-11-13.  
**Parent:** [Research attempt 001](MILLENNIUM_ATTACK_001.md).  
**Tracks:** Navier–Stokes global regularity, P versus NP via SAT.

Research attempt 001 ruled out two weak shortcuts (an energy-only critical-norm estimate and unit/pure-literal SAT simplification). Attempt 002 tests the *actual nonlinear PDE* on an explicit but restricted domain, and advances from 2-CNF to genuine width-three clauses and independently replayable resolution certificates. Neither task solves a Millennium problem, and both are standard or elementary constructions without a novelty claim.

## NS-002: a nontrivial exact solution of the full nonlinear Navier–Stokes equations

### Exact claim

On the flat torus \(\mathbb T^3=(\mathbb R/2\pi\mathbb Z)^3\), take \(\nu>0\) and

\[
U(x,y,z)=(\sin z+\cos y,\;\sin x+\cos z,\;\sin y+\cos x).
\]

Define for every \(t\geq0\)

\[
u(t,x)=e^{-\nu t}U(x),\qquad
p(t,x)=-\tfrac12e^{-2\nu t}|U(x)|^2.
\]

Then \(u,p\) are globally smooth, unforced, incompressible solutions of the **full nonlinear three-dimensional Navier–Stokes equations**

\[
\partial_tu+(u\cdot\nabla)u+\nabla p=\nu\Delta u,\qquad\nabla\cdot u=0.
\]

In particular, this is **not** a Stokes-only approximation. It is a known ABC/Beltrami solution on a periodic domain, and it is **not** a global-regularity theorem for arbitrary smooth finite-energy data on \(\mathbb R^3\).

### Analytical proof

Direct differentiation gives

\[
\nabla\cdot U=0,\qquad\nabla\times U=U,\qquad\Delta U=-U.
\]

For any sufficiently smooth vector field \(v\),

\[
(v\cdot\nabla)v=\nabla\frac{|v|^2}{2}-v\times(\nabla\times v).
\]

Since \(\nabla\times U=U\), the cross product vanishes. Thus

\[
(U\cdot\nabla)U=\nabla\left(\frac{|U|^2}{2}\right).
\]

Writing \(a(t)=e^{-\nu t}\), we obtain
\(\partial_tu=-\nu aU\),
\((u\cdot\nabla)u=a^2\nabla(|U|^2/2)\),
\(\nabla p=-a^2\nabla(|U|^2/2)\), and
\(\nu\Delta u=-\nu aU\). Both sides of the nonlinear PDE therefore agree identically for all \(t\).

The nonlinearity \((U\cdot\nabla)U\) is **not identically zero**. The pressure gradient balances it. For this field,

\[
\fint_{\mathbb T^3}|U|^2=3,\quad
\|u(t)\|_2^2=3(2\pi)^3e^{-2\nu t},\quad
\|\nabla u(t)\|_2^2=3(2\pi)^3e^{-2\nu t}.
\]

The identity \(\frac d{dt}\|u\|_2^2+2\nu\|\nabla u\|_2^2=0\) follows. For any \(T>0\), the mixed \(L^4(0,T;L^6(\mathbb T^3))\) norm is finite, but this regularity belongs to **this explicit special family**. The classical Prodi–Serrin criterion uses \(2/p+3/q=1\), including \((p,q)=(4,6)\), and requires an a priori finite norm; this special solution does not establish such a bound for arbitrary data.

### Reproducible Fourier identity check

The file \`mathos/research/millennium_attacks_002.py\` represents all six Fourier modes of \(U\) with dyadic-rational complex coefficients. It computes independently:
- divergence and curl by Fourier differentiation;
- Laplacian by the multipliers \(-|k|^2\);
- the **quadratic nonlinear convection** by Fourier convolution; and
- the pressure gradient by the Fourier coefficients of \(|U|^2/2\).

All arithmetic is exact for this small dyadic mode set. The tests require \((U\cdot\nabla)U\not\equiv0\) and verify that it equals the gradient exactly. This checks the derivation for the stated trigonometric polynomial; it is not a computer-assisted proof about all Navier–Stokes solutions.

### New obstruction and next targeted question

The ABC flow is a particularly favorable configuration: vorticity and velocity are parallel, so the Lamb-vector term \(u\times\omega\) vanishes. It therefore cannot be extrapolated to generic vortex stretching. A substantive next attempt is to add a smooth divergence-free perturbation \(w\), derive the exact evolution for \(w\) about \(u_{\mathrm{ABC}}\), isolate the nonzero interaction \((w\cdot\nabla)w+(w\cdot\nabla)u_{\mathrm{ABC}}+(u_{\mathrm{ABC}}\cdot\nabla)w\), and attempt a **conditional** stability inequality with explicit norms and constants. Uniform global control for arbitrary \(w\) remains unproved and would require new mathematics.

## PNP-002: genuine 3-CNF with an explicit short resolution refutation

### Exact family

Start with the contradictory parity-cycle 2-CNF of attempt 001 on \(x_1,\ldots,x_n\), \(n\ge3\): impose \(x_i=x_{i+1}\) for all \(i<n\), and \(x_1\ne x_n\). It has \(2n\) binary clauses.

For each binary clause \(C_j=(a_j\lor b_j)\), introduce a fresh variable \(z_j\) and replace the clause by

\[
(C_j\lor z_j)\land(C_j\lor\neg z_j).
\]

This creates **exactly \(4n\) clauses of width three** on **\(3n\) variables**. Every variable appears with both signs. There are no unit clauses or pure literals, and therefore the unit/pure-literal method from attempt 001 still stalls.

For any Boolean assignment (including any auxiliary values),

\[
(C_j\lor z_j)\land(C_j\lor\neg z_j)\;\longleftrightarrow\; C_j.
\]

This is a pointwise equivalence, not merely existential equisatisfiability. The new 3-CNF is unsatisfiable for every \(n\ge3\).

### Explicit resolution proof, only \(4n-1\) steps

Resolution combines \(A\lor v\) and \(B\lor\neg v\) into \(A\lor B\). The generated certificate:
1. resolves the two 3-clauses at each fresh auxiliary \(z_j\), recovering all \(2n\) original binary clauses in \(2n\) steps;
2. chains the equality implications to derive \(\neg x_1\lor x_n\) and \(x_1\lor\neg x_n\) in \(2(n-2)\) steps; and
3. resolves these against endpoint inequality clauses to derive \(\neg x_1\) and \(x_1\), then resolves to the empty clause in three steps.

The total is \(2n+2(n-2)+3=4n-1\) resolution steps. This is an **upper bound for one deliberately easy unsatisfiable 3-CNF family**, not a worst-case algorithmic bound.

The Python module returns explicit initial clauses and parent/pivot references for every derived clause. A separate verifier replays the rules, rejects future/nonexistent parents and wrong pivots, and demands a final empty clause. Regression tests also corrupt certificates to verify that the checker rejects them, independently brute-force small instances \(n=3,4\), and check pointwise lifting equivalence over all assignments for \(n=3\).

### What this does and does not show

This demonstrates that the absence of unit clauses and pure literals is **not** evidence of difficult 3-SAT instances: resolution solves this family linearly even though the local method is stuck. It does not yield an exponential lower bound for resolution, DPLL, CDCL, general Boolean circuits, or arbitrary Turing machines, and says nothing new about \(\mathrm P=\mathrm{NP}\).

A serious next attack should specify a **restricted proof system** and investigate a genuinely hard family with a quantified lower-bound statement. Even proving such a system-specific lower bound would not settle unrestricted \(\mathrm P\) versus \(\mathrm{NP}\).

## Reproduce

Python 3.10–3.12, standard library only:

\`\`\`sh
python -m unittest discover -s tests -p 'test_millennium_attacks_002.py' -v
python -m mathos.research.millennium_attacks_002
\`\`\`

Results are mathematical **checks for exact examples and proof certificates**, not an independent specialist review. The existing register \`docs/proof-analysis/OBLIGATIONS.v1.md\` remains **NOT_CERTIFIED**. No open Millennium obligation has been promoted.

## References and novelty boundary

- [ABC flows on the torus and their Beltrami property](https://pmc.ncbi.nlm.nih.gov/articles/PMC11962483/) — published established mathematics, not a novel discovery.
- [Galloway–Frisch, stability of periodic Beltrami flows](https://electronicsandbooks.com/edt/manual/Magazine/J/Journal%20of%20Fluid%20Mechanics/1987%20Volume%20180/S0022112087001952.pdf) — notes that the unforced ABC solution decays as \(e^{-\nu t}\).
- [Pineau–Yu, Prodi–Serrin conditions](https://www.sciencedirect.com/science/article/pii/S0362546X19302573) — external context for conditional 3D Navier–Stokes regularity.

The algebra and resolution-certificate construction above are self-contained and use only elementary, already-known identities. A passing CI run is not a claim to have solved either Millennium problem.
