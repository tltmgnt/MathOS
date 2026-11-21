# REMETHEON

**Mathematical Memory Intelligence**

*Every insight remembered. Every proof advanced.*

REMETHEON is the selected public-facing brand identity for mathematical research and learning tools built on the existing **MathOS** repository and **TECT-X** mathematical assurance toolkit. The name combines *remembrance* with *theorem*: its long-term promise is that mathematical reasoning should preserve context, provenance and unresolved questions across time.

**Brand adoption is not a claim that all planned product capabilities already exist.** The current repository contains research prototypes for TECT-X Topological Gap Analysis, evidence provenance and scoped Lean formal certificates. Persistent temporal mathematical memory, an autonomous AI tutor, and a finished unified researcher/student app are **roadmap features**, not shipped services.

## Brand positioning

**Category:** Mathematical intelligence and proof-assurance software.

**For:** Professional researchers, graduate/undergraduate mathematics students, and educators. The brand is designed to be useful at both research and learning levels; it does not imply endorsement or affiliation by any named mathematician.

**Promise:** Make mathematical ideas traceable and help users distinguish what is conjectured, tested, formally verified and externally validated. Long-term, preserve the *history* of how arguments and understanding change.

**Voice:** Rigorous, curious, intelligible, precise about scope. Avoid claims of universal theorem proving, guaranteed semantic fidelity, independent proof approval, or cross-session memory until demonstrated.

**Primary name:** `REMETHEON` (uppercase wordmark) or `Remetheon` in prose.

**Descriptor:** `Mathematical Memory Intelligence`.

**Brand line:** `Every insight remembered. Every proof advanced.` This expresses a *design ambition*, not an assertion that a persistent memory engine is already deployed or that all proposed proofs are valid.

## Product architecture

| Public family name | Function | Current repository reality |
|---|---|---|
| **Remetheon TGA** | Map proof dependencies, structural holes, evidence-scope errors | Implemented **research prototype**; see [TGA gap analysis](../research/TECT_X_INTELLIGENT_PROOF_VERIFIER.md) |
| **Remetheon Kernel** | Formal certificates for exact typed propositions, finite topology and bounded graphs | Implemented **scoped research tooling**, with pinned Lean checks; see [formal verification](../research/TECT_X_FORMAL_VERIFICATION.md) and [typed arguments](../research/TECT_X_TYPED_ARGUMENT_VERIFICATION.md) |
| **Remetheon Chronicle** | Temporal reasoning memory: attempts, dependencies, revision history and provenance | **Planned**; no persistent mathematical memory service added by this rebrand |
| **Remetheon Research** | Researcher-facing exploration, candidate bridges, chronological evidence review | **Planned integrated product experience**; individual MathOS research modules exist |
| **Remetheon Scholar** | Adaptive student instruction with a history of mathematical understanding | **Planned**; no completed learning assistant or long-term learner memory is claimed |

TECT-X remains a technical/research subsystem identifier. MathOS remains the GitHub repository, existing import/package namespace, CLI and historical identifier. Neither is silently renamed or removed.

## Temporal remembrance: proposed semantics

When the future Chronicle capability is implemented, the intended record is an **event with provenance**, not an assumed fact. Suggested record fields include `record_id`, `created_at`, `observed_at`, `source_id`, `author_role`, `statement`, `claim_status`, `depends_on`, `revision_of`, `evidence_hash`, `verification_artifacts` and `privacy_scope`.

An event should preserve whether it is a hypothesis, experiment, counterexample, finite or formal result, or an independently reviewed conclusion. Later revisions must not silently overwrite historical failed attempts; sources and verification status remain inspectable. Different researcher and student presentations must share the same underlying claim status.

This paragraph defines a **future product requirement**, not a deployed database schema, user memory setting, connector or service.

## Working naming examples

- **REMETHEON** — Mathematical Memory Intelligence
- **Remetheon TGA**, powered by TECT-X — topological proof-gap analysis
- **Remetheon Kernel** — Lean-backed exact formal goal checks
- **Remetheon Chronicle** — *planned* temporal mathematical knowledge histories
- **Remetheon Scholar** — *planned* learner experience

Suggested announcement copy:

> Introducing REMETHEON, the mathematical memory intelligence identity for MathOS and TECT-X research software. The current research tooling traces proof obligations and checks selected formal propositions. Temporal remembrance and unified student/researcher experiences are part of the roadmap, not claims of an already-deployed system.

## Compatibility and adoption

1. Keep the upstream repository at `tltmgnt/MathOS` and preserve the `mathos`, `mathosx` and TECT-X code paths, public links, published evidence records, workflows and imports.
2. Use REMETHEON for public-facing README, product/design language, and future interfaces. When clarifying lineage use “REMETHEON, built on MathOS and TECT-X.”
3. Maintain the machine-readable [brand manifest](remetheon.brand.json) as the source of truth for product names and maturity statuses.
4. Keep existing proof results and research limitations unchanged; a new name adds **no** independent mathematical validation or mathematical theorem.
5. Do not claim exclusive rights: trademark clearance, conflicting-name assessment, trademark applications, domain registration, and copyright/brand ownership verification are separate tasks that have **not** been performed as part of this commit.

## Core principle

*A mathematical memory should remember not merely what was claimed, but what was actually checked, where it was checked, and what remained unknown.*
