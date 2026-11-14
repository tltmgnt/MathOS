# A Lean-checked certificate for disjoint-factor expansion words

*Technical research note for independent mathematical review — draft v0.1*

**Status:** `REVIEW_DRAFT_NOT_SUBMITTED`. **No claim of mathematical novelty or a solution to P versus NP.** Author attribution, affiliation, and corresponding-author contact are deliberately omitted pending confirmation by the repository maintainers. This note has not been independently refereed.

## Abstract

We document a mechanically checked combinatorial result concerning an indexed three-choice expansion model associated with the formal product
\[
F_m=\prod_{i=1}^{m}(x_i+y_i-x_i y_i).
\]
For each natural number \(m\), a Lean 4.14.0 development proves that the recursively generated list of factor-choice words has exactly \(3^m\) entries, no repeated words, and a nonzero signed coefficient for every word. The checked result applies to the **choice-word representation**, not to a generic multivariate polynomial-ring formalization or to any computational-complexity lower bound. We give a short mathematical explanation, an elementary compact-expression counterpoint, a reproducibility procedure, and a structured list of omissions requiring independent review. No originality, external acceptance, or Clay Prize eligibility is asserted.

## 1. Motivation and prior context

SAT and propositional proof systems are classical topics in complexity theory [1]. Algebraic proof representations and lower bounds require careful selection of the resource measure and computational model; related algebraic proof-system literature includes Clegg–Edmonds–Impagliazzo [2] and Grochow–Pitassi [3]. These citations **situate** the topic and do not establish that this elementary factor expansion is a new result, or that the cited authors proved this particular formal lemma. The targeted reference discovery is documented in `SAT1_LITERATURE_LEDGER.v1.json`; systematic priority/novelty screening and expert reading remain outstanding.

This note contributes a reproducible *formalization artifact* for a simple fact, not a new complexity-theoretic breakthrough. In particular, counting expanded terms must never be conflated with the running time of a general SAT decision algorithm.

## 2. Definitions and exact formal theorem

Let \(C=\{\mathsf{x},\mathsf{y},\mathsf{xy}\}\) denote three *different symbols*. For each nonnegative integer \(m\), let \(T_m\) be the list of choice words over \(C\), defined recursively by

\[
T_0=[\epsilon],\qquad
T_{m+1}=(\mathsf{x}::T_m)\;\mathbin{+\!+}\;
(\mathsf{y}::T_m)\;\mathbin{+\!+}\;
(\mathsf{xy}::T_m),
\]

where \(a::T\) means prefixing each word in \(T\) by symbol \(a\), and \(+\!+\) is list concatenation. The empty word \(\epsilon\) corresponds to the empty product.

Define the signed coefficient \(c(w)\in\mathbb Z\) recursively by \(c(\epsilon)=1\), \(c(\mathsf{x}::w)=c(w)\), \(c(\mathsf{y}::w)=c(w)\), and \(c(\mathsf{xy}::w)=-c(w)\).

**Theorem 1 (checked in the Lean choice-word model).** For every \(m\in\mathbb N\):

1. \(|T_m|=3^m\);
2. \(T_m\) contains no duplicate words;
3. \(c(w)\ne0\) for every \(w\in T_m\) (indeed \(c(w)\in\{-1,1\}\)).

The exact Lean declaration is `MathOS.satSupport_certificate` in `formal/SATSupport.lean`. The imported library is Lean `Init`, pinned to toolchain version **4.14.0** in `.github/workflows/proof-route-lean.yml`. An audit can reproduce the *exact source-file digest* rather than trusting these prose statements.

**Proof outline (not a substitute for Lean replay).** The base list has one word. In each inductive step, three copies of \(T_m\) are prefixed by distinct first symbols, making the new length triple. Prefixing preserves uniqueness, and no word with one first symbol can equal a word with a different first symbol. Finally, each prefix preserves or negates a unit coefficient. The Lean source proves these assertions using structural induction, explicit disjointness of the prefix classes, and a separate nonzero-coefficient theorem. No `sorry` or declared new axiom appears in the checked artifact.

## 3. Relationship to the displayed polynomial

One may interpret the three factor choices at index \(i\) as the monomials \(x_i\), \(y_i\), and \(-x_i y_i\). With *pairwise disjoint sets of indexed variables* across factors, different choice words give different exponent vectors: choose the first index where the words differ and compare the two exponents associated with that index. Thus the ordinary fully distributed product has \(3^m\) distinct nonzero monomials. This last **polynomial-ring interpretation is given as elementary informal mathematics**; an explicit polynomial type and the coefficient/support homomorphism are **not presently kernel-checked in this repository**.

The factor \(x+y-xy\) evaluates to Boolean disjunction on inputs \(x,y\in\{0,1\}\). The product of these factors therefore evaluates to the conjunction of the corresponding OR conditions under Boolean assignments. Neither observation by itself supplies a general SAT algorithm or shows an intractable family of instances.

## 4. Central non-implication: expansion size is not SAT complexity

