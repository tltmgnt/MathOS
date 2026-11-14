# SAT1 formal-support theorem and independent research-assurance gate

**Result:** a bounded but genuinely quantified mathematical subresult in Lean 4.14.0, accompanied by explicit novelty, expert-review, and implication boundaries. **No Millennium Problem is solved.**

## Actual formal theorem

The source [`formal/SATSupport.lean`](../../formal/SATSupport.lean) defines an inductive choice with three possible terms for each disjoint factor of the polynomial

\[
F_m=\prod_{i=1}^{m}(x_i+y_i-x_i y_i).
\]

For each natural number `m`, the recursively generated `satTerms m` is a list of indexed choice words, where list positions distinguish the variable pairs. The Lean theorem `MathOS.satSupport_certificate` formally establishes in this **abstract representation**:

1. `(satTerms m).length = 3 ^ m`;
2. `(satTerms m).Nodup` — distinct choice words (separate indexed exponent patterns) do not collide;
3. Every word's signed coefficient, defined by the three factor choices, is either +1 or -1, hence nonzero.

Together these are a meaningful all-`m` combinatorial fact behind the repository's informal `SAT1` claim. Lean checks it **only after** the pinned workflow passes on the exact commit. The source does **not** formalize the ring-level embedding from choice words into the standard polynomial ring over all `2m` variables, and it does not prove that this encoding cannot be avoided by a different computational representation.

This is not presented as novel mathematics. It is a familiar disjoint-variable expansion phenomenon: formally verifying its encoded model is an engineering and proof-assurance milestone, **not a breakthrough on P vs NP**.

## Why SAT1 does not close `PNP.sat_runtime`

An explicit product with `3^m` distinct expanded terms does not imply that every deterministic SAT algorithm requires exponential time. A smarter symbolic representation, shared computation, dynamic programming, branching strategy or different proof method may avoid explicit expansion. The existing P=NP MathOS route requires an actual SAT algorithm, full correctness and worst-case total bit-polynomial runtime, plus a valid class-level reduction. The P!=NP route requires an unrestricted lower bound. The checked SAT1 term model establishes neither.

In particular, do **not** interpret `3^m` as a lower bound on general algorithmic complexity; it is a support count for a particular expansion.

## New assurance module and reproducibility

`mathos.research.theorem_assurance` reads these protected inputs: theorem assurance manifest, Lean source, official Clay targets, original obligation register, hypotheses, candidate route graph and external-claims snapshot. It reuses the fail-closed Clay topology auditor and checks that:

- The theorem is exactly the known local `SAT1` subresult, attached to the open `PNP.sat_runtime` obligation and the author-proposed `PNP.equality` route.
- All 14 original canonical work packages and 10 supplemental proposed proof bridges remain open.
- The external-review and novelty fields remain **not independently assessed**, publication is **not submitted**, route sufficiency and Clay implication are **not established**.
- The Lean file includes the intended theorem and intermediate statements and does not contain simple disallowed proof shortcuts. This static screening is not itself a kernel or trusted-base audit.
- All sources remain byte-for-byte unmodified. Reported SHA-256 values make the handoff reproducible.

The optional `--verify-lean` mode invokes the actual pinned Lean 4.14.0 executable through an argument list (never a shell). Only a successful compilation can produce `LEAN_COMPILED_EXACT_SUBRESULT_ONLY`. A failed or unavailable compiler stops that verification. Without the flag, the status remains `NOT_RUN`.

The tool writes `theorem_assurance.json` and `sat1_review_handoff.md` with the exact theorem scope, source hash, review checklist, literature search plan, and explicit logical gap. It never edits the canonical mathematical register or automatically asserts peer review.

```sh
python -m unittest discover -s tests -p 'test_theorem_assurance.py' -v
python -m mathos.research.theorem_assurance --output-dir artifacts/theorems

# Only with pinned Lean 4.14.0 installed:
python -m mathos.research.theorem_assurance \
  --verify-lean --output-dir artifacts/theorems
```

CI runs the assurance and negative tests on Python 3.10, 3.11, and 3.12. The repository's pinned Lean workflow also compiles `formal/SATSupport.lean`, executes the formal assurance check and uploads its verification artifact.

## Still-open human and scientific work

**Independent literature novelty assessment:** A disinterested researcher must perform documented primary-source searches, compare stronger related SAT-algebraic expansion facts and record a dated bibliography. The manifest explicitly says `NOT_INDEPENDENTLY_ASSESSED`. A script cannot truthfully certify novelty in open mathematical research.

**Independent proof review:** A mathematical reviewer must inspect the exact Lean definitions and their relation to standard multivariate polynomials, the trusted toolchain/imports, and any claimed implications. This remains `NOT_PERFORMED` until genuine review occurs.

**Mathematically valid route implication:** A separate theorem would need to connect a meaningful bound to the *full* SAT machine model; SAT1 currently does not. As no such theorem exists in this change, the result is `NOT_PROVEN`, not merely untested.

**Other Clay obligations:** None of the 14 canonical Millennium work packages is closed. No solution to the other six Clay problems is offered.

The purpose of this implementation is to turn one known, previously informal finite-support argument into a reproducibly checked **well-defined partial mathematical artifact**, and ensure the remaining much harder scientific claims stay clearly unestablished.
