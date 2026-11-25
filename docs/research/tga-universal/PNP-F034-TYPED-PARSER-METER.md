# PNP-F034 — Typed parser token-read metering

PNP_RESOLUTION_STATUS = OPEN. PR #183 merged at
a28a1558c61b7489aa1a132db77ccc0ce1714062. Initial CI
45513952084 job 138868448725 failed:
deep recursion was detected at 'interpreter' (potential solution: increase stack space in your system)
Process completed with exit code 1.
Repository correction 5fa212c23cc2f501addf376122d6b5213c33da6c
added a tail-recursive scanAux and proved correspondence to
scanSpec, avoiding pending per-byte additions on the interpreter
stack. Final CI 45515510539 job 138873787021 passed all seven
gated zero-axiom declarations, 134 files (127 lexical accepts,
7 lexical rejects), eight hand controls, total selected 1726755.
Artifact 14977249494.
https://github.com/tltmgnt/MathOS/actions/runs/45513952084/job/138868448725
https://github.com/tltmgnt/MathOS/actions/runs/45515510539/job/138873787021

## New selected charge semantics

MeterParser returns the normal optional parsed value/remainder
plus a natural count. Charge one per attempted natural-token
read (including failed read at EOF). Guard comparisons, bind,
list iteration, reversal, constructor and integer costs are
not charged. This is a selected submeter, NOT a complete
parser runtime bound. Good is a resource invariant:
success: count + remainder.length = input.length;
failure: count <= input.length+1.
The generic bind composition conserves consumed tokens
and passes at most one EOF failure charge. Pure and
explicit failure cost zero. List parsing counts its length
prefix even when the guard rejects. A tail-recursive
manyRun carries charge in its accumulator, with candidate
correspondence to manySpec to avoid the previous scanner
stack issue. This is not a verified stack-space bound.

All typed parser branches are mirrored, including malformed
magic, boolean, length and terminal tag rejection, nested
lists and exact trailing-token rejection. Value theorem
for each parser relates it to the existing production
parser. Good proves its token read bound on all inputs,
including malformed, oversized list declarations and
truncation. Combined decodeMeter adds verified scanner
charges, typed read count and one trailing-remainder test
if tokenization succeeds (even if typed parsing fails,
a conservative charge). The bound is tokenBudget(A)+A+2,
i.e. 4A+4, using the prior wire-length theorem. This
counts selected scanner operations and token reads only,
not even all parser primitive operations.

41 candidate gated declarations. Static tests on all
134 files from 67 custom-data pairs; expected 53 decoded
pairs and eight direct token hand controls. Envelope tests
compare canonical encoded outputs and suffixes, not an
unavailable DecidableEq instance. Required marker:
F034_TYPED_PARSER_METER_OK files=134 decoded_pairs=53 hand_controls=8.
New CI pending, no local Lean. Existing production checker
and strict zero-axiom gates unchanged. No independent review,
original scratch port, full machine/runtime, stack bound,
proof discovery/size theorem or unrestricted SAT claim.
Next: charge list/control/reversal work and meter DIMACS
lexing, then bit-cost refinement and unified raw input model.
