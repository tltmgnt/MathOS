# RH-Ω — integrated research and finite-to-global assurance

**Status:** bounded research orchestration implemented; **RH is OPEN**.
No universal theorem, full analytic continuation proof, universal Li positivity,
global Weil positivity, fixed self-adjoint Hilbert–Pólya operator, or
independently accepted Riemann Hypothesis proof is claimed.

This implements the RH-Ω proposal from the supplied 13-page
technical architecture document. It lives **inside MathOS**, not in a
disconnected repository.

## Quick start

From MathOS root (Python 3.10+, standard library):

    python -m mathos.research.rh_omega --output artifacts/rh-omega/report.json
    python -m mathos.research.rh_omega --audit artifacts/rh-omega/report.json
    python -m unittest discover -s tests -p 'test_rh_omega.py' -v
    python scripts/rh_omega_benchmark.py --repetitions 2
    lean formal/RHTransferLogic.lean
    coqc -q formal/coq/RHOmegaFinitePrefix.v

## Eight integrated checks

| PDF subsystem | RH-Ω check | Actual output |
|---|---|---|
| Mathematical Foundation | mathematical_foundation | Source-map zeta/xi identities and their domains |
| Li Criterion Universal Positivity | li_universal_positivity | Float formula for first Li coefficient; exact **synthetic** finite-prefix countermodel |
| Weil Positivity Verification | weil_positivity | Finite **uncertified** arithmetic Weil Gram; L2 comparison explicitly distinct |
| Analytic Continuation Audit | analytic_continuation | Bounded numerical theta-reflection sample, not analytic continuation |
| Zero Distribution Analysis | zero_distribution | Zero-counting main-term estimates only; zero locations not certified |
| Adversarial Proof Testing | adversarial_proof_testing | Four explicit invalid-inference challenges |
| Lean Formal Verification | lean_formal_verification | Existing Lean conditional-transfer source; Coq finite-prefix lemma; separate CI kernel checks |
| TECT Evidence Acceptance Gate | tect_evidence_acceptance | Enforces existing G1-G6 plus G5P and blocks proof-state promotion |

The proposed ten agent roles appear as **deterministic review records**:
analytic, zero, prime, spectral, positivity, conjecture, counterexample,
formal verification, evidence and consensus. They are not running LLMs,
nor independent mathematical experts. See [agent contracts](RH_OMEGA_AGENTS.md).

## Relationship to the source document

The PDF decomposes RH into analytic foundation, functional symmetry,
zero distribution, prime connection, equivalence criteria, proof construction
and verification. These are a **research agenda**, not seven proven theorems.
In the half-plane Re(s)>1, zeta's Dirichlet series and Euler product
converge absolutely. The completed xi function satisfies xi(s)=xi(1-s).
Its reflection symmetry alone does not confine zeros to the critical line.
The approximate N(T) formula reports zero counts, not horizontal locations.

The full target is to show that every nontrivial zeta zero has real part 1/2,
equivalently that the set of nontrivial off-line zeros is empty.
Li's criterion requires lambda_n >= 0 for **every** n>=1, with the correct
zero-summation convention; finite checks are not sufficient.

## Reuse instead of duplication

- [RH proof firewall](../../mathos/research/rh_proof_firewall.py) and
  [canonical obligations](rh_proof_obligations.json);
- [exact synthetic Li-prefix obstruction](../../mathos/research/riemann_li_prefix_005.py);
- [arithmetic Weil Gram](../../mathos/research/riemann_weil_gram.py);
- [theta/Fredholm numeric diagnostic](../../mathos/research/riemann_theta_fredholm.py);
- [existing Lean finite-to-global logic](../../formal/RHTransferLogic.lean).

The finite-to-global firewall rejects all of the following inferences:

1. A finite Li prefix or computed zero sample implies all-index positivity.
2. A finite Weil Gram implies positivity on every admissible test.
3. Lower semicontinuity and positivity on a dense subset imply positivity everywhere.
4. A parameter-dependent Fredholm determinant is a fixed self-adjoint zero operator.
5. A green proof-assistant test for a bounded logical lemma proves RH.

In (3), the countermodel f(0)=-1 and f(x)=1 for x != 0 is lower
semicontinuous and positive on a dense subset but negative at the origin.
This is why the existing G3 continuity/sign-stability gate remains necessary.

## TECT research-acceptance boundary

All generated packets retain global_claim_status=OPEN,
certification=NOT_CERTIFIED, proof_promotion=NONE and
decision=RESEARCH_ONLY. They carry source SHA-256 digests, a payload
fingerprint, eight bounded stages, and ten scoped role records.
The auditor checks canonical RH proof-state and explicitly rejects
promotions even if a forged packet has a recomputed digest.

Hashes are not independent signatures or theorem proof objects;
valid schemas and local runs establish only software evidence.
Model-authored proposals cannot change the canonical register.

See [Phase I Li obligations](RH_OMEGA_LI_PHASE1.md) and
[benchmarks](RH_OMEGA_BENCHMARKS.md). The unresolved mathematical
obligations G1-G6 and G5P are not discharged by this implementation.

## New external theorem-claim verification track

The November 20, 2026 Alpöge/Claude Lean proof announcement and independent
MIT kernel-check evidence are audited separately from RH-Ω's numerical
experiments. See [the pinned external source review](RH_EXTERNAL_CLAIM_2026.md)
and [its machine-readable snapshot](RH_EXTERNAL_CLAIM_2026.v1.json).
This external-source audit does not replay the full proof or update canonical
proof obligations. Consult the live MIT status page for changes after the
19:45 UTC snapshot.
