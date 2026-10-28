"""MathOS Internal Reasoning Laboratory: activation capture."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def capture_activations(model_name, prompt):
    """Capture hidden states from an open-weight transformer."""

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Install torch and transformers to run this experiment."
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True,
        )

    hidden_states = outputs.hidden_states

    layers = []
    for index, hidden in enumerate(hidden_states):
        last_token = hidden[0, -1, :].float()

        layers.append({
            "layer": index,
            "hidden_size": last_token.numel(),
            "last_token_activation": last_token.tolist(),
        })

    return {
        "schema_version": "1.0",
        "experiment": "MathOS internal activation capture",
        "model": model_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "token_count": inputs["input_ids"].shape[1],
        "layers": layers,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="sshleifer/tiny-gpt2",
    )
    parser.add_argument(
        "--prompt",
        default="Policy A has score 8. Policy B has score 4.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/internal_reasoning/activations.json",
    )

    args = parser.parse_args()

    result = capture_activations(args.model, args.prompt)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Captured {len(result['layers'])} hidden-state tensors")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
