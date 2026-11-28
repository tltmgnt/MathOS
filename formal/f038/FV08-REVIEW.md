# FV-08 — verification and independent review gate

Reviewed source checkpoint: c1ab923a1b1278ffd45cb164e0bb53e64edf6fc6 (FV-07).
Status: REVIEW OPEN; MECHANIZED VERIFICATION UNCONFIRMED.
PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Executed evidence

A fresh JS-runtime execution loaded exact committed modules for the FV-04 certificate bridge, FV-05 resource accounting and FV-06 physical audit. Results matched their published counts: seven portable packets and nine corruption rejections; 132 graph cases and 448 sub-budget/264 completion controls; 14,802 transition rows, 42 four-way physical comparisons and 28 cutoffs. FV-07's existing integrated suite remains configured in CI; it was not separately rerun in this checkpoint.

The new FV-08 adversarial audit independently enumerates truth assignments for 384 small Boolean formulas (1–5 coordinates), including satisfiable and unsatisfiable cases. For UNSAT it constructs a complete exponential resolution tree by branching on each variable and citing an actual forbidden original row at each leaf. The existing portable checker and fail-closed release adapter must accept these proofs. For SAT it tests every assignment and tries forged direct and residual refutations. It does not depend on the D7I search algorithm.

|Check|Count|Outcome|
|---|---:|---|
|Formulas|384|155 SAT, 229 UNSAT|
|Valid witnesses|1117|all accepted|
|Invalid witnesses|3625|all rejected|
|Constructed UNSAT certificates|229|all accepted|
|False UNSAT release attempts on SAT formulas|310|all rejected|
|Corrupted UNSAT packets|916|all rejected|
|Timeout controls|384|all UNKNOWN|

No false release was observed in this finite audit. Neither exponential certificate construction nor finite testing is a complexity theorem or proof of general solver completeness.

## Proof-source and axiom gate

A static source inventory of the twelve Lean files at FV-07 found 86 named theorem scripts in seven implementation modules, 11 fixture theorem scripts in five test modules, and 69 authored anonymous examples. No explicit axiom declaration, sorry/admit tactic, unsafe definition or native_decide occurrence was detected in that source scan (a comment containing the English word admit is not a tactic). This is not evidence of Lean elaboration, kernel acceptance, or actual theorem dependencies.

The new axiom_audit.py generates fully qualified #print axioms commands for all 97 named theorem scripts, including the named fixtures. It requires exactly one report per expected theorem and rejects missing, duplicate, unexpected and non-allowlisted dependency reports. The accepted standard Lean axioms are propext, Classical.choice and Quot.sound. No sorryAx is allowed. The Python log parser self-test passed locally on synthetic reports, including five negative controls; the local script blob hash matched the repository file. Actual Lean output has not been parsed. The anonymous examples and three generated bridge fixtures are compiled by the workflow but are not part of the 97-name inventory.

The formal Proctor now runs the new independent algorithmic audit, compiles every existing module/test, collects the named theorem axiom reports, and retains logs, audit JSON and the generated dependency manifest as an artifact. It can run for a draft review PR into the isolated research review base, which is anchored at the original pre-formal D7I checkpoint 70dd9f17e1024da4e65f9ef2b46d53b4a40323c9. No merge to main or production promotion is authorized by this gate.

## Open obligations and review disposition

|Gate|Disposition|
|---|---|
|Fresh algorithmic evidence|PASS for the scoped audits listed above|
|Full Lean 4.19.0 build|BLOCKED locally: lean/lake/elan absent; GitHub DNS unavailable in execution container|
|Actual axiom dependency report|PENDING successful Lean build and CI artifact|
|D7A/D7B concrete log and materialized residual refinement|OPEN; current reference transfer enumerates assignments|
|JS raw parsing, source provenance and operational semantics|OPEN; typed proof interface does not verify the whole program|
|D7I graph/count operational proof and total bit complexity|OPEN; conditional count model only|
|IR compiler, exact physical clock formula, raw selector, universal witness semantics|OPEN; quotient equivalence is narrower|
|Independent human mathematical review|OPEN; no external reviewer has approved|
|General SAT completeness or polynomial total running time|NOT ESTABLISHED|
|P vs NP resolution|OPEN|

A successful Lean build would verify the stated scoped theorem scripts, not discharge the open refinement or complexity obligations. Do not mark FV-08 complete or promote the research merely because finite JS tests pass, source contains no admissions, or the CI workflow is configured. Required next action is to obtain real compiler output, fix any build errors, audit the dependency report, and review the assumptions and scope with an independent reviewer.

Reproduce: node mathos/research/f038_rex_fv08_audit.js from repository root; from formal/f038 run python3 axiom_audit.py self-test, compile all modules/tests per the Proctor, python3 axiom_audit.py generate /tmp/F038AllAxioms.lean, lake env lean /tmp/F038AllAxioms.lean > /tmp/f038-axioms.log, then python3 axiom_audit.py verify /tmp/f038-axioms.log.
