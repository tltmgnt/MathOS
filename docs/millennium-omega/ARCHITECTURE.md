# Architecture

The implementation is additive. The canonical sources of truth remain:

- docs/proof-analysis/OBLIGATIONS.v1.json — seven MathOS research-route graphs.
- docs/research/HYPOTHESES.v1.json — bounded test plans.
- docs/research/CLAY_FULL_TARGETS.v1.json — authored Clay target alignment.
- mathos/research/hypothesis_pipeline.py — deterministic bounded probes.

Flow:

    Canonical obligation register + target mapping + hypothesis plan
                             |
                     run_exploration()
                             |
              seven stable Millennium Ω engine adapters
                             |
      discovery -> conjecture -> derivation -> falsification
                             -> verification -> evidence
                             |
       TECT audit (status, schema, provenance, stage trace, digest)
                             |
                    Research-only JSON packet

Engine adapters have stable names and report each mathematical gap, dependency
list, finite/conditional probe and its assumptions. The six Ω agents are
deterministic typed records in this first implementation; the derivation agent
does not generate mathematical proofs, the falsification stage records a
falsifier but does not claim to have executed a universal test, and the
verification agent acknowledges that the global Lean/Coq/independent reviews
have not occurred.

TECT is a **fail-closed research acceptance gate**, not an oracle for
mathematical truth. It can reject a malformed or overclaimed record; passing
TECT establishes only a locally consistent research packet. SHA-256 covers
canonical input files and the emitted packet, but is not an authenticity
signature or an independent review. External proof-status upgrades must be
handled via a separate human-reviewed process outside this runner.

Lean 4 and Coq are separate foundational examples formalizing the tiny
Boolean acceptance decision. They use independent kernels; neither connects
a formal theorem to the analytic or geometric Millennium statements.

The runner is read-only with respect to all existing MathOS files and uses
the standard library for deterministic/offline execution. CI verifies the
new Python harness, runs adversarial tampering cases, compiles Lean and Coq,
and preserves a scoped benchmark artifact.
