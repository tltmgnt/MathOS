# SAT1 adversarial desk critique (internal, **not independent peer review**)

**Prepared by the project assistant for external reviewers.**
This is a critical mathematical reading of the manuscript and Lean source, not a report from an outside mathematician and not an independently authenticated result. Status: `AUTHOR_SIDE_CRITIQUE_ONLY`.

## Main finding: formal theorem is narrower than the displayed polynomial theorem

The Lean declaration `MathOS.satSupport_certificate` applies to the inductively generated list `satTerms m : List (List SATFactorChoice)` and recursive sign function `satCoefficient`. This is an actual all-`m` statement in its own syntax, with no finite bound on `m`.

However, the current Lean file does **not** define the polynomial ring
\(\mathbb Z[x_1,y_1,\dots,x_m,y_m]\), a homomorphism from factor choices to monomials, a support-coefficient map, or a theorem that the formal product has exactly \(3^m\) nonzero polynomial coefficients. The corresponding polynomial claim is plausible elementary algebra, but an **independent** checker cannot infer that it was formalized simply because a word-list theorem compiles.

**Reviewer action:** Check the word-list theorem against the prose statement. If algebraic scope is the goal, ask the maintainers to formalize the missing representation map and its injectivity before calling the polynomial theorem Lean-verified.

## Main finding: exponential expansion size does not imply exponential algorithmic complexity

The expression
\[
F_m=\prod_{i=1}^m (x_i+y_i-x_i y_i)
\]
has \(3^m\) terms after naive distribution into disjoint indexed monomials. But the factored expression contains \(m\) factors, each with constant-size local arithmetic, and is representable by a straight-line arithmetic circuit using \(O(m)\) operations. The same mathematical object can have a large dense expansion and a succinct factored representation.

A concrete counterpoint: the Boolean formula
\[
\Phi_m=\bigwedge_{i=1}^{m}(x_i\lor y_i)
\]
is satisfiable for every \(m\): simply assign all \(x_i=1\). This can be checked in linear time. The factors \(x_i+y_i-x_i y_i\) encode OR on Boolean inputs. Exponential symbolic expansion in one representation therefore does **not** establish that the corresponding SAT decision family is hard. It certainly does not prove a lower bound for *every possible algorithm* for unrestricted SAT.

**Reviewer action:** Reject any implication from `satSupport_certificate` to unrestricted SAT lower bounds or a polynomial-time SAT algorithm unless a new, independently justified complexity theorem is supplied. The `PNP.sat_runtime` connection is only a proposal in a research graph.

## Main finding: novelty has not been demonstrated

Counting fixed-size sequences is a routine combinatorial technique: three choices independently at \(m\) positions give \(3^m\) words. The signed-coefficient observation is likewise elementary in this indexed, disjoint-choice encoding. This suggests that the result is primarily a proof-formalization exercise, not evidence of original complexity-theoretic mathematics.

The [Cook (1971)](https://doi.org/10.1145/800157.805047) and [Clegg–Edmonds–Impagliazzo (1996)](https://doi.org/10.1145/237814.237860) papers establish background around SAT and algebraic proof systems, respectively. Their presence in a bibliography **does not** show that the precise SAT1 word theorem is new, previously published, or relevant to a lower bound. A dated independent review of closer combinatorics and formalized algebra literature is still needed.

**Reviewer action:** Decide if the manuscript has value as an educational note or reproducible formal artifact. Do not infer novelty from a mechanically checked known-style statement.

## Formal audit improvement

A compiler success does not alone reveal whether the statement relies on `sorryAx`, custom axioms, or native compilation trust. The updated source explicitly requests `#print axioms MathOS.satSupport_certificate`. The repository's strict `lean_axiom_audit` requires a pinned Lean 4.14.0 result and permits only Lean's standard logical axioms, reporting the exact transitive set and proof-file digest. This follows the [Lean reference manual](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

An axiom-clean result still does **not** establish that the formal theorem matches the author's full informal mathematical intent. A knowledgeable human must read and judge that correspondence.

## Evidence matrix

| Question | Current answer | Independent human work required |
|---|---|---|
| Does Lean verify the syntactic all-`m` choice-word result? | Earlier workflow replay passed; new axiom audit must pass separately | Independent replay of exact source and imports |
| Is the full multivariate polynomial statement formalized? | No | Create and verify explicit map to polynomial coefficients |
| Is `3^m` an unrestricted SAT time lower bound? | No; explicit compact circuit and easy CNF family rebut the inference | Any different meaningful complexity theorem must be rigorously specified |
| Is SAT1 demonstrably new mathematics? | No evidence of novelty | Independent full-text scholarship and source comparison |
| Has an unaffiliated mathematician signed off? | No | A real outside reviewer must publish a dated, source-pinned critique |

**Provisional internal assessment:** suitable to send **for technical criticism**, not as a peer-reviewed new mathematical result or a Clay solution. This is not a verdict from an independent mathematician and creates no certification.
