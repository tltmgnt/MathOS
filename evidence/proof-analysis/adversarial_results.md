# Topological adversarial analysis

Stress tests of seven precisely stated shortcuts; no automatic theorem discovery or Millennium solutions.

All findings below are scoped to the stated shortcut. Abstract witnesses do not satisfy the full geometric or arithmetic hypotheses of the Millennium Problems.

| Problem | Evidence | Outcome |
|---|---|---|
| Birch-Swinnerton-Dyer | EXACT_LINEAR_ALGEBRA_COUNTERMODEL | ABSTRACT_SHORTCUT_REFUTED |
| Hodge | EXACT_ABSTRACT_LINEAR_MAP_COUNTERMODEL | ABSTRACT_SHORTCUT_REFUTED |
| Navier-Stokes | EXACT_FIELD_AND_SCALING | SHORTCUT_REFUTED |
| P-versus-NP | EXACT_EXPANSION_AND_GENERAL_COUNTING_ARGUMENT | SHORTCUT_REFUTED |
| Poincare | EXACT_FINITE_GROUP_COUNTERMODEL | WEAK_TOPOLOGICAL_PROXY_REFUTED |
| Riemann | EXACT_POLYNOMIAL_COUNTEREXAMPLE | SHORTCUT_REFUTED |
| Yang-Mills | EXACT_ABSTRACT_LIMIT_COUNTERMODEL | SHORTCUT_REFUTED |

## Birch-Swinnerton-Dyer

**Tested claim:** Existence of a nondegenerate alternating pairing alone determines the dimension of the underlying vector space.

**Result:** Block diagonal symplectic forms are nondegenerate in dimensions 2,4,8, and in every positive even dimension. Duality alone does not select one dimension.

**Limit:** These vector spaces are not Selmer groups or elliptic curves; no counterexample to BSD or its actual arithmetic duality statements is claimed.

**Next obligation:** Prove the precise analytic/arithmetic comparison; additional arithmetic input is indispensable.

## Hodge

**Tested claim:** Declaring a rational cohomological space to be of type (p,p) forces a specified cycle map onto it.

**Result:** In Q^2, the image of q -> (q,0) misses (0,1), regardless of an assigned type label. Surjectivity does not follow from these abstract data.

**Limit:** Not realized as the cycle map of a smooth projective variety. Thus this is not a Hodge counterexample and cannot refute arguments using additional geometric structure.

**Next obligation:** Use the actual geometry to construct rational algebraic cycles and prove coverage.

## Navier-Stokes

**Tested claim:** Helicity and dilation-preserved vortex topology alone bound vorticity magnitude for all smooth decaying divergence-free initial fields.

**Result:** Positive dilation preserves vortex-line topology. The family u_lambda(x)=lambda*u(lambda*x) has identical zero helicity and |omega_lambda(0)|=4*lambda^2. Thus no finite bound depending only on these fixed invariants can hold on this family.

**Limit:** Initial fields only, not a singular evolving solution. Does not reject estimates using additional quantitative hypotheses or all possible geometric approaches.

**Next obligation:** Prove a quantitative bound with enough geometric and analytic information to close a continuation criterion.

## P-versus-NP

**Tested claim:** Explicit expansion of the satisfaction polynomial always has polynomially many monomials.

**Result:** Each factor has three choices with distinct variable-pair supports. Different choices yield distinct monomials of coefficient +/-1. Hence there are exactly 3^m nonzero monomials for every m>=0.

**Limit:** No lower bound for arbitrary SAT algorithms or compressed representations. Does not resolve P versus NP.

**Next obligation:** Specify an algorithm and bound its full bit complexity; a topological invariant also needs an efficient construction and evaluation theorem.

## Poincare

**Tested claim:** Trivial abelianization of a fundamental group implies that the group is trivial.

**Result:** A5 is nontrivial but equals its commutator subgroup. First homology detects the abelianization and cannot generally replace a simple-connectivity check.

**Limit:** No closed three-manifold is constructed here, and no challenge to Perelman is implied. Refutes the group-theoretic shortcut only.

**Next obligation:** Retain exact fundamental-group hypotheses and reconstruct the established geometric argument.

## Riemann

**Tested claim:** Evenness, real coefficients and strict positivity on the real axis force all zeros of an entire function to be real.

**Result:** The polynomial is even and >=1 on the real axis. The displayed nonreal z satisfies z^4+1=0 exactly.

**Limit:** Not the zeta or xi function; only refutes a symmetry/positivity-only implication.

**Next obligation:** Construct a noncircular spectral realization and prove the exact zero correspondence.

## Yang-Mills

**Tested claim:** A positive gap at every regulator value necessarily gives a positive limiting physical gap.

**Result:** Let spacing a_n=1/n and dimensionless gap mu_n=a_n^2>0. The physical gap mu_n/a_n=1/n tends to zero despite positivity at each n.

**Limit:** Abstract sequence, not Yang-Mills. No assertion that this sequence occurs in that theory; fixed topological sectors would not supply the missing energy estimate.

**Next obligation:** Establish a nontrivial continuum theory and a strictly positive regulator-uniform physical gap.

## Reproduce

Python 3.10+ and standard library only.

```sh
python -m unittest discover -s tests -p "test_proof_*.py" -v
python -m mathos.proof_analysis --output-dir artifacts/proof-analysis
```

This is a fixed suite of exact witnesses and authored arguments, not a general counterexample search engine. Passing tests establish program behavior; formal proof checking and external mathematical review remain outstanding.
