# MathOS BSD 007 — research approach and eventuality matrix (v1)

**Research status: NOT_CERTIFIED • NO_BSD_SOLUTION • MATHEMATICAL_NOVELTY_NOT_ESTABLISHED.**

This is a **structured search map**, not an assertion that every conceivable mathematical method can be enumerated. It expands the MathOS 007 local-factor diagnostic into a portfolio of mechanisms and a **logical coverage matrix**, while keeping the canonical proof-obligation status unchanged.

## Official problem and end states

For every elliptic curve \(E/\mathbb{Q}\), the **core BSD rank conjecture** predicts

\[
\operatorname{ord}_{s=1}L(E,s)=\operatorname{rank}E(\mathbb{Q}).
\]

At the level of logical outcomes there are two mutually exclusive classes:
1. **Proof:** an unconditional argument for the equality for **every** elliptic curve over the rationals.
2. **Disproof:** one elliptic curve with **rigorously proved unequal** analytic and algebraic ranks.

A conditional theorem, a result for many curves, a computation, or a new formula that assumes an open conjecture is **neither** outcome. The **refined BSD leading-term formula** is a separate stronger objective involving the normalized leading derivative, periods, regulator, torsion, Tamagawa factors, and the Tate–Shafarevich group.

This document respects MathOS's existing proposed stronger route `BSD.rank_refined` and open claims `BSD.analytic_selmer`, `BSD.sha_finiteness`, `BSD.leading_term`, with `BRIDGE.BSD.full_formula`. The author-proposed route's sufficiency remains **NOT_VALIDATED**. The official core rank conjecture does **not** require that this particular proposed decomposition be proved first.

## Matrix A — proof mechanisms, obstacles, adversarial failure tests

Legend: `KNOWN_SPECIAL_CASE` means a published theorem under restricted hypotheses; `ACTIVE_PARTIAL` is a research program with restricted results; `EXPLORATORY` is a possible line of attack but not validated as sufficient; `INSUFFICIENT_ALONE` identifies a demonstrably inadequate method; `SUPPORTING_TOOL` cannot directly replace a theorem; `TARGET_RESTATEMENT` expresses what needs proving and is not progress by itself.

