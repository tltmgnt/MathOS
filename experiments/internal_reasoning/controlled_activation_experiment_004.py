import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"

TRIALS = [
    {"a": 8, "b": 4, "incorrect": 15},
    {"a": 7, "b": 5, "incorrect": 14},
    {"a": 6, "b": 3, "incorrect": 11},
    {"a": 9, "b": 2, "incorrect": 13},
    {"a": 4, "b": 5, "incorrect": 12},
]


def score_continuation(model, tokenizer, prompt, answer):
    """
    Compute the conditional log probability of an answer
    following an arithmetic prompt.
    """
    prefix = prompt
    continuation = " " + str(answer)
    full_text = prefix + continuation

    prefix_ids = tokenizer(
        prefix,
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

    total_log_probability = 0.0

    for index in range(len(prefix_ids), len(full_ids)):
        token_id = full_ids[index]

        token_log_probability = log_probs[
            0,
            index - 1,
            token_id,
        ].item()

        total_log_probability += token_log_probability

    if not math.isfinite(total_log_probability):
        raise ValueError("Non-finite log probability")

    return {
        "answer": answer,
        "answer_token_ids": answer_ids,
        "answer_token_count": len(answer_ids),
        "log_probability": total_log_probability,
    }


def run_experiment(output_path):
    torch.manual_seed(406)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    results = []
    margins = []
    correct_preferences = 0

    for trial_number, trial in enumerate(TRIALS, start=1):
        a = trial["a"]
        b = trial["b"]

        correct_answer = a + b
        incorrect_answer = trial["incorrect"]

        if correct_answer == incorrect_answer:
            raise ValueError("Answers must differ")

        prompt = f"{a} + {b} ="

        correct_score = score_continuation(
            model,
            tokenizer,
            prompt,
            correct_answer,
        )

        incorrect_score = score_continuation(
            model,
            tokenizer,
            prompt,
            incorrect_answer,
        )

        margin = (
            correct_score["log_probability"]
            - incorrect_score["log_probability"]
        )

        prefers_correct = margin > 0

        if prefers_correct:
            correct_preferences += 1

        margins.append(margin)

        results.append({
            "trial": trial_number,
            "prompt": prompt,
            "correct": correct_score,
            "incorrect": incorrect_score,
            "log_probability_margin": margin,
            "prefers_correct": prefers_correct,
        })

        print(
            f"Trial {trial_number}: "
            f"margin={margin:.6f}, "
            f"prefers_correct={prefers_correct}"
        )

    accuracy = correct_preferences / len(TRIALS)

    report = {
        "experiment": "MathOS-EXP-004",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": 406,
        "method": (
            "Conditional answer log-probability comparison "
            "for arithmetic continuations"
        ),
        "trial_count": len(TRIALS),
        "results": results,
        "summary": {
            "correct_preferences": correct_preferences,
            "trial_count": len(TRIALS),
            "pairwise_accuracy": accuracy,
            "mean_log_probability_margin": (
                statistics.mean(margins)
            ),
            "standard_deviation": (
                statistics.stdev(margins)
            ),
            "minimum_margin": min(margins),
            "maximum_margin": max(margins),
        },
        "limitations": [
            "Only five arithmetic problems",
            "Only one incorrect alternative per problem",
            "Pairwise accuracy is not open-ended generation accuracy",
            "Answer tokenization may differ between candidates",
            "The model is a tiny demonstration model",
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

    print("\nMathOS Experiment 004 completed")
    print(f"Pairwise accuracy: {accuracy:.2%}")
    print(f"Report: {output_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_004.json"
        ),
    )

    args = parser.parse_args()

    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
