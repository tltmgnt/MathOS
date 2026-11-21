# TGA proof-gap performance baseline

**Scope:** Synthetic AND/OR proof-obligation software measurements. This is
not a mathematics benchmark, RH proof, kernel certificate, or novel theorem.

## Reproduce

Run from the repository root (Python 3.11+):

    python -m unittest discover -s tests -p 'test_proof_gap_benchmark.py' -v
    python scripts/tga_gap_benchmark.py --sizes 10 30 100 500 --layers 4 6 8 \
      --repeats 3 --output artifacts/proof-analysis/tga-performance.json

The separate GitHub Actions workflow tga-gap-benchmark.yml runs those tests
and uploads the JSON as a short-lived artifact on relevant pull requests or
manual dispatch. The report includes platform, Python version, per-case wall
time, peak tracemalloc allocations, graph size, open leaves, and completion-set
count. Measurements include allocation instrumentation, so they are not
unmodified production latency. Benchmark CI is not a continuous performance
regression gate and makes no cross-machine speed claim.

## Fixture design

- chain: a chain of derived obligations ultimately requiring one open leaf;
  linear graph size, single completion set.
- shared: many derived nodes depending on the same open leaf and a shared
  target AND route; stresses overlapping dependencies.
- alternatives: each independent open leaf is an alternative sufficient route;
  grows the antichain of minimal singleton sets.
- binary_choices: an AND of independent OR pairs; has 2^k distinct minimal
  completion sets for k pairs. The report uses k=4,6,8 by default, up to 10.

The fixture families have explicitly computed expected completion sets that are
checked against the existing analyze() implementation. For fixtures with at
most 10 open leaves, an additional exhaustive Boolean valuation cross-check
uses certification_audit.exhaustive_check. Larger cases are marked NOT RUN for
that independent cross-check, rather than silently implying completeness.

## What the results can establish

The benchmark can reveal growth in software work and memory and establish
correct outputs on its synthetic fixtures. The original analyzer enumerates
Cartesian products and only then removes supersets; therefore execution and
output may grow exponentially with distinct alternative completion sets.
Deep recursive chains can also exceed Python's recursion depth; the benchmark
records an explicit RECURSION_LIMIT case and keeps processing other fixtures.
A benchmark workflow can complete while reporting failed cases, so review
both the job result and the JSON failed_cases array.
No implementation can enumerate 2^k required results in sub-exponential
total output time. If performance is inadequate, compare an incrementally
pruned antichain algorithm with the unchanged baseline on both cases where
pruning reduces intermediate work and cases where exponential output is
unavoidable. For compressed representations consider BDD/ZDD methods, but
require exact answer equivalence on bounded instances.

## Quality gates before optimizing

1. Record a baseline on pinned commit, Python version and runner.
2. Preserve every existing graph semantics and error condition.
3. Differential-test optimized and baseline completion sets on deterministic
   and randomized acyclic AND/OR cases with an exhaustive finite-model oracle.
4. Include adversarial cases: shared dependencies, dominated supersets,
   high branch fanout, unrelated cycles, and malformed leaves.
5. Report latency, peak allocation, and output cardinality separately. Cap
   resource-intensive enumeration and fail closed instead of reporting proof.

The present implementation checks only user-authored routes. It does not prove
that a route captures the intended mathematical theorem, that an external leaf
is true, or that a formal proof has been completed. Performance progress must
not update any RH or Millennium problem certification state.
