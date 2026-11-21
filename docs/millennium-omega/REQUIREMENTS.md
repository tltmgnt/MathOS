# Requirements and acceptance criteria

## Environment
- Python 3.10+ (no extra Python packages required for the new layer).
- Lean 4.14.0 for the dedicated policy example.
- Coq from the CI Ubuntu package repository for the dedicated policy example.
- Existing repository canonical JSON inputs must be present and unchanged.

## Functional requirements
1. Enumerate exactly seven stable engines with a one-to-one correspondence
   to the canonical Millennium model keys and their real missing steps.
2. Use the existing seven bounded probes, preserving the original output scope,
   instead of generating fictitious proof certificates.
3. Emit all six Ω stages with a deterministic evidence digest and explicit
   statements that the global theorem has **not** been checked.
4. Reject proof-status promotion, absent/duplicate engines, forged external
   recognition, unsupported claim scope, missing obligations and altered
   evidence traces.
5. Preserve Poincare's external status, independently of MathOS reconstruction.
6. Do not write to, edit or promote canonical proof registries.
7. Preserve both successful and failed CI logs for review.

## Nonfunctional and security requirements
- No network calls, API secrets, model-authored code execution or autonomous
  repository writes in the framework runner.
- A passing test is a software quality finding, never a new Millennium proof.
- Stable JSON contracts and fingerprinted source inputs.
- Keep proof-checker tools pinned or installed as explicitly documented, and
  audit all trust bypasses in the added formal files.
- Independently challenge the software with adversarial fixture mutation.

## Explicit exclusions
- No full Lean/Coq formalizations of the six open problems.
- No automatically certified Clay prize eligibility or CMI endorsement.
- No autonomous discovery or theorem promotion.
- No claim of external replication or comparative research superiority.
