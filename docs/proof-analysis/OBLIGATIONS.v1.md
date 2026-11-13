# MathOS proof-obligation register v1.0.0

Date: 2026-11-13. Source: [gap_analysis.py](../../mathos/proof_analysis/gap_analysis.py) and [review handoff](HANDOFF.md).

**Scope:** This is a review register for *authored routes*, not seven solved proofs, a formal certificate, or a list of independent mathematical axioms. Mathematical edges and generic background assumptions remain unverified. Current overall certification: **NOT_CERTIFIED**.

## Status

| Model | Target in repository | Open work packages | Graph interpretation |
|---|---|---:|---|
| Birch-Swinnerton-Dyer | Full BSD for elliptic curves over Q | 3 | BLOCKED under authored route |
| Hodge | Rational Hodge conjecture | 2 | BLOCKED under authored route |
| Navier-Stokes | Unforced global smoothness branch | 1 | BLOCKED under authored route |
| P-versus-NP | P=NP via SAT | 2 | BLOCKED under authored route |
| Poincare | Our independent proof reconstruction | 1 | BLOCKED under authored route |
| Riemann | Riemann hypothesis via spectral realization | 2 | BLOCKED under authored route |
| Yang-Mills | Four-dimensional Yang-Mills existence and mass gap | 3 | BLOCKED under authored route |

Poincaré's **published theorem** is recorded separately as `established_external`; **MathOS independent reconstruction remains open**. P versus NP models only the P = NP route, not the P != NP route. None of the open work packages below is a verified proof.

## Obligations by track

### Birch-Swinnerton-Dyer — Full BSD for elliptic curves over Q

The leading-term obligation overlaps other work packages; this is not a decomposition into independent lemmas.

- **`BSD.analytic_selmer` (open):** Prove the general complex analytic rank / Selmer corank comparison. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`BSD.sha_finiteness` (open):** Prove finiteness of the Tate-Shafarevich group. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`BSD.leading_term` (open):** Prove the full leading-term identity with specified normalizations. **Evidence:** no proof artifact; no formal replay; subject review pending.

### Hodge — Rational Hodge conjecture

The primitive case may restate the central conjecture; reduction validity requires specialist review.

- **`HODGE.primitive_cycles` (open):** Construct rational algebraic cycle representatives for all remaining primitive rational Hodge classes on all smooth projective varieties. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`HODGE.reduction` (open):** Prove coverage of all classes from primitive cases, including rationality and algebraicity of every reduction. **Evidence:** no proof artifact; no formal replay; subject review pending.

### Navier-Stokes — Unforced global smoothness branch

One proposed sufficient route, not an assessment of other approaches or announcements.

- **`NS.critical_bound` (open):** Prove an a priori L^4_t L^6_x bound up to every finite candidate breakdown time for all admissible data. **Evidence:** no proof artifact; no formal replay; subject review pending.

### P-versus-NP — P=NP via SAT

Models only the P=NP direction. Failure does not prove P!=NP.

- **`PNP.sat_correctness` (open):** Supply a fully specified deterministic SAT algorithm and prove correctness. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`PNP.sat_runtime` (open):** Prove polynomial worst-case total bit complexity, including all intermediate representations. **Evidence:** no proof artifact; no formal replay; subject review pending.

### Poincare — Our independent proof reconstruction

The Poincare conjecture itself is recorded as externally established via Perelman's proof; independent reconstruction is a separate open project.

- **`POINCARE.reconstruction` (open):** Supply a complete independently checked reconstruction of the proof. **Evidence:** no proof artifact; no formal replay; subject review pending.

### Riemann — Riemann hypothesis via spectral realization

The spectral identity must be noncircular and account for zero multiplicities and any regularization.

- **`RH.operator` (open):** Construct an independently defined self-adjoint operator with a rigorous domain. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`RH.zero_identity` (open):** Prove a spectral/determinant identity accounting for every nontrivial zero with multiplicity. **Evidence:** no proof artifact; no formal replay; subject review pending.

### Yang-Mills — Four-dimensional Yang-Mills existence and mass gap

These work packages interact; they are not independently verified.

- **`YM.continuum` (open):** Construct a nontrivial continuum limit for each required compact simple gauge group. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`YM.axioms` (open):** Verify the required quantum-field axioms and reconstruction hypotheses. **Evidence:** no proof artifact; no formal replay; subject review pending.
- **`YM.uniform_gap` (open):** Prove regulator-uniform bounds yielding a strictly positive physical spectral gap. **Evidence:** no proof artifact; no formal replay; subject review pending.

## Bounded subresults and verification targets

- **`GRAPH1`:** An informal induction argument exists for inclusion-minimal completion-set recurrence on finite acyclic Boolean AND/OR graphs. Formal replay and concrete Python correctness verification have **not** been performed. The graph's authored mathematical edges remain assumptions.
- **`SAT1`:** The expansion of `PRODUCT_i(x_i + y_i - x_i*y_i)` over distinct variable pairs has exactly `3**m` monomials by an informal combinatorial proof. No proof-assistant certificate exists; it is not a lower bound for arbitrary SAT algorithms.
- **`POINCARE.published`:** Established externally, not independently proved by MathOS. `POINCARE.reconstruction` stays open.

## Promotion gate

To update an `open` obligation, record (1) exact quantified theorem statement and hypotheses, (2) precise source and theorem locator or proof artifact, (3) why it implies the specific target route, (4) review findings, and (5) any formal proof-assistant result with its trusted axioms. Do not mark a Millennium problem solved from software tests, a closed Boolean graph, or a conditional theorem.

The accompanying [machine-readable register](OBLIGATIONS.v1.json) is checked against the IDs, statements and leaf states of `models()` by [the register regression test](../../tests/test_proof_obligation_register.py).
