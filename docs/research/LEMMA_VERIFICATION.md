# MathOS bounded mathematical lemma verification — exact arithmetic and Lean witnesses

**Status:** experimental, deterministic verification of a small language of *toy integer-polynomial equalities*. **NOT_CERTIFIED** for any Clay problem or route. The tool is neither a general theorem prover nor a proof of the SAT/P-vs-NP conjecture.

This feature builds on the merged Clay target alignment, topology and agent-focus work. It implements an actual, reproducible **counterexample search** for a formally delimited statement class and generates safe Lean handoffs from a restricted JSON AST, rather than executing model-authored mathematical code or accepting unsupported proof claims.

## What it can and cannot establish

The checker accepts polynomial expressions in at most four integer variables with bounded constants, depth, arity and degree. The *only* operators are `const`, `var`, `add`, `mul`, `sub`, `neg` and `pow`. No Python `eval`, dynamic import, arbitrary script, external model callback or untrusted Lean body is possible.

1. **Concrete counterexample**: enumerate a bounded grid of exact integer assignments. When the proposed universal equality fails, record the first witness (the actual variable values and the two different integer results). This falsifies **that equality**, not a conjecture or Clay problem.
2. **Exact polynomial normalization**: separately reduce the two ASTs to coefficient/exponent maps over `Z`. If their difference is zero, return `EXACT_POLYNOMIAL_IDENTITY_BY_PYTHON_NORMALIZATION`, indicating an exact, symbolic result under the implemented polynomial semantics, **not** a formally or independently checked theorem.
3. **Inconclusive search**: if normal forms differ but no witness occurs in the enumerated grid, return `FINITE_SEARCH_INCONCLUSIVE`. Absence of a bounded witness does not establish universal truth.
4. **Lean witness**: generate, solely from validated integer ASTs and a concrete assignment, a closed Lean theorem of the form `lhs ≠ rhs := by decide`. When `--verify-lean` is *explicitly* enabled, use only pinned Lean 4.14.0. A successful check is recorded with the Lean version and source SHA-256. **It proves only the displayed concrete counterexample.**
5. **Lean statement-only handoff**: a candidate identity that Python normalizes to zero receives a commented proposed Lean theorem without a proof term. Compiling a comment is not formal verification, and the report does not present it as such. No `sorry`, `axiom` or injected model proof term is generated.

The sample manifest `LEMMA_CANDIDATES.v1.json` contains two intentionally elementary polynomial calculations attached to the **open** `PNP.sat_runtime` research obligation on route `PNP.equality`:

- Distributivity of `(a+b)(c+d)` — true by exact symbolic normalization. This is an illustration of algebraic expansion, **not** an algorithmic complexity result.
- The false universal claim `(x+y)^2=x^2+y^2` — refuted by `x=1, y=1`, where left is 4 and right is 2.

These fixtures are **not new mathematical discoveries**. They make the verification mechanism testable on both sides of the validity boundary before supporting more useful, independently reviewed lemmas.

## Reproduce

From the repository root, without Lean (Python 3.10+):

```sh
python -m unittest discover -s tests -p 'test_lemma_verification.py' -v
python -m mathos.research.lemma_verification --output-dir artifacts/lemmas
python -m json.tool artifacts/lemmas/lemma_verification_report.json
```

To attach the exact source-hashed research packet produced by the existing agent:

```sh
python -m mathos.research.agentic_clay \
  --provider offline --track P-versus-NP \
  --route-id PNP.equality --claim-id PNP.sat_runtime \
  --rounds 1 --max-model-calls 4 \
  --output-dir artifacts/agents/pnp-algebra

python -m mathos.research.lemma_verification \
  --agent-report artifacts/agents/pnp-algebra/agentic_research_report.json \
  --output-dir artifacts/lemmas
```

The report is linked **only by exact source digest** (the registered official Clay targets, obligations, hypotheses, proposed routes, and external-claims snapshot) and by the selected open claim/route. A forged status or stale source is rejected. This digest establishes identity/provenance, **not** originality or proof validity.

To actually check the generated concrete counterexample in pinned Lean 4.14.0:

```sh
python -m mathos.research.lemma_verification \
  --verify-lean --output-dir artifacts/lemmas
```

That option refuses a missing or differently versioned Lean executable. The existing `.github/workflows/proof-route-lean.yml` installs the pinned compiler, compiles the generated witness, and uploads the exact report and Lean source. The bounded research workflow runs the symbolic checker, agent-linked provenance, tests and JSON report on Python 3.10, 3.11 and 3.12 without requiring Lean for all jobs.

## Evidence contract

`artifacts/lemmas/lemma_verification_report.json` contains:

- SHA-256 of every source registry, input candidate and optional agent packet;
- canonical polynomial difference coefficients/exponents;
- exact test window, number of evaluated points and first failed assignment;
- SHA-256 of each deterministic generated Lean file;
- `lean_certificate=NOT_RUN` unless pinned Lean has actually checked a concrete falsification;
- `research_claim_promoted=false`, `complete_proof_of_registered_claim=false`, `clay_problem_solved=false` for every candidate.

The audit runs `audit_clay_proof_topology` **before** evaluation and insists that each candidate's `model_key`/`route_id`/`claim_id` is an existing open obligation. It refuses a forged certification policy, missing dependencies, unsafe AST operators, unbounded search grids, excessive expression sizes, stale agent evidence or a fabricated formal-review status. It does not mutate the canonical obligation register.

## Next meaningful research step

Translate a mathematically meaningful **small and precisely scoped** sublemma, relevant to a selected open claim, into an independently reviewed formal statement. Prove it in Lean (or another trusted checker) using a reviewed proof term, then document the *separate* implication from that sublemma to the registered open mathematical obligation. Until then, all Clay proof-route statuses remain **NOT_VALIDATED** and **NOT_CERTIFIED**. A checked toy algebraic identity or counterexample cannot be counted as a solution to P vs NP or any other Millennium Problem.
