# A two-dimensional primitive middle-cohomology space on a product of four projective lines

**MathOS Millennium milestone HODGE-001 · 2026-11-24 · Unreviewed bounded technical note**

## Abstract

Do the three pair-difference products span the primitive degree-four kernel on (P¹)^4? Exact rational elimination confirms rank 4, kernel dimension 2, pairing span rank 2 and the stated relation. This is a project research milestone, not an assertion of mathematical priority or a Millennium solution.

## 1. Question and relation to previous work

Do the three pair-difference products span the primitive degree-four kernel on (P¹)^4? This follows the [November 23 research notebook](../../daily/2026-11-23.md).

## 2. Mathematical argument and method

Use rational cohomology Q[A1,A2,A3,A4]/(Ai²), deg Ai=2, and H=ΣAi. Multiplication by H from degree four to degree six has columns indexed by pairs and rows by triples, entry 1 exactly for inclusion. Its four rows are independent: each pair belongs to two triples, so a row relation would imply that every pair of row coefficients sums to zero; three distinct indices force each coefficient zero. Thus rank=4, kernel dimension=6−4=2. Define D_ij|kl=(Ai−Aj)(Ak−Al). All three pairings are primitive by Ai²=0, D12|34−D13|24+D14|23=0 by expansion, and the first two are independent by inspecting coefficients (A1A2 and A1A3). They span the entire kernel. Each is an explicit algebraic divisor-product combination.

## 3. Observed results

Exact rational elimination confirms rank 4, kernel dimension 2, pairing span rank 2 and the stated relation.

```json
{
  "multiplication_rank": 4,
  "primitive_dimension": 2,
  "pairing_span_rank": 2,
  "relation": "D12|34 - D13|24 + D14|23 = 0"
}
```

## 4. Reproducibility and evidence

Pinned source: [f5345f298feec5ae4fe24b1de50b8ff737465ce6](https://github.com/tltmgnt/MathOS/blob/f5345f298feec5ae4fe24b1de50b8ff737465ce6/mathos/research/millennium_followup_20261124.py). [Execution logs and artifact](https://github.com/tltmgnt/MathOS/actions/runs/45362915859).

```sh
python -m unittest discover -s tests -p 'test_millennium_followup_20261124.py' -v
python -m mathos.research.millennium_followup_20261124
```

## 5. Scope and limitations

Classical cohomology ring assumed, not formalized here. A specific product with known algebraic generators; no general primitive Hodge-class construction. No independent external review or literature-novelty determination has been obtained. No global proof status is promoted.

## 6. Next research obligation

Study primitive middle-degree cycle generation on (P¹)^{2m} and compare with varieties having nontrivial transcendental cohomology.
