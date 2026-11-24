# TGA-PROCTOR-701 — Autonomous Theorem Discovery and Verified Mathematical Research

**MathOS Academy | Eight-week advanced extension | 64–80 hours**

## Objective
Produce machine-verifiable theorems tied to exact mathematical contracts. The new agent integrates a target registry, typed planner, semantic proctor, symbolic evidence, proof compiler, Lean kernel, repair loop and training graph. It works over unbounded natural numbers, not only finite Boolean cases. The two initial identities are classical. The live model may choose an approved strategy; it does not invent arbitrary proof code or mathematical statements. Offline search is deterministic, not AI-generated research.

## Operating process
1. Freeze a registered recurrence definition and theorem statement, with exact coefficient data and contract hash.
2. Obtain a typed strategy from the deterministic planner or optional live model. Reject substitutions of the target, digest, statement or method. No arbitrary model code is executed.
3. For S(0)=0 and S(n+1)=S(n)+an+b, compare with P(n)=cn²+dn: P(n+1)−P(n)=2cn+c+d. Equality follows by induction if a=2c and b=c+d. If either coefficient differs, n=1 or n=2 gives a counterexample. This is a symbolic argument, not sample extrapolation.
4. Generate Lean from the frozen definition and strategy. The initial reflexivity strategy deliberately fails in the offline fixture; feedback selects induction with distributive and associative-commutative normalization.
5. Run pinned Lean 4.14.0 with warnings as errors and require the theorem's empty axiom report. Preserve source, log, exit code, toolchain and hashes. Failed proof is not proof of falsity.
6. On verified result update only the registered training theorem graph. Publish Markdown, DOCX and JSON evidence. No canonical Millennium status changes, no independent proof authentication inferred from hashes.
7. Stop at proof, counterexample, error or attempt limit. Reserve live calls before invocation and retain partial reports. Start a fresh directory for subsequent batches; existing full-target agent has separate checkpoint/resume.

## Initial benchmarks
Odd sum: S(n+1)=S(n)+2n+1 and S(0)=0. Prove S(n)=n² for every natural n. Even sum: S(n+1)=S(n)+2n+2; prove S(n)=n²+n. Base case is zero; induction substitutes the hypothesis and distributes the successor square. The previous finite-prefix countermodel compiled with propext, failing only the strict empty-axiom policy. The repair uses explicit if_pos and if_neg.

## Eight-week curriculum
Week 1: exact statement and definition, quantifier audit, contract binding and rejected substitutions.
Week 2: symbolic coefficient comparison and invalid recurrence counterexample.
Week 3: unbounded induction; hand proofs of odd and even sums; inspect Lean proof.
Week 4: typed compiler and safe grammar; reject unknown methods and injected code.
Week 5: actual kernel rejection, repair and proof acceptance; interpret diagnostics.
Week 6: provenance, source hashes, toolchain, empty-axiom check and independent replay exercise.
Week 7: training dependency closure and optional authorized live strategy selection; propose a specialist formal contract without asserting its proof.
Week 8: capstone with unseen equivalent recurrence, independent derivation, audit and defense; instructor can extend the trusted registry in a separate branch.

Assessment: statement fidelity 20, symbolic reasoning 20, induction and kernel 25, repair and evidence 15, graph and scope defense 20. Proposed threshold 85/100, at least half in each dimension, at least 20/25 induction, all 501 integrity gates; accountable human assessment only. Accommodations, revision and appeal. No learner outcomes or credentials established.

## Launch
```sh
python -m unittest discover -s tests -p 'test_tga_proctor701.py' -v
python -m mathos.research.tga_proctor701 --target odd_sum --output-dir artifacts/701-odd
python -m mathos.research.tga_proctor701 --target even_sum --output-dir artifacts/701-even
```
After merge to main, configure MATHOS_OPENAI_MODEL repository variable and MATHOS_OPENAI_API_KEY Actions secret. Manually dispatch Proctor 701 agentic induction research with provider openai; two calls maximum. Local --provider openai uses OPENAI_MODEL and OPENAI_API_KEY. No automated paid schedule. Live AI operation requires authorization and has not been established by offline CI.

## Remaining scope gaps
Partial G01/G03: registered statement and typed binding; G04: narrow unbounded induction; G07: local hash-bound records; G08: training graph only. G02 live typed selection implemented but not executed. G05 approved mathlib reasoning, G06 stronger execution isolation, G09 actual specialist mathematical objects, G10 broader proof discovery, G11 independent live deployment, G12 learner outcomes remain open. No claim of solving Millennium conjectures.
