MathOS Arithmetic Benchmark Comparison

Experiments 007 and 008

Project: MathOS
Phase: 3 — Internal Reasoning Experiments
Benchmark: MathOS-Arithmetic-Grid-v1
Experiment IDs: MathOS-EXP-007 and MathOS-EXP-008
Date: October 28, 2026
Seed: 406

⸻

1. Objective

Compare the arithmetic answer-ranking behavior of two language models under a fixed benchmark:

* Experiment 007: sshleifer/tiny-gpt2
* Experiment 008: distilgpt2

The objective is to measure candidate-answer accuracy, prediction diversity, correct-answer ranking, and variation in candidate scores.

This benchmark does not establish whether either model performs mathematical reasoning internally.

2. Experimental Setup

Both experiments use the same arithmetic benchmark.

Parameter	Configuration
Benchmark	MathOS-Arithmetic-Grid-v1
Arithmetic operation	Addition
First operand	3 through 7
Second operand	2 through 6
Number of problems	25
Candidate answers	5 through 13
Seed	406
Scoring method	Conditional answer log-probability ranking

For each arithmetic problem, the benchmark scores nine candidate answers and selects the highest-scoring candidate as the prediction.

Accuracy is calculated only within this restricted candidate set.

3. Benchmark Results

Metric	Experiment 007: TinyGPT2	Experiment 008: DistilGPT2
Problems evaluated	25	25
Correct predictions	3	1
Candidate-set accuracy	12%	4%
Incorrect predictions	22	24
Mean correct-answer rank	4.68	5.28
Unique predicted answers	1	2
Most common prediction	7	5

Experiment 007

TinyGPT2 selected answer 7 for all 25 arithmetic problems.

Its three correct predictions occurred when the true answer was 7.

The model’s candidate scores changed very little across the operand grid.

This indicates strong answer-selection bias under the tested prompt format and candidate-ranking procedure.

Experiment 008

DistilGPT2 selected:

* Answer 5 for 20 problems.
* Answer 6 for 5 problems.

Its only correct prediction was for:

3 + 2 = 5

DistilGPT2 showed substantially greater candidate-score variation across prompts than TinyGPT2.

However, this variation did not produce higher arithmetic accuracy.

4. Comparative Findings

Finding 1 — Both models performed poorly

TinyGPT2 achieved 12% candidate-set accuracy.

DistilGPT2 achieved 4% candidate-set accuracy.

Neither result demonstrates reliable arithmetic performance on this benchmark.

Finding 2 — Prediction diversity differed

TinyGPT2 produced one unique predicted answer.

DistilGPT2 produced two unique predicted answers.

DistilGPT2 therefore exhibited greater prediction diversity, although its predictions remained heavily concentrated on small candidate values.

Finding 3 — Score sensitivity did not imply correctness

TinyGPT2’s candidate log-probabilities were nearly constant across the 25 prompts.

DistilGPT2’s candidate log-probabilities varied more noticeably.

Despite this difference, DistilGPT2 produced fewer correct predictions.

This demonstrates that greater variation in answer scores is not sufficient evidence of improved arithmetic performance.

Finding 4 — Answer preferences dominated the benchmark

Both models repeatedly preferred particular candidate answers rather than consistently selecting the arithmetic sum.

TinyGPT2 favored 7.

DistilGPT2 favored 5 and 6.

These observations are consistent with strong answer-ranking biases under the tested conditions.

They do not identify the internal mechanisms responsible for those biases.

5. Interpretation

The experiments demonstrate that language models can produce different candidate-score patterns while both performing poorly on a fixed arithmetic benchmark.

The results also show why prediction diversity and score variation should be evaluated separately from correctness.

The experiment does not establish that TinyGPT2 has better general arithmetic capabilities than DistilGPT2.

It establishes only that TinyGPT2 achieved a higher accuracy on this specific 25-problem, nine-candidate evaluation.

6. Limitations

1. The benchmark contains only 25 arithmetic problems.
2. All problems use addition.
3. Candidate answers are restricted to integers 5 through 13.
4. Results may depend on the exact prompt format.
5. Candidate tokenization may differ between models.
6. Candidate log-probabilities should not be treated as directly comparable measures of model quality without accounting for tokenization and scoring differences.
7. Candidate-set accuracy is not open-ended generation accuracy.
8. A single deterministic evaluation does not establish robustness.
9. Score variation does not establish causal mechanisms or internal reasoning processes.

7. Conclusion

MathOS Experiments 007 and 008 successfully produced comparable benchmark records using a shared arithmetic operand grid and candidate-ranking procedure.

Experiment 007: 3 correct predictions out of 25, with a strong preference for answer 7.

Experiment 008: 1 correct prediction out of 25, with predictions concentrated on answers 5 and 6.

The main result is that different models exhibit different answer-ranking behavior, but neither demonstrated reliable arithmetic performance in this evaluation.

These findings provide a documented baseline for future MathOS experiments.

8. Recommended Follow-Up

Future experiments should consider:

* Additional arithmetic operations.
* Larger and more varied operand ranges.
* Alternative prompt formats.
* Open-ended answer generation.
* Tokenization-aware scoring comparisons.
* Multiple independent evaluation conditions.
* Statistical analysis across expanded problem sets.

Any future claims about internal reasoning mechanisms should require additional evidence beyond answer-ranking statistics.

⸻

MathOS Research Status: Benchmark comparison documented.

Scientific interpretation: Descriptive and non-causal.
