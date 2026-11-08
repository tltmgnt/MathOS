# Proof dependency and review evaluation

This implementation measures graph analysis correctness, local performance and recorded
review outcomes. It does not award a 5/5 rating or establish comparative superiority.
Repeated external validation remains necessary for that rating. No expert study or
independent reproduction has been performed by adding this code.

## Run the graph comparison

```bash
python -m unittest discover -s tests -p 'test_proof_review.py' -v
python -m mathos.proof_review benchmarks/proof_review/example.json --repeats 7 > local-report.json
```

The example is synthetic. The report includes a claim review packet, all inclusion-minimal
completion sets, their shared obligations and graph identity. Claims are open,
established_external or derived. A derived claim has alternative routes (OR), each of
which requires all its dependencies (AND). Missing nodes, cycles and empty routes are
rejected. Statement text and route sufficiency are not mathematically verified.

The analyzer propagates minimal sets and is checked against a separately implemented
Boolean exhaustive baseline. Both receive the same graph. Execution order alternates;
raw nanosecond timings and Python peak allocations are retained. Allocation measurement
is separate from timing. Enumeration is potentially exponential; the baseline accepts
at most 16 open leaves. Peak allocations are not process RSS. Repeated local runs are
timing samples, not independent empirical replications. A fast result on this tiny example
does not predict performance on larger graphs or outperform specialized BDD/SAT tools.

## Measure missed dependencies

Call `dependency_metrics(reference_graph, candidate_graph)` with independently adjudicated
graphs. It returns missed and spurious edges, precision and recall; undefined denominators
return null. It checks coverage of authored edges, not mathematical necessity. Edge
coverage alone cannot detect incorrect AND/OR grouping: assess route sufficiency separately
and compare completion sets when the graphs share the same claim semantics.

Freeze the reference before evaluating candidates. Keep held-out labels out of candidate
adapters. Report invalid candidate graphs as failures, not excluded successful cases.
Do not count synthetic graph agreement as evidence of fewer real mathematical omissions.

## Record expert review

Collect actual consented review observations as a JSON list, with one baseline and one
assisted observation per reviewer/case pair. Each observation contains `reviewer_id`,
`case_id`, `graph_sha256`, `condition` (baseline or assisted), `order` (1 or 2), positive
`seconds`, and unique `expected_issue_ids` and `found_issue_ids` arrays. Issue IDs must
refer to the same independently adjudicated set in both conditions.

```bash
python -m mathos.proof_review observations.json --reviews > review-report.json
```

The report retains review time, missed findings and false positives together. Missing,
duplicate or mismatched pairs are rejected. Review order and learning remain possible
confounds. Counterbalance assignment across participants; use disjoint matched cases or
an independently designed parallel-arm study for causal conclusions. This paired importer
does not analyze a parallel-arm design. Protect reviewer identity using pseudonyms.
Do not publish invented timings as expert observations.

## Evidence gates toward a defensible rating

| Rating | Required evidence |
| --- | --- |
| 1 | Scoped hypothesis and comparator |
| 2 | Implemented, tested measurement workflow |
| 3 | Held-out comparative advantage meeting preregistered practical and statistical criteria |
| 4 | Independent external replication on the scoped task |
| 5 | Repeated external validation across representative datasets and operators |

Complete and freeze `benchmarks/proof_review/protocol.json` before collecting evaluation
outcomes. Specify thresholds, sample-size rationale, hardware, runtime versions, comparator
versions, graph sizes and density, review assignment, accuracy noninferiority margin and
handling of timeouts. Retain negative outcomes and raw evidence. Analyze correlated
observations at the independent unit level. Use the existing R3B paired reporting utilities
only when their independence and coverage assumptions hold. Do not infer a confidence
interval from repeated deterministic correctness checks.

External reviewers must supply their own reviewed references, collection records and
replication reports. Local tests, digests and CI cannot fulfill those gates. Assess the
three criteria separately; improvement in runtime cannot establish review quality.
