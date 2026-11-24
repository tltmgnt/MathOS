# Conditional integrating-factor extinction estimate across summably controlled surgery jumps

**MathOS Millennium milestone POINCARE-001 · 2026-11-24 · Unreviewed bounded technical note**

## Abstract

Can the smooth-time width inequality be chained across surgeries with bounded sum of distortion parameters? The initial 19-step budget failed to reach negativity (run 45362861519); extending to the proved finite horizon produced the first negative value at step 22. This is a toy comparison result, not a geometry simulation. This is a project research milestone, not an assertion of mathematical priority or a Millennium solution.

## 1. Question and relation to previous work

Can the smooth-time width inequality be chained across surgeries with bounded sum of distortion parameters? This follows the [November 23 research notebook](../../daily/2026-11-23.md).

## 2. Mathematical argument and method

Assume C>0, W≥0 and on smooth intervals V=W(t)(t+C)^(−3/4) satisfies V'≤−4π(t+C)^(−3/4). Assume locally finite surgery times t_j, V(t_j+)≤(1+ξ_j)^2 V(t_j−), ξ_j≥0, and Σξ_j≤S<∞. Set P(t)=∏_{t_j≤t}(1+ξ_j)^2. Then 1≤P≤e^(2S); V/P cannot increase at jumps and satisfies (V/P)'≤−4π e^(−2S)(t+C)^(−3/4) between jumps. Integrate to obtain V(t)/P(t)≤V(0)−16π e^(−2S)[(t+C)^(1/4)−C^(1/4)]. This is eventually negative if all hypotheses and nonnegative width persist, a conditional extinction contradiction. The rational toy uses r=(t+C)^(1/4), width normalized by 16π, initial value 5, unit r intervals and ξ_j=2^(−j). Since S≤1 and e²<8, more than 40 intervals suffice; exact replay detects negativity earlier.

## 3. Observed results

The initial 19-step budget failed to reach negativity (run 45362861519); extending to the proved finite horizon produced the first negative value at step 22. This is a toy comparison result, not a geometry simulation.

```json
{
  "conditional_only": true,
  "toy_first_negative_step": 22,
  "final_rescaled_width_sign": "negative",
  "steps_checked": 22
}
```

## 4. Reproducibility and evidence

Pinned source: [f5345f298feec5ae4fe24b1de50b8ff737465ce6](https://github.com/tltmgnt/MathOS/blob/f5345f298feec5ae4fe24b1de50b8ff737465ce6/mathos/research/millennium_followup_20261124.py). [Execution logs and artifact](https://github.com/tltmgnt/MathOS/actions/runs/45362915859).

```sh
python -m unittest discover -s tests -p 'test_millennium_followup_20261124.py' -v
python -m mathos.research.millennium_followup_20261124
```

## 5. Scope and limitations

The width inequality, surgery comparison, locally finite jumps, persistence of transported sweepout class and summable control are assumed. The actual geometric hypotheses must be established in a reconstruction of Perelman’s already accepted proof. See Perelman arXiv:math/0307245 and Colding–Minicozzi arXiv:0707.0108, Theorem 1.7 and equation (1.8), as referenced in the prior notebook. No independent external review or literature-novelty determination has been obtained. No global proof status is promoted.

## 6. Next research obligation

Map the summability and comparison assumptions to precise geometric statements in the Ricci-flow proof; distinguish conditional algebra from independently reconstructed geometric arguments.
