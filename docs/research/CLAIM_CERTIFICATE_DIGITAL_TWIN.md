# MathOS mathematical claim-certificate digital twin v1

**What is automatically certifiable today:** seven *precisely bounded mathematical claims* (one per Millennium research track), using exact rational/integer arithmetic, a replayed propositional-resolution proof, or an explicit finite chain-complex calculation.

**What is not certified:** **any entire Millennium Prize Problem**, any new universal theorem, originality, expert peer review, or a proof assistant theorem checked in Lean. The canonical MathOS proof-obligation status remains **`NOT_CERTIFIED`** with **14 open obligations across seven `BLOCKED` tracks**. Poincaré remains independently solved externally, not re-proved by MathOS.

The term `CERTIFIED_BOUNDED` in the output means **"this exact, explicitly declared finite witness was checked by the local finite checker."** It is not a Clay status, an expert endorsement, a formal Lean kernel certificate, or a digital signature. SHA-256 digests show content identity only, not a cryptographic signature, trusted execution environment or author identity.

## Digital twin process

```text
Immutable source snapshot                      External AI / untrusted candidates
Clay target + canonical obligation register                   |
      |                                                        |
      +-- [1] Fail-closed 7-target and 14-open-claim audit     |
      |                                                        |
      +-- [2] Compare exact pinned finite claims <--------------+
      |           reject broader statements / new proof kinds / status fields
      |
      +-- [3] Verify witness using a tiny, fixed, bounded checker:
      |           SAT: resolution replay + exhaustive assignments
      |           Arithmetic: exact rational / finite-field / ring checks
      |           Topology: mod-2 boundary maps and ranks
      |           No generated code execution; no AI verdict as evidence
      |
      +-- [4] All checks pass -> issue FINITE-only attestations
      |           proof statement / scope / witness SHA-256 / checker method
      |
      +-- [5] Mirror canonical proof states read-only
                  CERTIFIED_BOUNDED (one exact finite model)
                  NOT_CERTIFIED (all seven Clay problem targets)
                  14 canonical obligations remain OPEN and BLOCKED
                  no automatic repo promotion / no automatic merge
```

## Seven actual fixed-scope certificates

| Track | Automatically checked proposition | Check method | What is **not** established |
|---|---|---|---|
| **RH** | Exact rational harmonic sum \(H_{16}\) | Independent rational reduction over 16 terms | Positivity of all Li coefficients, any nontrivial zero location |
| **P vs NP** | Unsatisfiability of one fixed odd-charge \(K_4\) 3-CNF | Resolution-derivation replay and exhaustive 64-assignment check | A general SAT algorithm or any lower bound on unrestricted algorithms |
| **Navier–Stokes** | Four rational substitutions into \(2K(1-q)/\nu\) with \(K=3\), \(\nu=1\) | Exact rational equality | Validity of all conditional energy-estimate assumptions or global PDE regularity |
| **Yang–Mills** | Exact eigenvalue ratios of eight finite 2×2 positive transfer matrices | Rational determinant, trace and ratio checks | Existence, axioms or a physical mass gap of 4D non-Abelian quantum field theory |
| **Hodge** | Five top-degree products and \(h^5=0\) in the **stipulated** algebra \(\mathbb Q[h]/(h^5)\) | Independent truncated polynomial convolution | All rational Hodge classes algebraic for arbitrary varieties |
| **BSD** | Eight exact \(\#E(\mathbb F_p)\) counts for \(y^2=x^3-x\) | Independent point enumeration, Legendre-character and Hasse tests | Analytic/algebraic rank equality or Sha finiteness |
| **Poincaré** | Boundary ranks (4,6,4) and mod-2 Betti numbers (1,0,0,1) for one finite simplicial complex | GF(2) boundary \(\partial^2=0\) and rank computation | A self-contained reconstruction of Perelman's full proof |

**Why these are called "mathematical" rather than software-only:** Each witness is checked against a stated, fixed mathematical object using exact arithmetic (or explicit finite resolution rules). Nevertheless, *correctness of the checker implementation* is supported by tests, not independently proved in a theorem prover. External mathematical significance and a bridge to the Clay statement are **not** part of these certificates.

## Execute a digital twin snapshot

From repository root on Python 3.10+, no model key or additional Python package required:

```sh
# Generate all seven witnesses; replay independently; emit read-only digital-twin snapshot.
python -m mathos.research.claim_twin --track all \
  --output-dir artifacts/claim-twin

# Verify a single track.
python -m mathos.research.claim_twin --track P-versus-NP \
  --output-dir artifacts/claim-twin/pnp

# Run adversarial and mutation testing.
python -m unittest discover -s tests -p 'test_claim_twin.py' -v
```

Output: `artifacts/claim-twin/bounded_claim_certificates.json`, containing seven `witness_attestations`, exact claim statements, checker methods, witness hashes, source code and registry SHA-256 digests, and **zero certified Millennium solutions**. The canonical register and Clay targets are read and audited but never written.

### Accept an untrusted witness without executing its code

```sh
# trusted-cases.json must be a JSON list of the exact candidate schema:
# model_key, claim_id, kind, statement, parameters, scope, witness
python -m mathos.research.claim_twin --track P-versus-NP \
  --input untrusted-cases.json --output-dir artifacts/claim-twin/replay
```

The checker rejects new claim IDs, duplicate tracks, changes to the pinned theorem text, new proof kinds, modified assumptions, unrecognized keys, forged `CERTIFIED_CLAY` flags, fake `proof_completed` fields, and invalid rational/resolution/point-count/homology witnesses. Input size and resolution steps are bounded, and the program has **no model-provided code execution** or arbitrary network calls.

A failed candidate raises an error **before** issuing the new attestation file. An existing output file from a previous run is not an authoritative current status: consumers must check the `source_sha256` digests against current pinned files and use fresh CI evidence. Report hashes are integrity fingerprints, not signatures.

## How this connects to the AI agent

The [planner–proposer–skeptic–reviewer agent](AGENTIC_RESEARCH_PROCESS.md) may generate candidate statements and proof attempts. Those statements are **untrusted research proposals**. Only witnesses for one of the seven pinned, exactly stated finite propositions can be sent to the twin's `--input` interface.

The twin cannot accept an AI-generated general Clay proof and conclude it is true. New theorem types require (1) a precisely formalized statement, (2) a trusted appropriate proof checker or full derivation, (3) explicit assumption/dependency and scope matching, (4) independently reviewed verifier changes, and (5) independent expert mathematical assessment before any broader scientific claim is considered. The `NOT_CERTIFIED` canonical register may only be changed through a **separate** reviewed mathematical certification process; this digital twin has no such permission.

## Automatic CI and human review boundaries

The [Millennium research CI](../../.github/workflows/millennium-research-tests.yml) runs this digital twin and its corruption tests on Python 3.10, 3.11 and 3.12 and uploads the finite receipt report. The [guarded AI agent workflow](../../.github/workflows/agentic-clay-research.yml) continues to separate offline simulation and manually activated live model runs; it cannot promote proposed lemmas through the twin.

**No hidden advancement:** The only automatically awarded status is `CERTIFIED_BOUNDED` for the **exact finite proposition** as spelled out in each receipt. All seven *Millennium-target* statuses stay `NOT_CERTIFIED`.

See also: [full Clay target traceability](CLAY_TARGET_ALIGNMENT.md), [seven baseline hypothesis experiments](SEVEN_HYPOTHESIS_LAB.md), [mathematical obligation register](../proof-analysis/OBLIGATIONS.v1.json), and [Clay official rules](https://www.claymath.org/millennium-problems/rules/).
