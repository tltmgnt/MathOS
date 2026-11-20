# External RH Lean claim — pinned evidence review (20 November 2026)

**Disposition:** substantial third-party kernel evidence reported; MathOS has
**not** independently replayed the full proof, nor does this record change
MathOS's canonical RH OPEN / NOT_CERTIFIED research states. The Clay
Mathematics Institute continued to list RH as **Unsolved** when this
snapshot was prepared.

## Primary and independent sources

- Author's announcement: https://alpo.ge/remark.pdf (20 November 2026)
- Original joined source archive SHA-256:
  9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc
- Browsable public *mirror* for the small source audit:
  https://github.com/CocoSgt/riemann-hypothesis-lean
  pinned to commit 7cbf7a0c32fca1badf05931879a37c3f8a2b03b4.
  This is not an endorsement or a substitute for verifying the
  author's original archive.
- Andrew Sutherland (MIT), independent verification log:
  https://math.mit.edu/~drew/grh/ .
  **Snapshot as of 2026-11-20 19:45 UTC**;
  consult the live page for subsequent changes.
- Clay RH listing: https://www.claymath.org/millennium/riemann-hypothesis/

## What the external technical checks say

The MIT verification page reports:

| Check | MIT report at snapshot |
|---|---|
| 175,187 Lean modules using Lean/Mathlib v4.33.1 | Compiled successfully |
| Axioms for five headline theorems | Only propext, Classical.choice, Quot.sound |
| leanchecker per-module kernel replay | All modules accepted |
| Independent nanoda Rust kernel on exported proof | Accepted, exit 0 |
| lake comparator end-to-end | Still running at snapshot |
| Lean default/paranoid export kernel checks | Still running at snapshot |
| Sandboxed independent source rebuild | Not reported complete at snapshot |

These are meaningful independent checks and stronger than a mere
self-declaration of verification. MIT notes that the source compilation
and export used an **unsandboxed** environment; the entire build was
not compared against a lake build, and mathlib definitions must be
interpreted correctly. This repository does not independently
certify those runs.

The external theorem in src/Main.lean is
riemannHypothesis : RiemannHypothesis. At the pinned Mathlib revision,
RiemannHypothesis quantifies over all nontrivial zeta zeros and
asserts real part 1/2. Related declarations concern Dirichlet
L-functions. The headline bridge is
Formalism.VW.rh_of_every allChi, where allChi references
UpperTheory.FinalTheorems.everyCharacter. Checking this short
source chain is *not* replaying its transitive proof dependencies.

The author's phrase "without assumptions" does not mean "without
foundational axioms": the MIT axiom audit reports three standard
Lean axioms, not additional unproved conjectural axioms.

## Run MathOS small pinned audit

    python -m mathos.research.rh_external_claim_audit
    python -m mathos.research.rh_external_claim_audit --fetch-pinned --output artifacts/rh-external/headline-audit.json
    python -m unittest discover -s tests -p 'test_rh_external_claim_audit.py' -v

Offline mode checks the fixed source/status snapshot. The fetch mode
downloads only six small files via HTTPS from immutable GitHub commit
URLs, checks exact Git blob SHA-1 identifiers, parses theorem headers,
checks Lean/Mathlib pins, and confirms the Mathlib RH target structure.
It does not execute upstream code, run the enormous transitive proof,
or download a multi-gigabyte export.

**Threat model:** edited source references, status promotions and source
hash mismatches must fail closed. Matching a source hash does not
mathematically verify a proof, nor does a hash sign the author identity.
The independent kernel report is evidence from MIT, not a new result
obtained by this small MathOS audit.

## Remaining work

Study the mathematical content of the critical implication from
UpperTheory.FinalTheorems.everyCharacter to the full RH theorem.
Obtain sandboxed full-source kernel replay, precise axiom audit,
scope equivalence and knowledgeable independent mathematical review.

No MathOS open proof obligation is automatically discharged.
See docs/research/RH_OMEGA.md for MathOS's separate Li/Weil research
pipeline.