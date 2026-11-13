"""MathOS EXP-015: tiny-GPT2 operand-swap consistency benchmark."""

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"
CANDIDATES = list(range(5, 14))
OPERANDS_A = range(3, 8)
OPERANDS_B = range(2, 7)


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def candidate_log_probability(model, tokenizer, prompt, answer):
    """Score an answer conditioned on the complete prompt."""
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    answer_ids = tokenizer.encode(str(answer), add_special_tokens=False)

    if not prompt_ids or not answer_ids:
        raise ValueError("Prompt and answer must tokenize to nonempty sequences")

    full_ids = prompt_ids + answer_ids
    input_ids = torch.tensor([full_ids], dtype=torch.long)

    with torch.no_grad():
        logits = model(input_ids).logits[0]

    log_probs = torch.log_softmax(logits, dim=-1)

    total = 0.0
    for offset, token_id in enumerate(answer_ids):
        token_position = len(prompt_ids) + offset - 1
        total += float(log_probs[token_position, token_id].item())

    return total


def score_prompt(model, tokenizer, prompt):
    return [
        candidate_log_probability(model, tokenizer, prompt, candidate)
        for candidate in CANDIDATES
    ]


def standardized(values):
    array = np.asarray(values, dtype=float)
    mean = float(np.mean(array))
    std = float(np.std(array))

    if std == 0:
        return np.zeros_like(array)

    return (array - mean) / std


def euclidean_distance(left, right):
    return float(
        np.linalg.norm(standardized(left) - standardized(right))
    )


def rank_of_answer(scores, answer):
    order = sorted(
        range(len(scores)),
        key=lambda index: (-scores[index], index),
    )
    return order.index(CANDIDATES.index(answer)) + 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/internal_reasoning/experiment_015.json",
    )
    parser.add_argument("--seed", type=int, default=406)
    args = parser.parse_args()

    set_seed(args.seed)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()

    records = []

    for first in OPERANDS_A:
        for second in OPERANDS_B:
            correct_answer = first + second

            original_prompt = f"{first}+{second}="
            swapped_prompt = f"{second}+{first}="

            original_scores = score_prompt(
                model, tokenizer, original_prompt
            )
            swapped_scores = score_prompt(
                model, tokenizer, swapped_prompt
            )

            original_prediction = CANDIDATES[
                int(np.argmax(original_scores))
            ]
            swapped_prediction = CANDIDATES[
                int(np.argmax(swapped_scores))
            ]

            records.append({
                "first_operand": first,
                "second_operand": second,
                "correct_answer": correct_answer,
                "original_prompt": original_prompt,
                "swapped_prompt": swapped_prompt,
                "original_prediction": original_prediction,
                "swapped_prediction": swapped_prediction,
                "prediction_changed": (
                    original_prediction != swapped_prediction
                ),
                "original_correct_rank": rank_of_answer(
                    original_scores, correct_answer
                ),
                "swapped_correct_rank": rank_of_answer(
                    swapped_scores, correct_answer
                ),
                "standardized_distance": euclidean_distance(
                    original_scores, swapped_scores
                ),
                "original_candidate_scores": original_scores,
                "swapped_candidate_scores": swapped_scores,
            })

    distances = [
        record["standardized_distance"]
        for record in records
    ]
    changed = sum(
        record["prediction_changed"]
        for record in records
    )
    original_correct = sum(
        record["original_prediction"] == record["correct_answer"]
        for record in records
    )
    swapped_correct = sum(
        record["swapped_prediction"] == record["correct_answer"]
        for record in records
    )

    report = {
        "experiment": "MathOS-EXP-015",
        "source_experiment": "MathOS-EXP-007",
        "model": MODEL_NAME,
        "benchmark": "MathOS-Arithmetic-Grid-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": (
            "Paired operand-swap comparison of candidate "
            "log-probability vectors"
        ),
        "seed": args.seed,
        "problem_count": len(records),
        "candidate_answers": CANDIDATES,
        "summary": {
            "prediction_change_count": changed,
            "prediction_change_rate": changed / len(records),
            "original_accuracy": original_correct / len(records),
            "swapped_accuracy": swapped_correct / len(records),
            "mean_standardized_distance": float(
                np.mean(distances)
            ),
            "minimum_standardized_distance": float(
                np.min(distances)
            ),
            "maximum_standardized_distance": float(
                np.max(distances)
            ),
            "mean_original_correct_rank": float(
                np.mean([
                    record["original_correct_rank"]
                    for record in records
                ])
            ),
            "mean_swapped_correct_rank": float(
                np.mean([
                    record["swapped_correct_rank"]
                    for record in records
                ])
            ),
        },
        "records": records,
        "limitations": [
            "Candidate answers are restricted to integers 5 through 13",
            "The experiment uses only 25 addition problems",
            "Some operand-swapped pairs overlap within the grid",
            "Candidate score consistency is not arithmetic understanding",
            "No causal conclusions can be drawn",
        ],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], indent=2))
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
