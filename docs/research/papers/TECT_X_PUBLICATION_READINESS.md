# ResearchOS | TECT-X — manuscript scope, reproducibility, and submission gate

**Status:** PRELIMINARY WORKING MANUSCRIPT / NOT PEER REVIEWED / NOT SUBMITTED  
**Manuscript:** [TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex](TECT_X_NONISOTRIVIAL_SELMER_PRELIMINARY.tex)  
**Date:** 19 November 2026

## New literature finding: rank-three Pell family and points are prior art

The model `y²=x³−a²x+b²`, the Pell condition `a²−3b²=1` and
**all three original rational points** `(0,b)`, `(a,b)`, `(-1,2b)`
are explicitly documented by Patel, Chakraborty and Chattopadhyay,
*Two infinite families of elliptic curves with Mordell–Weil rank at
least 3*, Czechoslovak Mathematical Journal (published online
26 October 2026), DOI [10.21136/CMJ.2026.0080-26](https://doi.org/10.21136/CMJ.2026.0080-26).
Its proof treats an integer Pell subfamily and includes `26+15√3`
as a seed. Our rational parameterization and modular certificate may
provide a distinct presentation but cannot be marketed as the
original discovery of the model, points or rank-three mechanism.

A related published study by the same authors,
*On the Mordell–Weil rank and 2-Selmer group of a family of elliptic
curves*, Ramanujan J. **69** (2026), article 46,
[DOI 10.1007/s11139-026-01317-5](https://doi.org/10.1007/s11139-026-01317-5),
must be reviewed for overlap of exact descent techniques.
Zywina's [2026 theorem](https://arxiv.org/abs/2602.10865) already
establishes infinitely many geometrically distinct rank-three
curves in general; that conclusion is not novel here.

**Journal submission as a NEW Selmer-infinitude theorem remains
strictly blocked** until a genuine, independently checked
unconditional Selmer-dimension-three infinitude proof exists.

See [target theorem proof modules](TECT_X_SELMER_INFINITUDE_PROOF_OBLIGATIONS.md)
and [machine-readable submission gate](TECT_X_SUBMISSION_STATUS.v1.json).

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

## Automated status audit (not a proof checker)

Run `python -m mathos.research.tect_x_submission_gate` to print
the current blockers and `python -m mathos.research.tect_x_submission_gate
--require-ready` to return a nonzero exit status until they are
discharged. Independent human proof review is indispensable even
after all declarations are updated. CI also checks the blocked state.

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
