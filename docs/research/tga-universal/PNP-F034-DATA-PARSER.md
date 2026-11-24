# PNP-F034 — Data-only input and proof parsing

PNP_RESOLUTION_STATUS = OPEN. PR #167 merged at
ecab9172c26e41b213303a9c31e57c0fc4d93b19. Actual CI run
45482717723 job 138759825233 passed all three Python tests,
all six unified declarations with zero axioms on Lean 4.14.0,
and F034_UNIFIED_REPLAY_OK cases=53. Artifact 14963716032.
https://github.com/tltmgnt/MathOS/actions/runs/45482717723/job/138759825233

## Wire format v1

Each natural number is an ASCII decimal token terminated by
exactly one LF byte. No leading zeros except token 0; no
blank tokens, signs, CR, spaces, comments or trailing data.
A literal is two naturals (variable ID, sign bit: 1 positive,
0 negative). Every list begins with its element count, then
its elements. No data-supplied code or identifiers are parsed.

Expected file: magic 3401, declared variable bound, formula
(list of clauses; each clause is a list of literals).
Proof file: magic 3402, claimed bound, claimed formula, list
of batches (each batch a list of steps), augmented bit,
terminal tag and payload. Step: left index, right index,
pivot, tail clause. Indices zero-based. Terminal tag 0:
empty clause (no payload). Tag 1: lists of demand references,
groups and conflict references. Ref: index then annotated
clause. Group: literal list then capacity. Tag 2: list of
parity blocks; each block is a list of variable IDs, RHS bit,
list of references. All order and duplicates are retained.
Both files must be consumed entirely. The existing typed
bound checker validates labels, indices, exact formula/bound
equality and proof soundness. The custom wire format is not
DIMACS, LRAT, DRAT or a general SAT solver interface.

## Limits and formal scope

ProctorDataParser.lean implements the scanner and recursive
count-prefixed parser. It limits each input to 1,000,000
bytes, each natural to 128 decimal digits and each list
count to 100,000. Counts do not allocate arrays sized by
the variable bound. No claim of a verified resource limit
for total parsing/checking time or memory: the CLI reads
files in full before checking length; the limits apply to
the pure decoder. File I/O, runtime and compiler are not
formally refined. An I/O error fails rather than certifies.

Three candidate theorems link Boolean byte acceptance to
successful decoding and typed boundCheck, UNSAT of the
decoded expected formula, and exact decoded envelope binding.
The semantics of the expected input in these theorems is the
output of the explicit decoder. No separate grammar completeness,
canonical encoding round-trip or DIMACS correspondence theorem
is claimed. The independently supplied expected bytes remain
the caller's responsibility. The theorem is not about file
identity outside the pure checker.

## Static executable path and tests

ProctorDataParserMain.lean is static code. It reads two files
as raw bytes, calls checkBytes and prints CERTIFIED_UNSAT
(exit 0) or REJECTED (exit 1); usage error exit 2. Rejection
does not assert SAT. Build by concatenating the same verified
sources used for the unified checker (without generated fixture
Lean source), then the parser and static main. Run with
lean -DwarningAsError=true --run COMBINED.lean EXPECTED PROOF.
The CI fixture mode reads 67 file pairs with expected verdicts:
53 previous unified cases and 14 malformed byte controls
(trailing tokens, missing LF, bad digits, CRLF, leading zero,
wrong magic, list/digit/byte limits, unknown tag and bad bits).
19 expected acceptances, 48 rejections. A Python exporter
serializes data only; static Lean checks independently supplied
files. No Lean code from these fixture files is evaluated.
Earlier generated-source controls remain unchanged.

Exact marker F034_DATA_REPLAY_OK cases=67 accepted=19 rejected=48
and three zero-axiom declarations required on pinned Lean 4.14.0.
New CI pending. Prior push trigger restriction inherited;
no new gate disabled. No local Lean, independent review,
full Python refinement, machine-cost theorem, original scratch
port or main change. Next: separately specified grammar and
encoder round-trip, file loading resource bounds and a small
standalone checker distribution, before adding proof routes.
