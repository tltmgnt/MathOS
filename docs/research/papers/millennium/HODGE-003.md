# Explicit invariant and primitive divisor-product ranks on the fourth power of a non-CM elliptic curve

**MathOS Millennium milestone HODGE-003 · 2026-11-24 · Unreviewed bounded technical note**

## Abstract

Can the primitive calculation be extended from projective lines to a positive-genus product with cross-factor degree-one cohomology? 10 independent degree-two classes, 55 products tested, rank 20 in degree four and primitive dimension 10. These are exact finite linear-algebra results given the stated classical inputs. This is a project-level research milestone; no new global Millennium solution or literature priority is asserted.

## 1. Research obligation

Can the primitive calculation be extended from projective lines to a positive-genus product with cross-factor degree-one cohomology? Follows [HODGE-002](HODGE-002.md).

## 2. Mathematical argument and method

Take a complex elliptic curve E without complex multiplication. Use as classical external inputs the exterior algebra H*(E⁴,Q)=∧*(H¹(E,Q)^⊕4), the special Mumford–Tate group SL₂ for non-CM E, the equivalence of rational Hodge classes with its invariants in even degrees, and Lefschetz (1,1). A symplectic rational basis e_i,f_i gives four invariant divisor classes e_i∧f_i and six cross-factor classes e_i∧f_j−f_i∧e_j (i<j). They are invariant determinants and thus rational algebraic divisor classes by Lefschetz (1,1). In ∧⁴ of four copies of the standard SL₂ module, the weight-zero subspace has dimension C(4,2)²=36 and weight-two dimension C(4,3)C(4,1)=16. In a semisimple SL₂ representation their difference counts trivial summands, hence 20 invariants. Enumerate the 55 unordered products of the 10 divisors (including squares), using exact antisymmetric wedge signs in the 70-dimensional exterior basis. Exact rational elimination gives rank 20. Cup product with H=Σe_i∧f_i (product polarization) maps this span to ∧⁶ with rank 10, giving a 10-dimensional primitive Hodge subspace; every vector is a rational divisor-product combination. External reference: D. Arapura, notes on complex algebraic geometry, sections 6.6–6.7 and Proposition 8.3.2, https://www.math.purdue.edu/~arapura/preprints/cmplAG.pdf . The classical Hodge theorem for elliptic powers is prior work; this calculation is a scoped reconstruction.

## 3. Observed results

10 independent degree-two classes, 55 products tested, rank 20 in degree four and primitive dimension 10. These are exact finite linear-algebra results given the stated classical inputs.

## 4. Reproducibility

Pinned source: [2b5f3a9ffc3177681695afd9d471d1ca1448188a](https://github.com/tltmgnt/MathOS/blob/2b5f3a9ffc3177681695afd9d471d1ca1448188a/mathos/research/millennium_followup_round3.py). [Execution evidence](https://github.com/tltmgnt/MathOS/actions/runs/45366064464). Full report: [round3-evidence.json](round3-evidence.json).

```sh
python -m unittest discover -s tests -p 'test_millennium_followup_round3.py' -v
python -m mathos.research.millennium_followup_round3
```

## 5. Limitations

Does not establish the Hodge group theorem, Lefschetz theorem or the general Hodge conjecture. No novelty relative to the classical Tate result. Independent review and prior-art novelty assessment remain outstanding.

## 6. Next research obligation

Extract explicit primitive bases with rational coefficients, then study mixed products and the failure of divisor generation for nontrivial transcendental Hodge structures.
