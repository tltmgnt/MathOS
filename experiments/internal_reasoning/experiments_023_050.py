"""MathOS EXP-023..050: preregistered, bounded arithmetic follow-up evaluations.

A registered experiment is NOT a completed model evaluation. This runner emits
explicit BASELINES_ONLY or MODEL_EVALUATED status and preserves raw continuations.
All 28 IDs are predeclared; changing their meaning requires a new protocol version.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import re
from datetime import datetime, timezone
from pathlib import Path

PROTOCOL = "MathOS-Arithmetic-Followup-v1"
SEED = 406
DEFAULT_CASES = 12
MODEL_IDS = {"distilgpt2": "distilgpt2", "tiny-gpt2": "sshleifer/tiny-gpt2"}
MAX_NEW_TOKENS = 8

# (title, falsifiable comparison or descriptive question, sample regime).
EXPERIMENTS = {
    23: ("Out-of-grid two-digit addition", "Does the model exceed fixed zero/nine baselines?", "two_digit_add"),
    24: ("Addition with zero", "Does the model preserve the additive identity?", "add_zero"),
    25: ("Mixed-sign addition", "Does the model handle positive plus negative?", "mixed_sign_add"),
    26: ("Both-negative addition", "Does the model produce negative sums?", "negative_add"),
    27: ("Carrying in two-digit addition", "Does a ones-place carry affect accuracy?", "carry_add"),
    28: ("Noncarrying two-digit addition", "What is the accuracy on no-carry controls?", "no_carry_add"),
    29: ("Three-digit addition", "Does accuracy persist at larger magnitudes?", "three_digit_add"),
    30: ("Doubling", "Does repeated-operand structure help addition?", "double_add"),
    31: ("Positive-result subtraction", "Can the model compute positive differences?", "positive_sub"),
    32: ("Negative-result subtraction", "Can the model compute negative differences?", "negative_sub"),
    33: ("Zero in subtraction", "Does subtraction respect zero placement?", "zero_sub"),
    34: ("Small integer multiplication", "Can the model multiply small nonzero integers?", "small_mul"),
    35: ("Multiplication by zero", "Does the model respect the zero product?", "zero_mul"),
    36: ("Mixed-sign multiplication", "Does the model apply the sign rule?", "mixed_sign_mul"),
    37: ("Two-digit by one-digit multiplication", "Does accuracy extend beyond tables?", "medium_mul"),
    38: ("Addition commutativity", "Are swapped prompts equal and independently correct?", "commute_add"),
    39: ("Multiplication commutativity", "Are swapped products equal and correct?", "commute_mul"),
    40: ("Addition associativity", "Are regrouped sums equal and correct?", "associate_add"),
    41: ("Subtraction order sensitivity", "Do swapped differences negate each other?", "swap_sub"),
    42: ("Addition-subtraction cancellation", "Do two equivalent cancellation forms agree?", "cancel_add"),
    43: ("Multiplication distribution", "Do factored and expanded arithmetic prompts agree?", "distribute_mul"),
    44: ("Addition word-problem transfer", "Does narrative phrasing preserve numerical accuracy?", "word_add"),
    45: ("Subtraction word-problem transfer", "Does narrative phrasing preserve numerical accuracy?", "word_sub"),
    46: ("Multiplication word-problem transfer", "Does narrative phrasing preserve numerical accuracy?", "word_mul"),
    47: ("Addition question prompt", "Does direct questioning change answer parsing or accuracy?", "question_add"),
    48: ("Subtraction question prompt", "Does direct questioning change answer parsing or accuracy?", "question_sub"),
    49: ("Fixed few-shot addition prompt", "Does a preregistered demonstration improve accuracy?", "fewshot_add"),
    50: ("Four-digit addition stress test", "Does larger-magnitude addition generalize?", "four_digit_add"),
}
PAIRED = {38, 39, 40, 41, 42, 43}


def extract_integer(continuation: str) -> int | None:
    """Only an integer at the start, rejecting percentages, decimals and commas."""
    if not isinstance(continuation, str):
        return None
    match = re.match(r"^\s*(-?\d+)(?![\d.,%])(?=\s|$|[;!?])", continuation)
    return int(match.group(1)) if match else None


def _operands(experiment: int, rng: random.Random) -> tuple[int, int, int]:
    """Finite, protocol-defined populations; not evidence of pretraining exclusion."""
    if experiment in (23, 38, 44, 47, 49):
        return rng.randint(21, 79), rng.randint(20, 77), 0
    if experiment == 24:
        a = rng.randint(1, 200)
        return (a, 0, 0) if rng.randrange(2) else (0, a, 0)
    if experiment == 25:
        return rng.randint(8, 60), -rng.randint(9, 69), 0
    if experiment == 26:
        return -rng.randint(3, 87), -rng.randint(4, 83), 0
    if experiment in (27, 28):
        while True:
            a, b = rng.randint(12, 89), rng.randint(12, 89)
            if ((a % 10 + b % 10 >= 10) == (experiment == 27)):
                return a, b, 0
    if experiment == 29:
        return rng.randint(100, 899), rng.randint(100, 899), 0
    if experiment == 30:
        a = rng.randint(5, 90)
        return a, a, 0
    if experiment in (31, 45, 48):
        a, b = rng.sample(range(21, 151), 2)
        return max(a, b), min(a, b), 0
    if experiment == 32:
        a, b = rng.sample(range(21, 151), 2)
        return min(a, b), max(a, b), 0
    if experiment == 33:
        a = rng.randint(1, 200)
        return (a, 0, 0) if rng.randrange(2) else (0, a, 0)
    if experiment in (34, 39, 46):
        return rng.randint(2, 12), rng.randint(2, 12), 0
    if experiment == 35:
        a = rng.randint(1, 70)
        return (a, 0, 0) if rng.randrange(2) else (0, a, 0)
    if experiment == 36:
        return -rng.randint(2, 18), rng.randint(2, 16), 0
    if experiment == 37:
        return rng.randint(12, 89), rng.randint(2, 9), 0
    if experiment == 40:
        return rng.randint(2, 40), rng.randint(3, 40), rng.randint(4, 40)
    if experiment == 41:
        return rng.randint(50, 120), rng.randint(4, 35), 0
    if experiment == 42:
        return rng.randint(20, 110), rng.randint(2, 49), 0
    if experiment == 43:
        return rng.randint(2, 10), rng.randint(3, 15), rng.randint(2, 14)
    if experiment == 50:
        return rng.randint(1000, 9999), rng.randint(1000, 9999), 0
    raise ValueError(f"unknown experiment {experiment}")


def _make_case(experiment: int, index: int, a: int, b: int, c: int) -> dict:
    subtraction = {31, 32, 33, 41, 45, 48}
    multiplication = {34, 35, 36, 37, 39, 46}
    if experiment == 40:
        expected = a + b + c
    elif experiment == 42:
        expected = a
    elif experiment == 43:
        expected = a * (b + c)
    elif experiment in subtraction:
        expected = a - b
    elif experiment in multiplication:
        expected = a * b
    else:
        expected = a + b
    operation = "-" if experiment in subtraction else "*" if experiment in multiplication else "+"
    prompt = f"{a} {operation} {b} ="
    paired_prompt = None
    paired_expected = None
    relation = None
    if experiment == 38:
        paired_prompt, paired_expected, relation = f"{b} + {a} =", expected, "same"
    elif experiment == 39:
        paired_prompt, paired_expected, relation = f"{b} * {a} =", expected, "same"
    elif experiment == 40:
        prompt = f"({a} + {b}) + {c} ="
        paired_prompt, paired_expected, relation = f"{a} + ({b} + {c}) =", expected, "same"
    elif experiment == 41:
        paired_prompt, paired_expected, relation = f"{b} - {a} =", b - a, "negated"
    elif experiment == 42:
        prompt = f"({a} + {b}) - {b} ="
        paired_prompt, paired_expected, relation = f"{a} + ({b} - {b}) =", expected, "same"
    elif experiment == 43:
        prompt = f"{a} * ({b} + {c}) ="
        paired_prompt, paired_expected, relation = f"{a} * {b} + {a} * {c} =", expected, "same"
    elif experiment == 44:
        prompt = f"A box holds {a} apples and another holds {b}. How many apples in total? Answer:"
    elif experiment == 45:
        prompt = f"A store had {a} cards and sold {b}. How many cards remain? Answer:"
    elif experiment == 46:
        prompt = f"There are {a} rows with {b} chairs per row. How many chairs? Answer:"
    elif experiment == 47:
        prompt = f"What is {a} plus {b}? Answer:"
    elif experiment == 48:
        prompt = f"What is {a} minus {b}? Answer:"
    elif experiment == 49:
        prompt = f"3 + 4 = 7\n5 + 6 = 11\n{a} + {b} ="
    return {
        "case_id": f"EXP-{experiment:03d}-CASE-{index:02d}",
        "operands": [a, b] if experiment not in (40, 43) else [a, b, c],
        "prompt": prompt,
        "correct_answer": expected,
        "paired_prompt": paired_prompt,
        "paired_correct_answer": paired_expected,
        "paired_relation": relation,
    }


def build_cases(experiment: int, count: int = DEFAULT_CASES, seed: int = SEED) -> list[dict]:
    if experiment not in EXPERIMENTS:
        raise ValueError("experiment must be in the closed range 023..050")
    if not 1 <= count <= 100:
        raise ValueError("count must be 1..100")
    rng = random.Random(seed * 1000 + experiment)
    selected: set[tuple[int, int, int]] = set()
    cases = []
    for _ in range(10000):
        if len(cases) == count:
            break
        a, b, c = _operands(experiment, rng)
        key = (a, b, c)
        if key in selected:
            continue
        selected.add(key)
        cases.append(_make_case(experiment, len(cases) + 1, a, b, c))
    if len(cases) != count:
        raise RuntimeError("population cannot supply the requested unique sample")
    return cases


def _basic_metrics(records: list[dict], key: str, correct_key: str) -> dict:
    count = len(records)
    parsed = [(rec[key], rec[correct_key]) for rec in records if rec[key] is not None]
    correct = sum(pred == truth for pred, truth in parsed)
    return {
        "problem_count": count,
        "parsed_count": len(parsed),
        "parse_rate": len(parsed) / count,
        "correct_count": correct,
        "accuracy": correct / count,
        "mean_absolute_error_on_parsed": (
            sum(abs(pred - truth) for pred, truth in parsed) / len(parsed)
            if parsed else None
        ),
    }


def evaluate(records: list[dict]) -> dict:
    if not records:
        raise ValueError("cannot evaluate empty records")
    primary = _basic_metrics(records, "prediction", "correct_answer")
    baseline = {}
    for name, value in (("constant_zero", 0), ("constant_nine", 9)):
        correct = sum(record["correct_answer"] == value for record in records)
        baseline[name] = {"correct_count": correct, "accuracy": correct / len(records)}
    metrics = {"primary": primary, "fixed_baselines": baseline}
    paired = [r for r in records if r["paired_prompt"] is not None]
    if paired:
        second = _basic_metrics(paired, "paired_prediction", "paired_correct_answer")
        parsed_both = [r for r in paired if r["prediction"] is not None and r["paired_prediction"] is not None]
        consistent = sum(
            (r["prediction"] == r["paired_prediction"] if r["paired_relation"] == "same"
             else r["prediction"] == -r["paired_prediction"])
            for r in parsed_both
        )
        correct_both = sum(
            r["prediction"] == r["correct_answer"]
            and r["paired_prediction"] == r["paired_correct_answer"]
            for r in paired
        )
        metrics["paired"] = {
            "secondary": second,
            "pair_count": len(paired),
            "both_parsed_count": len(parsed_both),
            "consistent_count": consistent,
            "consistency_rate_on_both_parsed": consistent / len(parsed_both) if parsed_both else None,
            "both_correct_count": correct_both,
            "both_correct_rate": correct_both / len(paired),
        }
    return metrics


def _blank_record(case: dict) -> dict:
    return {
        **case,
        "generated_text": None,
        "prediction": None,
        "paired_generated_text": None,
        "paired_prediction": None,
    }


def _predict(model, tokenizer, torch, prompt: str) -> tuple[str, int | None]:
    batch = tokenizer(prompt, return_tensors="pt")
    with torch.inference_mode():
        sequence = model.generate(
            **batch,
            do_sample=False,
            max_new_tokens=MAX_NEW_TOKENS,
            pad_token_id=tokenizer.eos_token_id,
        )
    continuation = sequence[0][batch["input_ids"].shape[1]:]
    text = tokenizer.decode(continuation, skip_special_tokens=True)
    return text, extract_integer(text)


def _load_model(key: str, revision: str):
    # Local tests and BASELINES_ONLY never import heavy optional dependencies.
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_IDS[key], revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL_IDS[key], revision=revision)
    model.eval()
    config_sha = getattr(model.config, "_commit_hash", None)
    if config_sha != revision:
        raise RuntimeError(f"model revision mismatch: {config_sha} != {revision}")
    return model, tokenizer, torch, transformers.__version__, config_sha


def run_experiments(
    first: int, last: int, *,
    backend: str = "baseline", model_key: str | None = None,
    revision: str | None = None, count: int = DEFAULT_CASES,
    output_dir: Path | None = None,
) -> list[dict]:
    if not 23 <= first <= last <= 50:
        raise ValueError("range must be inside 023..050")
    if backend not in {"baseline", "model"}:
        raise ValueError("invalid backend")
    if backend == "model":
        if model_key not in MODEL_IDS:
            raise ValueError("model_key must be distilgpt2 or tiny-gpt2")
        if not revision or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError("model evaluations require a pinned 40-character commit SHA")
        model, tokenizer, torch, transformers_version, sha = _load_model(model_key, revision)
    else:
        if model_key is not None or revision is not None:
            raise ValueError("baseline-only mode must not name a model or revision")
        model = tokenizer = torch = transformers_version = sha = None
    results = []
    for experiment in range(first, last + 1):
        title, question, regime = EXPERIMENTS[experiment]
        cases = build_cases(experiment, count)
        records = []
        for case in cases:
            record = _blank_record(case)
            if backend == "model":
                record["generated_text"], record["prediction"] = _predict(model, tokenizer, torch, case["prompt"])
                if case["paired_prompt"] is not None:
                    record["paired_generated_text"], record["paired_prediction"] = _predict(
                        model, tokenizer, torch, case["paired_prompt"]
                    )
            records.append(record)
        report = {
            "protocol": PROTOCOL,
            "experiment": f"MathOS-EXP-{experiment:03d}",
            "title": title,
            "research_question": question,
            "sample_regime": regime,
            "status": "MODEL_EVALUATED" if backend == "model" else "BASELINES_ONLY_NO_MODEL",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "seed": SEED,
            "case_count": count,
            "model": MODEL_IDS[model_key] if backend == "model" else None,
            "model_revision": sha,
            "tokenizer_revision_requested": sha,
            "torch_version": torch.__version__ if backend == "model" else None,
            "transformers_version": transformers_version,
            "python_version": platform.python_version(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "decoding": {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS} if backend == "model" else None,
            "metrics": evaluate(records),
            "records": records,
            "limitations": [
                "One fixed small generated sample per experiment; no statistical power claim",
                "Other experiment IDs share model family and protocol, not independent replication",
                "Integer-at-start parsing can reject legitimate responses or misread some prose",
                "Fixed zero/nine baselines are descriptive; not tuned on a training set",
                "Test cases are not shown to be absent from model pretraining",
                "Greedy decoding is not a complete test of mathematical competence",
                "Passing software tests is not independent scientific validation",
            ],
        }
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / f"experiment_{experiment:03d}.json"
            target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        results.append(report)
    if output_dir is not None:
        summary = {
            "protocol": PROTOCOL,
            "mode": backend,
            "completed_model_evaluations": len(results) if backend == "model" else 0,
            "baseline_only_experiment_records": len(results) if backend == "baseline" else 0,
            "experiments": [r["experiment"] for r in results],
            "model": MODEL_IDS[model_key] if backend == "model" else None,
            "model_revision": sha,
        }
        (output_dir / "batch_manifest.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=23)
    parser.add_argument("--end", type=int, default=50)
    parser.add_argument("--count", type=int, default=DEFAULT_CASES)
    parser.add_argument("--backend", choices=("baseline", "model"), default="baseline")
    parser.add_argument("--model", choices=tuple(MODEL_IDS))
    parser.add_argument("--revision", help="Required immutable 40-character model commit SHA in model mode")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    reports = run_experiments(
        args.start, args.end, backend=args.backend, model_key=args.model,
        revision=args.revision, count=args.count, output_dir=args.output_dir
    )
    print(json.dumps({
        "protocol": PROTOCOL, "status": reports[0]["status"],
        "count": len(reports), "first": reports[0]["experiment"],
        "last": reports[-1]["experiment"],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
