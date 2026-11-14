# SAT1 adversarial-behavior pilot: blinded double-rating protocol

**Status:** `PROTOCOL_ONLY_NO_HUMAN_DATA` as shipped. This is an **exploratory pilot implementation**, not a conducted human study, externally registered preregistration, validated psychometric instrument, independent mathematical peer review, or Clay result.

## Research aim and limits

The current [seven SAT1 adversarial cards](SAT1_ADVERSARIAL_BEHAVIOR_USE_CARD.md) test whether a participant recognizes unsupported mathematical claims without reflexively rejecting an accurately scoped Lean result. The existing [behavior-review script](../../../mathos/research/behavior_review.py) compares selected decision labels to disclosed keys; that score alone does not establish meaningful reasoning.

The new pilot adds **a separate human evidence-quality task**. Two purported human raters assess the participant's *written* justifications against a source-specific rubric. The scripts can describe and compare **supplied** judgments; they cannot recruit participants, obtain independently verifiable consent, authenticate raters or adjudicate mathematical truth.

## Fixed rubric and protocol

The versioned [pilot protocol](SAT1_BEHAVIOR_PILOT_PROTOCOL.v1.json) specifies all seven case IDs, exactly two separate raters, and three binary judgments per case:

1. Does the justification include the **first required observation** for that card?
2. Does it include the **second required observation**?
3. Is its claimed source genuinely **relevant** to the assertion? This criterion does *not* establish that the participant actually read the source.

These amount to **21 paired binary judgments per participant**, each independently entered by two rater accounts. Each rater must supply a substantive per-card explanation, declare conflicts and identify themselves with a **study pseudonym**. Those fields are merely self-attested; they are not verified expert qualifications.

**Analysis specified in advance:** for each rubric dimension and for the pooled 21 judgments, report matched ratings, observed agreement, chance-expected agreement, and Cohen's kappa. If chance-expected agreement is 1.0, kappa is **undefined** and is reported as `null`, not as perfect reliability. These are descriptive metrics for a very small, unvalidated pilot, not statistical proof of competence or a robust reliability estimate.

There is **no valid comparison group**, no representative participant sample, no preregistration in an external independent registry, no externally authenticated consent and no established minimum acceptable agreement. These shortcomings must be addressed before anyone claims a real behavioral validation study.

## Consent, pseudonyms, confidentiality

**Obtain appropriate consent outside this software.** The CLI requires `--consent-attested` before processing participant responses. That flag is only the operator's assertion; it is not verified consent, ethical approval or any research-institution approval. If the study involves research subjects, the operator is responsible for any applicable human-subjects review and requirements.

Use only *pseudonyms*; avoid names, email addresses, health data or confidential information in notes, source references or rater comments. These files must stay in a **private local directory outside the MathOS repository**, never in a public Git commit or uploaded CI artifact. The script refuses participant input or private output paths inside the repository and does not send responses to an API.

The rater-facing package hides the participant pseudonym, selected decision and answer key. However, free-form explanations may disclose the person's decision, identity or personal information; this is **partial blinding**, not guaranteed double blinding. Since the answer-key casebook is public in the repository, the tool cannot ensure raters are blind to the rubric or key.

The status report contains SHA-256 digests and agreement summaries rather than participant note text. Digests are integrity markers, **not digital signatures or proof of human authenticity**.

## Reproduce without any human data

```bash
python -m unittest discover -s tests -p 'test_behavior_pilot.py' -v
python -m mathos.research.behavior_pilot --output-dir artifacts/behavior-pilot
```

This produces `pilot_status.json` with `PROTOCOL_ONLY_NO_HUMAN_DATA`, no study results, and no participant content. CI is intentionally limited to this offline no-data verification and synthetic unit tests.

## Conduct a locally managed exploratory pilot

In a *separate private workspace*, obtain the participant's voluntary consent and their complete response file produced with `behavior_review.py`:

```bash
python -m mathos.research.behavior_pilot \
  --responses /tmp/mathos-private/answers.json \
  --consent-attested \
  --output-dir /tmp/mathos-private/pilot
```

The output includes:

- `private_blinded_rater_packet.json`, containing the scenarios, written explanations, supplied citations and the two case-specific rubric criteria, but **not** the participant's decision labels or their study pseudonym
- `private_rater_template.json`, a source-digest-bound template for **each** rater's independent assessment
- `pilot_status.json`, which remains explicitly **unauthenticated**

Make **two separate copies** of the template. Each reviewer must independently fill in `rater_pseudonym`, `conflicts_declaration`, the three `0`/`1` judgments per case and `rater_comment`. Keep those full documents private. Then run:

```bash
python -m mathos.research.behavior_pilot \
  --responses private/answers.json \
  --consent-attested \
  --rater-a /tmp/mathos-private/rater_a.json \
  --rater-b /tmp/mathos-private/rater_b.json \
  --output-dir private/pilot
```

The tool checks exact file and note hashes, full coverage of seven cards, valid binary ratings, differing rater pseudonyms, and complete written explanations. It returns **`DOUBLE_RATINGS_RECEIVED_UNAUTHENTICATED`** and descriptive agreement values; it does not mark a researcher independent, a behavior instrument validated or a mathematical proof correct.

## Independent oversight required

A separate researcher must assess the study's sampling, informed consent, potential answer-key exposure, rater independence, supporting explanations and any adjudication of disagreement. The present software **does not** perform that oversight. A high Cohen kappa, matching key decisions or an attractive summary must never be reported as independent mathematical acceptance.

The [SAT1 mathematical reviewer invitation](https://github.com/tltmgnt/MathOS/issues/30) remains a **separate process**. It solicits actual mathematical review of the Lean result; a behavioral pilot is not a replacement.

**Clay status:** `NOT_CERTIFIED` throughout.

## Next step: independent handling of rater disagreements

The separate [source-pinned disagreement adjudication protocol](SAT1_BEHAVIOR_ADJUDICATION.md) prepares a private third-reader handoff **only** for genuinely conflicting rubric judgments. It preserves original Cohen-kappa calculations, rejects participant data stored inside the repository and does not automatically authenticate a third reader or certify the research. Public [methods and ethics feedback issue #33](https://github.com/tltmgnt/MathOS/issues/33) requests outside critique without collecting participant responses.
