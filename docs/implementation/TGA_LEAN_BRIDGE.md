# TGA → Lean 4 kernel-check bridge

**Implemented scope:** compile a finite MathOS TGA dependency-graph implication into a *fully quantified Boolean proposition*, then check the generated proof with **pinned Lean 4.14.0**. This is a genuine step beyond Python-only replay for the stated propositional semantics, not a general-purpose mathematical theorem prover.

## Trust boundary

**What is formally checked:** For **every** valuation of up to six open Bool leaves, the graph's authored premise formula implies its authored goal formula. The generated Lean theorem has no unrestricted user-provided Lean code; all structure comes from the validated TGA graph model.

**What is not checked:** That a graph node label faithfully expresses a real mathematical theorem, that a user-authored route represents a mathematically sound implication, or that externally assumed background claims are true. In this bridge they are *definitions of Boolean composite nodes*, not imported mathematical lemmas. A successful compiler return cannot automatically be promoted into a Millennium Problem or independent research result.

## Usage

```bash
# Emit the exact theorem source for inspection.
python -m mathos.tga_lean_bridge emit \
  benchmarks/lean/tga_graph_smoke.json --output /tmp/TGA.lean

# Verify its proof under an installed, pinned Lean 4.14.0.
python -m mathos.tga_lean_bridge check \
  benchmarks/lean/tga_graph_smoke.json

# Test correct generation and adversarial failures.
python -m unittest discover -s tests -p 'test_tga_lean_bridge.py' -v
```

The `check` command rejects an unavailable/wrong Lean toolchain, a compile error, and a missing or nonempty Lean axiom report. It only reports `lean_kernel_checked: true` when the compiler actually succeeds and the report indicates no axioms. **Even then** it always reports `mathematical_statement_verified: false`, and reports all assumed-external graph nodes.

Unlike a human-written mathlib proof, the theorem is a generated finite Boolean formula. The generator builds the goal from the exact same authorized graph input but Lean rechecks the universal proposition independently. It rejects graphs whose implications fail the existing finite truth-table procedure rather than attempting to prove a false implication.

## Reproducibility and limitations

- 6 open leaves maximum in this initial Lean bridge to constrain `decide` resource usage; the Python finite-graph checker separately supports up to 16 leaves.
- Output is capped at 64 KiB. Cyclic, malformed or missing-dependency graphs are rejected.
- Input is capped at 1 MiB in the CLI. Source and graph SHA-256s are retained for content association, **not** source authenticity.
- `lean --version` must be exactly 4.14.0, and axiom report must indicate no transitive axioms.
- The Lean process checks generated code; use CI isolation, no credentials and trusted toolchain installation controls. The workflow follows the repository's existing elan-based Lean installation approach; further pinning of installation infrastructure and attestation is future work.
- The generator's expansion of shared graph nodes into Boolean formulas is not itself a formal Python/Lean refinement theorem. That requires further research and an independent semantics proof.

## Next milestones for competitive theorem proving

1. Replace opaque Boolean labels with typed Lean propositions and explicit, kernel-checked proof terms for every claimed inference edge.
2. Add trusted source mappings, independently reviewed theorem statements and a sound translation contract.
3. Add proof-search agents that propose Lean tactics; check all candidates inside isolated, resource-limited environments and retain failed attempts.
4. Compare with Aesop/LeanDojo and SMT baselines under shared held-out benchmarks with pinned budgets, versions, timeouts and negative outcomes.
5. Commission external reproducibility and security audits before claiming research-level correctness or a 10/10 quality rating.

## Related work

`mathos.tga_theorem` remains the bounded Boolean decision procedure; `formal/FiniteRouteDAG.lean` formalizes related smaller DAG semantics; `mathos.research.lean_benchmark` provides separate Lean tactic-benchmark infrastructure; `mathos.evidence_gap` supports artifact lineage, not theorem correctness.
