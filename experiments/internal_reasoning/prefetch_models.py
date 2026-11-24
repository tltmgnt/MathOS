"""Fetch required public model snapshots; fail if unavailable, never synthesize results."""
import time
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

MODELS = ('sshleifer/tiny-gpt2', 'distilgpt2')
FILES = ['config.json', 'generation_config.json', 'tokenizer.json',
         'tokenizer_config.json', 'special_tokens_map.json', 'vocab.json',
         'merges.txt', 'model.safetensors', 'pytorch_model.bin']


def load(model):
    for attempt in range(5):
        try:
            snapshot_download(repo_id=model, allow_patterns=FILES,
                              local_files_only=(attempt == 0), max_workers=2)
            AutoTokenizer.from_pretrained(model, local_files_only=True)
            AutoModelForCausalLM.from_pretrained(model, local_files_only=True)
            print(f'Model cache validated: {model}', flush=True)
            return
        except (OSError, RuntimeError, ValueError) as exc:
            if attempt == 4:
                raise RuntimeError(f'Real model unavailable: {model}') from exc
            if attempt:
                time.sleep(20 * 2 ** (attempt - 1))


if __name__ == '__main__':
    for model in MODELS:
        load(model)
