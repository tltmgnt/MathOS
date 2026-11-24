# MathOS TGA full-target agentic research process

**Status: executable research orchestration, not a Millennium solution.**

## Objective and inputs
The target is the full seven official Millennium statements, not completion of special use cases. Poincaré is externally established. The current TGA-U003 core graph has 13 distinct modeled open hypotheses, eight alternative joint completion sets of nine leaves each, and seven gaps common to those sets. These are graph-relative counts, not proof percentages. The unchanged canonical register has 14 open work packages. Source audit and SHA-256 digests bind each run to the exact registered targets, proof topology and prior research notes.

## Research loop
1. Gap manager: validate the protected register; compute the joint AND/OR topology and select the least-attempted open leaf. Ties follow the explicit priority order RH, Hodge, Yang–Mills, BSD, P/NP and NS. Alternatives remain visible. This is a fairness policy, not a probability of solution.
2. Planner: specify the actual universal hypothesis, quantifiers, attack and decisive falsifier. No restating a conditional reduction as its proof.
3. Deriver: attempt a mathematical proof or counterexample with numbered steps, dependencies, exact remaining inference and source leads.
4. Adversary: audit the argument for circularity, missing quantifiers, false generalization, analytic assumptions and known barriers. An AI role is not independent review.
5. Evidence runner: execute the registered finite control and, for RH and Hodge, the U003 exact controls. The adversary may additionally request a typed finite computation: exact rational Hankel quadratic form (degree at most seven), rational determinant (dimension at most eight), or exhaustive CNF decision (at most twelve Boolean variables and 64 clauses). The runner validates types and size limits and records the supplied data and actual exact result. Invalid requests are rejected; no generated command or code executes. These checks do not establish the input's relationship to a candidate theorem or verify a universal proof. Other candidate-specific checks need a separately implemented verifier; formalization plans are not proof certificates.
6. Synthesizer: revise the argument using the criticism and actual evidence; classify the packet as unresolved, scoped candidate, proof candidate or counterexample candidate. If the adversary rejects or requests revision, the controller records UNRESOLVED. Even NO_OBVIOUS_FLAW is not proof validation.
7. Publisher: save role results, evidence, source hashes, usage, the exact remaining gap and the next attack in state.json and a standalone Markdown/DOCX packet. Existing paper generator checks text equivalence. Model-authored text is untrusted.
8. Resume and pivot: charge each call before execution; checkpoint after each role; a failed or interrupted attempt stays visible. A new batch selects least-attempted leaves. On return after three attempts on the same leaf the prompts demand a distinct mechanism informed by the three most recent criticisms. No leaf is silently removed.

## Launch and resume
Python 3.11, repository root. No third-party Python dependencies. Run:

```sh
python -m mathos.research.tga_agent --provider offline --attempts 2 --max-calls 8
python -m mathos.research.tga_agent --provider offline --attempts 2 --max-calls 8 --resume
```

Offline mode is a deterministic orchestration fixture, not AI research. It runs real registered tests but produces no new mathematical argument.

For live AI, provision a restricted API project key as GitHub Actions secret MATHOS_OPENAI_API_KEY and choose a Responses-compatible model via repository variable MATHOS_OPENAI_MODEL. After merge to main, manually dispatch Actions > TGA full-target agentic research > openai. Select 1, 2, 4 or 8 attempts (4, 8, 16 or 32 model calls). Only explicit main-branch dispatch can access the API key. Subsequent live runs can specify the previous live run ID to restore its checkpoint and papers. Local execution uses securely configured OPENAI_API_KEY and OPENAI_MODEL with --provider openai. --resume refuses mismatched source hashes, model or provider; choose a new directory for a changed research baseline. The workflow has no automatic paid schedule. API calls may incur charges; ChatGPT subscription does not provide API credits. The output-token cap defaults to 6000 per call (local range 1000–12000); input charges are additional. No automatic API retry or silent mock fallback. One writer per checkpoint directory; do not run concurrent local batches there.

## Completion and process governance
Each run is bounded; completion means a candidate packet with reproducible provenance, not a solved mathematical conjecture. A proof candidate is only a candidate even if all agent roles agree. An independent human reviewer is nonblocking for research continuation. Actual logical validity, complete universal quantifiers, formal checks where available and the official prize process cannot be replaced by AI consensus. The code cannot execute arbitrary model code, change canonical proof states, merge, submit or certify. It does not claim to verify new proofs in Lean or to search external literature automatically. Source leads need verification. To advance a genuine theorem use separately authored, checkable proof artifacts; preserve all counterexamples. End a campaign only on a separately justified mathematical solution or an explicit budget/stop decision, not a pass count.

## Artifacts and regression
state.json (checkpoint and evidence), summary.json (per-run coverage and remaining gaps), attempt-NNNN.md and .docx (standalone packets). A failed API call still consumes one reserved call and is recorded; resume selects the next fair gap. Pull requests and push CI use offline fixtures only, without secrets. Test: python -m unittest discover -s tests -p 'test_tga_agent.py' -v. Existing guarded agent remains available. API reference: https://platform.openai.com/docs/api-reference/responses/create .
