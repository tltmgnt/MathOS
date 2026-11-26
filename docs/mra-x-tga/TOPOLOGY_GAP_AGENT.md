# MRA-X / RE-X Topology Gap Agent

Experimental agentic campaign for the logical reference, not the physical RE-X machine.

## Process
1. Observer: enumerate constraint-topology families and explicitly open evidence gates.
2. Planner: optionally request an AI-generated family priority permutation. Validate it strictly; on failure use a deterministic default.
3. Experimenter: generate seeded heterogeneous finite-domain factors, feasible controls and contradictory controls; test factor additions/removals by recomputation.
4. Execution agent: try four elimination-order strategies on every admitted instance.
5. Verification agent: compare each optimum to exhaustive enumeration; replay JSON witness recovery and verify domain bounds and factor cost.
6. Learning agent: track logical assignment counts by family and strategy, prioritize families with higher observed min-fill overhead, and prefer historically cheaper strategies first.
7. Arbiter: halt on a counterexample or enumeration-budget exhaustion; retain evidence and mark unresolved obligations. Never promote a mathematical or physical claim or autonomously merge code.

## Run
From the repository root with Python 3.11+:

    python tools/mra_x_topology.py --self-test
    python tools/mra_x_gap_agent.py --rounds 2 --output topology-agent-evidence.json

Use a fresh output path; existing files are not overwritten. Set a different seed or a bounded enumeration budget with --seed and --budget. All default runs are offline. For optional AI planning, install the OpenAI Python SDK, configure OPENAI_API_KEY in the environment, and add --model YOUR_AVAILABLE_MODEL. Only a synthetic taxonomy and fixed open-gate descriptions are sent; API charges may apply. The live API path has not been exercised here. The model cannot execute code or alter the evidence gate.

## Local run
Default two-round campaign: 104 bounded instances, 416 candidate checks, zero reported counterexamples. Gate checks also exercised invalid planner output, budget exhaustion, and injected execution failure. The retrospective best of four strategies used 20,570 logical assignments versus 21,570 for min-fill alone. This is an oracle selection after all four executions, not a speedup of the whole campaign. Counts exclude ordering, oracle, serialization, and other overhead. The maximum width observed across all tried orders was 7, not an optimal treewidth claim.

Evidence JSON contains deterministic seeds, instance hashes, candidate checks, selected order strategy, learning events, source hash, and full failing instances if any. Digests are consistency checks, not authenticated signatures. No independent replication or competitor comparison is implied.

## Open gates
- Locate and integrate the real RE-X single-tape implementation.
- Mechanize correctness, termination, physical/logical equivalence and complexity bounds.
- Implement sound incremental reuse rather than full recomputation.
- Run matched time/memory/accuracy comparisons against external solvers.

The campaign is an on-demand bounded process, not an always-on autonomous coding agent. It does not modify its own source, install dependencies, execute model-generated code, or merge branches.