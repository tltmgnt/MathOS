# RH transfer milestone: exact logical bridge and analytic blockers

**Status:** an abstract logical implication can be checked in Lean, while the
actual RH-relevant hypotheses remain **UNPROVED**.

## Transfer theorem (not yet a Weil theorem)

Let `X` be the actual admissible test-function space with a specified topology,
`D ⊆ X` the chosen compact-bump family, and `q` the real-valued Weil
quadratic form. If:

1. `D` is dense in `X` in the **same topology** needed for the argument;
2. every point `x ∈ X` is approximated by admissible elements of `D`;
3. whenever `q(x) < 0`, that negativity is retained in some sufficiently
   close approximant from `D` (for example because `q` is continuous or
   **upper semicontinuous** on `X`);
4. `q(d) ≥ 0` for **every** `d ∈ D`, with all Weil-form arithmetic terms
   rigorously defined and controlled as needed;

then `q(x) ≥ 0` for every `x ∈ X`.

**Proof:** If `q(x)<0`, upper semicontinuity makes the strict sublevel
set `{y∈X:q(y)<0}` open. Density gives an element of `D` in this
neighborhood, contradicting positivity on all of `D`. Continuity suffices
as a special case. This is an abstract standard implication, not a proof
that the Weil form has these properties.

For an **extended-real** functional, further care is required with
well-definedness; no such full Weil-space formalization is present.

## Important correction: lower semicontinuity is insufficient

Lower semicontinuity **alone** does not preserve nonnegativity from a dense
subset. Example on the ordinary real line: `D = ℝ∖{0}`, dense in `ℝ`,
and `q(0)=-1`, `q(x)=1` for `x≠0`. This `q` is lower
semicontinuous; it is nonnegative on all of `D`, but negative at `0`.
Thus G3 demands continuity, upper semicontinuity, or an *independently*
proved negative-witness property, **not** an unqualified lower-
semicontinuity assertion.

## Formal scope

`formal/RHTransferLogic.lean` checks a logically similar but
*integer-valued* statement: a negative point must yield an admissible
negative approximant under an explicit `negative_stability` hypothesis.
It also proves a uniform finite-prefix obstruction. Neither result
formalizes real topology, Weil explicit-formula continuity, dense bump
families, prime-power convergence, or zeta zeros.

The independent `G5P` registry entry tracks whole-family positivity:
proving a transfer implication without proving **that premise** is
insufficient for RH. The finite Gaussian-cosine Gram stays a numerical
comparison baseline, never a dependency of the global transfer.

## Reproduction

```sh
lean formal/RHTransferLogic.lean  # Lean 4.14.0, pinned by GitHub Actions
python -m unittest discover -s tests -p 'test_rh_proof_firewall.py' -v
python -m mathos.research.rh_proof_firewall
```

**Open target:** specify an actual LF domain and a Weil-form topology in
which `D` is dense, verify the correct sign-continuity property, and prove
positivity for **the entire dense class**, not merely a finite lattice.
