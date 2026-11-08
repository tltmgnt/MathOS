# Proof dependency and adversarial analysis

This module integrates the version 3 review prototype into MathOS. It is a
proof-planning and software-checking tool, not mathematical certification.

## Reproduce from the repository root

Python 3.10+; the module uses only the standard library and no API or network.

```sh
python -m mathos.proof_analysis --run-tests --output-dir artifacts/proof-analysis
python -m unittest discover -s tests -p 'test_proof_*.py' -v
```

`--run-tests` executes the repository's proof-analysis tests before generating
reports. Without it, reports explicitly record `NOT_RUN` rather than asserting
a passing test result. Reports go only to the selected output directory; the
working directory is not changed. Generated local artifacts are ignored by git.

## Implemented components

| Component | Location | Scope |
|---|---|---|
| Claim graph and completion sets | `mathos/proof_analysis/gap_analysis.py` | Inclusion-minimal sets relative to authored AND/OR routes |
| Exhaustive checker | `mathos/proof_analysis/certification_audit.py` | All Boolean assignments, capped at 16 open leaves |
| Seven adversarial witnesses | `mathos/proof_analysis/adversarial_analysis.py` | Fixed exact examples, not autonomous discovery |
| Repository runner and result contract | `mathos/proof_analysis/runner.py` | Outputs, source/report hashes and explicit verification states |
| Tests | `tests/test_proof_*.py` | Original 42 checks plus four integration checks |
| CI | `.github/workflows/proof-analysis-tests.yml` | Python 3.10, 3.11 and 3.12; evidence uploaded as artifacts |

## Outputs

- `results.json` and `results.md`: seven authored proof-route models.
- `adversarial_results.json` and `.md`: witnesses, limitations and contested routes.
- `result_contracts.json`: seven records conforming to `result-contract.json`.
- `certification_audit.json`: finite-model checks and unmet mathematical gates.
- `verification_run.json` and `test_run.txt`: actual test execution status.
- `SHA256SUMS.json`: source and report content hashes, not signatures or proof.

Committed evidence in `evidence/proof-analysis/` is a review snapshot. Regenerate
into `artifacts/proof-analysis/` to avoid modifying that historical record.
The output schema for verification status is repository-native and supersedes
the standalone version 3 archive's top-level `tests_run` field.

## Mathematical limits

The NS witness concerns smooth initial fields, not finite-time blowup. The RH
witness concerns an unrelated polynomial, not zeta zeros. The BSD and Hodge
countermodels lack the full arithmetic/geometric hypotheses. The Yang-Mills
sequence is not a gauge theory. The Poincare witness is a finite group, not a
constructed closed three-manifold. The SAT example rules out only explicit
polynomial-size expansion. None is a counterexample to a Millennium conjecture.

External background claims and sufficiency of mathematical edges remain assumed.
Runtime/resource assumptions are separate from the proposed abstract algorithm
correctness theorem. The exhaustive checker and generator were developed in
the same project; agreement is not independent external review.

## Professional review

Start with [HANDOFF.md](HANDOFF.md) or the accompanying Word document, then use
[REVIEW_RESPONSE.md](REVIEW_RESPONSE.md). The first suggested task is proving
the abstract completion-set recurrence correct. The smaller alternative is a
formal proof of the SAT monomial-count theorem. Novelty is not claimed.

See [CERTIFICATION.md](CERTIFICATION.md) for unmet gates and
[the curriculum](../../curriculum/proof-analysis-verification.md) for a learning path.
An [outreach draft](OUTREACH_DRAFT.md) is included for optional use; no recipient
is contacted by the software.
