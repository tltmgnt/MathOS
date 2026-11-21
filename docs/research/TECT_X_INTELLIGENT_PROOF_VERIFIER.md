# TECT-X — Topological Gap Analysis intelligent proof-verifier prototype

**Research status:** `BLOCKED_NOT_MATHEMATICALLY_VERIFIED` for all modeled cases.  
**Scope:** Deterministic structural, evidence, and scope diagnostics. **Not** a proof assistant, automatic discovery model, independent theorem reviewer, or mathematical certification system.

This prototype links TECT-X's [six-theme evidence taxonomy](TECT_X_THEMATIC_REGISTER.v1.json) to
MathOS's existing [AND/OR proof-dependency engine](../../mathos/proof_analysis/gap_analysis.py).
It asks a bounded, falsifiable question: *What authored proof obligations remain unresolved,
which recur across candidate routes, where could a finite experiment be mistaken for a
universal theorem, and are the evidentiary links internally consistent?*

## How it works

1. **Typed claim intake.** A versioned [proof-case dataset](TECT_X_PROOF_VERIFIER_CASES.v1.json)
   declares each target, its mathematical scope, the alternative authored AND/OR proof routes,
   open obligations, and bounded evidence records. The dataset cannot mark leaves as
   proven or confer mathematical certification.
2. **Provenance crosswalk.** Each evidence ID must exist in the thematic source registry,
   which must itself pass the repository's existing TECT-X evidence-integrity check. Optional
   `mapped_claim` references must identify **open** work packages in
   [the legacy proof-obligation register](../proof-analysis/OBLIGATIONS.v1.json).
3. **Logical dependency diagnostics.** The existing proof graph engine rejects directed
   dependency cycles and computes **inclusion-minimal unresolved leaf sets** under the
   *authored* OR-of-AND graph semantics. Common blockers are the intersection of those sets.
   No route's real mathematical sufficiency is presumed.
4. **Topological bookkeeping.** Build the **undirected 1-skeleton** of the dependency graph.
   Its `H0` is the number of connected components; its `H1` is the cycle rank
   `edges − vertices + components`. A diamond from one shared dependency produces an
   undirected cycle even when the directed proof graph is acyclic. This is **not** the
   persistent homology of zeta zeros, a homological proof gap, or evidence of a theorem.
5. **Intelligent *rules-based* triage.** Open leaves are ranked by how often they occur
   across minimal authored completion sets, whether they affect all alternative routes,
   and whether evidence is bounded or narrower than the target. The score is an **ordering
   heuristic**, not a numerical probability of truth, a validated AI inference, or progress
   toward a mathematical proof.
6. **Nonpromotion report.** The report preserves evidence limitations, identifies
   finite-to-universal and conditional-to-unconditional scope transfers, and *always*
   emits `scientific_certification: false`. A structurally valid audit exits zero,
   while `--require-proof` exits code 2 because independent mathematical proof
   certification is not implemented.

## Supported initial research cases

| Case | Research target | What can be diagnosed | Unresolved proof boundary |
|---|---|---|---|
| `RH-TGA` | RH spectral and zeta/TDA paths | Shared global bridge, incomplete fixed operator and zero identity, finite scan scope mismatch | Noncircular all-zero proof; neither authored route is independently validated as sufficient |
| `SELMER-TGA` | Infinite exact 2-Selmer-dimension-three subfamily | Descent versus moment strategies; conditional counting lemma; class-group/local/image gaps | Uniform global arithmetic proof and genuinely infinite qualifying parameter set |
| `ZETA-FINITE` | Bounded one-million-function report | 128-point-per-family sample, controls and missing independent rerun | A successful finite experiment does not certify RH or the full million-point H1 computation |

The data model does **not** infer completeness merely because two proof routes are listed.
The actual theorem definitions, parameter ranges, hypotheses and prior-art boundaries remain
in the dedicated [Selmer proof-obligations document](papers/TECT_X_SELMER_INFINITUDE_PROOF_OBLIGATIONS.md)
and [RH spectral research files](TECTX_RH_FIXED_JACOBI_HILBERT_POLYA_GATE.md).

## Run the verifier

From the repository root (standard-library Python 3.11+; no network/model API):

```sh
python -m mathos.research.tect_x_intelligent_proof_verifier
python -m mathos.research.tect_x_intelligent_proof_verifier --json \
  --report artifacts/tect-x/proof-gap-report.json
python -m unittest discover -s tests -p 'test_tect_x_intelligent_proof_verifier.py' -v
```

For a gate that requires mathematical proof rather than internal consistency:

```sh
python -m mathos.research.tect_x_intelligent_proof_verifier --require-proof
# Exit 2: mathematical certification unavailable / modeled obligations still open
```

GitHub Actions runs the JSON audit and adversarial tests and uploads the report as a
short-lived CI artifact. It **does not** use CI passage as mathematical certification.

## Interpreting the report

- `ok: true` means that authored graph structure, crosswalks and status restrictions
  are internally consistent—not that any deduction is valid.
- `minimal_completion_sets` lists sets of unresolved leaves under the exact authored
  graph semantics, not guaranteed necessary/sufficient mathematical lemmas.
- `common_to_all_authored_routes` shows cross-route dependencies such as a
  noncircular RH bridge.
- `topological_gap_analysis.graph_h0_components` and `graph_h1_cycle_rank` measure
  *model graph structure*, not zero-set geometry or correctness of a mathematical argument.
- `scope_transfer_flags` highlight bounded or conditional evidence being used in
  a broader proof proposal without an established all-cases step.
- `prioritized_unresolved_obligations` carries a rule-based heuristic ranking and
  human-authored next verification actions. The scores are not scientific confidence.
- `source_sha256` fingerprints the local inputs, but hashes are not external signatures.

## Security and mathematical integrity

This is a **fail-closed metadata analyzer** with a bounded finite input model.
It does not ingest or execute untrusted proofs, call an LLM, invoke Lean/Coq, or
perform general mathematical semantic entailment. All input evidence remains
source-authored; adding an evidence link never establishes its proposition.
Reviewers must independently check every implication, the accuracy of mathematical
definitions and quantifiers, and the legitimacy of imported theorems.

The next credible upgrade is a **separate formally checked certificate adapter**
(Lean/Coq proof terms or similarly trusted checked artifacts) with pinned environments,
explicit axioms, scope/assumption matching and independent review. That would need an
actual checker invocation and artifacts. Merely declaring a certificate path or a
`verified=true` flag is prohibited by this prototype's schema.
