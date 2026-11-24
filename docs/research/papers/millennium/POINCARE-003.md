# Vanishing distortion at surgery times: a source-traced conditional width comparison

**MathOS Millennium milestone POINCARE-003 · 2026-11-24 · Unreviewed bounded technical note**

## Abstract

Does the actual surgery comparison use summable fixed jump factors or a limiting nonexpansion property? Six exact rational squeeze controls passed, and the primary-source comparison mechanism was traced to Remark 73.6. The algebraic jump factor in the limit is 1. This is a project-level research milestone; no new global Millennium solution or literature priority is asserted.

## 1. Research obligation

Does the actual surgery comparison use summable fixed jump factors or a limiting nonexpansion property? Follows [POINCARE-002](POINCARE-002.md).

## 2. Mathematical argument and method

The published Colding–Minicozzi paper Width and finite extinction time of Ricci flow (Geometry & Topology 12, 2008), Theorem 1.4, equations (1.5)–(1.6), and Corollary 1.7 treat the width inequality and extinction. Its discussion after Corollary 1.7 refers to Kleiner–Lott, Notes on Perelman's papers (2008), Remark 73.6, pp. 2762–2763, where comparison homotopy equivalences from nearby presurgery slices to the surviving postsurgery component have distance expansion bounded by a function ξ(t')→1 as t' approaches the surgery time. Perelman, finite extinction note §1.3, likewise uses almost nonexpanding maps, while his own functional uses filling disks (§1.2). Conditional reconstruction: for a consistently transported sweepout class, composing each slice with the map gives W_+≤ξ(t')² W(t'). If the presurgery width has finite liminf, take a sequence attaining it and pass to the limit to obtain W_+≤liminf W(t'). Thus there is no upward jump and P=1 in POINCARE-002; no summability hypothesis on fixed positive distortions is needed in this limiting argument. Under local finiteness of surgery times, smooth-time inequality, and persistence of the relevant nontrivial class, the integrated width comparison chains across surgeries. For an exact toy squeeze take W(t_j)=3+1/j, ξ=1+1/j; the bound is 3+7/j+5/j²+1/j³≤3+13/j. Sources: https://msp.org/gt/2008/12-5/gt-v12-n5-p02-p.pdf ; https://math.berkeley.edu/~lott/gt-2008-12-059p.pdf ; https://arxiv.org/abs/math/0307245 . The earlier notes cite arXiv numbering; the published paper uses Theorem 1.4, not Theorem 1.7.

## 3. Observed results

Six exact rational squeeze controls passed, and the primary-source comparison mechanism was traced to Remark 73.6. The algebraic jump factor in the limit is 1.

## 4. Reproducibility

Pinned source: [2b5f3a9ffc3177681695afd9d471d1ca1448188a](https://github.com/tltmgnt/MathOS/blob/2b5f3a9ffc3177681695afd9d471d1ca1448188a/mathos/research/millennium_followup_round3.py). [Execution evidence](https://github.com/tltmgnt/MathOS/actions/runs/45366064464). Full report: [round3-evidence.json](round3-evidence.json).

```sh
python -m unittest discover -s tests -p 'test_millennium_followup_round3.py' -v
python -m mathos.research.millennium_followup_round3
```

## 5. Limitations

The source's geometric map construction, coherent class transport, width regularity and local finiteness are not proved here; the scalar test is not Ricci-flow simulation or a full independent reconstruction. The Poincaré theorem was already solved externally. Independent review and prior-art novelty assessment remain outstanding.

## 6. Next research obligation

Trace the construction in Kleiner–Lott §73 and Perelman surgery paper §4.4, and establish the nontrivial sweepout-class transport and finite surgery count with expert review.
