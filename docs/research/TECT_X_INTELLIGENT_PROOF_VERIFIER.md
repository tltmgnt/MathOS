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

## Independently checked finite mathematical deductions

The [typed Lean certificate workflow](TECT_X_FORMAL_VERIFICATION.md) extends
this structural auditor with actual kernel-replayed finite graph-chain
deductions. Lean 4.14.0 must type-check a separately authored proposition
contract and report **no transitive axioms** for four lemmas about C4,
a three-edge path and a filled triangle. A successful run establishes
only these exact F2 topological facts, not the correctness of every TGA
graph algorithm, the validity of any human-authored dependency arrow, or
a theorem about zeta zeros. Formal certificate status is **never imported
as closure of RH or Selmer obligations**.

Run `python -m mathos.research.tect_x_formal_certificates --check-lean`
only when the pinned Lean toolchain is available in a disposable environment.
Static runs do not report kernel verification.

## Bounded general graph certificates

Beyond the four manually scoped finite Lean lemmas, the
[general finite graph module](../../mathos/research/tect_x_general_graph_certificates.py)
now checks author-declared simple graph incidence data. Two Python
connectivity methods and exhaustive F2 cycle enumeration cross-check
Gaussian-elimination results. **Lean then independently checks** that
every possible F2 edge chain has boundary zero exactly when it lies in
the proposed cycle-basis span, and that the basis is linearly independent.

The [five anchored cases](TECT_X_FINITE_GRAPH_CERTIFICATES.v1.json) span
cycle dimensions 0, 1, 2 and 3, including disconnected graphs. They
generate ten exact finite Lean theorems rather than simply trusting a
Python-computed Betti number.

```sh
python -m mathos.research.tect_x_intelligent_proof_verifier \
  --verify-general-graph-cycles --lean lean \
  --report artifacts/tect-x/validated-finite-graphs.json
```

The Lean proof remains scoped to each **bounded input graph**, not a
general all-graphs correctness theorem for TGA, nor a connection between
TGA's authored dependency graph and the topology of zeta zero sets.

## Typed mathematical argument proof checking

The [typed argument verifier](TECT_X_TYPED_ARGUMENT_VERIFICATION.md) now accepts
additional **repository-reviewed Lean formalizations**, each paired with a
separately authored exact formal reference proposition. An immutable
checker-generated Lean module directly checks that the candidate proof
inhabits the reference type, and `#print axioms` reports must show no
transitive axioms. Run
`python -m mathos.research.tect_x_intelligent_proof_verifier --verify-typed-arguments --lean lean`
with the pinned Lean toolchain.

The checker verifies only that precise formal deduction. It explicitly
reports open semantic edges from informal human intention to formal reference,
from local lemma to an authored TGA theorem route, and from CI to independent
external mathematical reproduction. It never certifies arbitrary English
arguments or closes RH, BSD, or Selmer research obligations.

## Security and mathematical integrity

This is a **fail-closed metadata analyzer** with a bounded finite input model.
By default it does not execute untrusted proofs, call an LLM, or
perform general mathematical semantic entailment. Optional pinned-Lean
flags invoke a kernel checker on the repository's validated finite-topology
propositions and reviewed typed argument proofs against separate formal goals. All input evidence remains
source-authored; adding an evidence link never establishes its proposition.
Reviewers must independently check every implication, the accuracy of mathematical
definitions and quantifiers, and the legitimacy of imported theorems.

The finite Lean proof-certificate adapters now perform actual kernel replay,
with pinned versions, explicit model assumptions and axiom reports. The still-open
next milestone is a **formally justified correspondence between intended
mathematical meaning, the independent typed reference, and each TGA proof edge**,
with a refinement theorem for the Python analysis, independently reviewed
axiom/import trust, and external expert assessment. Merely declaring
a certificate path or `verified=true` can never replace verification.
