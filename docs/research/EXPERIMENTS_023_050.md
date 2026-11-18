# MathOS experiments 023–050 — prospective evaluation protocol v1

**Registry status:** 28 distinct, executable experiment **protocols** (MathOS-EXP-023 through MathOS-EXP-050).  
**Prior results:** MathOS-EXP-001 through MathOS-EXP-022 are documented in [the v0.1 research report](MATHOS_RESEARCH_REPORT_v0.1.md).  
**Execution status (2026-11-18):** **28/28 experimental conditions were executed on each of the two models**, with all eight model jobs and the baseline job successful. The [observed results report](EXPERIMENTS_023_050_RESULTS.md) links the exact workflow run and [checksum-bearing manifest](../../evidence/internal_reasoning/EXPERIMENTS_023_050_SUMMARY.json). Execution is not independent replication or evidence of general mathematical understanding.

The frozen protocol source is [experiments_023_050.py](../../experiments/internal_reasoning/experiments_023_050.py). These are exploratory arithmetic tests on **DistilGPT2** and **sshleifer/tiny-gpt2**, not demonstrations of mathematical understanding, large-model capabilities, scientific replication or independent proof. The preregistered comparison is deliberately limited to strict-start integer parsing, per-condition accuracy, parsed-only absolute error, two fixed constant-answer baselines (zero and nine), and—where applicable—paired semantic consistency.

## Design and distinct experiment IDs

| ID | Contrast / population | ID | Contrast / population |
|---|---|---|---|
| 023 | Out-of-grid two-digit addition | 037 | Two-digit × one-digit multiplication |
| 024 | Additive identity with zero | 038 | Addition commutativity (paired) |
| 025 | Mixed-sign addition | 039 | Multiplication commutativity (paired) |
| 026 | Both-negative addition | 040 | Addition associativity (paired) |
| 027 | Two-digit addition with carry | 041 | Subtraction order / negation (paired) |
| 028 | Two-digit addition without carry | 042 | Add-subtract cancellation (paired) |
| 029 | Three-digit addition | 043 | Distribution vs expansion (paired) |
| 030 | Doubling a repeated operand | 044 | Addition in word-problem form |
| 031 | Subtraction yielding a positive answer | 045 | Subtraction in word-problem form |
| 032 | Subtraction yielding a negative answer | 046 | Multiplication in word-problem form |
| 033 | Subtracting zero / zero minus positive | 047 | Direct question: addition |
| 034 | Small-integer multiplication | 048 | Direct question: subtraction |
| 035 | Multiplication by zero | 049 | Fixed few-shot: addition |
| 036 | Mixed-sign multiplication | 050 | Four-digit addition stress test |

### Prospective sampling, endpoints and controls

