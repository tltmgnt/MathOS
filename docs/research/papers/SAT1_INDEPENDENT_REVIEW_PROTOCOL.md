# SAT1 external mathematical assessment: public call and evidence protocol

**Status:** external assessment requested, but **not performed or authenticated** merely by publishing this page. Neither ChatGPT nor the project maintainers are a disinterested external referee of their own work. A compiler passing checks the formal theorem *as stated* but does not independently establish that the formalization matches a useful research claim or that the result is novel.

## What a mathematically independent reviewer is being asked to do

Review this exact, **small** Lean result:

- [Manuscript](SAT1_FORMAL_NOTE.md)
- [Lean 4 source](../../../formal/SATSupport.lean), declaration `MathOS.satSupport_certificate`
- [Current prior-art ledger](SAT1_LITERATURE_LEDGER.v1.json)
- [Existing review form](SAT1_EXTERNAL_REVIEW.md)
- [Public review invitation](https://github.com/tltmgnt/MathOS/issues/30)
- [Machine-audited review register](SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json)

The theorem states, for each `m : Nat`, that the `SATFactorChoice` words produced by the repository's recurrence number `3^m`, are pairwise distinct, and have signed coefficient `±1`. The theorem **does not** formalize the polynomial ring `Z[x₁,y₁,…,xₘ,yₘ]` or derive any Turing-machine runtime lower bound.

In particular, the expression `∏(xᵢ+yᵢ−xᵢyᵢ)` has `3^m` monomials *after full expansion* but is represented by a compact arithmetic circuit with `O(m)` operations. The example Boolean CNF `∧ᵢ(xᵢ∨yᵢ)` is easily satisfiable (choose `xᵢ=1`), so expanded representation size alone cannot demonstrate SAT hardness.

A substantive external assessment should address formal statement fidelity, actual Lean assumptions/axioms, the algebraic interpretation, prior literature, validity of the non-implication to computational complexity, and whether the note has any publishable mathematical value.

## How the reviewer can conduct a verifiable review

1. State your *own* mathematical background and whether you have contributed to MathOS, advised the maintainers, or have a conflict of interest. There is no obligation to reveal private information beyond what you elect to publish.
2. Record the exact Git commit (or exact `SATSupport.lean` SHA-256), toolchain, imports, and commands. Replay the source using **Lean 4.14.0**. Run `python -m mathos.research.lean_axiom_audit` to inspect the transitive axioms of `MathOS.satSupport_certificate`. This guard rejects `sorryAx`, `Lean.trustCompiler`, and custom assumptions.
3. Read the actual definitions, not just the compiler result. Check `SATFactorChoice`, `satTerms`, `satCoefficient`, and the quantifier `∀ m : Nat`. Say explicitly whether the Lean theorem supports the informal paper's exact wording.
4. Give specific mathematical arguments or counterexamples. Address the gap between the choice-word list and standard multivariate polynomials, and the gap between full expansion and general SAT computational complexity.
5. Identify closest relevant published sources, with bibliographic details, links, and specific passage or theorem identifiers where possible. Distinguish a primary-source check from an unverified search lead.
6. Publish your own review as a **comment on the open issue** or as a GitHub pull request, tied to the reviewed version. Include your assessment, objections, and a recommendation: `LIMITED_SCOPE_ACCEPTABLE`, `REQUEST_REVISIONS`, `REJECT_UNSUPPORTED_CLAIMS`, or `INCONCLUSIVE`.
7. A repository maintainer must **separately** check that the public review actually comes from that account, that self-declared independence is credible, and that the exact formal source is identified. The machine does not authenticate credentials or decide mathematical truth.

## Review intake and immutable evidence

The file `SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json` starts with **zero external reviews**. When a genuine reviewer posts evidence, a maintainer may submit a PR containing a record with these fields: `review_id`, `reviewer_github_handle`, `external_review_url`, `reviewer_affiliation_or_background`, `reviewer_self_declares_independence`, `conflicts_of_interest`, `review_date_utc`, `source_sha256`, `lean_replay_description`, `formal_statement_assessment`, `mathematical_criticism`, `prior_art_findings`, `sat_complexity_assessment`, and `recommendation`.

The strict program `mathos.research.external_review` checks the record's internal consistency, pins exact source digests, and reports that even a structurally valid record has **not been independently authenticated or mathematically accepted**. A fabricated or stale citation must never be promoted to a valid expert endorsement.

```sh
python -m unittest discover -s tests -p 'test_external_review.py' -v
python -m mathos.research.external_review --output-dir artifacts/external-review

# With Lean 4.14.0 present, also run:
python -m mathos.research.lean_axiom_audit --output-dir artifacts/external-review
```

The axiom audit is supported by the [Lean reference manual's guidance on validating proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/). It audits *transitive formal assumptions*, not the external reviewer or paper's novelty.

## Desk assessment that does not count as independent review

The repository also includes [SAT1_DESK_CRITIQUE.md](SAT1_DESK_CRITIQUE.md), an author-side adversarial assessment with the decisive compact-expression counterpoint. This desk critique is useful as preparation for external reviewers, but it **must not be counted as a real independent assessment**.

## Decision policy

- Publishing a reviewer invitation: **request opened**, NOT REVIEWED.
- A GitHub user asserting independence: **self-attested**, NOT AUTHENTICATED.
- A real issue comment or PR: **submission received**, NOT AUTOMATICALLY APPROVED.
- A passing Lean axiom audit: **formal assumptions checked**, NOT NOVELTY VERIFIED.
- Human expert report after authenticated provenance: **eligible for genuine scholarly evaluation**, never automatically a complete Clay solution.
- Clay and original MathOS proof registers: **unchanged NOT_CERTIFIED**, regardless of reviewer recommendation.

**Real mathematical evaluation requires an actual independent mathematician to examine the claim. This repository cannot replace that person's work.**
