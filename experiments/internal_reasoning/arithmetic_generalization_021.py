"""MathOS EXP-021: Arithmetic generalization evaluation."""

import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODELS = {
    "distilgpt2": "distilgpt2",
    "tiny_gpt2": "sshleifer/tiny-gpt2",
}

SEED = 406
PROBLEM_COUNT = 25


def build_problems():
    rng = random.Random(SEED)

    # Deliberately outside the original operand ranges.
    pairs = [
        (a, b)
        for a in range(8, 21)
        for b in range(7, 20)
        if a != b
    ]

    selected = rng.sample(pairs, PROBLEM_COUNT)

    return [
        {
            "a": a,
            "b": b,
            "correct_answer": a + b,
        }
        for a, b in selected
    ]


def extract_answer(text):
    match = re.match(r"\s*(-?\d+)\b", text)

    if match is None:
        return None

    return int(match.group(1))


def predict(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    continuation = output[0][inputs["input_ids"].shape[1]:]
    generated_text = tokenizer.decode(
        continuation,
        skip_special_tokens=True,
    )

    return {
        "generated_text": generated_text,
        "prediction": extract_answer(generated_text),
    }


def evaluate(records, prediction_key):
    correct = 0
    parsed = 0
    absolute_errors = []

    for record in records:
        prediction = record[prediction_key]
        answer = record["correct_answer"]

        if prediction is not None:
            parsed += 1
            absolute_errors.append(abs(prediction - answer))

            if prediction == answer:
                correct += 1

    count = len(records)

    return {
        "problem_count": count,
        "parsed_count": parsed,
        "parse_rate": parsed / count,
        "correct_count": correct,
        "accuracy": correct / count,
        "mean_absolute_error_on_parsed": (
            sum(absolute_errors) / len(absolute_errors)
            if absolute_errors
            else None
        ),
    }


def evaluate_model(model_name, problems):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    records = []

    for problem in problems:
        a = problem["a"]
        b = problem["b"]

        original = predict(
            model,
            tokenizer,
            f"{a} + {b} =",
        )

        swapped = predict(
            model,
            tokenizer,
            f"{b} + {a} =",
        )

        records.append({
            **problem,
            "original_generated_text": original["generated_text"],
            "original_prediction": original["prediction"],
            "swapped_generated_text": swapped["generated_text"],
            "swapped_prediction": swapped["prediction"],
        })

    return {
        "model": model_name,
        "original_metrics": evaluate(
            records,
            "original_prediction",
        ),
        "swapped_metrics": evaluate(
            records,
            "swapped_prediction",
        ),
        "both_correct_count": sum(
            record["original_prediction"]
            == record["correct_answer"]
            and record["swapped_prediction"]
            == record["correct_answer"]
            for record in records
        ),
        "records": records,
    }


def constant_baseline(problems):
    answers = [problem["correct_answer"] for problem in problems]

    candidates = sorted(set(answers))

    best = min(
        candidates,
        key=lambda candidate: (
            sum(abs(candidate - answer) for answer in answers),
            candidate,
        ),
    )

    return {
        "constant_answer": best,
        "correct_count": sum(
            best == answer for answer in answers
        ),
        "accuracy": sum(
            best == answer for answer in answers
        ) / len(answers),
        "mean_absolute_error": sum(
            abs(best - answer) for answer in answers
        ) / len(answers),
        "selection": "In-sample minimum MAE",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    problems = build_problems()

    report = {
        "experiment": "MathOS-EXP-021",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": "Unrestricted arithmetic generation",
        "benchmark": "MathOS-Arithmetic-Generalization-v1",
        "seed": SEED,
        "problem_count": PROBLEM_COUNT,
        "prompt_template": "{a} + {b} =",
        "constant_baseline": constant_baseline(problems),
        "models": {},
        "limitations": [
            "Only 25 evaluation problems",
            "No fine-tuning performed",
            "Greedy generation may not reflect all model capabilities",
            "Numeric parsing requires an integer at the start",
            "The constant baseline is selected in-sample",
            "Unseen means outside the prior grid, not proven absent from pretraining",
            "Behavioral accuracy alone cannot prove internal reasoning",
        ],
    }

    for key, model_name in MODELS.items():
        print(f"Evaluating {model_name}", flush=True)
        report["models"][key] = evaluate_model(
            model_name,
            problems,
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(json.dumps({
        "experiment": report["experiment"],
        "constant_baseline": report["constant_baseline"],
        "model_metrics": {
            key: {
                "original": value["original_metrics"],
                "swapped": value["swapped_metrics"],
            }
            for key, value in report["models"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
