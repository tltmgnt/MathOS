# MathOS EFO reasoning integration

MathOS now accepts an optional EFO evidence bundle while preserving independent reasoning verification.

```python
from mathos.core import MathOS
from mathos.efo import record, export_chain

obs = record("observation", "2026-11-01T00:00:00Z", "2026-11-01T01:00:00Z",
             "fixture:experiment", "Observed latency", {"latency_ms": 10})
bundle = export_chain((obs,))
result = MathOS().solve("2x + 5 = 13", domain="mathematics", evidence_bundle=bundle)
print(result.verification_status)
print(result.empirical_evidence)
```

## Trust boundary
- EFO checks only internal integrity, reference consistency, and chronology.
- The evidence might be unrelated to the question: `claim_alignment` is always `not_assessed`.
- Source authenticity is `not_verified`; timestamps and sources are caller-supplied.
- AI-generated responses remain unverified; mathematical proof status is not promoted or downgraded by EFO.
- Falsified and inconclusive tests are counted rather than hidden.
- Invalid bundles fail before model invocation.
- No new paid API dependencies, autonomous interventions, or broker connectivity.

Run `python -m unittest discover -s tests -p 'test_mathos_efo_integration.py' -v`.
