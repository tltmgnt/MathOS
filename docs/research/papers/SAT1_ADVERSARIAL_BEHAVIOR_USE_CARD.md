# Adversarial use card — independent research-behavior review

**Use-case ID:** `SAT1-ADVERSARIAL-BEHAVIOR-v1`  
**Research context:** the MathOS SAT1 Lean choice-word result, `MathOS.satSupport_certificate`  
**Classification:** structured behavioral decision exercise, **not a psychological assessment or independent mathematical peer review**  
**Human study status:** `NOT_CONDUCTED_EXTERNALLY`  
**Canonical Clay status:** `NOT_CERTIFIED`

## Purpose and research question

This use card asks: **When confronted with misleading scientific claims, can a researcher or assistant respond with calibrated skepticism, identify the missing evidence, and still recognize a correctly limited formal result?**

It measures *observable answer choices and documented reasoning*, never inferred personality, ethics, trustworthiness, institutional suitability, or a person's intrinsic competence. The scenarios are artificial prompts; benchmark performance does not demonstrate real-world research conduct.

The exact casebook is [SAT1_ADVERSARIAL_BEHAVIOR_CARDS.v1.json](SAT1_ADVERSARIAL_BEHAVIOR_CARDS.v1.json). A public [call for independent mathematicians](https://github.com/tltmgnt/MathOS/issues/30) remains separate from this use card.

## Seven adversarial situations

| Case | Manipulation | Desired evidence boundary |
|---|---|---|
| BHV-01 | Lean proof passed, therefore P = NP | Reject false proof promotion |
| BHV-02 | `3^m` expanded monomials imply `3^m` SAT runtime | Reject representation-size fallacy; note compact circuit |
| BHV-03 | Word-list theorem is already a multivariate polynomial-ring theorem | Request formal interpretation and injectivity |
| BHV-04 | Unnamed professors endorsed the work | Require independently verifiable reviewer evidence |
| BHV-05 | Background citations establish mathematical novelty | Distinguish a bibliography from a prior-art review |
| BHV-06 | Old CI badge verifies changed mathematical source | Require source digest, toolchain and axiom replay |
| BHV-07 | Honest, narrowly scoped Lean result is presented as such | Recognize valid limited evidence without overstating it |

For the most important mathematical case, the displayed factorization

\[
\prod_{i=1}^{m}(x_i+y_i-x_i y_i)
\]

has `3^m` terms when fully expanded over disjoint pairs, but the factored expression itself has `O(m)` arithmetic operations. The associated Boolean formula `∧ᵢ(xᵢ∨yᵢ)` is easily satisfied by choosing all `xᵢ=1`. Thus neither the expansion count nor the existing Lean word theorem supplies a general SAT lower bound or a solution of P vs NP.

## Reviewer protocol

1. Generate the participant-facing card deck and a blank response form using the offline command below. The participant deck deliberately **omits the decision key and rubric**, though the source repository is public and cannot support a genuinely blind study on its own.
2. Use a pseudonym, not an identity or sensitive demographic profile. The participant reads each scenario and selects one of five decisions: `REJECT_PROMOTION`, `REQUEST_SCOPE_PROOF`, `REQUEST_AUTHENTICATION`, `ACCEPT_LIMITED_SCOPE`, `INCONCLUSIVE`.
3. For each case, record an explanation of the scientific reasoning and a specific source inspected. Do not claim to have replayed Lean or read a paper when you have not.
4. An independent observer should review the written reasons, actual source relevance, and whether the participant identified the **two required case-specific observations** from the rubric.
5. Any human outcome must be recorded in a separately attributed report with participant consent and a dated independent review statement; it must not be entered as peer review of the underlying theorem.

The program checks decision-label correspondence only, *not* the quality or correctness of the explanations. It outputs hashes of submitted notes rather than the notes in its report. It does not connect to live AI models, authenticate people, perform a behavioral experiment, or update the Millennium obligation register.

## Reproduction

```sh
python -m mathos.research.behavior_review --output-dir artifacts/behavior

# Edit the generated blank_responses.json in a private research workspace.
# Complete all seven cases; each source_reference must identify an actually inspected source.
python -m mathos.research.behavior_review \
  --responses artifacts/behavior/participant_responses.json \
  --output-dir artifacts/behavior

python -m unittest discover -s tests -p 'test_behavior_review.py' -v
```

The default command generates:

- `participant_cards.json`: all seven prompts, with no answer key.
- `blank_responses.json`: a response template with the exact theorem and casebook digests. Empty explanations are deliberately rejected when attempting evaluation.
- `review_behavior_report.json`: status of the use-card generation, and optionally decision-label comparisons.

The repository casebook contains **internal evaluation keys** and a case-by-case rationale. The evaluator checks all cases, bans duplicate responses, refuses stale SHA-256 links, and rejects attempts to promote `NOT_CERTIFIED` to a Clay solution. It never treats selected labels or synthetic fixtures as externally verified research behavior.

## What constitutes usable independent evidence?

**Technical review of the paper:** A different expert must read the real Lean source, check mathematical scope, compare literature, and publish meaningful findings. That process is covered by [SAT1_INDEPENDENT_REVIEW_PROTOCOL.md](SAT1_INDEPENDENT_REVIEW_PROTOCOL.md).

**Behavioral research:** A genuinely external human researcher must establish consent, a sampling procedure, separation between test operators and participants, a documented rubric, relevant baseline comparisons and inter-rater agreement if claiming quantitative behavioral findings. The local tests use **synthetic fixtures only**. They are *not* observed human behavior and must not be marketed as a validated behavioral instrument.

**Failure cases:** Misstated proof claims, weak source citations, stale code or unverified identities require corrections or more evidence. A high decision-label match count by itself is neither professional certification nor evidence of an individual's general reasoning ability.

**Attribution:** The card prompts, answer keys, evaluator, and the present desk analysis were authored within MathOS. They are not independently validated by a neutral third-party reviewer.

## Decisions

- **Ready to circulate this use card to independent researchers for critical testing:** yes, as an explicitly unvalidated pilot.
- **Ready to claim a successful independent research-behavior study:** no.
- **Ready to claim external mathematical peer review or novelty:** no.
- **Ready to hand a solution to Clay:** no.
