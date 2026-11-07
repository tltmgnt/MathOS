# MathOS Experience–Facts–Observation (EFO) v1

A **general-purpose, offline empirical validation layer** adapted from the EFO design in Grok-HedgeOps-DTI commit `9092a5d`. MathOS uses EFO for science, research, engineering and interventions—not only markets.

## Scope and separation
- `mathos.efo.EFORecord` is a provenance/claim record; it is **not** `mathos.r3b.Observation`, which represents benchmark metrics.
- Formal proof verification remains separate. An empirical observation cannot prove a mathematical theorem.
- EFO is an additive opt-in API; it does not alter `MathOS.solve()`, benchmark outcomes, or existing TOPO-406 registries.
- All EFO records are research-only. No external APIs, trades, interventions, or automatic decisions.

## Workflow
1. Record experience/observation with source label, observation time, recording time, and canonical measurement snapshot.
2. Link a fact to an observation, then link a hypothesis to its evidence.
3. Preregister a named numerical criterion, comparison, threshold, and outcome horizon.
4. Record the observed value **after** the horizon; a missing value is `inconclusive`.
5. Verify links, time ordering, criterion agreement, and the recomputed verdict.
6. Export a deterministic, SHA-256 fingerprinted bundle.

```python
from mathos.efo import record, register_test, evaluate_test, export_chain, verify_export

obs = record("observation", "2026-11-01T00:00:00Z", "2026-11-01T01:00:00Z", "fixture:latency", "Latency was 10 ms", {"latency_ms": 10})
hyp = record("hypothesis", "2026-11-01T01:00:00Z", "2026-11-01T02:00:00Z", "researcher", "Latency will fall below 8 ms", {"target_ms": 8}, (obs.digest,))
test = register_test(hyp, criterion="latency_ms", operator="lt", threshold=8, registered_at="2026-11-01T02:00:00Z", horizon_end="2026-11-02T00:00:00Z")
outcome = evaluate_test(test, criterion="latency_ms", observed_at="2026-11-02T00:00:00Z", recorded_at="2026-11-02T01:00:00Z", source_id="fixture:latency", value=7)
assert outcome.verdict == "supported"
assert verify_export(export_chain((obs, hyp), (test,), (outcome,)))
```

Run `python -m unittest tests.test_mathos_efo -v` or `python -m unittest discover -s tests -p 'test_mathos_efo.py' -v`.

## Trust boundaries
- User-supplied timestamps and source labels are not independently authenticated.
- SHA-256 checks internal consistency; it is not a signature or a tamper-proof ledger.
- Metric labels are checked for exact agreement, but values are supplied by callers; the system cannot independently verify they came from the named source.
- A supported threshold test is not statistical significance, causality, or future predictive validity.
- Hypothesis preregistration is checked chronologically **within the provided data**, not against an external trusted clock.
- EFO v1 does not claim that a result generalizes beyond the tested setting.