| ID | Approach | Known scope/status | Fundamental missing bridge | Falsification / limitation |
|---|---|---|---|---|
| BSD.M01 | Analytic L-function / complex derivatives | ACTIVE_PARTIAL | Prove unconditional upper and lower comparisons with Mordell–Weil rank, uniformly in analytic rank >=2. | Finite Euler coefficients, numerically small L-values, or parity cannot certify order of vanishing. |
| BSD.M02 | Descent and Selmer bounds | ACTIVE_PARTIAL | Control Sha obstructions and connect algebraic rank bounds to complex analytic order for every E/Q. | An upper bound on rank does not determine analytic order; finite descents may leave unresolved Sha. |
| BSD.M03 | Gross–Zagier / Kolyvagin (low rank) | KNOWN_SPECIAL_CASE | A genuinely new mechanism for arbitrary higher vanishing orders; the known theorem cannot simply be re-used as all-rank proof. | An argument that only produces one independent rational point cannot certify arbitrary rank. |
| BSD.M04 | Higher-rank Euler/Kolyvagin systems | EXPLORATORY | Existence, nontriviality, higher-rank bounds and noncircular link to higher complex derivatives for every E/Q. | Classes may vanish or bound only special primes and curves; 'higher-rank' labels do not confer needed rank inequalities. |
| BSD.M05 | Higher Gross–Zagier/height formulas | EXPLORATORY | A nondegenerate global height determinant matching the order for arbitrary E/Q. | Derivative formulas under special sign or CM hypotheses do not automatically cover all curves. |
| BSD.M06 | Iwasawa main conjectures | ACTIVE_PARTIAL | Remove all local/residual/rank restrictions and bridge p-adic comparisons to every complex analytic vanishing order. | A p-part of a formula, or result at one ordinary prime, is not the full complex or integral BSD formula. |
| BSD.M07 | p-adic heights and regulators | ACTIVE_PARTIAL | Unconditional nondegeneracy, exceptional-zero accounting and archimedean comparison in all ranks. | A zero of a p-adic L-function can arise from local exceptional factors and need not measure complex analytic rank. |
| BSD.M08 | Bloch–Kato / motivic / ETNC routes | EXPLORATORY | Prove applicable noncircular comparison theorems without assuming conjectures equivalent to the desired BSD conclusion. | Replacing BSD with Bloch–Kato or ETNC as a premise is a conditional reformulation, not a proof. |
| BSD.M09 | Finiteness of Tate–Shafarevich groups | EXPLORATORY | Uniform finiteness at every relevant prime for arbitrary E; still need separate complex analytic rank link. | Sha finiteness by itself does not prove analytic rank equals algebraic rank. |
| BSD.M10 | Automorphic / trace formula / spectral routes | EXPLORATORY | A spectral identity strong enough to determine exact multiplicity for every E and connect it to rational points. | Modularity provides continuation and a functional equation but not rank equality. |
| BSD.M11 | Twists, congruences and specialization | ACTIVE_PARTIAL | A rigorous all-curves coverage theorem with control of rank and leading terms through exceptional fibers. | A theorem for a dense or positive-proportion family is not a theorem for every E/Q. |
| BSD.M12 | Arithmetic statistics and average rank | ACTIVE_PARTIAL | Replace density or average claims with an all-curves theorem, or a universal reduction covering every excluded case. | Probability 1 or density 1 does not imply a property of every curve. |
| BSD.M13 | Direct computation and certified examples | ACTIVE_PARTIAL | A uniform proof covering unbounded conductors and arbitrary ranks, not merely a growing table of examples. | Numerical L-derivative zero tests and finite prime counts cannot prove an all-curves theorem. |
| BSD.M14 | Partial Euler-factor agreement (MathOS 007) | INSUFFICIENT_ALONE | A new theorem using sufficient complete global information, not merely a partial Euler product. | E1 and E5 have differing known ranks but matching counts for every p≡3 mod4; the argument cannot imply BSD. |
| BSD.M15 | Formal theorem verification | SUPPORTING_TOOL | A mathematically complete general theorem must first be identified, encoded, proved without hidden assumptions and linked to the official target. | Passing finite tests or formalizing a conditional identity does not prove missing hypotheses. |
| BSD.M16 | Logical counterexample (disproof branch) | LOGICAL_ALTERNATIVE | Unconditional proof of both exact ranks/orders for the same E with no numerical or conjectural gap. | Large computed discrepancy, inconclusive descent, or assumed Sha finiteness is not a counterexample. |
| BSD.M17 | Direct universal rank bridge | TARGET_RESTATEMENT | Both inequalities for all E, including analytic rank >=2 and all bad reduction types. | Stating either inequality as a conjectural lemma without proof is circular. |
| BSD.M18 | Universal refined leading-term formula | TARGET_RESTATEMENT | Prove Sha finiteness and every factor/normalization for all curves, plus analytic/algebraic rank equality. | A p-part, special-curve computation or formula assuming finiteness cannot establish the unrestricted refined claim. |

## Matrix B — coverage of eventualities and quantifiers

| Axis | Cases to audit | Non-negotiable acceptance gate |
|---|---|---|
| Global scope | fixed E; infinite family; positive proportion; density one; all E/Q | Only all E/Q closes the official core BSD target. |
| Analytic rank | 0; 1; >=2; not determined | Known low-rank theorems must be kept separate from arbitrary-rank proofs. |
| Algebraic rank | 0; 1; >=2; only lower/upper bounds | Descent/Selmer evidence must yield exact rank to claim an exact comparison. |
| Reduction and representation | CM / non-CM; ordinary / supersingular at p; residual irreducibility / reducibility; potentially multiplicative / additive bad reduction; p=2 or 3 / larger p | Every excluded local or residual case must be covered by an explicit theorem or valid reduction. |
| Functional equation sign | +1; -1 | Parity data alone cannot determine higher analytic orders. |
| Result type | core rank equality; refined formula; one-sided inequality; conditional theorem; counterexample; computation only | The type must match what has actually been proved. |

