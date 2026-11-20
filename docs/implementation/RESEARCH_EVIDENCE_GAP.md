# Research evidence gap gate (version 1)

**Status:** bounded, offline, structural integrity gate. **Not** a theorem prover, scientific validation system, external-review authenticator, or a replacement for existing `mathos.validation`.

The repository contains individual research modules, proof-dependency analysis, tests, review workflows and exports. This contract connects them through an **explicit, SHA-256-bound evidence chain** that records absent steps as gaps. It intentionally cannot decide whether the chain's authored claims are true, whether reviewers are independent, or whether an experiment establishes generalizable superiority.

## Contract

A package contains a `manifest.json` and one evidence file per **recorded** role. Pending roles must use `null` for `path` and `sha256`. A single manifest records an exact source commit, scoped claim ID and five ordered steps:

```
source -> analysis -> verification -> review -> export
```

A minimal incomplete example (all roles except source are pending):

```json
{
  "schema_version": "research_evidence_manifest/1",
  "claim_id": "demo_claim",
  "source_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "scope": "Demonstration only: no research correctness asserted",
  "records": [
    {"kind":"source","state":"recorded","path":"source.txt","sha256":"<replace with actual lowercase SHA-256>","depends_on":[]},
    {"kind":"analysis","state":"pending","path":null,"sha256":null,"depends_on":["source"]},
    {"kind":"verification","state":"pending","path":null,"sha256":null,"depends_on":["analysis"]},
    {"kind":"review","state":"pending","path":null,"sha256":null,"depends_on":["verification"]},
    {"kind":"export","state":"pending","path":null,"sha256":null,"depends_on":["review"]}
  ]
}
```

Each recorded role requires an existing regular file under the package directory and its exact file SHA-256; symlinks, absolute paths, parent traversal, duplicates, altered data, missing predecessors and missing steps fail closed. The version-1 contract permits only these five fields at the manifest root and five fields per record. Artifact bytes are capped at 32 MiB and the manifest at 1 MiB. It is intentionally a **single linear evidence chain**; branching and logical alternatives remain modeled separately by `mathos.proof_analysis.gap_analysis`.

## Run

```bash
python -m mathos.evidence_gap /path/to/evidence-package
python -m unittest discover -s tests -p 'test_evidence_gap.py' -v
```

Exit 0 means structurally valid, including intentionally pending steps. Check `status` and `unresolved_roles` in the JSON response:

- `lineage_packet_structurally_complete`: every required artifact is present and correctly linked **as declared**.
- `lineage_packet_structurally_valid_with_gaps`: records have no structural defects but one or more roles remain pending.
- `incomplete_or_invalid`: invalid schema, artifact integrity or claimed dependencies. Exit 1.

All responses explicitly set `mathematical_truth_verified=false`, `external_validation_established=false`, and `human_review_authenticated=false`. A recorded `review` file is **not** independent or authenticated expert review. Even a structurally complete five-file packet does not assert that any contained verification or adjudication succeeded.

## Relationship to MathOS

- **Proof routes:** `mathos.proof_analysis.gap_analysis` computes author-modelled minimal completion sets, not mathematical necessity. This evidence gate checks materialized lineage, not dependency theorem truth.
- **Expert studies:** `mathos.validation` audits richer external-study manifest packages, which require preregistration, observations and human independence checks. This evidence gate **does not** replace those gates.
- **First Proof public replay:** its run and grade artifacts may be referenced by suitable evidence records, but a user-supplied grade is not authenticated refereeing, private held-out evaluation, or formal proof.
- **Curriculum:** learner exercises and Academy checkers remain software/educational evidence, not externally demonstrated effectiveness.
- **Shared ResearchOs controller:** integration does not change upstream ownership or the pinned interoperability contract.

## Adoption requirements

A caller must explicitly specify which artifact is the exact source, analysis, verification, review and export packet. Do not infer status from file names, test exits or agent confidence. Before labeling a scientific result validated, independently verify the source claim, exact theorem/proof scope, reviewer identity and independence, held-out data policy, prospective protocol and empirical conclusions. Keep the existing `docs/portfolio/STATUS.json` flags unchanged until outside evidence meets their requirements.

**Threat boundary:** this offline audit has no sandbox. It reads local files and checks their content digests; it does not run any embedded model, script or proof. The audit does not defend against a privileged attacker modifying files concurrently or forging both file contents and SHA-256 fields. Use a stable, access-controlled snapshot and separately authenticated publication receipts for high-assurance use.
