# TGA-PROCTOR-601 — Beyond the verified scope: technical gap analysis

**MathOS | 24 November 2026 | Baseline: 6b800eb2754820babe8b4ff9da555c3e7525150f**

## Executive finding

The verified unified lab is a genuine proof-producing pipeline for supplied Boolean equalities with one to four variables, at most 64 syntax nodes per expression and depth at most 16. It enumerates at most 16 valuations and generates Lean proof text using cases and reflexivity. The previous CI run 45382795894 checked the distributive identity on all eight assignments, compiled it with Lean 4.14.0 and found no axiom dependencies. Eight other elementary supporting lemmas were also kernel-checked. A false Boolean candidate produces an exact counterexample.

But the mathematical research agent outputs natural-language planner, deriver, adversary and synthesizer records; it does not emit a proof object in this language. The candidate is supplied by an operator, not produced by the model. The proof-report's attempt reference is a provenance link, not a logical implication between the identity and a Millennium proof obligation. The decisive engineering gap is **semantic continuity from research claim to formal statement, verified proof and justified dependency closure**.

## 1. Actual verification boundary

| Component | Verified or implemented | Not established |
|---|---|---|
| TGA graph | Authored finite AND/OR routes; minimal completion sets | Truth, completeness or mathematical necessity of edges |
| Agent | Offline role handoff, bounded typed checks, resume | Live mathematical discovery or correctness of free-text derivations |
| Proctor | Schema, call counts, schedule, hash and finite replay checks | Authenticity of model identity, citations, or mathematical arguments |
| Evidence | Rational determinant, Hankel and small CNF controls | Arbitrary quantified real/complex, PDE or geometric theorems |
| Formal translator | Boolean AST, cases and rfl | Unbounded natural/integer arithmetic, induction, real analysis, library theorem use |
| Kernel | Pinned Lean 4.14.0, scoped theorem and axiom report | Semantic fidelity of arbitrary research statements, all open hypotheses |
| Ledger | HMAC with external key and anchored head/count | Independent authorship, public proof attestation, integrated acceptance ledger |
| Publication | Research packet and scoped theorem report | Evidence-backed change of canonical research obligations |

The current source does not claim the above missing properties. This audit therefore identifies extension requirements rather than accusing the existing limited lab of claiming false proofs.

## 2. Boundary experiments

Run the companion diagnostic with a fresh temporary offline agent checkpoint. It checks the following properties.

A. A Boolean identity using five variable slots, even the identity x=x, is rejected at validation. The cap is a resource/grammar boundary, not a mathematical impossibility.

B. The same supplied Boolean identity can be linked to either of two different recorded attempts (RH and Hodge). Both reports have the same mathematical expressions but different attempt provenance. The status is FINITE_CHECK_ONLY when no Lean executable is supplied. This demonstrates that linking an attempt does not establish relevance to its research target.

C. Replace a free-text derivation in a copied offline checkpoint by a different nonempty string. The read-only structural proctor audit still accepts it, because it validates fields and finite replay, not the authenticity or truth of prose. This is a controlled test of the stated trust boundary; it does not modify original evidence or bypass any formal theorem acceptance mechanism.

D. For any fixed N, define f_N(n)=0 if n≤N and 1 otherwise. The observations f_N(0)=...=f_N(N)=0 are all true, but f_N(N+1)=1. Thus no generic inference from a finite prefix to a universal equality can be sound, even with arbitrarily many exact observations. Check N=0,1,4,16,64,256 with integer arithmetic. The companion Lean module proves the general parameterized countermodel, not merely the six samples.

## 3. Topological gap model for the next evolution

The following is an engineering AND/OR model, separate from the seven-problem mathematical register. Open leaves are sufficient work packages in the proposed architecture; their counts are not percentages of a solution. Nodes marked available in this illustrative graph refer only to the successful baseline workflow.

| ID | Work package | Acceptance condition |
|---|---|---|
| G01 | Formal target registry | Freeze exact theorem, domain, definitions, quantifiers, hypotheses and approved dependencies; review mapping from source statement |
| G02 | Structured agent candidate | Live agent produces typed candidate and proposed proof tied to exact registered target; no operator substitution or silent fallback |
| G03 | Semantic translator | Reject mismatched target IDs, altered statements, missing hypotheses, wrong quantifier scopes and weaker conclusions |
| G04 | Inductive arithmetic proof path | Actual unbounded Nat/Int theorem; proof synthesis with induction or algebraic certificates; reject false claim beyond finite samples |
| G05 | Library-based proof path | Pinned Lean/mathlib import and checked proof using approved dependencies; audit the full axiom set and formal statement |
| G06 | Isolation and trusted execution | No arbitrary model code with credentials; network-disabled, resource-bounded execution; pin compiler/dependencies; preserve timeout/exit/log evidence |
| G07 | Acceptance ledger | Bind statement, proof, import and toolchain hashes, actual checker result and accepted assumptions; recheck artifacts and reject substitution, replay and truncation |
| G08 | Proof graph closure | Require checked edge implications and accepted antecedents; reject cycles, unproved assumptions, mismatched scopes; produce new graph version without silently changing register |
| G09 | Research-specific formalization | Define the real mathematical objects in one specialist target; prove one substantive source-aligned sublemma and integrate into actual route |
| G10 | Research search feedback | Use verified results, failed proofs and counterexamples to select and revise next attack with explicit budgets; measure on held-out tasks |
| G11 | Independent deployment evidence | A separately authorized live model run with real provider outputs; independent replay and expert statement-fidelity review |
| G12 | Educational outcome evidence | Actual learners, equivalent-time comparator, unseen assessment, blinded scoring, uncertainty, accessibility and independent replication |