**Universal quantifiers are the central blocker:** all CM/non-CM curves, all ranks, all conductors and relevant primes, and every excluded hypothesis must be covered. The official formulation concerns every elliptic curve over the rationals, not just the initially tested curves or an arbitrarily large finite sample.

## Matrix C — mathematical dependencies and valid combinations

### Core target

```text
EVERY E/Q: exact complex analytic order r_an(E)
                       AND
EVERY E/Q: exact algebraic rank r_alg(E)
                       AND
UNCONDITIONAL bridge proving r_an(E) = r_alg(E)
                       |
                CORE BSD PROVED
```

An alternative direct approach proves **both inequalities** \(r_{\mathrm{alg}}(E)\le r_{\mathrm{an}}(E)\) and \(r_{\mathrm{an}}(E)\le r_{\mathrm{alg}}(E)\) **for all E**, with no circular appeal to BSD. Proving Sha finiteness alone does not fill either missing analytic/algebraic bridge.

### Stronger refined MathOS route

```text
CORE rank/order equality for every E/Q
  + correct nonzero leading-term normalization
  + justified period/regulator/torsion/Tamagawa factors
  + Sha finiteness and Sha order for every E/Q
  + proof of exact leading-term relation
  = claimed refined BSD (all quantifiers checked)
```

This is a **logical dependency overview**, not a mathematically validated sufficient proof architecture. In particular, some leading-term or Sha assertions overlap or are conditional rather than independent.

### Portfolio combinations (research proposals, not completed implications)

| Candidate combined program | What it could contribute | What still blocks all-curves BSD |
|---|---|---|
| Heegner/Kolyvagin + generalized higher derivatives + higher-rank Euler systems | Extend rank-sensitive classes beyond analytic order one | Construction, nonvanishing, rank control for arbitrary E and arbitrary higher order |
| Iwasawa main conjectures + p-adic heights + complex L comparisons | Compare algebraic Selmer arithmetic with analytic special values | Exceptional local cases, arbitrary high order, all primes and archimedean comparison |
| Bloch–Kato/ETNC + motivic cohomology + descent | Unify Selmer and special-value formulas | Unconditional general theorems, no presupposed equivalent conjectures |
| Family twists + deformation + uniform specialization | Reduce general curves to cases with known comparisons | Genuine coverage of every E, no exceptional specialization gaps |
| Full analytic L data + exact algebraic descent | Prove ranks independently for a given curve | No finite algorithmic audit automatically proves the uniform all-curves theorem |
| Any route + formal theorem checking | Remove hidden assumptions from a completely stated argument | Formalization cannot supply an unknown theorem or confer novelty |
| Direct counterexample program | Disprove core BSD with one exact mismatch | Proving an actual rank/order discrepancy; numerical mismatch is insufficient |

## Matrix D — precise research experiments to attempt

