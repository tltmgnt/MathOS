# RH proof firewall: dense compact-bump strategy

**Status: research infrastructure implemented; mathematical gates unresolved.**
This system cannot certify the Riemann Hypothesis. It audits a claim registry,
not the mathematical truth of statements. There is no trusted-kernel proof of
RH or of the proposed finite-to-global transfer theorem.

## Primary target

The research target is a precise *conditional* finite-to-global transfer theorem
for the Weil positivity criterion: if a chosen class of admissible compact-bump
test functions is dense in a specified topology, if approximation respects
admissibility and the relevant quadratic form admits a correct positivity-
preserving limit, and if the arithmetic contributions are controlled as
required, then positivity **on the entire dense family** transfers to the full
criterion domain. Proving density alone does not prove positivity on that family.
Proving the transfer theorem alone does not prove RH.

The term "LF-dense" must not be used as shorthand for a theorem: the LF space,
test-function involution, target domain, comparison topology, and approximation
nets or sequences are currently **unspecified research obligations**.

## Gates

| Gate | Blocking obligation |
| --- | --- |
| G1 | Exact density theorem for the stated space and topology |
| G2 | Preservation of the needed admissibility constraints |
| G3 | Continuity, upper semicontinuity, or a proved negative-witness property; lower semicontinuity alone is insufficient |
| G4 | Uniform arithmetic support, tails and error control |
| G5 | Valid global transfer, **assuming separately proved G5P whole-family positivity** |
| G6 | Independent trusted-kernel checking with statement/axiom audit |

A constructive, topology-specific auxiliary density argument for rational
bump spans in the usual LF test-function space is documented in
[RH_LF_DENSITY_CORE.md](RH_LF_DENSITY_CORE.md). It **does not** discharge
G1 for the actual Weil criterion, whose domain and topology must still
be proved compatible.

An additional G5P obligation is tracked separately: positivity on the
**entire** dense family is mathematically essential and not certified.
See [the conditional transfer milestone](RH_TRANSFER_MILESTONE.md) for
the precise sign-stability hypothesis and a counterexample to the
incorrect lower-semicontinuity shortcut.

The existing fixed-width Gaussian-cosine calculation in
`mathos/research/riemann_weil_gram.py` remains an **uncertified finite
diagnostic**. It neither proves a density theorem nor Weil global positivity.
The independent positive L2 Gram is not the Weil Gram.

## Fail-closed claim semantics

Statuses are EXPERIMENTAL, CONJECTURED, CONDITIONAL, PROVED, and
FORMALLY_VERIFIED. The registry deliberately rejects PROVED and
FORMALLY_VERIFIED promotions until **independent trusted-kernel integration**
exists. A reviewer cannot turn an open theorem into a proof by editing JSON,
adding a URL, or making tests green. The global RH status is locked OPEN.

G5 must depend on G1–G4 **and G5P**, G6 must depend on G5, and G5P
must depend on G1, G2 and G4. The finite baseline cannot be used as a
direct or indirect proof dependency of G5 or G5P. Dependency graphs must be acyclic.
This is a **metadata firewall**, not a soundness proof or a complete dependency
checker: even a passing registry may contain false mathematics.

## Reproduce

```sh
python -m unittest discover -s tests -p 'test_rh_proof_firewall.py' -v
python -m mathos.research.rh_proof_firewall --report artifacts/rh/proof_obligations.json
python -m unittest discover -s tests -p 'test_riemann_weil_gram.py' -v
```

The first two commands require only the Python standard library. The Weil
experiment is the existing finite baseline and has its own CI. To extend the
firewall responsibly, add a separate, pinned trusted-kernel verification
pipeline and verify the exact theorem statements, hypotheses, topology,
provenance and permitted axioms. A kernel checker cannot establish RH simply
from the existence of formal syntax.

**Milestone:** either prove the exact G5 implication with all hypotheses,
including the family-wide positivity premise, or produce a counterexample
that identifies which transfer assumption fails.
