# Riemann Hypothesis: source-level review of the critical Lean bridge

Scope: **Pinned, eight-file source review only**. This is not a complete
independent reproduction of the 175,187-module claimed proof.

The source examined is the public mirror
[CocoSgt/riemann-hypothesis-lean](https://github.com/CocoSgt/riemann-hypothesis-lean/tree/7cbf7a0c32fca1badf05931879a37c3f8a2b03b4)
at commit 7cbf7a0c32fca1badf05931879a37c3f8a2b03b4.
Pinning exact Git blobs makes the examination reproducible but does not
provide a signature of author identity. See [the external proof-status
snapshot](RH_EXTERNAL_CLAIM_2026.md) for the separate third-party kernel
reports and their historical timestamp.

## What the short bridge actually says

The source defines UpperTheory.EveryCharacter as

    ∀ (N : ℕ) [NeZero N] (χ : DirichletCharacter ℂ N) (s : ℂ),
      1 / 2 < s.re → (χ ≠ 1 ∨ s ≠ 1) →
      DirichletCharacter.LFunction χ s ≠ 0

In words: every Dirichlet character L-function has no zero to the right
of the critical line, except for the special trivial character/pole
case excluded by the hypotheses. This is much stronger than the Euler
product's standard no-zero half-plane Re(s)>1.

The main-conclusion source contains these dependencies:

    UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter
       |
       v
    UpperTheory.FinalTheorems.everyCharacter_of_row
       |                   |
       |                   +-- UpperTheory.Zero.LLC.recTExists
       |                   +-- UpperTheory.One.vwin_of_row
       |                   +-- LiteratureTheorems.every_character_of_literature_of_vWin
       |
       v
    UpperTheory.FinalTheorems.everyCharacter
       |
       +-- Formalism.VW.rh_of_every
       |         |
       |         +-- Formalism.VW.rh_of_right
       |         |       +-- classical zeta functional equation
       |         |
       |         +-- Dirichlet L-function mod-one = zeta
       |
       +-- UpperTheory.riemannHypothesis_of_everyCharacter
                 +-- completed zeta functional equation

The two routes from EveryCharacter to RH are **conditional** logical
implications (their input theorem is already a zero-free half-plane).
The much more difficult claim is the unconditional construction of
EveryCharacter, especially the global Galois/automorphic/literature
input chain.

## Independent mathematical analysis of the final bridge

Assume ζ(s) ≠ 0 for all Re(s)>1/2, except s=1. A nontrivial zero with
Re(s)>1/2 is then impossible by direct contradiction. If a nontrivial
zero ρ had Re(ρ)<1/2, the completed zeta functional equation gives a
zero at 1-ρ, with Re(1-ρ)>1/2. The gamma/trivial-zero exclusions and
removal of poles must be justified, as the Lean bridge files attempt
to do. Therefore the zero-free half-plane plus the classical
functional equation is sufficient for RH.

This verifies a **conditional reasoning pattern**, not that the
zero-free hypothesis has been proved. In particular a statement
asserting nonvanishing only when Re(s)>1 does not suffice.

## Evidence and explicit limitations

The new small-file auditor:
- verifies eight *additional* upstream Git blob SHA-1 pins and exact
  theorem/reference patterns, beyond the six-file headline audit;
- distinguishes independent Galois input, local Langlands existence,
  automorphic window and literature-to-every-character theorem steps;
- identifies two proof-to-RH routes and the classic symmetry
  mechanism;
- runs offline tamper tests and optionally fetches immutable upstream
  source bytes over HTTPS;
- reports every link as source-traced only: no kernel is invoked.

**What is NOT established by this check:** that the named automorphic
and local Langlands lemmas are true in their intended generality; that
all transitive theorem dependencies are sound; that a local MathOS
kernel has replayed the full proof; any community acceptance or Clay
recognition. The huge
EveryCharacterOfLiteratureOfVWin.lean source and its transitive imports
are out of scope. The separately reported independent MIT kernel tests
remain external evidence, not outputs of this MathOS job.

## Commands

    python -m unittest discover -s tests -p 'test_rh_external_bridge_audit.py' -v
    python -m mathos.research.rh_external_bridge_audit
    python -m mathos.research.rh_external_bridge_audit --fetch-pinned --output artifacts/rh-external/bridge-trace.json

The audit is **read-only** with respect to canonical MathOS proof
obligations. Its conclusions cannot promote RH to solved.

## Most useful next mathematical review

Review, with an independent specialist, the exact definitions and
hypotheses behind:

- UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter;
- UpperTheory.One.vwin_of_row;
- UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin.

The decisive question is whether the deep lemmas truly imply the
unconditional character nonvanishing statement under *standard*
definitions and without smuggling RH or GRH into a definition or
mathematical modeling assumption. A full sandboxed source rebuild,
axiom audit and verified theorem statement equivalence are essential
technical complements, not substitutes for this mathematical review.
