# TECT-X typed mathematical argument verifier and formalization-fidelity gaps

## Verified boundaries

**What this feature can verify:** For any **repository-reviewed mathematical
proposition written in Lean 4 with the supported `Init` environment**, a
candidate proof module may be submitted alongside a *separately authored* Lean
reference specification. With pinned Lean 4.14.0, the independent contract
requires the candidate term to inhabit **the exact reference proposition**,
and the kernel checks it. The checker demands zero transitive axioms for both
the candidate theorem and the contract theorem.

**What this feature cannot claim:** An arbitrary English-language argument
cannot generally be parsed into a mathematically faithful formalization
without interpretation. The kernel cannot determine whether the human author
meant the chosen reference proposition, nor whether a mathematically correct
local lemma proves a conjecture with unverified dependency bridges.
**A successful type check is not independent validation of informal meaning.**

This extends the existing
[Topological Gap Analysis](TECT_X_INTELLIGENT_PROOF_VERIFIER.md), rather than
replacing its author-scoped proof-obligation model or its open RH/Selmer gaps.

## Three distinct correctness questions

| Question | Status of this implementation |
|---|---|
| Does the Lean proof term type-check at a precise independent formal goal? | Checked by pinned Lean when `--check-lean` is used |
| Does the formal goal faithfully encode the intended mathematical definition and assumptions? | **Not automatically verified**; requires independent semantic review |
| Is the checked local result sufficient to establish the overall theorem or research claim? | **Not established**; requires separately proved and checked mathematical bridges |

The word **independent** in "independent formal reference" describes an
architecturally separate theorem *type* file. It does not imply another person,
institution, or third-party prover has reviewed that file.

## Proof bundles

The [versioned manifest](TECT_X_TYPED_ARGUMENTS.v1.json) stores explicit
informal descriptions, model hypotheses, exact theorem names and separate
`formal/tectx_arguments/*.lean` and
`formal/tectx_contracts/*Contract.lean` files.

Two different forms of deduction are included:

- **Propositional reasoning:** For arbitrary propositions `P Q R`,
  `(P → Q) → (Q → R) → P → R`.
- **Universal natural-number arithmetic:** For every `n : Nat`,
  `n + 0 = n`.

For each example, the contract defines its **own expected proposition**
and must construct a term of exactly that type from the candidate theorem.
The proof source cannot choose or derive the expected type at verification
time. A candidate with an extra premise, missing quantifier or different
result is rejected unless the reference goal itself has been compromised.

The manifest is extensible: add a reviewed Lean source, a genuinely
separate reference contract, explicit assumptions and a new bundle
entry. Validated proof theorem names are not hard-coded to these two cases.
The initial trust boundary accepts only the repo's Lean `Init`
environment and bounded, repository-controlled source; arbitrary
mathlib imports or uploaded untrusted executable Lean scripts are **not**
supported in the trusted workflow.

## Check and reproduce

From repository root:

```sh
# Static file, path, policy, status and digest checks ONLY.
python -m mathos.research.tect_x_typed_argument_gate

# Real proof checking under Lean 4.14.0. This executes Lean code;
# use trusted repository code and a disposable machine.
python -m mathos.research.tect_x_typed_argument_gate \
  --check-lean --lean lean \
  --report artifacts/tect-x/typed-arguments/verification.json

# Attach scoped Lean results to the TGA gap analysis.
python -m mathos.research.tect_x_intelligent_proof_verifier \
  --verify-typed-arguments --lean lean --json \
  --report artifacts/tect-x/typed-arguments/tga-report.json

python -m unittest discover -s tests \
  -p 'test_tect_x_typed_argument_gate.py' -v
```

The dedicated GitHub Actions workflow performs an actual pinned Lean
replay and **negative control**: a deliberately incorrect reference goal
must be rejected by the kernel. It uploads reproducible source/contract
SHA-256 digests and axiom reports. Tests that mock Lean never count as
formal theorem verification.

## Formalization-fidelity gap ledger

The analyzer preserves three non-certification gaps even after exact proof
checking succeeds:

1. **`GAP.LANGUAGE_TO_FORMAL_REFERENCE`:** A separately written reference
   is still a mathematical interpretation; the human-language to
   formal-language correspondence has no general automated truth oracle.
2. **`GAP.AUTHORED_PROOF_ROUTE_SUFFICIENCY`:** The fact that a proof term
   proves one lemma does not establish that arbitrary surrounding TGA
   dependency arrows are valid, complete or jointly sufficient.
3. **`GAP.EXTERNAL_REPRODUCTION`:** Passing in-project CI does not
   establish independent expert review, public trust of the binaries,
   or a reproducible external mathematical interpretation.

The TGA case statuses remain
`BLOCKED_NOT_MATHEMATICALLY_VERIFIED`; the certificate report always
contains `semantic_faithfulness_certified: false` and
`closed_research_obligations: []`.

## How actual faithfulness can be established for a particular theorem

Start by precisely specifying the *intended statement and its definitions*
in a formal reference library that is maintained separately from the
candidate proof. Require proof authors to compile against that reference.
Formally check equivalence of alternative definitions or translations
when the hypotheses and mathematical interpretation themselves can be
formalized. Then have qualified independent specialists compare the
definitions, quantifiers, hypotheses and theorem with the original
human-authored mathematical intent. Record their dated reviews with
authenticated provenance; a boolean manifest field cannot replace this.

That process can establish a strong, **theorem-specific** faithfulness case,
but no automatic procedure can guarantee correct interpretation of
*arbitrary informal mathematical prose*, and no formal checker can
rule out all specification mistakes made by the people who authored it.

## Security and proof trust

Lean proof source can execute metaprograms during compilation. The Python
runner uses finite path/size limits, distinct proof and contract modules,
an `Init`-only import policy, basic bypass-token rejection, a temporary
`LEAN_PATH`, a pinned compiler version, subprocess timeouts, source
digests, zero-transitive-axiom checks and fail-closed exit codes.
**Static screening is not a security sandbox or an independent audit.**
Only trusted and code-reviewed repository sources should be run here.
For third-party argument submissions, an isolated container without
network/credentials and an attested compiler distribution would be required.

No proof of the Riemann hypothesis, BSD, Selmer infinitude, or other open
conjecture is claimed by these example proofs.
