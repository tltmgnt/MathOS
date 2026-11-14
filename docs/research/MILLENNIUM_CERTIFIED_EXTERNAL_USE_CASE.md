# Millennium `CERTIFIED` use case — Poincaré external recognition

**Demonstrated certified case:** **Poincaré conjecture**, already solved by Grigori Perelman and awarded the Millennium Prize by the **Clay Mathematics Institute (CMI)** in 2010.

**Meaning of the word `CERTIFIED`:** A *MathOS status-mirror classification* indicating that an **external authoritative body already recognized this Millennium problem as solved and awarded the prize**. It is NOT a certificate issued by Clay, not a new proof certified by MathOS, not a digital identity/signature, and not automatic verification of the full Ricci-flow proof.

**MathOS independent proof status:** `NOT_CERTIFIED` for all seven authored routes, including the separate `POINCARE.reconstruction` task, with **14 open obligations**.

## Independent public basis

The following official CMI publications were directly inspected when creating the fixed review record:

1. [CMI official Millennium Problems list](https://www.claymath.org/Millennium%20Problems/) — lists Poincaré in the solved section and the remaining unsolved/active problems separately.
2. [CMI Poincaré conjecture](https://www.claymath.org/millennium/poincare-conjecture/) — attributes the proof to Perelman and provides supporting published proof materials.
3. [CMI's March 18, 2010 prize announcement](https://www.claymath.org/wp-content/uploads/2022/06/Poincare-press-release.pdf) — announces the award to Grigori Perelman and identifies the CMI review and approval process.
4. [CMI Millennium Prize rules](https://www.claymath.org/millennium-problems/rules/) — external CMI process; no proposed Millennium solution can be accepted directly through MathOS.

These records are **pinned references, not live-fetched web content by the Python certification runner**. The workflow verifies local identity, consistency and policy against an independently inspected historical case. A new claimed solution or new CMI award can be added **only through a reviewed evidence and checker change**, not via a model-generated "CERTIFIED" claim. Reviewers must themselves re-open and authenticate official CMI records. If CMI changes a public status, the pinned mirror must be reviewed and updated; it is not a real-time status service.

## Exactly one Millennium-level externally certified use case

| Problem | External recognition mirror | MathOS-authored proof |
|---|---|---|
| Poincaré | **`CERTIFIED`**, externally solved/awarded, Perelman (2010) | `NOT_CERTIFIED`; independent reconstruction open |
| Birch–Swinnerton-Dyer | `NOT_CERTIFIED` | `NOT_CERTIFIED` |
| Hodge | `NOT_CERTIFIED` | `NOT_CERTIFIED` |
| Navier–Stokes | `NOT_CERTIFIED` (public registry records *Active*) | `NOT_CERTIFIED` |
| P versus NP | `NOT_CERTIFIED` | `NOT_CERTIFIED` |
| Riemann | `NOT_CERTIFIED` | `NOT_CERTIFIED` |
| Yang–Mills mass gap | `NOT_CERTIFIED` | `NOT_CERTIFIED` |

No one is claiming a solution to the remaining six problems or asserting that the MathOS team has independently reconstructed Perelman's proof.

## Certification-mirror process

```text
CMI public solved listing + 2010 prize press release
                      |
     Human source review / pinned official URLs + attribution
                      |
      Machine rejects altered award provenance or added problems
                      |
     Match CMI Poincaré with separate canonical MathOS record
                      |
       Confirm 7 MathOS tracks BLOCKED / 14 obligations open
                      |
    Create SHA-256-evidenced classification: Poincaré CERTIFIED
                      |
      Six other Millennium records remain NOT_CERTIFIED
                      |
    No proof promotion / no publication claim / no CMI issuance
```

This is a real-world **external certification recognition** use case. It is different from the seven `CERTIFIED_BOUNDED` finite witness checks implemented in [the claim digital twin](CLAIM_CERTIFICATE_DIGITAL_TWIN.md). Neither system confers external Clay prize eligibility or establishes an original MathOS solution.

## Execute

Run in MathOS at Python 3.10+:

```sh
python -m mathos.research.millennium_certification \
  --output-dir artifacts/millennium-certification

python -m unittest discover -s tests \
  -p 'test_millennium_certification.py' -v
```

The runner writes `artifacts/millennium-certification/millennium_certification.json`, with:
- `use_case=MILLENNIUM_EXTERNAL_CERTIFIED_POINCARE`
- `status=CERTIFIED` **only within scope `EXTERNALLY_RECOGNIZED_MILLENNIUM_RESOLUTION`**
- `recognized_by=Clay Mathematics Institute` and `reported_by=MathOS external-recognition mirror`
- links to CMI solved listing, problem page and prize announcement
- `source_verification_mode=PINNED_OFFICIAL_RECORDS_NOT_LIVE_FETCH`
- one externally recognized solved case; six not certified
- `certified_new_mathos_millennium_proofs=0`
- `mathos_canonical_certification=NOT_CERTIFIED`, `canonical_proof_promotion=NONE`, `mathos_open_work_packages=14`
- source and report SHA-256 fingerprints (these are **not digital signatures**)

The runner cannot accept new problem IDs, award dates, recipients or official-source URLs at runtime. It cannot approve a model-proposed proof and never writes to the canonical obligation register.

## Acceptance and future extension

Automated CI runs the verifier and 17 adversarial tests on Python 3.10/3.11/3.12 and uploads the JSON snapshot. These tests detect source-schema and local-status forgery. They do **not** refetch CMI pages or independently prove Poincaré, so they establish reproducibility of the historical source classification, not a new mathematics certificate.

To handle a **future** accepted resolution: first review the official problem's full target, exact publication and community review record under the CMI rules, then record CMI's actual published decision and independently re-review source identity before modifying the mirror allowlist. AI reviewers, numerical experiments and passing CI alone must never mint a new Millennium `CERTIFIED` state.

See [canonical MathOS obligations](../proof-analysis/OBLIGATIONS.v1.json), [Clay target register](CLAY_FULL_TARGETS.v1.json) and [proof-assurance work](THEOREM_ASSURANCE.md).