The displayed product has a compact arithmetic expression with \(O(m)\) factors and a straight-line arithmetic circuit of \(O(m)\) additions and multiplications. The *fully expanded monomial list* has \(3^m\) entries. Both statements can hold simultaneously.

Consequently an exponential-size expanded representation does **not** imply a superpolynomial arithmetic-circuit lower bound, much less an unrestricted deterministic Turing-machine lower bound for SAT. In fact, deciding satisfiability for the example formula \(\bigwedge_{i=1}^m (x_i\lor y_i)\) is straightforward: set each \(x_i=1\). Such a restricted formula family is not a candidate for demonstrating SAT hardness.

The actual MathOS `PNP.sat_runtime` obligation involves a *specified algorithm*, correctness on every encoded instance, uniformity, and a worst-case **total bit-complexity** bound, which this note does not establish. Nor does this note prove the complementary unrestricted SAT lower bound needed for a P \(\ne\) NP route. Those are separate and presently open mathematical implications.

## 5. Reproducibility and exact evidence

Repository: [tltmgnt/MathOS](https://github.com/tltmgnt/MathOS). Source: [`formal/SATSupport.lean`](../../formal/SATSupport.lean); formal assurance: [`mathos/research/theorem_assurance.py`](../../mathos/research/theorem_assurance.py). The pinned CI job executes:

```sh
lean formal/SATSupport.lean
python -m mathos.research.theorem_assurance \
  --verify-lean --output-dir artifacts/theorems
```

The assurance output records the precise source SHA-256, toolchain check, and open-status links to the original MathOS proof register. A GitHub Actions run is evidence of successful compilation for a particular commit; it is **not** peer review or proof of new mathematical significance. Reviewers should replay the Lean source and inspect its definitions independently.

## 6. Claim/evidence table

| Proposition or assertion | Evidence | Status |
|---|---|---|
| Choice-word list has length \(3^m\) for every \(m\) | `MathOS.satTerms_length` | Lean checked on recorded CI runs |
| List contains no repeated words | `MathOS.satTerms_nodup` | Lean checked on recorded CI runs |
| Every word has coefficient \(+1\) or \(-1\) | `MathOS.satCoefficient_sign` | Lean checked on recorded CI runs |
| Combined model theorem | `MathOS.satSupport_certificate` | Lean checked on recorded CI runs |
| Full embedding into \(\mathbb Z[x_1,y_1,\ldots,x_m,y_m]\) | Informal interpretation in §3 | **Not formalized** |
| Any unrestricted SAT running-time bound | None | **Not proved** |
| Either outcome of P versus NP | None | **Not proved** |
| Research novelty and independent acceptance | No independent assessment | **Not established** |

## 7. Limitations and requested independent review

The record is a small mechanically checked statement about indexed syntax. A substantial subsequent formalization would require an explicit multivariate polynomial ring and a proved interpretation preserving coefficients and supports. Any complexity-theoretic use would additionally require a legitimate computational model and proof tying the relevant representation constraints to every algorithm in scope. Neither bridge is present.

Independent review should (i) replay the pinned Lean proof, (ii) compare the statements with standard expansion and algebraic proof-complexity results, (iii) evaluate whether the note should be classified as exposition, formalization, or an original result, and (iv) document any gap, counterexample, missing assumption, or existing stronger theorem. The review questions and fields are supplied in `SAT1_EXTERNAL_REVIEW.md`. No reviewer, approval, journal acceptance, or publication date is asserted.

## References

[1] Stephen A. Cook, “The Complexity of Theorem-Proving Procedures,” *Proceedings of STOC*, 151–158 (1971). DOI: [10.1145/800157.805047](https://doi.org/10.1145/800157.805047).

[2] Matthew Clegg, Jeffery Edmonds, Russell Impagliazzo, “Using the Gröbner Basis Algorithm to Find Proofs of Unsatisfiability,” *Proceedings of STOC*, 174–183 (1996). DOI: [10.1145/237814.237860](https://doi.org/10.1145/237814.237860).

[3] Joshua A. Grochow, Toniann Pitassi, “Circuit Complexity, Proof Complexity and Polynomial Identity Testing,” *ECCC* TR14-052 (2014). [ECCC report](https://eccc.weizmann.ac.il/report/2014/052/).

[4] Clay Mathematics Institute, [Millennium Prize rules](https://www.claymath.org/millennium-problems/rules/). These rules concern **complete solutions** in qualifying outlets after the required review/acceptance process; this note is neither such a solution nor submitted to Clay.

---

**Repository metadata:** `SAT1`; `P-versus-NP`; `PNP.equality`; `PNP.sat_runtime` (OPEN). Manuscript classification: **unsubmitted technical note / research review draft**. `NOT_CERTIFIED`, `NOT_INDEPENDENTLY_ASSESSED`, `NOT_PERFORMED`, `NOT_PROVEN`.

**Final scope declaration:** This manuscript is not a complete solution to any Millennium Prize Problem. It has not been submitted to any academic journal, reviewer or the Clay Mathematics Institute. It establishes no unrestricted SAT complexity bound and makes no claim of a completed independent novelty review.
