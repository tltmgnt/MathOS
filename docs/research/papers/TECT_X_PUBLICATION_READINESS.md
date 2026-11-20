# ResearchOS | TECT-X — manuscript scope, reproducibility, and submission gate

**Status:** PRELIMINARY WORKING MANUSCRIPT / NOT PEER REVIEWED / NOT SUBMITTED  
**Manuscript:** [TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex](TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex)  
**Date:** 19 November 2026

## Theorems actually supplied

1. For (n=5+759m) with (m\ge0), the elliptic curves
   (E_n:y^2=x^3-a_n^2x+b_n^2),
   (a_n=(n^2+27)/(27-n^2)), (b_n=6n/(27-n^2)),
   have no rational 2-torsion. Three displayed rational points
   are independent in (E_n(\mathbb Q)/2E_n(\mathbb Q)). This
   establishes a rank lower bound of three.
2. The (j)-invariant is nonconstant and assumes infinitely many values.
3. At (n=5), the additional point ((-18,81)) is independent of
   the three points modulo doubling, establishing rank at least four.
   Thus a blanket Selmer-dimension-three claim over the full
   progression is false.
4. **Conditional only:** If the average 2-Selmer cardinality among
   (m<X) is eventually at most (16-\varepsilon), then at least
   ((\varepsilon/8)X) fibers have Selmer dimension exactly three,
   exact rank three and (\Sha[2]=0).

## Non-claims / material publication blockers

- **OPEN:** no proof of the mean 2-Selmer cardinality bound below 16;
  no proved infinite subset on which the three Kummer classes exhaust
  the full 2-Selmer group.
- **OPEN:** no uniform control of the varying cubic-field class-group
  2-torsion and local Kummer conditions.
- **NOT CHECKED:** no independent numerical `Selmer_2` computation
  for a positive sample of fibers using Magma or Sage.
- **OPEN:** no original statistical theorem for this thin progression.
- **NOT ESTABLISHED:** novelty of the elementary point construction or
  moment implication, journal-level significance, analytic rank,
  finiteness of the full Tate--Shafarevich group or any BSD leading term.
- **PENDING:** specialist proof review and complete bibliography audit;
  author attribution, acknowledgments, licensing/rights and choice of
  venue have not been approved.

The manuscript may be circulated as a **clearly labeled preliminary
research note** if authorship and proof attribution are settled.
Do not label it an accepted paper, independently certified theorem,
new BSD proof, or proof of positive-density exact-rank-three fibers.

## Reproducibility

Run from the MathOS repository root:

```sh
python -m mathos.research.tect_x_rank3_family_certificate
python -m mathos.research.tect_x_rank4_fiber_certificate
python -m unittest discover -s tests -p 'test_tect_x_noni_selmer.py' -v
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory /tmp docs/research/papers/TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex
```

The code checks finite arithmetic witnesses and rejects any inferred
global Selmer dimension. The LaTeX build checks typesetting only, not
mathematical correctness. Review all third-party citations before
submission, especially later preprint/journal revisions.

## Independent review checklist

- [ ] Independently verify each marked point and every good reduction.
- [ ] Confirm the 3, 5, 11 and 23 finite-field calculations without
      reusing the same code path.
- [ ] Recheck the cubic-field change of variables and Kummer
      representatives, and distinguish candidate local-condition
      matrices from a constructed global Selmer computation.
- [ ] Audit Schaefer--Stoll descent, Bhargava--Shankar generic height
      averages, Bhargava--Ho marked-point families, Zywina's rank
      results, and other relevant literature for novelty and scope.
- [ ] Independently verify the conditional average-size argument.
- [ ] Obtain specialist review of mathematical statements and
      assumptions; record reviewer remarks and required corrections.
- [ ] Establish the genuinely new arithmetic-statistics theorem,
      or submit only as an appropriately scoped preliminary note.
- [ ] Confirm authorship, rights, venue and submission formatting.

## Related source records

- [TECT-X original proof-scope audit](../TECT_X_NONISOTRIVIAL_SELMER_AUDIT.md)
- [MathOS BSD local-factor research track](../MILLENNIUM_ATTACK_007.md)
- [Bhargava--Shankar, Annals (2015)](https://annals.math.princeton.edu/2015/181-1/p03)
- [Schaefer--Stoll, full p-descent methods](https://eref.uni-bayreuth.de/id/eprint/6228/)
- [Bhargava--Ho, marked-point families](https://arxiv.org/abs/2207.03309)
- [Zywina, nonjump elliptic surface (2025)](https://arxiv.org/abs/2502.01026)
- [Zywina, prescribed small ranks (2026)](https://arxiv.org/abs/2602.10865)
