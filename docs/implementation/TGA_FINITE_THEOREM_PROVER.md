# Topological Gap Analysis as a finite theorem prover

**Status:** implemented decision procedure for finite Boolean entailment **relative to an explicitly supplied AND/OR dependency graph**. This is *not* a theorem prover for arbitrary mathematical statements, arbitrary topology, continuous mathematics, or Millennium problems.

The repository's existing `gap_analysis.py` finds minimal sets of author-described open obligations. The new `mathos.tga_theorem` takes the next bounded step: it decides a precisely specified logical proposition of the form

`(premise_1 AND ... AND premise_n) -> goal`

for **all Boolean assignments to at most 16 open leaves**, where derived nodes are ORs of nonempty AND routes and externally established leaves are true *by assumption*. If the implication is false, the tool returns a witness assignment. If true, it produces a replayable finite-model certificate that records exact graph hashes, inputs and how many assignments were checked.

No theorem is established about the real mathematical meaning of a node label or whether an authored route is sound. **This is a semantic decision procedure for a defined propositional model, not Lean kernel verification.** The existing Lean formalization in `formal/` addresses some finite route semantics separately; it does not prove a refinement theorem for this Python implementation.

## Example

Create `example.json`:

```json
{
  "schema": 1,
  "claims": {
    "definition": {"state": "established_external", "routes": []},
    "a": {"state": "open", "routes": []},
    "b": {"state": "open", "routes": []},
    "intermediate": {"state": "derived", "routes": [["definition", "a"], ["a", "b"]]},
    "goal": {"state": "derived", "routes": [["intermediate"]]}
  },
  "premises": ["a"],
  "goal": "goal"
}
```

From the repository root:

```sh
python -m mathos.tga_theorem prove example.json > certificate.json
python -m mathos.tga_theorem verify example.json certificate.json
python -m unittest discover -s tests -p 'test_tga_theorem.py' -v
```

Here, `a` entails `goal` under the *graph semantics* because `definition` is assumed true. Remove `a` from the premises and the prover will return a countermodel with `a=false` rather than fabricating a proof.

The certificate is deterministic and checked by replaying truth-table evaluation, not by relying on its digest alone. The JSON results explicitly have:

```json
{"mathematical_theorem_certified": false, "kernel_checked": false}
```

The complete result also records `verdict`, `assignments_checked`, `premise_satisfying_assignments_checked`, `countermodel` and `spec_sha256`. Certificate replay rejects any altered verdict, countermodel, source graph, flag or count.

## Input and resource limits

- Up to 16 open leaves (at most 65,536 assignments), 256 nodes and a 1 MiB input JSON limit; the complexity of checking all assignments is exponential in open-leaf count.
- The graph must be acyclic; derived nodes require nonempty alternatives made of nonempty AND dependencies; external/open nodes are leaves.
- The specification rejects duplicate dependencies and premises, missing nodes and extra schema keys.
- Arbitrary Python source is not executed from graph input; the CLI only reads JSON and emits JSON. Run local inputs under normal file-access controls.

## Assurance and trust boundaries

| Check | What it supports | What it cannot support |
|---|---|---|
| Finite entailment | A Boolean implication is true for every allowed open-leaf assignment | Truth or necessity of authored mathematical routes |
| Countermodel | A specific assignment refutes a modeled implication | Counterexample to a real-world theorem absent a proved encoding |
| Certificate replay | The same finite model produces the recorded verdict | Independent source authenticity or formal kernel proof |
| Existing Lean modules | Bounded, precisely stated logical results accepted by the kernel when CI succeeds | Full Python refinement or general mathematics |

**Do not convert** `ENTAILED_WITHIN_GRAPH` into `FORMALLY_VERIFIED`, `CERTIFIED` or a Millennium proof. The next meaningful research milestone is a verified translation of concrete mathematical statements into Lean propositions, with trusted kernel proofs for each essential inference and a formal Python/refinement correspondence. Independent mathematicians must check the statement's fidelity and novelty.

The existing `mathos.proof_analysis.certification_audit`, `mathos.research.lean_benchmark`, `mathos.validation`, and `mathos.evidence_gap` (when merged) remain separate tools with their own assurance scopes.
