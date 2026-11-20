# First Proof public-replay benchmark adapter (experimental)

This adapter is **not** an official First Proof harness, endorsement, scoring implementation, or independent scientific assessment. It is an optional, offline, non-authoritative experiment script. This integration does not alter the repository's existing evidence or proof-review logic. No results are ingested into authoritative mathematical claims or research-evaluation state.

First Proof's third batch measures research-math solutions with expert refereeing for correctness, exposition, and attribution. It uses one shot per question. Publicly released questions are suitable for **retrospective public replay**, not an uncontaminated held-out benchmark; prior training or exposure may invalidate research-performance comparisons. Do not distribute private/unpublished problem material without authorization. See https://1stproof.org/third-batch.html.

## Input manifest

Create a directory with UTF-8 problem snapshots, e.g. `p01.txt`. Record exact SHA-256 hashes of their original bytes. Supply a JSON manifest:

```json
{
  "schema_version": "mathos_firstproof_benchmark/1",
  "benchmark_id": "firstproof-batch3-public-replay",
  "source_url": "https://1stproof.org/third-batch.html",
  "problems": [
    {"id": "p01", "path": "p01.txt", "sha256": "<64 lowercase hex characters>"}
  ]
}
```

Problems must be unique, sorted by ID, inside the manifest directory, and hash-pinned; no symlinks or path traversal. This repository does not bundle Third Batch questions, official solutions, or referee reports. Users must populate verified, licensed source snapshots themselves.

## Run one attempt per problem

```bash
python3 scripts/firstproof_benchmark.py run \
  --manifest /data/firstproof/manifest.json \
  --output /data/firstproof/run.json --timeout 300 \
  -- python3 /path/to/model_runner.py
```

The runner must consume the problem text on **stdin** and emit a UTF-8 solution on **stdout**. The command executes once per problem, without shell interpolation or retry. Runner process errors and timeouts are recorded as attempts, not dropped or silently retried. Outputs include runner argv, immutable source-manifest hash, result hashes, separate stderr, and explicit `authoritative: false`, `firstproof_certified: false`, and `evaluation_mode: public_replay_ungraded` markers. The output path must not exist.

The adapter intentionally does **not** implement a model runner, Lean verification, or official First Proof scoring. It does not create a true trusted sandbox: run only commands you trust, with no secrets in their environment, and run untrusted models or plugins in a separately secured container. Process limits are limited to a wall-clock timeout; stdout/stderr are spooled to temporary files with a 2 MiB per-stream result cap, but runner CPU, RAM, disk, process count, filesystem access, and network access are NOT sandboxed; apply external quotas and isolation. The inputs and output files can contain copyrighted or sensitive material; manage their access separately.

## Bind manual, independent review

Prepare a separate `grades.json` using this local, explicitly **nonofficial** 0–5 ordinal scale:

```json
{
  "reviewer": "independent-expert-identifier",
  "scores": [
    {"problem_id": "p01", "correctness": 3, "exposition": 4, "attribution": 2, "notes": "Reviewer rationale"}
  ]
}
```

```bash
python3 scripts/firstproof_benchmark.py grade \
  --run /data/firstproof/run.json \
  --grades /data/firstproof/grades.json \
  --output /data/firstproof/review.json
```

The review hash-binds the exact run bytes. This is merely a record of self-supplied grading; it is **not** independent referee authentication or a First Proof grade. Reviewer identity and score provenance must be established out of band. No aggregate research success claim is calculated.

## Verify replay and review integrity

```bash
python3 scripts/firstproof_benchmark.py verify \
  --manifest /data/firstproof/manifest.json \
  --run /data/firstproof/run.json \
  --review /data/firstproof/review.json
```

Verification rechecks every problem SHA-256, the exact manifest hash, run output hashes,
run identity, and optional review-to-run binding. It **does not** rerun the model,
authenticate a reviewer, or validate the mathematical correctness of any solution.
Inputs are capped at 1 MiB per problem and output capture at 2 MiB per stream.
Invalid UTF-8, runner failures, timeouts, and output overflow are marked explicitly.

## Test

```bash
python3 -m unittest discover -s tests -p 'test_firstproof_benchmark.py' -v
```

## Next integration gates

For a formal MathOS release, establish an approved dataset license, isolated/pinned model execution with resource and network controls, authenticated external referee attestations, trusted source publication receipts, leakage and prepublication controls, independent result audit, and a reviewed local integration contract. Do not promote public replay into held-out evaluation or mathematical authority.
