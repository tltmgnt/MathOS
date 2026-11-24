# PNP-F034 — Independent DIMACS raw-byte grammar

PNP_RESOLUTION_STATUS = OPEN. PR #171 merged at
c773e80394447fee4497bbe62779e721705d6256. Initial run 45491016028
job 138789029363 failed:
artifacts/pnp-f030/f034-dimacs-combined.lean:1810:46: error: unknown identifier 'tail'
artifacts/pnp-f030/f034-dimacs-combined.lean:1912:39: error: unknown identifier 'v'
artifacts/pnp-f030/f034-dimacs-combined.lean:1912:46: error: unknown identifier 'g'
Process completed with exit code 1.
Repository correction 0795c264f667e045a41ac996adbf2a07efe6cc3f
constructed evidence before dependent substitution. Final run
45491901662 job 138792136542 passed three Python tests, nine
zero-axiom declarations and F034_DIMACS_REPLAY_OK cases=73
parsed=56 accepted=22 rejected=51. Artifact 14967276741.
https://github.com/tltmgnt/MathOS/actions/runs/45491016028/job/138789029363
https://github.com/tltmgnt/MathOS/actions/runs/45491901662/job/138792136542

## Independent grammar

ProctorDimacsLexical defines raw-byte relations for ASCII whitespace,
maximal whitespace-separated runs (state-indexed grammar with reverse
accumulators), first-LF header separation, fixed header prefix, two
canonical natural fields, signed words and ordered signed sequences.
Natural words use the earlier independent Wire relation on the word
plus one LF, including the decimal and byte limits. Negative zero is
excluded; positive zero is the clause delimiter. LexMeaning combines
these relations with the overall byte bound. RawMeaning combines
LexMeaning with the existing independent zero-terminated Rows grammar
and count bounds. Neither meaning definition invokes the executable
lexer, token scanner or clause parser. The relational split grammar
uses an explicitly defined flush of the accumulator, not splitWords.

Seventeen candidate declarations establish both directions for the
lexical components and complete lexer, then raw_decode_iff and
raw_accepted_unsat. The latter concludes unsatisfiability of the
independently specified raw-byte meaning of the expected file.
The theorem concerns the strict comment-free subset, not full DIMACS.

## Small implementation refactoring

The previous lexer is refactored to use explicit propositional
whitespace tests, an explicit nonempty signed word branch and separate
stripPrefix/headerNumbers helpers. Intended accepted language remains
unchanged; there is no separate proof of equivalence with the prior
implementation. Prior 73 file-pair tests and all nine token-level
theorems are retained. New static CLI bundle includes the grammar
proofs, not generated certificate code. CI executes the same fixture
files through the new lexer and requires all seventeen new exact
zero-axiom declarations. New results pending; no local Lean.

No claim of full DIMACS compatibility, unique external byte encoding,
verified compiler/IO, total resource bound or independent review.
No proof-format extension, main change or unrestricted SAT result.
Next: machine-independent structural resource accounting for the
actual checker, separating local tuple enumeration, reference scans,
sparse integer bit costs and certificate size; then a scoped machine
refinement or explicitly abstract bound.
