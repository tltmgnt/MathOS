# PNP-F034 — Strict DIMACS zero-terminated row meter

PNP_RESOLUTION_STATUS = OPEN. Independent candidate starts from
f8169a3b27a56cf112dbb579e84a2101384dff09, the verified research
parent. Complete lexer composition PR #187, exact head
8cd005b94087aca25b8d929e11e2b22eddc8f70f, passed mandatory
preflight run 45520558958 job 138891011870, all 17 zero-axiom
declarations, 73 fixtures, 63 lexical accepts, 10 rejects, six
hand controls, 1641507 selected charges. Artifact 14978304227.
It was opened only after preflight and remains a separate
unmerged PR at this branch's creation. No dependency on #187.
https://github.com/tltmgnt/MathOS/actions/runs/45520558958/job/138891011870

## Meter and candidate invariants

rowAux scans signed tokens tail-recursively. One charge per
attempted token read including EOF. It stops on positive zero,
rejects negative zero and out-of-range labels, preserves order
and duplicates, and returns exact unconsumed suffix on success.
row_aux_value relates the accumulator to the production parser.
row_aux_good: success count + suffix length = initial count +
input length; failure count <= initial count + input length + 1.
Public rowMeter starts with empty accumulator and zero count.
On success row_count plus prior grammar row_count gives read
count = clause length + 1.

rowsAux parses exactly the declared number of rows, checks
each row length and rejects trailing tokens. It accumulates
rows and charges tail-recursively. Triple each row read charge:
on a successful row of length c, 3(c+1) covers c+1 reads,
c inner reversal cells, c length-traversal cells, one row
length comparison and one outer reversal credit. Failed
row reads are also tripled conservatively. Accumulator
reversal of initial cells is not counted (public initial
accumulator is empty). One charge for final remainder test
when row count reaches zero. This is a selected charge scheme,
not a complete runtime or a measured machine instruction trace.

For T signed tokens, rowMeter <= T+1, rowsMeter <= 3(T+1)+1.
The latter holds even on failure, truncation, arbitrary
declared row count, or size rejection. Independent LexMeaning
proves T <= raw byte length A on successful lexing, including
inputs later rejected by clause parsing. decodeRowsMeter uses
the original lexer without charging it, then adds one credit
for declared-row-limit comparison and row meter if permitted.
Its row-stage bound is 3A+5. It charges zero when lexing fails.
This is not the whole decoder cost until combined with the
complete lexer meter. No arithmetic-bit or stack-space theorem.

13 candidate declarations, strict Lean 4.14.0 zero-axiom gate.
73 DIMACS fixtures, expected 63 lexed, 56 decoded, twelve
direct controls including an over-limit row (100001 literals).
The long control tests the tail-recursive meter, not production
stack safety. Required marker:
F034_DIMACS_ROW_METER_OK files=73 lexed=63 parsed=56 hand_controls=12.
Exact candidate pre-PR replay required by AGENTS.md. No local
Lean, candidate only until replay succeeds; no production
checker changes or main changes. No proof discovery, proof
size, independent review or unrestricted SAT theorem.
Next: integrate verified lexer and row meter, then custom
parser control/reversal and bit-cost refinement.
