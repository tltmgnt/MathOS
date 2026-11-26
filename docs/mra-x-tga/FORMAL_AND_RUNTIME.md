# MRA-X formal verification integration

This separate registry uses MathOS's existing pinned Lean-first verification gate without weakening its trust policy. The three proposed lemmas concern exact scope-projection relaxations, not the F038 theorem or efficient SAT algorithms.

From a checkout with Lean 4.14.0 installed:

```sh
python -m mathos.research.lean_first inspect --registry docs/research/MRA_X_LEAN_CLAIMS.v1.json
python -m mathos.research.lean_first verify --registry docs/research/MRA_X_LEAN_CLAIMS.v1.json --output mra-x-lean-report.json
```

The scope-monotonicity lemma uses inclusion of scope families; it does not alone prove the exact-k hierarchy. The latter additionally requires extending smaller scopes to larger scopes. All registry entries are pending statement and external review. Lean was unavailable in the authoring runtime; kernel replay is not claimed. Review the pinned replay, theorem/expected-type witness and transitive axiom audit before assigning a checked status. No automatic theorem promotion.

## Persistent advisory ledger

```sh
python tools/mra_x_runtime.py --self-test
python tools/mra_x_tga.py --example > record.json
python tools/mra_x_runtime.py --record record.json --db /private/path/mra-x.sqlite
python tools/mra_x_runtime.py --audit --db /private/path/mra-x.sqlite
python tools/mra_x_runtime.py --benchmark
```

Keep the ledger and evidence private. The event hash chain is consistency-only and cannot authenticate origin, prevent an owner rewriting or truncating history, or certify scientific truth. The ledger records hashes/dispositions, not evidence bodies; retain the original records in a separate controlled store. Budget validation does not reserve or spend actual resources. The benchmark uses 100 synthetic inputs and modeled stage counts, not live model calls or conventional scientific research. Independent validation remains pending.
