# SAT1 adversarial behavior pilot: external handoff and disagreement adjudication

**Current status: PROTOCOL-READY ONLY.** No participants or outside raters have been recruited, no informed consent has been independently verified, and no human behavioral study or mathematical peer review has been completed. This is a **research-methods workflow**, not a Clay Millennium Problem solution.

## What the next step accomplishes

The seven [adversarial research-use cards](SAT1_ADVERSARIAL_BEHAVIOR_USE_CARD.md) already allow participants to record evidence-based decisions. The [two-rater pilot](SAT1_BEHAVIOR_PILOT.md) makes it possible for two separately identified reviewers to mark 21 rubric judgments (seven scenarios × three yes/no criteria), then reports observed agreement and Cohen's kappa.

This component adds a **human-only adjudication stage** for disagreements. It generates an exact-hash-bound packet of disputed ratings, a third-reader template with no prefilled verdict, and a status-only result. It never silently resolves disputes, changes the original agreement statistics, or claims that a submitted file proves reviewer independence.

The versioned [adjudication protocol](SAT1_BEHAVIOR_ADJUDICATION_PROTOCOL.v1.json) requires a source-pinned third-party 0/1 decision and meaningful rationale for each discrepant rubric judgment. The program refuses invented, duplicated, incomplete or stale judgments.

## Status-only demonstration (no human data)

From the MathOS repository:

```sh
python -m unittest discover -s tests -p 'test_behavior_adjudication.py' -v
python -m mathos.research.behavior_adjudication \
  --output-dir artifacts/adjudication
```

The output `adjudication_status.json` says `PROTOCOL_ONLY_NO_HUMAN_DATA`; CI **only** executes this mode. No participant or human assessment should appear in CI artifacts.

## Real private exploratory pilot — only with appropriate consent and oversight

First establish a genuine human-research protocol, applicable human-subjects/ethics review, a voluntary invitation, informed consent, a data retention/deletion policy, and separate private records for participant, rater and adjudicator. A CLI flag cannot prove any of these occurred. Do not collect behavioral data publicly in GitHub issues or store records in a repository.

After obtaining the participants' informed consent through an appropriate process, complete the [two-rater workflow](SAT1_BEHAVIOR_PILOT.md) in a private directory **outside the repository**. For example:

```sh
python -m mathos.research.behavior_adjudication \
  --responses /tmp/mathos-private/answers.json \
  --rater-a /tmp/mathos-private/rater_a.json \
  --rater-b /tmp/mathos-private/rater_b.json \
  --consent-attested \
  --output-dir /tmp/mathos-private/adjudication
```

The software validates exact evidence digests and writes:

- `private_disagreement_packet.json`: only discrepant rubric judgments, relevant card text, submitted explanations, sources and the two original ratings. It conceals decision choices and participant identifiers as fields, but free-form statements **may still disclose identity or choices**; a human operator must inspect the packet for sensitive information before sharing it privately.
- `private_adjudicator_template.json`: empty decisions for precisely the disputes found, bound to the exact Lean proof, casebook, two-rater protocol, adjudication protocol, participant-response digest, rater-file digests, and individual explanation hashes.
- `adjudication_status.json`: hashes, count of disputes, original agreement metrics, and explicit noncertification flags, but **not** the full participant statements.

A third reader must independently inspect the disputed evidence, declare conflicts, and enter an explicit binary judgment, substantive explanation and source for **every** dispute. After that file exists:

```sh
python -m mathos.research.behavior_adjudication \
  --responses /tmp/mathos-private/answers.json \
  --rater-a /tmp/mathos-private/rater_a.json \
  --rater-b /tmp/mathos-private/rater_b.json \
  --adjudicator /tmp/mathos-private/adjudicator.json \
  --consent-attested \
  --output-dir /tmp/mathos-private/adjudication
```

The outcome is `ADJUDICATION_SUBMITTED_BUT_NOT_AUTHENTICATED`, not `PEER_REVIEWED`. If there are no disagreements, the outcome is `NO_RATER_DISAGREEMENTS_UNAUTHENTICATED` and no adjudicator verdict is fabricated. Both cases preserve the original pre-adjudication agreement analysis.

## Scientific and privacy boundaries

- **Partial blinding only:** decision labels, participant pseudonyms and answer keys are hidden from structured packet fields, but explanations can reveal them. The repository contains the rubric and cannot establish truly blind assessment.
- **Source and integrity linkage:** SHA-256 records exact bytes; it is not a digital signature, consent artifact, source-authenticity proof, independent expertise check or author identification.
- **Independent human participation:** a rater name and conflict statement are self-attested data only. A real external methods reviewer must separately authenticate identity and independence.
- **Evidence quality:** the program checks data shape, completeness and original agreement statistics, **not** whether a mathematical argument or adjudicator decision is valid.
- **Privacy:** processing of real participant/rater/adjudicator files and any private outputs **inside MathOS is rejected**. Keep them outside the repository. Follow a documented deletion/retention plan; never upload raw records as GitHub Actions artifacts.
- **Study validity:** this pilot has no external preregistration, representative sample or control group. Cohen's kappa is descriptive; agreement is not proof of behavioral competence, generalizability or a validated instrument.
- **Separate mathematics:** the [real independent SAT1 mathematical reviewer issue](https://github.com/tltmgnt/MathOS/issues/30) is still a distinct request. Adversarial behavioral testing is not a mathematical proof review and cannot close any Clay obligation.

The next human action is a methods/ethics review, appropriate consent planning, and independent collaborators willing to conduct the pilot. None is claimed as complete.

## Independent methods feedback

An external [research methodology and ethics review invitation (#33)](https://github.com/tltmgnt/MathOS/issues/33) asks for criticism of sampling, consent, potential answer leakage, blinding, reliability measurements and human-subjects review requirements. This invitation **does not** represent a completed study or an independent opinion.
