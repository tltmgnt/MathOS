# Topological Gap Analysis Ω — Curriculum practicum

**Status:** proposed instructional application of MathOS's structural gap framework. This does not validate a topological theorem, mathematical research outcome, or causal impact. Use [the MathOS architecture](../../docs/architecture.md) and [proof-dependency semantics](../../mathos/proof_analysis/gap_analysis.py) as the existing operational boundary.

## Study goal

Construct a directed prerequisite/dependency graph for the academy. Distinguish (a) missing curriculum connections, (b) proof obligations, (c) evidence/assessment gates, and (d) empirical educational outcomes. An edge is a *documented requirement* or model assumption, not proof that a learner possesses that skill.

## Suggested four-session TGA exercise

| Session | Task | Evidence |
|---|---|---|
| 1 — Represent | Draw course and skill nodes; label each prerequisite edge and cite its syllabus | Adjacency list and source references |
| 2 — Diagnose | Identify disconnected outcomes, prerequisite cycles, missing reviewers, and unverified skill transfers | Gap register with priority and falsification checks |
| 3 — Compare | Propose a minimal remediation plan; compare it against a simpler curriculum map without topology-specific machinery | Alternative plans and a necessity argument |
| 4 — Audit | Test a blocked outcome, one incorrect shortcut and an external-review gate; publish a bounded result | Reproducible report with unresolved limitations |

## Worked dependency model

Use these *abstract*, user-authored sufficient routes to explore the existing analyzer:

- `logic`: externally accepted mathematical foundation for this **illustrative model only**;
- `proof_scope`: open learner competence requirement;
- `reproduction`: open reproducible practical requirement;
- `external_review`: open independent review requirement;
- `ready_for_independent_review`: derived from `logic AND proof_scope AND reproduction AND external_review`.

The modeled minimal completion set is `{proof_scope, reproduction, external_review}`. The computation is **not** evidence that actual students satisfied any of them, nor that these are the only educational requirements. Change one AND prerequisite into an OR alternative and explain how the completion sets change. A missing independent reviewer cannot be automatically replaced by multiple agreeing agents.

## Reproduce with the repository analyzer

```python
from mathos.proof_analysis.gap_analysis import Claim, analyze

graph = {
    "logic": Claim("Foundational logic (assumed for this model)", "established_external"),
    "proof_scope": Claim("Proof-scope competence", "open"),
    "reproduction": Claim("Reproducible exercises", "open"),
    "external_review": Claim("Independent review", "open"),
    "ready": Claim("Review-ready portfolio", "derived",
                   (("logic", "proof_scope", "reproduction", "external_review"),)),
}
result = analyze(graph, "ready")
assert result["status"] == "BLOCKED"
assert result["minimal_completion_sets"] == [["external_review", "proof_scope", "reproduction"]]
```

Run this from repository root. The result is scoped to Boolean AND/OR *proof-route modeling*. It is not algebraic topology or persistent homology, and neither graph reachability nor Betti numbers automatically establish educational effectiveness.

## Required human rubric (20 points)

- Represent the source assumptions correctly (0–4)
- Identify a meaningful missing prerequisite or evidence gate (0–4)
- Demonstrate a falsifying/negative-control example (0–4)
- Compare a simpler baseline and discuss resource costs (0–4)
- Maintain honest proof/empirical scope and independent-review boundaries (0–4)

A human reviewer can recommend progression at 16/20 or above with no zero on scope. No software command awards learner completion or 10/10 quality.

## Quality upgrade gates

1. **Structural**: prerequisite graph is traceable, acyclic and every course objective has an assessment path.
2. **Mathematical**: independent subject experts audit sample solutions and counterexamples.
3. **Accessibility**: real novices demonstrate task comprehension with inclusive accommodations.
4. **Reproducible**: separate operators run pinned exercises and document deviations.
5. **Educational**: prospectively evaluated learner outcomes show benefit beyond an appropriate comparison group.
6. **External**: independent replication and disclosed negative outcomes support a defensible quality claim.

Until the last gates have evidence, the quality score is **not established**, irrespective of how many repository tests pass.
