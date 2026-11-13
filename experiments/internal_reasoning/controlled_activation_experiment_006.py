import argparse
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"

FIRST_OPERANDS = [3, 4, 5, 6, 7]
SECOND_OPERANDS = [2, 3, 4, 5, 6]

CANDIDATE_ANSWERS = list(range(5, 14))


def score_answer(model, tokenizer, prompt, answer):
    prefix_ids = tokenizer(
        prompt,
        add_special_tokens=False,
    )["input_ids"]

    full_ids = tokenizer(
        prompt + " " + str(answer),
        add_special_tokens=False,
    )["input_ids"]

    if full_ids[:len(prefix_ids)] != prefix_ids:
        raise ValueError("Prompt tokenization mismatch")

    answer_ids = full_ids[len(prefix_ids):]

    if not prefix_ids or not answer_ids:
        raise ValueError("Empty token sequence")

    input_ids = torch.tensor([full_ids])

    with torch.no_grad():
        outputs = model(input_ids=input_ids)

    log_probs = torch.log_softmax(
        outputs.logits,
        dim=-1,
    )

    score = sum(
        log_probs[0, index - 1, full_ids[index]].item()
        for index in range(len(prefix_ids), len(full_ids))
    )

    if not math.isfinite(score):
        raise ValueError("Non-finite score")

    return score


def run_experiment(output_path):
    torch.manual_seed(406)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()

    results = []
    predictions = []
    score_vectors = []
    correct_count = 0

    for a in FIRST_OPERANDS:
        for b in SECOND_OPERANDS:
            prompt = f"{a} + {b} ="
            correct_answer = a + b

            scores = {
                answer: score_answer(
                    model,
                    tokenizer,
                    prompt,
                    answer,
                )
                for answer in CANDIDATE_ANSWERS
            }

            predicted = max(scores, key=scores.get)

            if predicted == correct_answer:
                correct_count += 1

            predictions.append(predicted)
            score_vectors.append(scores)

            correct_score = scores[correct_answer]

            better_answers = sum(
                score > correct_score
                for score in scores.values()
            )

            results.append({
                "prompt": prompt,
                "correct_answer": correct_answer,
                "predicted_answer": predicted,
                "correct_answer_rank": better_answers + 1,
                "is_correct": predicted == correct_answer,
                "candidate_scores": scores,
            })

            print(
                f"{prompt} predicted={predicted}, "
                f"correct={correct_answer}"
            )

    candidate_variation = []

    for answer in CANDIDATE_ANSWERS:
        values = [
            scores[answer]
            for scores in score_vectors
        ]

        candidate_variation.append({
            "answer": answer,
            "mean_log_probability": statistics.mean(values),
            "standard_deviation": statistics.stdev(values),
            "range": max(values) - min(values),
        })

    prediction_counts = Counter(predictions)

    report = {
        "experiment": "MathOS-EXP-006",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": 406,
        "method": (
            "Arithmetic operand grid with fixed candidate "
            "answer ranking and score variation analysis"
        ),
        "problem_count": len(results),
        "candidate_answers": CANDIDATE_ANSWERS,
        "results": results,
        "summary": {
            "correct_predictions": correct_count,
            "candidate_set_accuracy": (
                correct_count / len(results)
            ),
            "prediction_counts": dict(prediction_counts),
            "unique_predicted_answers": len(prediction_counts),
            "mean_correct_answer_rank": statistics.mean(
                item["correct_answer_rank"]
                for item in results
            ),
            "candidate_variation": candidate_variation,
        },
        "limitations": [
            "Restricted candidate answer set",
            "Only addition problems",
            "Small deterministic operand grid",
            "Candidate-set accuracy is not open-ended accuracy",
            "Score variation does not establish causal mechanisms",
            "Tiny demonstration model may not generalize",
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

    print("\nMathOS Experiment 006 completed")
    print(
        "Candidate-set accuracy: "
        f"{correct_count / len(results):.2%}"
    )
    print(f"Report: {output_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_006.json"
        ),
    )

    args = parser.parse_args()

    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