- **Problem selection:** exactly 12 unique operand tuples per experiment, using Python's local RNG seeded from \`406 * 1000 + experiment_id\`. The same cases are evaluated by each model. All inputs, prompts and exact answers appear in the emitted record.
- **Total distinct sampled condition records:** 28 × 12 = **336 per model**. Paired experiments 038–043 produce a **second** semantically related response for each of 72 cases, yielding **408 raw generations per model** and **816 across two models** if all eight jobs succeed. Paired responses are *not* additional independent problems.
- **Predictor:** each frozen model is evaluated separately, with greedy text generation (\`do_sample=False\`, \`max_new_tokens=8\`). The model must be loaded from a **full 40-character commit SHA**; the current public Hugging Face SHA is resolved per CI execution and recorded. Different job executions can resolve different SHAs and therefore must be compared by provenance, not assumed identical.
- **Primary endpoint:** arithmetic exact-match accuracy over **all 12 cases**; a response not parseable as a leading integer counts as incorrect. Report parse rate separately; compute absolute error only for parseable results and never treat a missing parsed response as a zero error.
- **Paired endpoints:** both-correct rate and semantic consistency **among pairs with two parseable responses**. For subtraction swap the expected relation is negation, not equality. Report both-parsed denominator; never count an unparseable pair as consistent.
- **Controls:** always-zero and always-nine policies applied directly to each sample (not optimized on that sample). They are deliberately weak descriptive baselines and do not establish comparative superiority.
- **No multiple-testing conclusions:** these 28 dependent conditions form one exploratory evaluation program. No primary confirmatory endpoint, power analysis, confidence interval, causal claim, strong-model benchmark, or generalization guarantee is asserted. Favor inspecting failures over ranking hypotheses by small differences in observed accuracy.

### Run the testable baseline protocol locally (no model downloads)

\`\`\`sh
python -m unittest discover -s tests -p 'test_experiments_023_050.py' -v
python -m experiments.internal_reasoning.experiments_023_050 \
  --backend baseline --start 23 --end 50 \
  --output-dir artifacts/followup/baselines
\`\`\`

A baseline-only artifact is labeled \`BASELINES_ONLY_NO_MODEL\`: **model predictions and model accuracy are null**. It is not a result for either GPT-2 model. The test suite checks exact ID coverage, seed reproducibility, arithmetic reference answers, response parsing, paired-relations and explicit result-status separation.

### Run model-backed evaluations

The [arithmetic-followup GitHub Actions workflow](../../.github/workflows/arithmetic-followup.yml) has eight independent jobs (2 models × 4 batches of seven IDs). It installs CPU PyTorch/Transformers, resolves an immutable Hugging Face revision for each model/job, runs every sampled case, and uploads JSON reports with the exact model revision, source-code digest, Python and library versions, every prompt, generated text, parsed prediction, expected answer, per-experiment metrics and completion mode. Each job's 30-day artifact retention means **the source repository alone does not guarantee preservation of raw outputs**.

To reproduce one batch after obtaining the actual model commit from a prior artifact:

\`\`\`sh
python -m pip install --index-url https://download.pytorch.org/whl/cpu "torch>=2.2,<3"
python -m pip install "transformers>=4.40,<5"
python -m experiments.internal_reasoning.experiments_023_050 \
  --backend model --model distilgpt2 \
  --revision ACTUAL_40_CHARACTER_MODEL_COMMIT_SHA \
  --start 23 --end 29 --count 12 \
  --output-dir artifacts/followup/distilgpt2/shard-0
\`\`\`

The \`--revision\` placeholder must be replaced by a real commit hash; passing \`main\` is intentionally rejected. No model secrets or external paid API are required.

### Evidence gate for claiming "50 experiments"

1. Verify historical EXP-001..022 records against the original research report; do not silently alter their numerical findings.
2. Confirm all **28 EXP-023..050 model artifacts exist for both specified models** with \`MODEL_EVALUATED\`, 12 records, exact model SHA, complete raw continuations and no failed jobs. Verify every ID exactly once per model and match GitHub run commit to the code digest.
3. Archive artifacts with a release/DOI-backed repository if public reproducibility is claimed; ensure the frozen source SHA, dependency versions and model revisions are recorded together.
4. Independently inspect surprising values, parse ambiguities and failures. Summarize negative results and narrow limitations, using accurate denominators, without transferring conclusions to untested models.
5. **Only then** describe the project as having *50 numbered experiments executed* (not 50 independent studies). Until then, the supported status is **22 previously reported experiments plus 28 new executable protocols**.

### Release-draft boundary

GitHub currently has an unpublished **v0.1.0 — Initial Research Release** draft that covers EXP-001..022. Do not publish it as a 50-experiment release merely because this protocol exists. A maintainer must either (a) preserve the v0.1.0 release at its historical 22-experiment scope and create a separately versioned extension release, or (b) revise the draft and its source commit **after** the complete new evidence is verified. In either case the [original report](MATHOS_RESEARCH_REPORT_v0.1.md) remains a historical record, not an automatically updated empirical report.

**Interpretive limit:** behavioral pass/fail on 12 samples is not proof of internal reasoning or lack of reasoning. Passing GitHub Actions is software execution evidence, not independent external replication.
