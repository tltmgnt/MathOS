# TECT-X — Proof-aware decision topology and Weil positivity gap router

**Research status:** implemented governance/control architecture, **not** a new Weil positivity theorem. No claim of RH proof or automatic theorem proving.

## Purpose

ResearchOS previously accumulated certified finite Weil Gram computations (2D, 3D, 4D) and separately established analytic density of an explicit compact-bump family in the natural LF test-function domain `D(R)=C_c^∞(R)`. The missing step is a **universal** arithmetic positivity theorem. The control layer prevents a finite certificate from silently becoming an all-index or global RH claim.

The module `mathos/research/tectx_proof_decision_topology.py` implements:
- an **ordered evidence hierarchy** with EXPERIMENTAL → INTERVAL_VERIFIED → FINITE_THEOREM → UNIFORM_THEOREM → GLOBAL_WEIL_THEOREM;
- ten potentially overlapping **decision attributes** (axiomatic, probabilistic, game-theoretic, reinforcement learning, counterfactual, regime, behavioral, information-theoretic, topological and meta-decision);
- a **prefix metric** on labeled decision paths, rather than pretending these ten classes exhaust all possible decision trees;
- six explicit unresolved proof gaps and associated domain/topology/quantifier checks;
- exact `fractions.Fraction` norm-error calculations and a **fail-closed vanishing-limit gate**;
- a JSON evidence ledger with explicit false global RH flags, even for externally supplied alleged proof candidates.

The ten decision families are descriptive and **overlap**. They are not mathematically exhaustive or mutually disjoint, and they do not themselves establish Weil positivity.

## 1. The correct tree topology

On labeled root-to-leaf paths, define the first divergence depth `k` (zero-indexed) and `d(a,b)=2^-k`, with `d(a,a)=0`. For finite sequences, an exhausted prefix counts as a difference at that first missing position. This satisfies the ultrametric inequality on the represented path set. A proof-decision tree can be modeled as a compatible family of finite prefixes; convergence means agreeing on increasingly deep prefixes.

**Important:** This metric models agreement of proof-navigation choices; it is *not* a topology on the admissible Weil test functions. The correct analytic topology remains the strict LF topology of `D(R)`.

## 2. The six auditable proof gaps

| Code | Gap | What must eventually be established |
|---|---|---|
| `G1_FINITE_TO_INFINITE` | Finite-to-infinite | One valid all-index argument, not finite extrapolation |
| `G2_SUPPORT_WINDOWS` | Support windows | Arithmetic control on arbitrary supports, including every prime-power window |
| `G3_TOPOLOGY` | Test topology | A core dense in the **correct** domain, plus Weil-form continuity |
| `G4_SPECTRAL_STABILITY` | Reference norm | Uniformly justified norm comparisons and bounds across expanding spaces |
| `G5_NORMALIZATION` | Explicit formula | Fixed sign, involution, pole moments and domains for the precise Weil criterion |
| `G6_LOGICAL_COMPLETION` | Universality | A noncircular positive quadratic form on every admissible test function |

A past finite Gram result discharges *none* of the all-index positivity requirements. The separately constructed compact-bump LF-density theorem can discharge a **density** obligation but does not discharge the *positivity* obligation.

## 3. Correct finite-to-infinite estimate

Suppose for support windows `K_n` and suitable seminorms `N_n` one can establish

```text
Q(f,f) >= -epsilon_n * N_n(f)^2.
```

For every **fixed admissible** `f` the norms must be controlled, not just the errors: one needs

```text
epsilon_n * N_n(f)^2 -> 0.
```

For example, `epsilon_n=4^-n` and `N_n(f)=2^n` make the product **identically one**, despite `epsilon_n->0`. The module checks any finite list of rational products but **never** infers the infinite limit from finitely many samples.

It only labels an externally claimed limit as `candidate_requires_independent_mathematical_review` when these proof obligations have been **declared**: a universal asymptotic rate, eventual admissibility for each fixed test, and compatibility of the reference norms. This is not software validation of the external proof.

There is a second elementary obstacle: for an exactly nested Gram sequence `H_m`, a universally proved bound `H_m >= -epsilon_m I` with `epsilon_m->0` already implies *all* leading principal submatrices are PSD by zero-extending any fixed finite vector. Thus that hypothetical theorem would itself prove the RH-equivalent positivity condition for a suitably admissible LF-dense core. No such theorem is present.

## 4. Five evidence states and nonpromotion contract

| Evidence level | Permitted interpretation |
|---|---|
| `EXPERIMENTAL` | Screening, heuristics and approximate eigenvalues |
| `INTERVAL_VERIFIED` | Arithmetic enclosure for **specified** objects |
| `FINITE_THEOREM` | A mathematically proved **specified finite** span |
| `UNIFORM_THEOREM` | An alleged externally supplied theorem with all-index quantifiers; requires review |
| `GLOBAL_WEIL_THEOREM` | A claimed global result; accepted only as **candidate requiring independent review**, even if every required field is asserted |

The system explicitly refuses to infer the last two states from a count of finite tests, CI successes, decreasing numerical errors, or successful Schur pivots. Missing evidence, non-universal quantifiers, invalid rational errors, duplicates, absent LF density, incompatible test domains and unsupported normalization claims all fail closed.

**All global candidate fields are user-supplied declarations, not machine-checkable mathematical evidence.** Accordingly the report *always* sets `Riemann_hypothesis_proved=false` and `global_proof_externally_verified=false`. An independently verified mathematical proof would require independent expert or formal verification outside this gate.

## 5. Relation to existing MathOS work

The provided example ledger treats PRs #78, #87 and #89 as **fixed-span finite certificates**, while #83 contributes an analytic LF-dense-core and continuity result. It does not import PR #89 as a proof of all-support positivity. The example shows open gates `G1`, `G2`, `G4`, and `G6` while recording the separately documented topology result as evidence.

This module does not call an ML agent, assign posterior truth probabilities to RH, construct a dynamic Neo4j graph, automatically run the Weil numerical solvers, or alter the CI reports of earlier mathematical PRs. It is a self-contained, deterministic proof-audit control layer that can be integrated with those systems later.

## 6. Reproduce

```bash
python -m unittest discover -s tests -p 'test_tectx_proof_decision_topology.py' -v
python -m mathos.research.tectx_proof_decision_topology \
  --output artifacts/riemann/tectx_proof_decision_topology.json
```

All bounds in the norm-limit example are exact rational strings. Tests exercise the hierarchy, prefix metric, all six gaps, invalid numerical inputs, a deliberately false vanishing-limit argument, an attempt to promote 199 finite certificates, inconsistent quantifier/domain claims, and an alleged full proof that must remain marked **independently unverified**.

**Scientific boundary:** Decision topology is a research management tool. Neither an ontology of decision trees nor a repository workflow substitutes for the absent proof of global Weil positivity, the Riemann hypothesis, or a full positive Weil Hilbert-space completion.

## References

- MathOS compact Weil arithmetic PR #89: https://github.com/tltmgnt/MathOS/pull/89
- MathOS canonical Weil test-topology PR #83: https://github.com/tltmgnt/MathOS/pull/83
- MathOS exact all-index lower-floor obstruction PR #84: https://github.com/tltmgnt/MathOS/pull/84
- Suzuki, *On the Hilbert space derived from the Weil distribution*: https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/on-the-hilbert-space-derived-from-the-weil-distribution/FD33EBD117A6B448053450DD8D62ADB6
