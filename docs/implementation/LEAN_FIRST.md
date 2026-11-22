# Lean-first claim verification (bounded v1)

MathOS keeps Python for experimental mathematics, candidate generation, data analysis
and orchestration. **Lean 4 is the authority for formal mathematical proof claims
that have been explicitly registered in this gate.** This is an implemented
vertical slice, not a rewrite of MathOS or an automated proof of its broader
research portfolio.

## Run the gate

From the repository root, inspect the claims without assuming a compiler ran:

```sh
python -m mathos.research.lean_first inspect \
  --output artifacts/lean-first/inspect-only.json
```

After installing `leanprover/lean4:v4.14.0` via elan, run the real
kernel-backed replay:

```sh
python -m mathos.research.lean_first verify \
  --lean "$HOME/.elan/bin/lean" \
  --output artifacts/lean-first/kernel-replay.json
python -m unittest discover -s tests -p 'test_lean_first.py' -v
```

`inspect` explicitly records `NOT_RUN`, never verified. `verify`
**fails closed** if Lean is missing, the version differs, the Lean file
does not compile, the registered theorem fails to inhabit its declared
proposition, an axiom report is absent, or dependencies include
nonstandard axioms such as `sorryAx` or `Lean.trustCompiler`.

## Claim contract

The [versioned registry](../research/LEAN_FIRST_CLAIMS.v1.json) binds each
claim ID to:

- an exact Lean source file and fully qualified theorem name;
- an explicit Lean proposition that the named theorem must prove;
- a narrow informal research claim, its scope and known limitations;
- pending statement-faithfulness and external review;
- a permanent no-auto-promotion flag.

For every registered theorem, the runner copies the original file into
a temporary directory and appends a Lean `example` requiring the named
theorem to prove the expected type, plus a `#print axioms` audit.
It runs the pinned compiler with warnings treated as errors. The report
records the original source SHA-256, audit source SHA-256, toolchain,
transitive axioms and exact scope. The original repository source is
left unchanged.

The v1 gate supports direct `formal/*.lean` source files with no extra
imports beyond Lean's pinned `Init`. This deliberately excludes
multi-file and external Mathlib proofs until an import-closure and
dependency-pinning mechanism is implemented. A claim added to the
registry requires a reviewed code change.

### Current scope

`SAT1_SUPPORT` verifies the precise finite, syntactic
`MathOS.satSupport_certificate` proposition; `SAT1_LENGTH` checks
the subsidiary `MathOS.satTerms_length` proposition. Both are in
`formal/SATSupport.lean`. They do not prove P vs NP or the correctness
or complexity of a general SAT algorithm, and do not establish novelty.

This repository has many other Lean files and Python evidence tracks.
**They are not silently enrolled in this registry.** Passing this gate
is not a certification of all MathOS mathematical output.

## Separation of duties

1. **Python** generates candidate claims, explores counterexamples and
   creates evidence packets. Candidates remain unverified.
2. **Lean** checks the exact registered proposition and audits transitive
   axioms under the pinned toolchain. Only this check may yield
   `KERNEL_CHECKED_SCOPE_ONLY` within this report.
3. **Researchers** review whether the Lean proposition actually models
   the informal claim, including definitions, hidden restrictions and
   missing bridges. That review remains explicitly pending.
4. **External evaluation** separately considers novelty, mathematical
   relevance, independent replication and publication claims.

Reports always set `canonical_proof_certification=NOT_CERTIFIED`
and `automatic_claim_promotion=false`. A compiler pass does not change
the Clay obligation registers or assert an open conjecture is solved.

## Continuous integration

[Registered claim workflow](../../.github/workflows/lean-first-claims.yml)
runs tests, an inspect-only dry run, pinned Lean replay and a negative
false-theorem control on relevant pull requests and main-branch changes.
The artifact retains scope-limited provenance. Making this workflow a
*required branch protection check* is a separate GitHub repository
administration step; merely adding a workflow does not require it to pass
before merge.

Run generated/model-authored Lean only in an isolated and credential-free
environment. Lean can execute code during compilation; this runner is
intended for **trusted, reviewed repository sources**, not arbitrary AI
output.
