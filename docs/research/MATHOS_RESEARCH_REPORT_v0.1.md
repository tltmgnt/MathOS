MathOS v0.1 — Research Report

Project: MathOS
Research phase: Experiments 001–022
Status: Experimental evaluation completed; release verification pending
Report date: October 28, 2026

1. Executive Summary

MathOS is an experimental research project investigating arithmetic behavior, neural activation patterns, and the relationship between language-model outputs and mathematical competence.

The initial research phase comprises 22 experiments.

The later experiments evaluated two pretrained language models:

* DistilGPT2
* sshleifer/tiny-gpt2

The evaluations included arithmetic prediction, operand swapping, cross-model comparisons, error analysis, constant-answer baselines, unrestricted answer generation, and prompt-format variation.

Principal finding: The available experiments did not establish arithmetic understanding in either evaluated model.

Although some experiments identified differences in model behavior and sensitivity to operand order or prompt format, these observations were insufficient to demonstrate reliable arithmetic competence.

2. Research Questions

The research investigated four questions:

1. Do model outputs change when arithmetic operands are swapped?
2. Do changes in predictions correspond to improved mathematical correctness?
3. Can model performance exceed simple constant-answer baselines?
4. Can models generate correct answers on a different range of addition problems under multiple prompt formats?

3. Experimental Scope

Experiments 001–022 explored neural and arithmetic behavior.

This report emphasizes Experiments 013–022 because their results support the clearest comparative findings.

The experimental evaluations used pretrained models without additional fine-tuning.

The reported results concern the specific models, prompts, problem sets, and evaluation procedures tested.

They should not be generalized to all language models or all arithmetic tasks.

4. Operand-Swap Experiments

Experiments 013–018 investigated model behavior when the order of addition operands was reversed.

For example:

3 + 7

and:

7 + 3

These expressions have the same mathematical answer.

On the deduplicated set of 15 nonidentical operand pairs:

Measurement	DistilGPT2	Tiny-GPT2
Pairs evaluated	15	15
Prediction changes after swapping	8	0
Prediction-change rate	53.3%	0%
Correct in both orientations	1	3

DistilGPT2 exhibited greater sensitivity to operand order.

Tiny-GPT2 produced stable predictions under the tested candidate-ranking method.

Neither pattern established arithmetic understanding.

A prediction may change without becoming correct, and an unchanged prediction may simply reflect a preference for a constant answer.

5. Arithmetic Error Analysis

Experiment 019 measured signed and absolute prediction errors on the deduplicated operand pairs.

Measurement	DistilGPT2 original	DistilGPT2 swapped	Tiny-GPT2 original	Tiny-GPT2 swapped
Mean signed error	-3.73	-3.07	0.00	0.00
Mean absolute error	3.73	3.07	1.73	1.73

These results describe prediction errors on the selected problem set.

They do not establish that either model performed addition correctly.

6. Constant-Answer Baseline

Experiment 020 evaluated 25 addition problems with candidate answers restricted to integers 5–13.

It compared model predictions against constant-answer baselines.

Measurement	DistilGPT2	Tiny-GPT2	Constant answer 9
Correct answers	1/25	5/25	5/25
Accuracy	4%	20%	20%
Mean absolute error	3.80	1.60	1.60

Tiny-GPT2 consistently selected 9 and matched the constant-9 baseline.

DistilGPT2 performed worse than that baseline.

Interpretation: Neither model demonstrated performance exceeding the best constant-answer baseline on this benchmark.

The best baseline was selected using the evaluation grid itself. This is an in-sample comparison rather than an independent generalization estimate.

7. Arithmetic Generalization Evaluation

Experiment 021 evaluated 25 addition problems outside the operand ranges used in the earlier arithmetic grid.

Models generated unrestricted text rather than selecting from answers 5–13.

Measurement	DistilGPT2	Tiny-GPT2
Problems	25	25
Correct answers	0	0
Accuracy	0%	0%
Parsed numerical answers	25	0

DistilGPT2 frequently generated percentage-like text, including 0.0% and 0.5%.

The original parser interpreted these outputs as integer zero.

Tiny-GPT2 repeatedly generated nonnumerical text.

The in-sample constant baseline answered 27, achieving 6/25 correct predictions, or 24% accuracy.

Interpretation: Neither model demonstrated successful addition under the tested generation procedure.

The initial numerical parse rate for DistilGPT2 should not be interpreted as evidence that it generated valid arithmetic answers.

8. Prompt-Format Validation

Experiment 022 evaluated the same 25 problems using four prompt formats:

1. Equation
2. Direct question
3. Sentence completion
4. Worked examples

A stricter parser rejected percentage-like outputs.

Prompt format	DistilGPT2 correct	Tiny-GPT2 correct
Equation	0/25	0/25
Direct question	0/25	0/25
Sentence	0/25	0/25
Worked examples	0/25	0/25

DistilGPT2 produced parseable integers for all 25 worked-example prompts, but none were correct.

The mean absolute error for those 25 predictions was 14.24.

Tiny-GPT2 produced no parseable integer answers under any of the four prompt formats.

The experiment demonstrates prompt sensitivity in DistilGPT2’s output formatting, but not successful arithmetic.

The 200 evaluated responses represent repeated testing of the same 25 problems across models and prompt formats, not 200 independent arithmetic problems.

9. Evidence Assessment

The experiments support the following observations:

* Model outputs can depend on operand order.
* Model predictions can change without improving correctness.
* Constant-answer strategies can match or outperform model predictions on restricted benchmarks.
* Prompt formatting can influence whether a model produces numerical-looking output.
* Neither tested model demonstrated reliable addition on the evaluated generalization problems.

The experiments do not establish:

* Reliable arithmetic understanding in either model.
* A causal neural mechanism for mathematical reasoning.
* General arithmetic incapability across all possible prompts or evaluation methods.
* General conclusions about larger or instruction-tuned language models.

10. Methodological Limitations

The principal limitations are:

* Small evaluation sets.
* Restricted candidate answers in earlier experiments.
* In-sample constant-baseline selection.
* Reuse of the Experiment 021 problems in Experiment 022.
* Prompt formats selected after observing earlier results.
* Greedy text generation rather than a broad decoding study.
* Limited model selection.
* No fine-tuning.
* No independent held-out confirmation of prompt effects.
* No demonstration that evaluation problems were absent from pretraining data.

The results are exploratory and descriptive.

11. Reproducibility

The MathOS repository contains experiment scripts and a GitHub Actions workflow used to execute the evaluations.

The later experiments use deterministic problem selection where specified, including seed 406 for Experiments 021 and 022.

Generated experiment artifacts provide the detailed predictions and summary metrics.

For a fully reproducible release, the repository should also document:

* Python version.
* Dependency versions.
* Exact model revisions.
* Workflow configuration.
* Artifact retrieval instructions.
* Commands for running each experiment.

These items require verification before the v0.1 release is finalized.

12. Conclusion

MathOS completed its initial 22-experiment research phase.

The strongest supported conclusion is that arithmetic understanding was not demonstrated in DistilGPT2 or sshleifer/tiny-gpt2 under the tested conditions.

The research also highlights the importance of distinguishing genuine mathematical correctness from constant-answer behavior, prompt sensitivity, and mathematical-looking text generation.

The negative results provide a useful foundation for more rigorous future research.

MathOS v0.1 should be presented as an experimental research framework with documented findings and limitations—not as a system that has demonstrated arithmetic reasoning.

13. Release Status

Research experiments: Completed through EXP-022.

Research report: Prepared.

Repository verification: Pending.

MathOS v0.1 release: Pending successful verification.
