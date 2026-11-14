# MathOS agentic Millennium research workflow

**Status:** experimental research agent. **NOT_CERTIFIED**. This is not a proof engine and does not submit or evaluate claims on Clay's behalf.

**Purpose:** use multiple AI roles to *attempt* the missing Clay-aligned lemmas recorded in \`docs/research/CLAY_FULL_TARGETS.v1.json\`, challenge their assumptions, collect existing bounded evidence and produce clearly labeled packets for human mathematicians. This builds on the seven-track audit and the 14 open obligations without changing their state.

## Actual process and safety gates

\`\`\`text
Canonically registered Clay problem + missing mathematical bridge
             |
     [1] Source audit: exact Clay target, quantifiers, open obligations
             |          FAIL -> no run / no output
     [2] Deterministic bounded probe and source hashes
             |          PROBE FAIL -> no AI output / no promotion
     [3] Planner (AI) -> precise research question and success criterion
             |
     [4] Proposer (AI) -> conditional lemma, assumptions, argument attempt
             |
     [5] Skeptic (AI) -> counterexample plan and quantifier audit
             |
     [6] Reviewer (AI) -> REVISE / REJECT / HUMAN_REVIEW_REQUIRED
             |          REVISE -> [4] under max-rounds/call budget
             |
     [7] JSON + Markdown handoff with skeptical gaps and actual probe result
             |
     [8] Human mathematics and source review (outside automation)
             |          no automatic proof status changes
    NOT_CERTIFIED / BLOCKED / no Clay prize eligibility
\`\`\`

Every stage is bounded: no arbitrary model-provided Python, shell or URLs are executed. Only the repository's existing deterministic registered probes run. The model receives registered problem statements and the actual bounded-probe output, not a license to claim it verified them. Its text is candidate material, not accepted evidence.

**Important:** a skeptic saying \`NO_OBVIOUS_FLAW\` or reviewer saying \`HUMAN_REVIEW_REQUIRED\` never certifies a theorem. The existing code cannot verify model-proposed proof attempts. Independent human and, when appropriate, formal proof checking are required before any theorem is considered established.

## Offline deterministic smoke test (no AI)

From repository root, Python 3.10+:

\`\`\`sh
python -m mathos.research.agentic_clay --provider offline --track all \
  --rounds 2 --max-model-calls 56 --output-dir artifacts/agents/offline
python -m unittest discover -s tests -p 'test_agentic_clay.py' -v
\`\`\`

\`offline\` means **scripted agent handoffs** rather than independent reasoning; outputs explicitly report \`ai_generated=false\` and \`OFFLINE_TEMPLATE_ONLY\`. It verifies that the role loop, budgeting, data provenance, artifact formatting and fail-closed status gates work.

## Live AI research (requires an explicit API key)

Configure the repo's GitHub Actions secrets and variables:

- Secret \`MATHOS_OPENAI_API_KEY\` — a separately provisioned, appropriately restricted API key. **Never commit keys.**
- Repository variable \`MATHOS_OPENAI_MODEL\` — a model available in that API project, e.g. a current OpenAI Responses-compatible model. Choose the model explicitly; access, token use and charges depend on your API project.

Then open **Actions > Clay agentic research (guarded) > Run workflow** on **\`main\`**, and select \`provider=openai\`, problem track and \`rounds=1\` (or 2 for revision). Only a manual dispatch on \`main\` is allowed to read the API secret. Pull-request events run **offline-only** and have no access to the secret. No scheduled API costs are enabled. The live job is read-only for repository permissions and cannot merge or write proof status.

Local equivalent (set \`OPENAI_API_KEY\` and \`OPENAI_MODEL\` securely):

\`\`\`sh
python -m mathos.research.agentic_clay --provider openai --track Navier-Stokes \
  --rounds 2 --max-model-calls 7 --output-dir artifacts/agents/live
\`\`\`

For one track: at most 4 model calls for one round, 7 for two, 10 for three. For all seven tracks: worst case 28 calls in one round, 49 in two, 70 in three. **These calls may incur API charges.** Missing credentials, an unavailable model, invalid responses or insufficient budgets cause a hard failure; the tool does not silently fall back to mock outputs. Error messages do not echo the API response body or key.

The integration uses the OpenAI [Responses API](https://platform.openai.com/docs/api-reference/responses/create), with \`store=false\` and no model-accessible tools. System prompts require strict JSON with a fixed role schema; response validation rejects forged verdicts such as \`PROVED\` or \`CERTIFIED\`. GitHub secrets are not used in pull-request workflows.

## Delivered evidence

Each run writes two files to its chosen output directory:

- \`agentic_research_report.json\`: one entry per selected Clay problem, official target source/statement, missing global theorem, bounded probe evidence, four-agent outputs by iteration, skeptic criticisms, reviewer verdict, counts/budgets, and SHA-256 digests of the exact registered inputs.
- \`agentic_research_handoff.md\`: concise candidate/criticism/remaining-work summary for a human mathematical reviewer.

All artifacts have \`certification=NOT_CERTIFIED\`, \`proof_promotion=NONE\`, \`clay_prize_readiness=NOT_ELIGIBLE\`, and no \`proof_completed=true\` path. They are evidence of *research attempts*, not solved Clay theorems. The agent cannot write to \`docs/proof-analysis/OBLIGATIONS.v1.json\` or modify the seven Clay target definitions.

## Human review checklist

A human subject-matter specialist must perform the following before treating an AI-proposed lemma as new mathematics:

1. **Statement:** are all quantifiers, functional spaces, dimensions, boundary/forcing conditions and noncircular assumptions explicit?
2. **Novelty:** is this already known, and are any source references real? AI-produced citations are leads to check, not verified bibliography.
3. **Proof:** does each logical inference follow, including all analytic convergence, estimates, base cases or complexity-uniformity requirements?
4. **Adversarial challenge:** seek a counterexample, boundary case, known impossibility or circular lemma; record test data and independent derivations.
5. **Implication:** even if a special lemma is true, does it genuinely reach the **full** Clay statement, as formalized in the per-track \`missing_bridge\`?
6. **Formalization:** only formalize precise independently vetted lemmas, with actual compiler/checker confirmation and proof terms; passing a Python model-test is not such a check.
7. **Promotion:** no automatic promotion. A separately approved, mathematically complete and independently accepted proof process is mandatory. Clay's [published rules](https://www.claymath.org/millennium-problems/rules/) govern any prize consideration.

## Workflow failure and recovery policy

| Condition | Required response |
|---|---|
| Canonical register not \`NOT_CERTIFIED\`, any of 14 obligations closed | **Stop**, require human review; do not coerce an updated state |
| Clay target or hypothesis mapping fails | **Stop**; resolve discrepancy by a reviewed PR |
| Existing bounded probe fails | **Stop**, preserve logs, self-correct code only via ordinary CI and PR review |
| Missing API credentials or unavailable model | **Stop**; never silently claim a live AI run occurred |
| AI produces malformed JSON or forbidden verdict | **Stop**, mark candidate untrusted; no proof output |
| Skeptic finds a gap | Revise the candidate within the round/call budget, then hand off remaining concerns |
| AI reviewer requests human review | Stop generation and present evidence packet to human experts |
| Repeated rounds without proof | Report unresolved hypothesis and explicit missing bridge; **NOT_CERTIFIED** |

**What this agent does not do:** search the live web for sources; execute generated code; run unbounded simulations; conduct independent peer review; prove new lemmas in Lean automatically; submit to Clay; certify any of the seven problems; or monitor continually without an explicitly launched workflow.

## The seven targeted research questions

The seven problem-specific questions are drawn directly from \`docs/research/CLAY_FULL_TARGETS.v1.json\` and remain limited by their listed missing bridges: (1) all-zero Li/spectral correspondence on RH; (2) unrestricted SAT algorithm/complexity separation; (3) one exact official Navier–Stokes alternative; (4) physical-unit continuum 4D Yang–Mills; (5) primitive rational Hodge algebraic cycles; (6) elliptic analytic/algebraic rank and refined BSD; (7) independent reconstruction of the externally solved Poincaré proof.

MathOS will learn the most from **falsifiable, precise sublemmas**, with failed attempts recorded instead of hidden. AI generation accelerates hypothesis search, not mathematical certification.
