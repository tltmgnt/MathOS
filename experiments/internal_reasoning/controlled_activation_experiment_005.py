import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"

PROBLEMS = [
    {"a": 8, "b": 4},
    {"a": 8, "b": 5},
    {"a": 8, "b": 6},
    {"a": 8, "b": 7},
    {"a": 8, "b": 8},
]

CANDIDATE_ANSWERS = [12, 13, 14, 15, 16]


def score_answer(model, tokenizer, prompt, answer):
    continuation = " " + str(answer)
    full_text = prompt + continuation

    prefix_ids = tokenizer(
        prompt,
        add_special_tokens=False,
    )["input_ids"]

    full_ids = tokenizer(
        full_text,
        add_special_tokens=False,
    )["input_ids"]

    if full_ids[:len(prefix_ids)] != prefix_ids:
        raise ValueError(
            "Prompt tokenization changes when answer is appended"
        )

    answer_ids = full_ids[len(prefix_ids):]

    if not prefix_ids or not answer_ids:
        raise ValueError("Empty prompt or answer tokenization")

    input_ids = torch.tensor(
        [full_ids],
        dtype=torch.long,
    )

    with torch.no_grad():
        outputs = model(input_ids=input_ids)

    log_probs = torch.log_softmax(
        outputs.logits,
        dim=-1,
    )

    total = 0.0

    for index in range(len(prefix_ids), len(full_ids)):
        total += log_probs[
            0,
            index - 1,
            full_ids[index],
        ].item()

    if not math.isfinite(total):
        raise ValueError("Non-finite log probability")

    return {
        "answer": answer,
        "token_ids": answer_ids,
        "log_probability": total,
    }


def run_experiment(output_path):
    torch.manual_seed(406)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME
    )
    model.eval()

    results = []
    correct_count = 0
    margins = []
    score_vectors = []

    for trial_number, problem in enumerate(
        PROBLEMS, start=1
    ):
        a = problem["a"]
        b = problem["b"]

        prompt = f"{a} + {b} ="
        correct_answer = a + b

        candidate_scores = [
            score_answer(
                model,
                tokenizer,
                prompt,
                answer,
            )
            for answer in CANDIDATE_ANSWERS
        ]

        ranked = sorted(
            candidate_scores,
            key=lambda item: item["log_probability"],
            reverse=True,
        )

        predicted_answer = ranked[0]["answer"]
        is_correct = predicted_answer == correct_answer

        if is_correct:
            correct_count += 1

        correct_score = next(
            item["log_probability"]
            for item in candidate_scores
            if item["answer"] == correct_answer
        )

        incorrect_scores = [
            item["log_probability"]
            for item in candidate_scores
            if item["answer"] != correct_answer
        ]

        margin = correct_score - max(incorrect_scores)
        margins.append(margin)

        score_vectors.append([
            item["log_probability"]
            for item in candidate_scores
        ])

        results.append({
            "trial": trial_number,
            "prompt": prompt,
            "correct_answer": correct_answer,
            "predicted_answer": predicted_answer,
            "is_correct": is_correct,
            "margin_vs_best_incorrect": margin,
            "candidate_scores": candidate_scores,
        })

        print(
            f"Trial {trial_number}: "
            f"correct={correct_answer}, "
            f"predicted={predicted_answer}"
        )

    score_ranges = []

    for index, answer in enumerate(CANDIDATE_ANSWERS):
        values = [
            vector[index]
            for vector in score_vectors
        ]

        score_ranges.append({
            "answer": answer,
            "minimum_log_probability": min(values),
            "maximum_log_probability": max(values),
            "range": max(values) - min(values),
        })

    report = {
        "experiment": "MathOS-EXP-005",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": 406,
        "method": (
            "Fixed candidate-answer ranking across "
            "controlled operand changes"
        ),
        "candidate_answers": CANDIDATE_ANSWERS,
        "trial_count": len(PROBLEMS),
        "results": results,
        "summary": {
            "correct_predictions": correct_count,
            "candidate_set_accuracy": (
                correct_count / len(PROBLEMS)
            ),
            "mean_margin_vs_best_incorrect": (
                statistics.mean(margins)
            ),
            "candidate_score_ranges": score_ranges,
        },
        "limitations": [
            "Only five arithmetic problems",
            "Only one operand is varied",
            "Candidate answers are restricted to a fixed set",
            "Candidate-set accuracy is not open-ended accuracy",
            "Stable scores do not prove operands are ignored",
            "No causal conclusions can be drawn",
        ],
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nMathOS Experiment 005 completed")
    print(
        "Candidate-set accuracy: "
        f"{correct_count / len(PROBLEMS):.2%}"
    )
    print(f"Report: {output_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_005.json"
        ),
    )

    args = parser.parse_args()
    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