Modeled milestones:
- M1 autonomous bounded theorem production: G01,G02,G03,G06,G07,G11.
- M2 beyond finite Boolean enumeration: M1 AND (G04 OR G05). The alternatives represent two proposed starter proof paths; neither provides general mathematics.
- M3 specialist proof-obligation integration: M2 AND G08,G09,G10.
- M4 defensible course-quality validation: M3 AND G12.

The executable graph calculates minimal completion sets. The common blockers for M3 are all M1 gaps plus G08,G09,G10; one of G04/G05 must also be implemented. G12 is not necessary for the truth of a theorem, but it is necessary in this modeled educational acceptance route. No theorem becomes true because a graph node is marked available.

## 4. Proposed architecture and proof-acceptance contract

Research target registry → agent proposes typed claim/proof → proctor checks statement and scope → deterministic translator or curated theorem template → sandboxed Lean compilation with approved libraries → inspect transitive axioms and actual theorem type → seal reproducible evidence → check matching proof dependency and version graph → feedback to agent.

Proof acceptance must distinguish:
1. REJECTED_INPUT: invalid or unsupported language, target mismatch.
2. COUNTEREXAMPLE: exact witness to the supplied statement's falsity.
3. FINITE_CHECK_ONLY: samples or bounded domain check without formal replay.
4. KERNEL_VERIFIED_SCOPED_THEOREM: exact formal type checked under named hypotheses and approved axioms.
5. TARGET_ALIGNED_VERIFIED_LEMMA: above plus reviewed semantic match and source dependency.
6. ROUTE_DISCHARGED: verified sufficient implication plus all antecedents accepted.
7. GLOBAL_SOLUTION: only when the whole official statement and its mathematical quantifiers have been justified. External recognition is separate.

A kernel proof of P→Q proves that implication; it does not prove Q without P. A zero-axiom report does not eliminate explicit hypotheses. General proof search is not guaranteed to terminate or succeed, and a stronger verifier does not itself derive open theorems. Formal verification of one statement is not automatic verification that the statement is the intended mathematical claim.

## 5. Prioritized implementation sequence

Stage 1: G01/G03 — fixed theorem contracts and mutation tests before enlarging the grammar. Stage 2: G04 — one nontrivial universally quantified arithmetic identity with an induction proof generated from typed data; include false beyond-prefix control. Stage 3: G02/G06/G07/G11 — actual authorized model handoff to that safe compiler, trusted execution, anchored evidence and independent replay. Stage 4: G05/G08/G09 — approved library dependencies, formal edge implications and a real specialist lemma (start with a mathematical reduction whose source assumptions are already understood). Stage 5: G10/G12 — counterexample-guided feedback benchmarks and real educational validation. This sequence is proposed; the diagnostic code does not implement these acceptance gates.

## 6. Millennium mathematical boundary

The engineering milestones do not solve the six unresolved mathematical targets. The TGA-U003 core modeled register has thirteen distinct open leaves, eight alternative joint completion sets of nine leaves each, and seven common leaves. RH needs all-order sparse-shift Hankel positivity or a true negative witness. Hodge needs universal primitive algebraic representatives. P versus NP needs unrestricted polynomial decision or a valid separation. NS needs a full official regularity or breakdown alternative. YM requires continuum construction, axioms and uniform physical gap. BSD needs universal analytic rank equality. Poincare is externally established; local reconstruction remains a separate project. All fourteen canonical MathOS work packages retain their existing status. No promotion.

## Reproduction and sources

Pinned source: 6b800eb2754820babe8b4ff9da555c3e7525150f. Baseline successful workflow: https://github.com/tltmgnt/MathOS/actions/runs/45382795894. Source files: mathos/research/tga_proctor_unified.py, tga_proctor.py, tga_agent.py, tga_proctor_advanced.py; mathos/proof_analysis/gap_analysis.py; formal/Proctor601.lean; curriculum/academy/proctor/TGA-PROCTOR-601.md and 601-PILOT.md. Run python -m mathos.research.tga_proctor_scope_gap; tests python -m unittest discover -s tests -p 'test_tga_proctor_scope_gap.py' -v. Formal countermodel: lean -DwarningAsError=true formal/ProctorScopeGap.lean. The companion workflow records actual replay results separately from this plan. No live API call, learner grade, independent review, or universal solution is claimed.
