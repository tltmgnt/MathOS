# TGA Ω — exact gap analysis and Level 6 target

This upgrade changes the default finite proof-route engine. It does not prove
authored edges, verify external mathematical assumptions, or establish a new
Millennium theorem. Level 6 here is a proposed research maturity target,
not an accreditation or a status awarded by tests.

## Algorithm

Validate the entire graph with iterative topological sorting, including unused
routes. Compute reachable nodes in dependency order. A leaf contributes either
the singleton open obligation or the empty completion set for an assumed external
result. For an AND route, form unions one dependency at a time and discard any
set containing a smaller candidate immediately. OR alternatives are merged by
the same inclusion rule. This preserves exact results because union is monotone:
if A is a subset of B then A union C is a subset of B union C. Pruning B
cannot eliminate an inclusion-minimal final solution. The result is an antichain
of minimal sets, not a minimum-cardinality-only answer. It is relative to the
modeled routes, not a list of mathematically necessary axioms.

Compute minimal blocking sets as minimal hitting sets of all completion sets.
Withholding a blocking set prevents all modeled routes from closing. A modeled
closed route has no open-leaf blocker. Counts are not mathematical difficulty.

The legacy recursive implementation is retained for matched comparisons.
The new engine bounds graph nodes, edge occurrences, frontier cardinality,
retained cardinality and work units. These are algorithmic caps, not hard
wall-clock or byte guarantees. Exponential output remains possible.
On exhaustion the API raises ResourceLimitError, and the reporting layer emits
RESOURCE_LIMIT with null completions/blockers, never a partial closed result.
The default result fields are unchanged for exact successful calls.

## Reproduce

    python -m unittest discover -s tests -p 'test_proof_*.py' -v
    python -m mathos.proof_analysis.tga_level6 suite /tmp/tga-replay
    python -m mathos.proof_analysis.tga_level6 replay /tmp/tga-replay/Riemann.json
    python scripts/tga_exact_benchmark.py --output /tmp/tga-benchmark.json

Use a fresh output directory. The report binds the authored graph, target,
limits, exact sets and finite oracle status with SHA-256; replay recomputes the
result, not just its digest. A separate truth-table evaluator checks reachable
graphs of at most 10 open leaves and 100 nodes. Larger cases are explicitly
NOT_RUN_SIZE_LIMIT, not independently certified. The benchmark records source
SHA, Python, platform and instrumented measurements; Actions retains artifacts.
All checks are project-internal; hashes do not authenticate the author.
The current Lean finite-DAG theory is relevant but is not a refinement proof
of this optimized Python implementation.

## Level 6 gates

| Gate | Status at implementation |
|---|---|
| Exact incremental finite AND/OR engine and bounded failure semantics | Implemented, CI pending |
| Differential, truth-table and adversarial checks | Implemented, CI pending |
| Current repository model replay and matched baseline benchmark | Implemented, CI pending |
| Formal refinement connecting optimized implementation to abstract semantics | Not established |
| Independent specialist assessment of route fidelity and completeness | Not established |
| Preregistered held-out evaluation against external methods, including null results | Not established |
| Independently replicated novel result, archived release and sustained external use | Not established |

Use the existing external validation protocol and publication checklist.
No automated process may change canonical mathematical certification based on
this report, and no scientific claim or Level 6 status is promoted here.
