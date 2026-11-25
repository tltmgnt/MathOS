# PNP-F034 — Selected DIMACS lexical primitive meters

PNP_RESOLUTION_STATUS = OPEN. At submission PR #184 is still
open, adaptive run 45516923757 job 138878628888 in progress.
This independent branch starts from the verified #183 merge
a28a1558c61b7489aa1a132db77ccc0ce1714062 rather than relying
on unverified typed-parser meters. The separate additive
workflow avoids conflict with the pending adaptive workflow.
https://github.com/tltmgnt/MathOS/pull/184
https://github.com/tltmgnt/MathOS/actions/runs/45516923757/job/138878628888

## Selected charge model

Header meter counts visited bytes (including the first LF) or
EOF if reached, using a tail-recursive accumulator, plus the
length of the returned header to represent reversal cell visits.
For A input bytes it has selected bound 2A+1.

Splitting charges A+1 visits (all bytes and EOF), sum of
returned word lengths (inner reversal cell visits) and number
of returned words (outer reversal cell visits). It reuses the
production splitWords and derives structural reversal charges
from the output; reversal routines are not instrumented. The
independent Split grammar proves the mass bound even with
arbitrary accumulators. With empty accumulators, the bound
is 3A+1.

Natural word conversion charges copied word cells for appending
LF, verified decimal tokenizer charges and one result-shape test.
For length w, naturalUnit is 4w+6. Signed conversion adds one
sign/empty case charge, plus a conservative extra charge for the
negative-zero guard in the minus branch (even if the natural
word fails). signedUnit is 4w+8. Bounds include malformed words.
No claim of exact arithmetic/branch/allocator instruction count.

Thirteen candidate theorems: header accumulator projection
and bound, header length and composed meter, split mass and
meter, natural word projection/bound/monotonicity and signed
word projection/bound. No production checker changes.
The fixture runner checks 73 existing DIMACS files and nine
hand controls. Oversize files are explicitly skipped at the
same limit as the production lexer; no charge for reading them
is claimed. For other files the runner checks header, splitting
after valid prefix and individual word conversion. It deliberately
checks all split words, even after a malformed word; aggregate
fixture counts are not a production lexDimacs execution trace.
The candidate local bounds are not a whole-lexer theorem.
Marker F034_DIMACS_LEX_METER_OK files=73 hand_controls=9.
Strict Lean 4.14.0 zero-axiom gate, new CI pending, no local Lean.

Remaining: compose signed-word traversal and header/prefix/lex
stages, meter zero-terminated DIMACS rows, complete custom parser
control/reversal accounting once #184 is verified, then explicit
bit-cost accounting. No total runtime, stack-space, allocation,
compiler or IO refinement, independent review or proof discovery
or size result. Main unchanged.
