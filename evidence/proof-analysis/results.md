# Proof dependency gap analysis

Author-modeled proof dependencies; no theorem proving or new mathematical certification.

These are sufficient-route work packages, not minimal mathematical axioms. Counts are not difficulty scores.

| Problem / attempted route | Status | Unresolved work packages |
|---|---|---|
| Birch-Swinnerton-Dyer | BLOCKED | 3 |
| Hodge | BLOCKED | 2 |
| Navier-Stokes | BLOCKED | 1 |
| P-versus-NP | BLOCKED | 2 |
| Poincare | BLOCKED | 1 |
| Riemann | BLOCKED | 2 |
| Yang-Mills | BLOCKED | 3 |

## Birch-Swinnerton-Dyer

Full leading-term identity overlaps the other obligations. Graph tracks work packages, not independent axioms.

- Prove the general complex analytic rank / Selmer corank comparison
- Prove the full leading-term identity with specified normalizations
- Prove finiteness of the Tate-Shafarevich group

## Hodge

The primitive-class obligation remains a major geometric theorem, not an implemented construction.

- Construct rational algebraic cycle representatives for all remaining primitive rational Hodge classes on all smooth projective varieties
- Prove coverage of all classes from primitive cases, including rationality and algebraicity of every reduction

## Navier-Stokes

Uses the established continuation criterion. This is one sufficient branch, not a review of announced forced-breakdown proofs.

- Prove an a priori L^4_t L^6_x bound up to every finite candidate breakdown time for all admissible data

## P-versus-NP

Only a P=NP route is modeled. Failure does not imply P!=NP. Explicit expansion route is refuted separately.

- Supply a fully specified deterministic SAT algorithm and prove correctness
- Prove polynomial worst-case total bit complexity, including all intermediate representations

## Poincare

Independent reconstruction remains incomplete.

- Supply a complete independently checked reconstruction of the proof

## Riemann

The identity must be noncircular and include any determinant regularization and nonvanishing factors.

- Construct an independently defined self-adjoint operator with a rigorous domain
- Prove a spectral/determinant identity accounting for every nontrivial zero with multiplicity

## Yang-Mills

These are coupled work packages. No continuum construction or gap proof is supplied.

- Verify the required quantum-field axioms and reconstruction hypotheses
- Construct a nontrivial continuum limit for each required compact simple gauge group
- Prove regulator-uniform bounds yielding a strictly positive physical spectral gap

Poincare is externally established; only our independent reconstruction is blocked.

## SAT route rejection

Each factor has three nonzero terms on disjoint variables; choices yield distinct monomials, so no cancellation is possible.
Exact monomial count: 3**m. This rejects explicit expansion as a generally polynomial-size step; it does not resolve P versus NP.

## Reproduce

`python -m unittest discover -s tests -p "test_proof_*.py" -v`

`python -m mathos.proof_analysis --output-dir artifacts/proof-analysis`

No numerical confidence, independent-verification Boolean, or graph status is treated as mathematical proof.
