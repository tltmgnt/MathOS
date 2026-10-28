import argparse
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_MODEL = "sshleifer/tiny-gpt2"
DEFAULT_SEED = 406

FIRST_OPERANDS = [3, 4, 5, 6, 7]
SECOND_OPERANDS = [2, 3, 4, 5, 6]
CANDIDATE_ANSWERS = list(range(5, 14))


def load_model(model_name, seed):
    torch.manual_seed(seed)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    return model, tokenizer


def score_answer(model, tokenizer, prompt, answer):
    prefix_ids = tokenizer(
        prompt,
        add_special_tokens=False,
    )["input_ids"]

    full_ids = tokenizer(
        prompt + " " + str(answer),
        add_special_tokens=False,
    )["input_ids"]

    if not prefix_ids:
        raise ValueError("Empty prompt tokenization")

    if full_ids[:len(prefix_ids)] != prefix_ids:
        raise ValueError(
            "Prompt tokenization changed when answer was appended"
        )

    answer_ids = full_ids[len(prefix_ids):]

    if not answer_ids:
        raise ValueError("Empty answer tokenization")

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
        raise ValueError("Non-finite answer score")

    return total


def evaluate(model, tokenizer):
    results = []
    predictions = []
    score_vectors = []

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

            predicted = max(
                scores,
                key=scores.get,
            )

            correct_score = scores[correct_answer]

            correct_rank = 1 + sum(
                score > correct_score
                for score in scores.values()
            )

            results.append({
                "prompt": prompt,
                "correct_answer": correct_answer,
                "predicted_answer": predicted,
                "correct_answer_rank": correct_rank,
                "is_correct": predicted == correct_answer,
                "candidate_scores": scores,
            })

            predictions.append(predicted)
            score_vectors.append(scores)

            print(
                f"{prompt} "
                f"predicted={predicted} "
                f"correct={correct_answer}"
            )

    correct_count = sum(
        item["is_correct"]
        for item in results
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

    return {
        "problem_count": len(results),
        "results": results,
        "summary": {
            "correct_predictions": correct_count,
            "candidate_set_accuracy": (
                correct_count / len(results)
            ),
            "prediction_counts": dict(Counter(predictions)),
            "unique_predicted_answers": len(set(predictions)),
            "mean_correct_answer_rank": statistics.mean(
                item["correct_answer_rank"]
                for item in results
            ),
            "candidate_variation": candidate_variation,
        },
    }


def run_benchmark(model_name, output_path, seed, experiment_id=None):
    if experiment_id is None:
        experiment_id = (
            "MathOS-EXP-008"
            if model_name == "distilgpt2"
            else "MathOS-EXP-007"
        )

    model, tokenizer = load_model(model_name, seed)

    evaluation = evaluate(model, tokenizer)

    report = {
        "experiment": experiment_id,
        "benchmark": "MathOS-Arithmetic-Grid-v1",
        "model": model_name,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": seed,
        "method": (
            "Fixed arithmetic operand grid; "
            "conditional answer log-probability ranking"
        ),
        "candidate_answers": CANDIDATE_ANSWERS,
        **evaluation,
        "limitations": [
            "Restricted candidate answer set",
            "Only addition problems",
            "Small deterministic operand grid",
            "Candidate-set accuracy is not open-ended accuracy",
            "Answer tokenization can vary between models",
            "Different model tokenizers may affect score comparability",
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

    print("\nMathOS arithmetic benchmark completed")
    print(f"Model: {model_name}")
    print(f"Problems: {evaluation['problem_count']}")
    print(
        "Accuracy: "
        f"{evaluation['summary']['candidate_set_accuracy']:.2%}"
    )
    print(f"Report: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="MathOS reusable arithmetic benchmark"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_007.json"
        ),
    )

    args = parser.parse_args()

    run_benchmark(
        model_name=args.model,
        output_path=Path(args.output),
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
