# Fail-closed adversarial testing and cross-compiler replay of a bounded arithmetic claim

**MathOS milestone paper M002 · 2026-11-24 · Research technical note (not peer reviewed)**

## Abstract

We extend the bounded exact-arithmetic validation of milestone M001 with cross-compiler execution and ten targeted adversarial controls. The same 24,336 ordered input pairs passed using GCC and Clang. All ten controls rejected their intended failure, including a compiled sign-mutated C++ implementation. These results support local adversarial testing of the specified claim and its evidence gate; they do not establish independent reproduction, complete security, broader mathematical validity or deployment approval.

## 1. Question and contribution

Can a passing arithmetic oracle and its provenance gate detect targeted falsification rather than merely accept a valid baseline? This is a new MathOS project milestone, not a claim of mathematical or literature priority. The baseline is the finite polynomial multiplication domain defined in M001.

## 2. Methods

Replay the original exhaustive exact evaluation oracle with GCC and Clang separately. Copy the actual register and its hash-bound evidence into a temporary directory; inject one controlled modification at a time, require the expected rejection reason, and restore the baseline. For the arithmetic mutation, change coefficient accumulation from addition to subtraction in a temporary C++ source copy, compile it, and run the same exhaustive oracle. Require a wrong-product error rather than an unrelated compilation failure. Recheck the original register after the trials.

The policy gate was tightened so successful attack and reproduction records must match claim scope, stability evidence must match scope, and unauthenticated external reproduction cannot promote a claim.

## 3. Observed results

| Control | Observed outcome |
|---|---|
| Tampered evidence bytes | Rejected |
| Artifact path traversal | Rejected |
| Contradiction injection | Rejected |
| Failed attack evidence ignored | Rejected |
| Out-of-scope attack records | Rejected |
| Stale claim version | Rejected |
| Expired evidence | Rejected |
| Unauthenticated reproduction | Rejected |
| Unauthorized deployment | Rejected |
| Compiled arithmetic mutant | Rejected |

Both compiler executions passed 24,336 ordered pairs each (48,672 pair executions, not independent observations). The ten controls passed on [GitHub Actions run 45362051952](https://github.com/tltmgnt/MathOS/actions/runs/45362051952), which completed with all ten workflow steps successful. The observed log initially recorded SUPPORTED; the subsequent evidence-register update records the scoped claim as ADVERSARIAL_TEST and requires replay of the hash-bound report. No statistical or universal security inference is drawn.

## 4. Reproducibility

Pinned experimental source: [40e68218b04f9c137588a036fe02d9bade79dbf2](https://github.com/tltmgnt/MathOS/commit/40e68218b04f9c137588a036fe02d9bade79dbf2).

```sh
CXX=g++ python3 evidence_tect/validate_polynomials.py --check
CXX=clang++ python3 evidence_tect/validate_polynomials.py --check
python3 evidence_tect/adversarial.py
python3 evidence_tect/check.py
```

Requirements: Python 3, GCC, Clang, pinned repository checkout. Evidence: [job logs](https://github.com/tltmgnt/MathOS/actions/runs/45362051952/job/138334290303) and M001. No network model downloads are required for these tests.

## 5. Limitations

The two compilers used the same test protocol and execution organization. This is cross-toolchain robustness, not independent external replication. Ten selected perturbations cannot show resistance to all tampering, malicious code, compromised runners, hash trust-anchor substitution or invalid external identity claims. No actual governance approval is supplied. The broader MathOS claim remains UNVERIFIED.

## 6. Conclusion

All targeted controls were detected, and the finite arithmetic result survived two compiler toolchains. The next assurance milestone requires independently obtained evidence from an authenticated external operator. Further local work can extend bounded coverage, mutation diversity and formal proof without pretending that these substitute for external acceptance.
