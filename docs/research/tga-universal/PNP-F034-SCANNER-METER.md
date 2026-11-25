# PNP-F034 — Decimal scanner selected-resource metering

PNP_RESOLUTION_STATUS = OPEN. PR #182 merged at
6da3d3b7dc3538b6dc2e396bc6cc7a5184611541. Its original head
9ce36f1493342f167046f2cbd1e627f0f8a7d36d passed all 16
observed workflow runs, including adaptive CI 45513220008
job 138865979249. All 13 new declarations had zero axiom
dependencies. 73 DIMACS fixtures, 56 decoded pairs, 22
acceptances, 51 rejections. Artifact 14976298618.
https://github.com/tltmgnt/MathOS/actions/runs/45513220008/job/138865979249

## Scope and candidate theorems

The previous selected verification charges omitted parsing.
ProctorScannerMeter mirrors the custom decimal scanner, including
its exact byte/digit guards and early rejection. The selected count
is one per visited input byte, plus one EOF test if reached.
The tokenization meter additionally charges the entire initial
length traversal, one byte-limit comparison, and one reversal
cell per returned token. If the byte limit fails, charge only
the length traversal and comparison. These are specified charges
of a value-equivalent algorithm, not all operations of the original
implementation. Reversal cost is represented by output length,
not an instrumented reverse routine.

For any byte list of length A, scanMeter's count is <= A+1,
including rejection. Successful scan has count exactly A+1.
For tokenizeMeter, the bound is 3A+2, with exact success
count 2A+2+number of tokens. The successful Wire grammar
bounds returned token count by A. This is valid without assuming
the typed parser or certificate verifier accepts, and also for
oversized byte lists and non-ASCII values. The meter itself is
not used by production code.

Seven candidate theorems establish scanner/tokenizer projection,
scan bound, exact success counts, reversal charge bound and
tokenizer linear selected bound. Tests cover all 134 files from
67 custom data pairs, including malformed and over-limit input.
Eight hand controls include empty input, valid word, leading zero,
missing LF, blank word, two tokens and the 128/129 digit boundary.
Lexical acceptance is not typed or certificate acceptance.
Exact marker F034_SCANNER_METER_OK files=134 hand_controls=8.
New CI pending; no local Lean. Existing strict gates retained.

## Exclusions and follow-up

This does not charge each digit comparison, multiplication by ten,
addition, subtraction, digit counter increment, cons construction,
closure, recursion, memory allocation, actual integer representation
or runtime instruction. In particular 128 digits is a limit,
not a proof of bit-cost refinement. The fixed guard's arithmetic
must be accounted for separately. Typed parser metering, DIMACS
lexer metering, and combined meter for both accepting and rejecting
inputs remain future work. No proof discovery/size guarantee,
independent review, original scratch port, main change or P vs NP
result. Next: typed parser metering including early rejection
and explicit bounds in remaining tokens and nesting.
