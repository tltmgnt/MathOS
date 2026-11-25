# PNP-F034 — Complete DIMACS lexical selected-charge composition

PNP_RESOLUTION_STATUS = OPEN. Base f8169a3b27a56cf112dbb579e84a2101384dff09
contains both prior metering merges. PR #184 final head
80db72161321e3ee0e1dc71d08fb572bec5d4838 passed adaptive CI
45518854359 job 138885258193: 41 zero-axiom declarations,
134 files, 53 decoded pairs, 8 hand controls, expected_ok=59,
envelope_ok=61, selected=1748558. Artifact 14979651477.
Initial run 45516923757 job 138878628888 failed, including:
artifacts/pnp-f030/f034-typed-parser-meter-combined.lean:6977:54: error: unused variable `vs`
artifacts/pnp-f030/f034-typed-parser-meter-combined.lean:7051:4: error: type mismatch
artifacts/pnp-f030/f034-typed-parser-meter-combined.lean:7051:4: error: tactic 'changeLocalDecl' failed, given type
artifacts/pnp-f030/f034-typed-parser-meter-combined.lean:7071:6: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
PR #185 final head a9f8a0953a5f1a214ec61f1f888bd0a56c7d4f31,
merge 29694eeff56d20ba6b5cdd39651488278f8f40fa, final CI
45518639155 job 138884525439: 13 zero-axiom declarations,
73 files (one oversized skipped), nine hand controls, 71 headers,
140 splits, 3629 words, six bad words, selected=530552.
Artifact 14978882630. Initial run 45517269545 job 138879828656 failed:
artifacts/f034-dimacs-lex-meter/combined.lean:6899:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/f034-dimacs-lex-meter/combined.lean:6907:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/f034-dimacs-lex-meter/combined.lean:6923:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/f034-dimacs-lex-meter/combined.lean:6926:10: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Both initial jobs exited 1.
https://github.com/tltmgnt/MathOS/actions/runs/45518854359/job/138885258193
https://github.com/tltmgnt/MathOS/actions/runs/45518639155/job/138884525439

## Candidate composition

Sequential bind propagates failure. Signed-word traversal is
tail-recursive; two extra credits per attempted word represent
dispatch and reversal, conservatively even on a failed word,
plus EOF credit. Public loop has empty accumulator; auxiliary
bound does not charge reversal of initial accumulator cells.
With W = wordMass and t = word count, candidate sequence
budget is 4W+10t+1. Split grammar bounds both by byte length.
Complete lexMeter charges initial length/guard, header scan
and reversal, six fixed prefix comparison credits, header
split, shape and natural-word conversion, body split and
signed-word loop. Oversized input charges only length/guard.
lexUnit(A) expands to 31A+24 using independent stage maxima.
This is a linear selected-charge bound, not a runtime theorem.
Reversals are structural charges, not instrumented routines.
No integer bit, allocation, closure, stack-space or IO bound.

17 candidate declarations and six hand controls. All 73
DIMACS fixture files including oversize. Marker:
F034_LEX_COMPOSE_OK files=73 hand_controls=6.
The new AGENTS.md pre-PR gate requires exact candidate SHA
replay before opening a PR. No local Lean. Existing gates
preserved, production and main unchanged.
Next: zero-terminated row parsing, custom parser control and
reversal, bit costs, and independent review. No proof discovery
or proof-size theorem; P vs NP remains open.

## First candidate preflight failure and correction

Exact candidate 963b3366dbd3c52a3421d1c57834cf59342979d5,
preflight run 45520070646 job 138889394518, failed strict axiom
validation with exit code 1:
'ProctorDimacsLexerCompose.word_budget_linear' depends on axioms: [propext, Quot.sound]
strict axiom check failed: ProctorDimacsLexerCompose.word_budget_linear

Five downstream declarations inherited the same dependencies:
signed_words_bound, body_bound, rest_bound, after_header_bound,
lex_bound. The executable fixture marker did pass:
F034_LEX_COMPOSE_OK files=73 hand_controls=6
F034_LEX_COMPOSE_TOTAL lexical_accept=63 lexical_reject=10 selected=1641507
Artifact 14979403248. These are actual first-candidate fixture
results, not a successful kernel audit. Correction replaces
both AC tactic invocations with explicit constructive Nat.add_assoc,
Nat.add_comm, congrArg and equality transitivity. No theorem
statement, meter implementation, fixture or gate is changed.
Corrected candidate must pass exact-SHA preflight before PR.
https://github.com/tltmgnt/MathOS/actions/runs/45520070646/job/138889394518
