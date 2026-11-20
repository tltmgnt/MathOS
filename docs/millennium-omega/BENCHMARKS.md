# Benchmark protocol

Run a deterministic offline smoke benchmark:

    python scripts/millennium_omega_benchmark.py --runs 3 --output artifacts/millennium-omega/benchmark.json

The benchmark checks these structural outcomes for every run:
- exactly seven engine records;
- exactly six stages per engine;
- identical SHA-256 packet fingerprints across repetitions;
- RESEARCH_ONLY acceptance and zero globally proved problems.

The tool records minimum/median/maximum runtime in seconds for context,
but deliberately enforces **no arbitrary throughput target**. Runtime depends
on runner hardware and the existing finite probes.

The benchmark does not establish automated mathematical discovery, improved
scientific validity, theorem completeness, comparative superiority, or
external recognition. Formal compilation is a separate CI job and proves
only Boolean TECT policy examples.

Adversarial tests cover global proof-state forgery, fake agent proof claims,
duplicate engine IDs, altered evidence digests, canonical-register
promotion, and falsified probe mappings. Extend these fixtures when new
claims are added; never remove negative evidence to inflate a result.
