# SAT1 formal note — independent reviewer packet

**Circulation status:** `REVIEW_READY_NOT_SUBMISSION_READY`. This is a structured *request for external review*, not a completed review, an author-independent endorsement, or a Clay submission. No reviewer has been recruited or contacted by this repository.

## Manuscript and exact artifact

- Research note: [SAT1_FORMAL_NOTE.md](SAT1_FORMAL_NOTE.md)
- Formal artifact: [SATSupport.lean](../../../formal/SATSupport.lean)
- Reproducibility and assurance: [THEOREM_ASSURANCE.md](../THEOREM_ASSURANCE.md)
- Literature discovery ledger: [SAT1_LITERATURE_LEDGER.v1.json](SAT1_LITERATURE_LEDGER.v1.json)
- Release evidence: created by `python -m mathos.research.paper_packet --output-dir artifacts/paper`

**What is being reviewed:** a proof about three-choice indexed syntactic words for all natural numbers `m`, and the accuracy of its *informal* discussion of an associated disjoint-variable polynomial.

**Not being reviewed as a claimed solution:** P versus NP, full SAT worst-case complexity, any unvalidated proof route, any other Clay Millennium problem.

## Independent reviewer questions

1. **Formal model** — Does the Lean declaration `MathOS.satSupport_certificate` precisely state `3^m` list length, no duplicates, and nonzero signed coefficients? Does the proof pass with the pinned toolchain and trusted imports?
2. **Interpretation** — Is the correspondence from indexed words to distinct monomials of `∏(x_i+y_i−x_i y_i)` described correctly? Note that this mapping is *not* itself checked in Lean.
3. **Complexity limitation** — Does the note clearly explain that a compact `O(m)` product expression coexists with `3^m` expanded terms and thus rules out any inference to general SAT hardness?
4. **Prior literature** — Check known expansion-counting and formalized combinatorial-algebraic lemmas beyond the initial four background references. Is the manuscript primarily explanatory or formally novel? What closer sources should be cited?
5. **Claim audit** — Are any phrases too strong, e.g. implying that a Clay obligation is established, novelty is shown, or independent review has already happened?
6. **Publication suitability** — Would this material merit a short expository note, a formal verification reproducibility record, an educational appendix, or no publication on its own?

## Review log (unfilled until an actual independent review)

| Field | Status / to be supplied by the reviewer |
|---|---|
| Reviewer identity and institutional affiliation | NOT_PROVIDED |
| Reviewer independence / any conflicts | NOT_ASSESSED |
| Date and exact source commit reviewed | NOT_PROVIDED |
| Lean version, command, source hash and result | NOT_INDEPENDENTLY_REPLAYED |
| Mathematical objections and counterexamples | NOT_REVIEWED |
| Closest published prior art (full citations, page/section) | NOT_ASSESSED |
| Recommendation and reasons | NOT_PROVIDED |
| Reviewer permission to quote or publish comments | NOT_REQUESTED |

**Template verdicts**, to be selected *by a real independent reviewer*, not automatically: `ACCEPT_AS_EXPOSITION`, `MAJOR_REVISIONS`, `NOT_SUITABLE`, or `INSUFFICIENT_EVIDENCE`. The repository does not infer any verdict from CI success.

## Next actions for repository maintainers

- Confirm authorship and contribution credits; do not fabricate a corresponding author.
- Circulate the research note and exact Lean source to a specialist in proof complexity or formalized algebra.
- Request a separate documented prior-art review with dates, sources and reproducible search terms.
- Incorporate substantive reviewer feedback through an ordinary reviewed PR; preserve old versions and source hashes.
- Select an appropriate venue only after a human assessment of technical contribution. A mathematical or formal-methods venue may decline a purely elementary note, which is a legitimate outcome.
- Keep the core proof register and `SAT1` formalization status distinct from claims of novelty, community acceptance or a complete Millennium solution.

**Never represent this packet as a submission to the Clay Mathematics Institute.**