- **BSD.M01 — Analytic L-function / complex derivatives:** For a declared rank-2 curve, identify a provable exact derivative/height identity and list missing assumptions.
- **BSD.M02 — Descent and Selmer bounds:** Reproduce a complete 2-descent for E1/E5 and compare proved rank bounds to certified analytic data.
- **BSD.M03 — Gross–Zagier / Kolyvagin (low rank):** Formalize a known rank-one instance, documenting each cited theorem and hypothesis.
- **BSD.M04 — Higher-rank Euler/Kolyvagin systems:** State a candidate higher-rank norm-compatibility and reciprocity law with a falsifiable concrete example.
- **BSD.M05 — Higher Gross–Zagier/height formulas:** Locate a rank-2 specialization with a theorem-level equality and verify its hypotheses without assuming BSD.
- **BSD.M06 — Iwasawa main conjectures:** Audit exact local hypotheses of a published main-conjecture theorem; list excluded cases E,p.
- **BSD.M07 — p-adic heights and regulators:** Compare ordinary vs supersingular and exceptional-zero hypotheses for one curve and one p.
- **BSD.M08 — Bloch–Kato / motivic / ETNC routes:** Draft precise implication with all source theorems separated from open conjectures.
- **BSD.M09 — Finiteness of Tate–Shafarevich groups:** Produce an explicit family of Selmer classes and isolate the exact missing finiteness bound.
- **BSD.M10 — Automorphic / trace formula / spectral routes:** Write a proposed trace identity as a theorem with domains, multiplicities, and a counterexample search.
- **BSD.M11 — Twists, congruences and specialization:** Prove exact coverage for a finite candidate family and list omitted curves; test degeneration at excluded primes.
- **BSD.M12 — Arithmetic statistics and average rank:** Record the exact height ordering and exceptional-set quantifiers of an existing rank result.
- **BSD.M13 — Direct computation and certified examples:** Replicate E1/E5 local counts, then extend to a high-rank example with certified algebraic/analytic evidence.
- **BSD.M14 — Partial Euler-factor agreement (MathOS 007):** Use the MathOS 007 classical counterexample as an adversarial negative control for every local-data proposal.
- **BSD.M15 — Formal theorem verification:** Extend Lean beyond conditional character cancellation to an actual finite-field point-count theorem with explicit finite-field axioms.
- **BSD.M16 — Logical counterexample (disproof branch):** Write a complete certificate format for analytic order and Mordell–Weil rank before choosing cases.
- **BSD.M17 — Direct universal rank bridge:** Inventory every inequality from published results and identify exact high-rank missing hypotheses.
- **BSD.M18 — Universal refined leading-term formula:** Audit all factors for E1 and E5 and identify which are sourced rather than proved.

## Mandatory adversarial audit

1. Does the statement quantify over every E/Q, not just finitely many/families?
2. Does it handle analytic rank >=2 without invoking BSD?
3. Are complete complex L-function/analytic-continuation inputs justified?
4. Are Selmer and Sha statements unconditional and properly indexed by p?
5. Are all prime, CM, reduction and residual hypotheses covered?
6. Are period, regulator, Tamagawa and torsion factors normalized when refined formula is claimed?
7. Are asymptotic, density and average results prevented from becoming universal theorems?
8. Does any cited or proven theorem assume what the route purports to prove?
9. Are formal checker and finite computation scopes accurately separated?
10. Is there an independent novelty and expert-review record before publishing a theorem claim?

## What MathOS 007 currently excludes

The original MathOS 007 example proves that matching local factors for all primes \(p\equiv3\pmod4\), even though this prime set is infinite, **does not determine rational rank**. The companion draft [PR #48](https://github.com/tltmgnt/MathOS/pull/48) documents a more precise mod-20 classification. Neither result identifies the order of vanishing of the **complete** (L(E,s)), proves high-rank BSD, or establishes novelty.

## Current external evidence and references (not a systematic novelty review)

- [CMI: official Birch–Swinnerton–Dyer problem (unsolved)](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/)
- [CMI September 2026 workshop on recent BSD-related results](https://www.claymath.org/events/the-birch-and-swinnerton-dyer-conjecture-and-related-problems-recent-results/)
- [Chao Li: overview of the Gross–Zagier–Kolyvagin rank-0/1 theorem](https://www.math.columbia.edu/~chaoli/docs/BSD.html)
- [Yan–Zhu (2026): selected Iwasawa main-conjecture cases and p-parts in rank at most one](https://www.sciencedirect.com/science/article/pii/S0021869326000281)
- MathOS [original BSD 007 note](MILLENNIUM_ATTACK_007.md), [canonical proposed routes](CLAY_PROOF_ROUTES.v1.json), [official-target alignment](CLAY_FULL_TARGETS.v1.json), and [open obligation register](../proof-analysis/OBLIGATIONS.v1.json).

## Operational gate for MathOS

All matrix entries remain `NOT_CERTIFIED`; no research route is marked proven as an all-curves BSD solution. New candidate lemmas must include quantifiers, exact assumptions, reference provenance, a falsification plan, finite-versus-universal distinction, and independent expert review. **Do not alter canonical statuses, claim prize certification, or present this taxonomy as a proof.**
