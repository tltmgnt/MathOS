# MathOS discovery infrastructure: Level 6 target

This is a proposed project-specific maturity framework, not an external accreditation.
The target is established scientific discovery infrastructure. Passing the packet workflow
is a bounded engineering milestone only. No new discovery or independent result is asserted.

## Reproduce the first bounded packet

Use a fresh, isolated checkout of the exact source commit in the packet manifest, Python
3.12, Git and Lean 4.14.0. Do not execute unfamiliar Lean or Python with credentials
or access to confidential data. The existing Lean installer follows the upstream elan
bootstrap script; its bytes and the runner image are not hermetically pinned.

    python -m unittest discover -s tests -p 'test_discovery_release.py' -v
    python -m mathos.research.discovery_release build /tmp/mathos-discovery
    python -m mathos.research.discovery_release verify /tmp/mathos-discovery

The output directory must not already exist. GitHub Actions uses a temporary directory
outside the checkout. The manifest records the actual checked-out SHA (which can be a
PR merge commit), runtime versions and payload hashes. A verifier checks the fixed
inventory and byte integrity, not authenticity or truth. Obtain the expected manifest
from a trusted source; anyone can regenerate hashes. Compare scoped claims, axioms,
source hashes and benchmark trial outcomes with a fresh replay; do not require exact
diagnostic strings or platform metadata across environments.

The packet runs the existing Lean-first registry and three-task handwritten smoke
benchmark, including replay and negative controls. It is not coverage of all formal
files, a benchmark of automated discovery, or a substitute for domain review.

## Acceptance gates

| Gate | Evidence required | Current boundary |
|---|---|---|
| Reproducibility | Commit-bound packet, passing negative controls, archived environment and independently repeated replay | Packet proposed; external replay pending |
| Claim assurance | Exact proposition, trusted axioms, dependencies, limitations and independent statement-fidelity review | Bounded Lean registry; wider coverage and review pending |
| Level 5: independent validation | A real external operator, prespecified acceptance rule, genuine observations, review decision and conflict disclosure | Not established |
| Comparative performance | Frozen held-out tasks, matched resources, baseline methods, timeouts, errors, uncertainty and negative outcomes | Smoke controls only |
| Scientific contribution | Specific new result, prior-art review, checked proof or domain evidence, independent specialist acceptance | Not established |
| Level 6: established use | Versioned archival release, independently repeated contribution and sustained external research adoption with documented corrections | Not established |

For the first independent study, choose the SAT1 choice-word support statement as a
bounded mathematical target. Review the informal-to-formal correspondence separately
from kernel replay. Consult the existing [review register](papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json)
and [external-validation protocol](../EXTERNAL_VALIDATION.md). No one is represented
as having accepted an invitation. For comparative benefit, use a separate preregistered
held-out proof-review or theorem-proving study; handwritten Lean controls are not a
performance comparator for AI systems.

Use the existing [study package auditor](../../validation/manifest.template.json) and
[publication checklist](../PUBLICATION_READINESS.md). Keep missing reviews, failed
replications and null results visible. Authenticated human decisions, archival release
and documented adoption are required outside CI. No workflow may automatically
promote a Millennium Prize claim, certify maturity, or publish a release.
