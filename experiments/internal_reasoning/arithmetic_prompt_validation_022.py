"""MathOS EXP-022: Arithmetic prompt-format validation."""

import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


SEED = 406
PROBLEM_COUNT = 25

MODELS = {
    "distilgpt2": "distilgpt2",
    "tiny_gpt2": "sshleifer/tiny-gpt2",
}

PROMPT_TEMPLATES = {
    "equation": "{a} + {b} =",
    "direct_question": "What is {a} + {b}? Answer:",
    "sentence": "The sum of {a} and {b} is",
    "worked_examples": (
        "3 + 4 = 7\n"
        "5 + 6 = 11\n"
        "{a} + {b} ="
    ),
}


def build_problems():
    """Reproduce the exact EXP-021 problem selection."""
    rng = random.Random(SEED)

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
    """
    Accept an integer answer only when it is not followed
    by decimal notation, a percent sign, or another digit.
    """
    match = re.match(
        r"^\s*(-?\d+)(?![\d.%])(?=\s|$|[.,;!?])",
        text,
    )

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

    continuation = output[0][
        inputs["input_ids"].shape[1]:
    ]

    generated_text = tokenizer.decode(
        continuation,
        skip_special_tokens=True,
    )

    return {
        "generated_text": generated_text,
        "prediction": extract_answer(generated_text),
    }


def evaluate(records):
    count = len(records)

    parsed = [
        record
        for record in records
        if record["prediction"] is not None
    ]

    correct = sum(
        record["prediction"] == record["correct_answer"]
        for record in records
    )

    return {
        "problem_count": count,
        "parsed_count": len(parsed),
        "parse_rate": len(parsed) / count,
        "correct_count": correct,
        "accuracy": correct / count,
        "mean_absolute_error_on_parsed": (
            sum(
                abs(
                    record["prediction"]
                    - record["correct_answer"]
                )
                for record in parsed
            ) / len(parsed)
            if parsed
            else None
        ),
    }


def evaluate_model(model_name, problems):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    results = {}

    for template_name, template in PROMPT_TEMPLATES.items():
        print(
            f"Evaluating {model_name}: {template_name}",
            flush=True,
        )

        records = []

        for problem in problems:
            prompt = template.format(
                a=problem["a"],
                b=problem["b"],
            )

            result = predict(
                model,
                tokenizer,
                prompt,
            )

            records.append({
                **problem,
                "prompt": prompt,
                "generated_text": result["generated_text"],
                "prediction": result["prediction"],
            })

        results[template_name] = {
            "metrics": evaluate(records),
            "records": records,
        }

    return {
        "model": model_name,
        "prompt_results": results,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    problems = build_problems()

    report = {
        "experiment": "MathOS-EXP-022",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": "Arithmetic prompt-format validation",
        "benchmark": "MathOS-Arithmetic-Generalization-v1",
        "seed": SEED,
        "problem_count": PROBLEM_COUNT,
        "prompt_templates": PROMPT_TEMPLATES,
        "models": {},
        "limitations": [
            "Only 25 arithmetic problems",
            "Same problem grid as Experiment 021",
            "Prompt formats selected after observing EXP-021",
            "Prompt comparisons are exploratory",
            "No independent held-out confirmation set",
            "Greedy generation only",
            "Strict integer parsing may reject some valid responses",
            "No fine-tuning performed",
            "Behavioral success does not prove internal reasoning",
        ],
    }

    for key, model_name in MODELS.items():
        report["models"][key] = evaluate_model(
            model_name,
            problems,
        )

    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(report, file, indent=2)

    summary = {
        "experiment": report["experiment"],
        "results": {
            model_key: {
                template_name: result["metrics"]
                for template_name, result
                in model_data["prompt_results"].items()
            }
            for model_key, model_data
            in report["models"].items()
        },
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
