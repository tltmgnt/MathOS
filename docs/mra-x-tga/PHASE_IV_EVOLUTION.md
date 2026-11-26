# Phase IV — governed policy evolution
This extension generates bounded elimination-order policies, evaluates them in resource-limited subprocesses, freezes the best training policy, verifies it on disjoint synthetic seeds, and records review candidates and proposed curriculum nodes. It does not generate or run arbitrary source code, alter the trusted curriculum, promote proofs, or merge changes.

Run from repository root on Linux with Python 3.11+:
    python tools/mra_x_evolution.py --seed 401 --ledger evolution.sqlite --output campaign_401.json
    python tools/mra_x_evolution.py --seed 402 --ledger evolution.sqlite --output campaign_402.json
Use fresh outputs, trusted ledger storage and increasing seeds. Each policy uses a registered beam width; its predicted logical enumeration count is compared against the Phase II four-order predictor and the better order is executed. The scope model discards duplicate scopes only for enumeration planning, not actual factor costs. Worker processes have CPU, address-space, file-size and wall-time limits; they are not security sandboxes for untrusted code.

## Local results
Two campaigns selected width 16. Training candidates decreased from five to three after reading the first campaign's record. Across 416 training instances (counted by policy) and 104 held-out instances, 1,040 candidate/baseline comparisons with the exhaustive reference passed. Held-out enumeration counts: 13,563 versus 14,015 and 9,498 versus 9,891; combined 23,061 versus 23,906. Search also expanded 28,386 states in held-out evaluation. These counts do not establish runtime gains. Both policies are REVIEW_CANDIDATE only. Exact deterministic campaign replay, digest, ledger retrieval, malformed aggregate, incorrect-result, no-gain, simulated timeout and invalid-policy controls passed locally.

Each campaign proposes one unapproved curriculum node linked to OPT-702 and VER-602. The candidate graph has 25 nodes; original 24-module registry is unchanged. Evidence fingerprints cover the five imported source modules. Digests are not authentication.

## Remaining gates
True sandboxing for untrusted generated code, reviewed patch generation, independent holdout design, native runtime/memory and matched external benchmarking, original RE-X integration, Lean kernel proof and general equivalence remain open. This is bounded configuration evolution, not autonomous scientific discovery or general self-modification. No 10/10 maturity claim.
