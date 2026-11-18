# MathOS experiments 023–050 — observed results

**Executed:** 2026-11-18 on [GitHub Actions run 44332836125](https://github.com/tltmgnt/MathOS/actions/runs/44332836125).  
**Source tested:** [commit 17887db5](https://github.com/tltmgnt/MathOS/commit/17887db55c4fd1ec4a6a3512fb19370df291ea6d).  
**Protocol:** [EXP-023–050 protocol](EXPERIMENTS_023_050.md), \`MathOS-Arithmetic-Followup-v1\`.  
**Raw evidence:** Eight job-specific archived Action artifacts (30-day retention); artifact IDs/checksums and per-condition metrics are in [EXPERIMENTS_023_050_SUMMARY.json](../../evidence/internal_reasoning/EXPERIMENTS_023_050_SUMMARY.json).

## Status

**All 28 new experiment IDs (023–050) were executed against both selected pretrained models.** A separate baseline job and all eight model jobs completed successfully. The 56 model reports were downloaded and cross-checked for ID coverage, sample count, source hash, complete prompts and raw generations, arithmetic reference answers, metric arithmetic, paired predictions, and consistent sampled cases across models.

Together with the earlier [22-experiment report](MATHOS_RESEARCH_REPORT_v0.1.md), MathOS now has **50 numbered experiment protocols with documented executions**. This does **not** mean 50 independent scientific studies, statistically powered trials, external replications, or validated mathematical intelligence.

## Compact descriptive results

| Metric | DistilGPT2 | sshleifer/tiny-gpt2 |
|---|---:|---:|
| New experiment IDs executed | 28/28 | 28/28 |
| Primary cases (12 per condition) | 336 | 336 |
| Primary responses parseable as leading integers | 32/336 | 0/336 |
| Primary exact arithmetic matches | **7/336 (2.08%)** | **0/336 (0%)** |
| Paired comparison cases (EXP-038–043) | 72 | 72 |
| Both paired responses parseable | 0/72 | 0/72 |
| Paired consistency rate | **Undefined** (0 valid pairs) | **Undefined** (0 valid pairs) |
| Total generated responses, including second paired prompts | 408 | 408 |
| Always-zero reference baseline correct (same 336 cases) | 12/336 | 12/336 |
| Always-nine reference baseline correct (same 336 cases) | 0/336 | 0/336 |

**Do not interpret the pair consistency rate as zero percent.** It has zero *eligible* pairs, so the rate is not estimable. No comparison here supports causal mechanisms or internal reasoning competence. Aggregating across 28 heterogeneous, correlated conditions is descriptive rather than a preregistered confirmatory benchmark.

### Per-condition outcomes

Each entry is \`correct / parsed\` out of **12** prompts per model. An unparseable output is counted as incorrect.

| Experiment | DistilGPT2 | Tiny-GPT2 |
|---|---|---|
| 023 — Two-digit addition transfer | 0 / 0 | 0 / 0 |
| 024 — Additive zero | 0 / 0 | 0 / 0 |
| 025 — Mixed-sign addition | 0 / 3 | 0 / 0 |
| 026 — Negative plus negative | 0 / 5 | 0 / 0 |
| 027 — Addition with carry | 0 / 0 | 0 / 0 |
| 028 — Addition without carry | 0 / 0 | 0 / 0 |
| 029 — Three-digit addition | 0 / 0 | 0 / 0 |
| 030 — Doubling | 0 / 0 | 0 / 0 |
| 031 — Positive-result subtraction | 0 / 1 | 0 / 0 |
| 032 — Negative-result subtraction | 0 / 0 | 0 / 0 |
| 033 — Subtraction and zero | 0 / 0 | 0 / 0 |
| 034 — Small multiplication | 0 / 0 | 0 / 0 |
| 035 — Zero-product multiplication | **7 / 7** | 0 / 0 |
| 036 — Mixed-sign multiplication | 0 / 0 | 0 / 0 |
| 037 — Two-digit × one-digit | 0 / 0 | 0 / 0 |
| 038 — Addition commutativity | 0 / 0 | 0 / 0 |
| 039 — Multiplication commutativity | 0 / 0 | 0 / 0 |
| 040 — Addition associativity | 0 / 2 | 0 / 0 |
| 041 — Subtraction operand swap | 0 / 0 | 0 / 0 |
| 042 — Add/subtract cancellation | 0 / 2 | 0 / 0 |
| 043 — Distribution vs expansion | 0 / 0 | 0 / 0 |
| 044 — Addition word problem | 0 / 0 | 0 / 0 |
| 045 — Subtraction word problem | 0 / 0 | 0 / 0 |
| 046 — Multiplication word problem | 0 / 0 | 0 / 0 |
| 047 — Direct addition question | 0 / 0 | 0 / 0 |
| 048 — Direct subtraction question | 0 / 0 | 0 / 0 |
| 049 — Fixed few-shot addition | 0 / 12 | 0 / 0 |
| 050 — Four-digit addition | 0 / 0 | 0 / 0 |

DistilGPT2's seven correct answers all occurred in **EXP-035**, multiplication by zero. In those same 12 cases, the fixed always-zero baseline scored **12/12**, so those seven answers do not show an advantage over this simple control. Its EXP-049 few-shot condition generated parseable leading integers on **12/12** cases but **0** correct sums, an example of formatting rather than arithmetic improvement. Tiny-GPT2 yielded no leading integer under this parser on these new samples.

## Exact checkpoint and execution provenance

- DistilGPT2 model revision: \`2290a62682d06624634c1f46a6ad5be0f47f38aa\`.
- sshleifer/tiny-gpt2 model revision: \`5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be\`.
- All 56 reports identified the same runner SHA-256: \`221c945ceb3ec6036ace377ee5d7be9d26b886aead0ea3a528599ff20d737b0c\`.
- Per experiment: \`seed=406\`, 12 distinct deterministic samples, at most 8 greedily generated continuation tokens. Paired experiments add an extra prompt to each of their 12 cases.
- Each report saves raw text, parser outputs, truth labels, Python/torch/Transformers versions and the immutable checkpoint SHA. [The summary manifest](../../evidence/internal_reasoning/EXPERIMENTS_023_050_SUMMARY.json) records eight downloaded ZIP checksums and GitHub Actions artifact IDs for post-run checking.

**Scope of audit:** an offline record-integrity and arithmetic recomputation check performed during preparation of this repository change. It is not external, blinded, independent scientific peer review.

## Limitations and interpretation

1. **Small and correlated sample:** only 12 cases per condition. The 28 tests deliberately share a model architecture family and evaluation code. Their 672 primary responses do not represent 672 independent studies or a broad sampling of possible tasks.
2. **Decoding and parsing:** greedy, 8-token completions and strict leading-integer parsing. A model's failure to give an integer in that slot does not demonstrate an inability to represent arithmetic internally. Decimal and percent-like continuations are deliberately excluded; reported parsing errors are inspectable in the raw records.
3. **Weak fixed baselines:** zero and nine are not tuned independent controls. A stronger set of algorithms or language models might behave differently.
4. **No documented holdout from training:** random selection of numbers does not establish that problems were absent from any model's pretraining data.
5. **Provenance and permanence:** the Artifacts are retained for 30 days, not indefinitely. Preserve a reviewed immutable research archive before making claims of long-term raw-data accessibility. A passing CI workflow is not independent replication.

**Bounded conclusion:** these two older pretrained GPT-2 variants did not exhibit reliable arithmetic correctness under these exact prompts, sample sizes, decoding choices and parser. The findings provide negative controls for better evaluation designs, not a universal statement about AI mathematics or mathematical novelty.

## Publication gate

The existing GitHub draft titled **MathOS v0.1.0 — Initial Research Release** remains **unpublished**, and its current body describes only EXP-001–022. The newly observed EXP-023–050 results may support a separate versioned follow-up or a deliberately revised prepublication draft, but a maintainer must decide the release scope, archive raw evidence, review attribution/dependencies and approve the final text. Do **not** present an unreviewed draft as already published.
