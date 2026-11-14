# Clay proof-route topology and theorem-evidence gates (v1)

**State: NOT_CERTIFIED.** This is an *author-authored, unreviewed* AND/OR graph of candidate research routes. It is not a mathematical proof, a list of known sufficient lemmas, a probability-of-solution score, a verified theorem, a novelty assessment, or a statement of Clay prize eligibility.

## What was added after PR #19

PR #19 established full official-target **specification field coverage** (10 of 10 populated fields for each of seven topics). This follow-up separately tracks the dependencies that would need mathematical justification. Neither score measures solved mathematics.

- `CLAY_PROOF_ROUTES.v1.json`: 11 **proposed** routes and 10 additional **open** bridge claims. All 14 original canonical obligations are referenced and remain open in `../proof-analysis/OBLIGATIONS.v1.json`.
- `CLAY_EXTERNAL_CLAIMS.v1.json`: dated external-status ledger. Accepted Poincaré mathematics is different from MathOS reconstruction; the September 2026 Navier–Stokes announcement is different from a MathOS proof or Clay acceptance.
- `mathos.research.clay_proof_topology`: fail-closed registry checks, reuse of the verified structural traceability audit, and minimal missing-leaf sets computed from the existing AND/OR graph helper.
- `tests/test_clay_proof_topology.py`: mutation tests reject missing alternatives, omitted dependencies, fake proof/review claims, stale or forged external status, and altered canonical obligations.

## AND/OR route structure

The final target for each MathOS track is modeled as **OR** across the named candidate routes. Each route is an **AND** of the individually listed missing claims. Examples:

- **P vs NP**: SAT algorithm correctness AND polynomial-time bit complexity AND a class-level implication bridge; **OR** an unrestricted separation theorem. Failure of one branch never proves the other.
- **Navier–Stokes**: official alternatives A, B, C, **OR** D. The existing unforced critical-estimate package is relevant to proposed A/B routes only. A/C and B/D must not be conflated; C/D require smooth-forcing, domain, initial-data, and breakdown assumptions.
- **Riemann**: independent operator AND zero identity AND a noncircular universal implication to the location of *every* nontrivial zero.
- **BSD**: the MathOS author-route includes the **stronger refined formula**. Core rank equality is the official essential target and remains logically distinct; the route must not be characterized as a necessary decomposition of core BSD.
- **Poincaré**: already externally solved; the sole MathOS route is an independently checked reconstruction and cannot be presented as a new Clay solution.

The proposed bridge claims are research placeholders, not proved sufficiency theorems. In particular, completing a software checklist is **not** sufficient to close a mathematical target: first the *route-to-target implication* itself must receive independent mathematical review, and the route's quantifier and assumption coverage must be established. The v1 CLI explicitly refuses all statuses except `OPEN`, `PROPOSED_NOT_VALIDATED`, and `not_reviewed`. Any future promotion requires a separately designed, reviewable evidence schema, audit version and human/expert process.

### Reading a minimal completion set

A reported set is one inclusion-minimal collection of **currently open leaves** that would close a route *under the authored Boolean dependency model*. It is **not** a mathematically proven minimal set of necessary lemmas, a minimal cut set of the actual conjecture, or a difficulty estimate. Different proposed routes may have disjoint missing sets, so `common_to_all_modeled_routes` can be empty even while every route is blocked. There is no "percentage solved" computation.

Quantifier escape is a mandatory review consideration. Numerical examples, finite-height searches, small SAT instances, simple geometric cases, finite-volume lattice models or single smooth fluid solutions cannot be promoted to universal theorems without a rigorous bridge.

## External claim ledger (snapshot November 13, 2026)

| External situation | External status | MathOS status |
|---|---|---|
| [Poincaré / Perelman](https://www.claymath.org/millennium/poincare-conjecture/) | Already accepted externally | Independent MathOS reconstruction **BLOCKED** |
| [OpenAI Navier–Stokes announcement, September 8, 2026](https://openai.com/index/navier-stokes-solution/) | Claimed forced-breakdown result with Lean formalization; [CMI statement of September 11](https://www.claymath.org/news/navier-stokes-announcement/) says *apparently settled*, with review ongoing | **NOT_CERTIFIED**; CMI problem page still lists **Active** at the snapshot |

This is an explicitly dated source register, **not a live status checker**. New external review or CMI updates must be entered and reviewed separately; they must never silently change canonical MathOS proof states. Lean formalization of an external claim is not automatically MathOS provenance or an independent Clay award decision.

## Evidence required before a genuine theorem milestone

A separate proposed mathematical theorem should include a precise statement, domains and universal quantifiers, all assumptions and allowed reductions, references to the strongest applicable existing result, an inspectable derivation, counterexample attempts, and evidence of independent review. Formal proof checking is beneficial when feasible, but does not by itself establish novelty or coverage of the official problem. Do **not** mark a proposed bridge `PROVED` based on a passing test, citation alone, nonreviewed draft, or a bounded experiment.

The first meaningful outcome is a *new and independently checkable mathematical theorem* connected to a specific open dependency; none is claimed here. When a result is submitted for publication or review, track its actual evidence and peer feedback outside this fail-closed v1 manifest.

## Reproduce

```sh
python -m unittest discover -s tests -p 'test_clay_alignment.py' -v
python -m unittest discover -s tests -p 'test_clay_proof_topology.py' -v
python -m mathos.research.clay_proof_topology --output-dir artifacts/clay
python -m json.tool artifacts/clay/clay_proof_topology.json
```

The deterministic JSON report records the exact source hashes, all candidate alternative routes, their open dependencies, and conditional minimal completion sets. The audit checks that the source files were not modified, preserves all 14 canonical open claims, and always returns `NOT_CERTIFIED` and `NOT_ELIGIBLE`. GitHub Actions runs these checks on Python 3.10, 3.11 and 3.12. A passed audit means the **metadata and safety contract** held; it does not validate a proof.

See [CMI's official Millennium problem statements](https://www.claymath.org/millennium-problems/) and [CMI prize rules](https://www.claymath.org/millennium-problems/rules/) for the actual mathematical/prize requirements.
